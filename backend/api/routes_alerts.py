"""
Alerts & Interventions routes — Early Warning System, Ticket Management, Risk Breakdown, MTSS Plans.
Surfaces existing core engines (risk_scorer, mtss_engine, ticket_lifecycle) through REST API.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, case, desc
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from db.models import (
    AssessmentEvent,
    InterventionTicket,
    MasteryRecord,
    User,
)
from db.postgres import get_db

router = APIRouter()


# ─── Response Models ─────────────────────────────────────────────────────────

class AlertItem(BaseModel):
    student_id: str
    student_name: str
    alert_type: str
    risk_tier: str
    composite_score: float
    abc_scores: dict = {}
    contributing_factors: list[str] = []
    recommended_action: str = ""
    trend: str = "stable"
    gaps_count: int = 0


class AlertsResponse(BaseModel):
    alerts: list[AlertItem]
    total_critical: int = 0
    total_high: int = 0
    total_moderate: int = 0
    class_section: str


class TicketItem(BaseModel):
    ticket_id: str
    student_id: str
    student_name: str = ""
    teacher_id: str
    ticket_type: str
    priority: str
    status: str
    target_kc_id: str
    target_kc_name: str
    description: str
    created_at: str = ""
    history: list = []


class TicketStatsResponse(BaseModel):
    total: int = 0
    by_status: dict = {}
    by_priority: dict = {}


class RiskBreakdownResponse(BaseModel):
    student_id: str
    student_name: str = ""
    composite_score: float
    risk_tier: str
    abc_scores: dict
    contributing_factors: list[str]
    gap_details: list[dict] = []
    trend: str = "stable"


class MTSSActionItem(BaseModel):
    action_type: str
    target_kc_id: str
    target_kc_name: str
    priority: int
    description: str
    estimated_sessions: int = 1
    can_dispatch: bool = False


class MTSSPlanResponse(BaseModel):
    student_id: str
    assigned_tier: str
    tier_description: str = ""
    actions: list[MTSSActionItem]
    escalation_note: Optional[str] = None
    total_estimated_sessions: int = 0


class TransitionRequest(BaseModel):
    new_status: str
    note: str = ""


# ─── Helper Functions ────────────────────────────────────────────────────────

def _classify_risk_tier(avg_mastery: float) -> tuple[str, float]:
    """Classify risk tier and compute approximate composite score from mastery."""
    # Approximate composite: inverse mastery scaled to 0-100
    academic_risk = (1.0 - avg_mastery) * 60
    # Without behavioral/cognitive data, use academic as proxy
    composite = academic_risk + (10 if avg_mastery < 0.4 else 0)
    composite = min(100, composite)

    if composite >= 55:
        return "critical", composite
    elif composite >= 40:
        return "high", composite
    elif composite >= 25:
        return "moderate", composite
    else:
        return "low", composite


def _compute_factors(avg_mastery: float, gaps_count: int, trend: str) -> list[str]:
    """Determine contributing risk factors."""
    factors = []
    if avg_mastery < 0.4:
        factors.append("academic_performance_low")
    if gaps_count >= 3:
        factors.append("multiple_knowledge_gaps")
    if trend == "declining":
        factors.append("declining_trend")
    if gaps_count >= 5:
        factors.append("critical_gap_present")
    return factors


def _recommend_action(risk_tier: str, gaps_count: int) -> str:
    """Generate recommended action text."""
    if risk_tier == "critical":
        return "Immediate intervention needed — prerequisite review + parent meeting recommended"
    elif risk_tier == "high":
        return "Send targeted micro-test and begin remediation plan"
    elif risk_tier == "moderate":
        return "Monitor closely — extended practice on weak topics"
    return "Continue regular assessment"


async def _compute_student_trend(db: AsyncSession, student_id: str) -> str:
    """Compute trend from last 5 assessment events."""
    result = await db.execute(
        select(AssessmentEvent.total_obtained, AssessmentEvent.max_score)
        .where(AssessmentEvent.student_id == student_id)
        .order_by(desc(AssessmentEvent.created_at))
        .limit(5)
    )
    rows = result.all()
    if len(rows) < 3:
        return "stable"

    scores = [r.total_obtained / r.max_score if r.max_score > 0 else 0 for r in rows]
    if scores[0] > scores[-1] + 0.1:
        return "improving"
    elif scores[0] < scores[-1] - 0.1:
        return "declining"
    return "stable"


# ─── Alert Endpoints ─────────────────────────────────────────────────────────

@router.get("/teacher", response_model=AlertsResponse)
async def get_teacher_alerts(
    class_section: str = Query(...),
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get prioritized alerts for all at-risk students in a class."""
    # Get students in section
    students_result = await db.execute(
        select(User).where(
            User.class_section == class_section,
            User.role == "student",
        )
    )
    students = students_result.scalars().all()

    alerts = []
    total_critical = 0
    total_high = 0
    total_moderate = 0

    for student in students:
        # Get mastery records
        mastery_result = await db.execute(
            select(MasteryRecord).where(
                MasteryRecord.student_id == student.user_id,
                MasteryRecord.subject == subject,
            )
        )
        records = mastery_result.scalars().all()
        if not records:
            continue

        avg_mastery = sum(r.mastery for r in records) / len(records)
        gaps_count = sum(1 for r in records if r.mastery < 0.65)
        trend = await _compute_student_trend(db, student.user_id)

        risk_tier, composite = _classify_risk_tier(avg_mastery)

        # Only include at-risk students (moderate+)
        if risk_tier == "low":
            continue

        # Compute ABC scores approximation
        academic_score = round((1.0 - avg_mastery) * 60 + min(gaps_count * 5, 30), 1)
        cognitive_score = round(min(gaps_count * 20, 60), 1)
        behavioral_score = 25.0  # neutral without behavioral data

        abc_scores = {
            "academic": min(100, academic_score),
            "behavioral": behavioral_score,
            "cognitive": min(100, cognitive_score),
        }

        factors = _compute_factors(avg_mastery, gaps_count, trend)
        recommended = _recommend_action(risk_tier, gaps_count)

        # Determine alert type
        if risk_tier == "critical":
            alert_type = "risk_critical"
            total_critical += 1
        elif risk_tier == "high":
            alert_type = "risk_high"
            total_high += 1
        else:
            alert_type = "risk_moderate"
            total_moderate += 1

        if trend == "declining":
            alert_type = "trend_declining"

        alerts.append(AlertItem(
            student_id=student.user_id,
            student_name=student.full_name,
            alert_type=alert_type,
            risk_tier=risk_tier,
            composite_score=round(composite, 1),
            abc_scores=abc_scores,
            contributing_factors=factors,
            recommended_action=recommended,
            trend=trend,
            gaps_count=gaps_count,
        ))

    # Sort by composite score descending (most urgent first)
    alerts.sort(key=lambda a: a.composite_score, reverse=True)

    return AlertsResponse(
        alerts=alerts,
        total_critical=total_critical,
        total_high=total_high,
        total_moderate=total_moderate,
        class_section=class_section,
    )


# ─── Ticket Endpoints ────────────────────────────────────────────────────────

@router.get("/tickets", response_model=list[TicketItem])
async def get_tickets(
    class_section: str = Query(default=""),
    status: str = Query(default=""),
    student_id: str = Query(default=""),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """List intervention tickets for the teacher, filterable by status and student."""
    conditions = [InterventionTicket.teacher_id == user.user_id]

    if status:
        status_list = [s.strip() for s in status.split(",")]
        conditions.append(InterventionTicket.status.in_(status_list))

    if student_id:
        conditions.append(InterventionTicket.student_id == student_id)

    result = await db.execute(
        select(InterventionTicket)
        .where(*conditions)
        .order_by(InterventionTicket.priority, desc(InterventionTicket.created_at))
        .limit(100)
    )
    tickets = result.scalars().all()

    # Fetch student names in batch
    student_ids = list(set(t.student_id for t in tickets))
    if student_ids:
        names_result = await db.execute(
            select(User.user_id, User.full_name).where(User.user_id.in_(student_ids))
        )
        name_map = {r.user_id: r.full_name for r in names_result.all()}
    else:
        name_map = {}

    return [
        TicketItem(
            ticket_id=t.ticket_id,
            student_id=t.student_id,
            student_name=name_map.get(t.student_id, t.student_id),
            teacher_id=t.teacher_id,
            ticket_type=t.ticket_type or "progress_check",
            priority=t.priority or "P3",
            status=t.status or "open",
            target_kc_id=t.target_kc_id or "",
            target_kc_name=t.target_kc_name or "",
            description=t.description or "",
            created_at=t.created_at.isoformat() if t.created_at else "",
            history=t.history or [],
        )
        for t in tickets
    ]


@router.get("/tickets/stats", response_model=TicketStatsResponse)
async def get_ticket_stats(
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated ticket statistics."""
    result = await db.execute(
        select(InterventionTicket.status, func.count(InterventionTicket.id))
        .where(InterventionTicket.teacher_id == user.user_id)
        .group_by(InterventionTicket.status)
    )
    status_counts = {r[0]: r[1] for r in result.all()}

    priority_result = await db.execute(
        select(InterventionTicket.priority, func.count(InterventionTicket.id))
        .where(
            InterventionTicket.teacher_id == user.user_id,
            InterventionTicket.status.in_(["open", "assigned", "in_progress", "awaiting_evidence"]),
        )
        .group_by(InterventionTicket.priority)
    )
    priority_counts = {r[0]: r[1] for r in priority_result.all()}

    total = sum(status_counts.values())

    return TicketStatsResponse(
        total=total,
        by_status=status_counts,
        by_priority=priority_counts,
    )


@router.patch("/tickets/{ticket_id}/transition")
async def transition_ticket(
    ticket_id: str,
    body: TransitionRequest,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Transition a ticket to a new status (state machine enforced)."""
    from core.ticket_lifecycle import VALID_TRANSITIONS, TicketStatus

    result = await db.execute(
        select(InterventionTicket).where(InterventionTicket.ticket_id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.teacher_id != user.user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your ticket")

    # Validate transition
    current_status = ticket.status
    new_status = body.new_status

    # Check valid transitions
    try:
        current_enum = TicketStatus(current_status)
        target_enum = TicketStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    valid_targets = VALID_TRANSITIONS.get(current_enum, set())
    if target_enum not in valid_targets:
        valid_options = [s.value for s in valid_targets]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_status} → {new_status}. Valid: {valid_options}",
        )

    # Apply transition
    history = ticket.history or []
    history.append({
        "from_status": current_status,
        "to_status": new_status,
        "actor": user.user_id,
        "note": body.note,
        "timestamp": datetime.utcnow().isoformat(),
    })
    ticket.status = new_status
    ticket.history = history

    if new_status == "resolved":
        ticket.resolved_at = datetime.utcnow()

    await db.commit()

    return {"status": "ok", "ticket_id": ticket_id, "new_status": new_status}


# ─── Risk Breakdown ──────────────────────────────────────────────────────────

@router.get("/student-risk/{student_id}", response_model=RiskBreakdownResponse)
async def get_student_risk(
    student_id: str,
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get full ABC risk breakdown for a student."""
    # Get student info
    student_result = await db.execute(
        select(User).where(User.user_id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get mastery records
    mastery_result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.subject == subject,
        )
    )
    records = mastery_result.scalars().all()

    avg_mastery = sum(r.mastery for r in records) / len(records) if records else 0.0
    gaps = [r for r in records if r.mastery < 0.65]

    # Compute ABC scores
    academic_risk = min(100, (1.0 - avg_mastery) * 60 + min(len(gaps) * 5, 30))
    cognitive_risk = min(100, len(gaps) * 20)
    behavioral_risk = 25.0  # neutral without behavioral data

    composite = 0.50 * academic_risk + 0.25 * behavioral_risk + 0.25 * cognitive_risk
    composite = round(min(100, composite), 1)

    # Tier
    if composite >= 55:
        risk_tier = "critical"
    elif composite >= 40:
        risk_tier = "high"
    elif composite >= 25:
        risk_tier = "moderate"
    else:
        risk_tier = "low"

    # Trend
    trend = await _compute_student_trend(db, student_id)

    # Factors
    factors = _compute_factors(avg_mastery, len(gaps), trend)

    # Gap details with severity
    gap_details = []
    for r in gaps:
        if r.mastery < 0.30:
            severity = "critical"
        elif r.mastery < 0.40:
            severity = "severe"
        elif r.mastery < 0.55:
            severity = "moderate"
        else:
            severity = "mild"

        gap_details.append({
            "kc_id": r.kc_id,
            "kc_name": r.kc_name or r.kc_id,
            "mastery": round(r.mastery, 3),
            "severity": severity,
        })

    gap_details.sort(key=lambda g: g["mastery"])

    return RiskBreakdownResponse(
        student_id=student_id,
        student_name=student.full_name,
        composite_score=composite,
        risk_tier=risk_tier,
        abc_scores={
            "academic": round(academic_risk, 1),
            "behavioral": round(behavioral_risk, 1),
            "cognitive": round(cognitive_risk, 1),
        },
        contributing_factors=factors,
        gap_details=gap_details,
        trend=trend,
    )


# ─── MTSS Plan ───────────────────────────────────────────────────────────────

@router.get("/student-mtss/{student_id}", response_model=MTSSPlanResponse)
async def get_student_mtss(
    student_id: str,
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Compute MTSS intervention plan for a student."""
    # Get mastery records (gaps)
    mastery_result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.subject == subject,
        ).order_by(MasteryRecord.mastery)
    )
    records = mastery_result.scalars().all()

    if not records:
        return MTSSPlanResponse(
            student_id=student_id,
            assigned_tier="tier_1",
            tier_description="Universal support — no specific gaps detected",
            actions=[],
            total_estimated_sessions=0,
        )

    avg_mastery = sum(r.mastery for r in records) / len(records)
    gaps = [r for r in records if r.mastery < 0.65]

    # Determine tier from risk level
    academic_risk = min(100, (1.0 - avg_mastery) * 60 + min(len(gaps) * 5, 30))
    cognitive_risk = min(100, len(gaps) * 20)
    composite = 0.50 * academic_risk + 0.25 * 25.0 + 0.25 * cognitive_risk

    if composite >= 55:
        tier = "tier_3"
        tier_desc = "Intensive — individual intervention with specialist support"
    elif composite >= 30:
        tier = "tier_2"
        tier_desc = "Targeted — small-group intervention with focused practice"
    else:
        tier = "tier_1"
        tier_desc = "Universal — classroom-level support with monitoring"

    # Generate actions based on gaps
    actions = []
    priority = 1

    for gap_record in gaps[:5]:  # max 5 actions
        mastery = gap_record.mastery
        kc_id = gap_record.kc_id
        kc_name = gap_record.kc_name or kc_id

        if mastery < 0.30:
            # Critical gap — remediation + micro-test
            actions.append(MTSSActionItem(
                action_type="remedial_content",
                target_kc_id=kc_id,
                target_kc_name=kc_name,
                priority=priority,
                description=f"Intensive remediation for {kc_name} (mastery: {mastery:.0%})",
                estimated_sessions=3,
                can_dispatch=False,
            ))
            priority += 1
            actions.append(MTSSActionItem(
                action_type="micro_test",
                target_kc_id=kc_id,
                target_kc_name=kc_name,
                priority=priority,
                description=f"Diagnostic micro-test to assess current level on {kc_name}",
                estimated_sessions=1,
                can_dispatch=True,
            ))
        elif mastery < 0.40:
            # Severe gap — micro-test
            actions.append(MTSSActionItem(
                action_type="micro_test",
                target_kc_id=kc_id,
                target_kc_name=kc_name,
                priority=priority,
                description=f"Assessment quiz for {kc_name} to pinpoint specific weaknesses",
                estimated_sessions=1,
                can_dispatch=True,
            ))
        elif mastery < 0.55:
            # Moderate gap — extended practice
            actions.append(MTSSActionItem(
                action_type="extended_practice",
                target_kc_id=kc_id,
                target_kc_name=kc_name,
                priority=priority,
                description=f"Extended practice sessions for {kc_name}",
                estimated_sessions=2,
                can_dispatch=False,
            ))
        else:
            # Mild gap — peer tutoring
            actions.append(MTSSActionItem(
                action_type="peer_tutoring",
                target_kc_id=kc_id,
                target_kc_name=kc_name,
                priority=priority,
                description=f"Peer collaborative practice for {kc_name}",
                estimated_sessions=1,
                can_dispatch=False,
            ))
        priority += 1

    # Tier 3 gets parent meeting
    escalation_note = None
    if tier == "tier_3":
        actions.append(MTSSActionItem(
            action_type="parent_meeting",
            target_kc_id="OVERALL",
            target_kc_name="Overall Performance",
            priority=priority,
            description="Schedule parent-teacher meeting for comprehensive support plan",
            estimated_sessions=1,
            can_dispatch=False,
        ))
        escalation_note = f"Student requires Tier 3 intensive intervention. Composite risk: {composite:.0f}. Recommend specialist referral if no improvement in 2 weeks."

    total_sessions = sum(a.estimated_sessions for a in actions)

    return MTSSPlanResponse(
        student_id=student_id,
        assigned_tier=tier,
        tier_description=tier_desc,
        actions=actions,
        escalation_note=escalation_note,
        total_estimated_sessions=total_sessions,
    )
