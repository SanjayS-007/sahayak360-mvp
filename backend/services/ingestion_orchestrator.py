"""
Ingestion Orchestrator — Master pipeline that coordinates all ingestion steps.
Takes raw input → validates → computes gaps → updates mastery → updates graph → triggers interventions.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ast_schema import (
    AssessmentEventAST,
    EventMetadata,
    AcademicPayload,
    IngestionChannel,
    IngestResponse,
    StructuredIngestRequest,
    ValidationResult,
)
from core.pandas_validator import run_full_validation
from core.rehydration_governor import route_structured, ProcessingLane
from core.threshold_evaluator import evaluate_assessment, needs_intervention, compute_overall_mastery
from core.mastery_updater import batch_update_mastery, MasteryUpdate
from core.risk_scorer import (
    compute_academic_risk,
    compute_behavioral_risk,
    compute_cognitive_risk,
    compute_composite_risk,
    RiskAssessment,
)
from core.mtss_engine import build_mtss_plan, MTSSPlan
from core.knowledge_dag import propagate_gap_upstream, KnowledgeNode
from core.ticket_lifecycle import create_ticket_from_action, TicketPriority
from db.models import AssessmentEvent, MasteryRecord, InterventionTicket


class IngestionResult:
    """Full result of processing an assessment event."""

    def __init__(self):
        self.event_id: str = ""
        self.lane: str = "fast_lane"
        self.validation: Optional[ValidationResult] = None
        self.gaps: list = []
        self.mastery_updates: list[MasteryUpdate] = []
        self.risk: Optional[RiskAssessment] = None
        self.mtss_plan: Optional[MTSSPlan] = None
        self.tickets_created: list[str] = []
        self.graph_mutations: list[str] = []


async def orchestrate_structured_ingest(
    request: StructuredIngestRequest,
    db: AsyncSession,
    neo4j_driver=None,
) -> IngestionResult:
    """
    Full pipeline for structured data ingestion.
    Steps: Route → Validate → Gaps → Mastery → Risk → MTSS → Tickets → Persist
    """
    result = IngestionResult()
    result.event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"

    # Step 1: Route through governor (fast lane for structured)
    decision = route_structured(request)
    ast = decision.ast
    result.lane = decision.lane.value

    # Step 2: Run cross-field validation
    validation = run_full_validation(ast)
    ast.validation = validation
    result.validation = validation

    # Step 3: Evaluate threshold gaps
    gaps = evaluate_assessment(ast)
    result.gaps = gaps

    # Step 4: Fetch current mastery state and update
    current_masteries = await _fetch_current_masteries(
        db, ast.metadata.student_id, ast.metadata.subject
    )
    mastery_updates = batch_update_mastery(ast.academic.items, current_masteries)
    result.mastery_updates = mastery_updates

    # Step 5: Compute overall mastery and risk
    overall_mastery = compute_overall_mastery(ast)
    academic_risk = compute_academic_risk(overall_mastery, gaps)
    behavioral_risk = compute_behavioral_risk(ast.behavioral)

    # Compute cognitive risk from prerequisite gap depth
    prereq_gaps = []
    if neo4j_driver and gaps:
        prereq_gaps = await _get_prerequisite_gaps(neo4j_driver, gaps[0].kc_id)
    cognitive_risk = compute_cognitive_risk(len(prereq_gaps))

    risk = compute_composite_risk(
        ast.metadata.student_id,
        academic_risk,
        behavioral_risk,
        cognitive_risk,
        gaps,
    )
    result.risk = risk

    # Step 6: Build MTSS plan if intervention needed
    if needs_intervention(gaps):
        mtss_plan = build_mtss_plan(risk, gaps, [g for g in prereq_gaps[:3]])
        result.mtss_plan = mtss_plan

        # Step 7: Create intervention tickets
        for action in mtss_plan.actions[:5]:  # max 5 tickets per event
            priority = _map_priority(risk.tier.value)
            ticket = create_ticket_from_action(
                student_id=ast.metadata.student_id,
                teacher_id=ast.metadata.teacher_id,
                action_type=action.action_type.value,
                target_kc_id=action.target_kc_id,
                target_kc_name=action.target_kc_name,
                description=action.description,
                priority=priority,
            )
            result.tickets_created.append(ticket.ticket_id)

            # Persist ticket
            db.add(InterventionTicket(
                ticket_id=ticket.ticket_id,
                student_id=ticket.student_id,
                teacher_id=ticket.teacher_id,
                ticket_type=ticket.ticket_type.value,
                priority=ticket.priority.value,
                status=ticket.status.value,
                target_kc_id=ticket.target_kc_id,
                target_kc_name=ticket.target_kc_name,
                description=ticket.description,
            ))

    # Step 8: Persist assessment event
    event = AssessmentEvent(
        event_id=result.event_id,
        student_id=ast.metadata.student_id,
        teacher_id=ast.metadata.teacher_id,
        institution_id=ast.metadata.institution_id,
        department_id=ast.metadata.department_id,
        class_section=ast.metadata.class_section,
        subject=ast.metadata.subject,
        channel=ast.channel.value,
        assessment_type=ast.academic.assessment_type.value,
        assessment_date=ast.metadata.assessment_date,
        max_score=ast.academic.max_score,
        total_obtained=ast.academic.total_obtained,
        items=[item.model_dump() for item in ast.academic.items],
        validation_result=validation.model_dump(),
        cognitive_analysis={
            "gaps": [{"kc_id": g.kc_id, "severity": g.severity.value, "mastery": g.mastery} for g in gaps],
            "needs_intervention": needs_intervention(gaps),
            "risk_tier": risk.tier.value,
            "composite_risk": risk.composite_score,
        },
        pet_data=ast.pet.model_dump() if ast.pet else None,
        behavioral_data=ast.behavioral.model_dump() if ast.behavioral else None,
        parental_data=ast.parental.model_dump() if ast.parental else None,
    )
    db.add(event)

    # Step 9: Upsert mastery records
    for update in mastery_updates:
        record = await _get_mastery_record(db, ast.metadata.student_id, update.kc_id)
        if record:
            record.mastery = update.posterior_mastery
            record.mastery_level = update.new_level.value
            record.attempts += 1
            record.last_event_id = result.event_id
        else:
            kc_name = next(
                (i.knowledge_component_name for i in ast.academic.items
                 if i.knowledge_component_id == update.kc_id),
                update.kc_id,
            )
            db.add(MasteryRecord(
                student_id=ast.metadata.student_id,
                kc_id=update.kc_id,
                kc_name=kc_name,
                subject=ast.metadata.subject,
                mastery=update.posterior_mastery,
                mastery_level=update.new_level.value,
                attempts=1,
                last_event_id=result.event_id,
            ))
        result.graph_mutations.append(f"MASTERY_UPDATE:{update.kc_id}")

    # Step 10: Update Neo4j graph (async, non-blocking on failure)
    if neo4j_driver:
        try:
            await _sync_mastery_to_neo4j(
                neo4j_driver, ast.metadata.student_id, mastery_updates
            )
            result.graph_mutations.append("NEO4J_SYNC:complete")
        except Exception:
            result.graph_mutations.append("NEO4J_SYNC:failed_graceful")

    return result


# --- Private helpers ---

async def _fetch_current_masteries(
    db: AsyncSession, student_id: str, subject: str
) -> dict[str, float]:
    """Load current mastery levels from PostgreSQL."""
    stmt = select(MasteryRecord).where(
        MasteryRecord.student_id == student_id,
        MasteryRecord.subject == subject,
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return {r.kc_id: r.mastery for r in records}


async def _get_mastery_record(
    db: AsyncSession, student_id: str, kc_id: str
) -> Optional[MasteryRecord]:
    """Get a specific mastery record."""
    result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.kc_id == kc_id,
        )
    )
    return result.scalar_one_or_none()


async def _get_prerequisite_gaps(driver, kc_id: str) -> list[str]:
    """Query Neo4j for unmastered prerequisites."""
    from core.knowledge_dag import get_prerequisite_chain
    try:
        chain = await get_prerequisite_chain(driver, kc_id)
        return [item["prereq_id"] for item in chain]
    except Exception:
        return []


async def _sync_mastery_to_neo4j(driver, student_id: str, updates: list[MasteryUpdate]):
    """Sync mastery updates to Neo4j knowledge graph."""
    from core.knowledge_dag import CYPHER_UPSERT_MASTERY
    async with driver.session() as session:
        for update in updates:
            await session.run(
                CYPHER_UPSERT_MASTERY,
                student_id=student_id,
                kc_id=update.kc_id,
                mastery=update.posterior_mastery,
                mastery_level=update.new_level.value,
                attempts=0,
            )


def _map_priority(risk_tier: str) -> TicketPriority:
    """Map risk tier to ticket priority."""
    mapping = {
        "critical": TicketPriority.P1,
        "high": TicketPriority.P2,
        "moderate": TicketPriority.P3,
        "low": TicketPriority.P4,
    }
    return mapping.get(risk_tier, TicketPriority.P3)
