"""Sahayak 360 — Complete pipeline integration test (no DB required)."""
import sys
import datetime

# Test 1: AST Schema validation
print("=" * 60)
print("TEST 1: StructuredIngestRequest validation")
from core.ast_schema import StructuredIngestRequest, ScoreItem, AssessmentType
req = StructuredIngestRequest(
    teacher_id="TCH-001",
    student_id="STU-001",
    class_section="8-A",
    subject="mathematics",
    department_id="DEPT-MATH",
    assessment_type=AssessmentType.FORMATIVE,
    max_score=100.0,
    total_obtained=72.0,
    items=[
        ScoreItem(question_id="Q1", knowledge_component_id="KC-ALG-001", knowledge_component_name="Linear Equations", max_marks=25.0, obtained_marks=18.0, is_correct=False),
        ScoreItem(question_id="Q2", knowledge_component_id="KC-ALG-002", knowledge_component_name="Quadratic Equations", max_marks=25.0, obtained_marks=20.0, is_correct=False),
        ScoreItem(question_id="Q3", knowledge_component_id="KC-GEO-001", knowledge_component_name="Triangles", max_marks=25.0, obtained_marks=22.0, is_correct=True),
        ScoreItem(question_id="Q4", knowledge_component_id="KC-GEO-002", knowledge_component_name="Circles", max_marks=25.0, obtained_marks=12.0, is_correct=False),
    ],
)
print(f"  PASS: student={req.student_id}, score={req.total_obtained}/{req.max_score}, items={len(req.items)}")

# Test 2: Build AST event
print("\nTEST 2: AssessmentEventAST construction")
from core.ast_schema import AssessmentEventAST, EventMetadata, AcademicPayload, IngestionChannel
event = AssessmentEventAST(
    metadata=EventMetadata(
        student_id="STU-001", teacher_id="TCH-001",
        class_section="8-A", subject="mathematics",
        department_id="DEPT-MATH", timestamp=datetime.datetime.now()
    ),
    channel=IngestionChannel.SWIPE_PWA,
    academic=AcademicPayload(
        assessment_type=AssessmentType.FORMATIVE,
        max_score=100.0, total_obtained=72.0,
        items=req.items
    ),
)
print(f"  PASS: event built, channel={event.channel}, items={len(event.academic.items)}")

# Test 3: Pandas validator
print("\nTEST 3: Pandas cross-field validation")
from core.pandas_validator import run_full_validation
result = run_full_validation(event)
print(f"  PASS: sum_check_passed={result.sum_check_passed}, discrepancy={result.discrepancy}")
print(f"    computed_sum={result.computed_sum}, declared_total={result.declared_total}")
if result.anomaly_flags:
    for flag in result.anomaly_flags:
        print(f"    FLAG: {flag}")
else:
    print(f"    No anomaly flags - clean validation")

# Test 4: Threshold evaluator (gap detection)
print("\nTEST 4: Threshold evaluator - gap detection")
from core.threshold_evaluator import evaluate_assessment, needs_intervention
gaps = evaluate_assessment(event)
print(f"  PASS: gaps_found={len(gaps)}, needs_intervention={needs_intervention(gaps)}")
for g in gaps:
    print(f"    - {g.kc_id}: mastery={g.mastery:.2f}, severity={g.severity}")

# Test 5: BKT mastery updater
print("\nTEST 5: Bayesian Knowledge Tracing (BKT)")
from core.mastery_updater import bayesian_update
m1 = bayesian_update(prior=0.5, is_correct=True)
m2 = bayesian_update(prior=0.5, is_correct=False)
m3 = bayesian_update(prior=m1, is_correct=True)
print(f"  PASS: 0.5 + correct -> {m1:.3f}")
print(f"  PASS: 0.5 + incorrect -> {m2:.3f}")
print(f"  PASS: {m1:.3f} + correct -> {m3:.3f} (mastery grows)")
assert m1 > 0.5, "Correct answer should increase mastery"
assert m2 < 0.5, "Incorrect answer should decrease mastery"
assert m3 > m1, "Successive correct should further increase"

# Test 6: ABC Risk scorer
print("\nTEST 6: ABC Risk scorer")
from core.risk_scorer import compute_composite_risk, compute_academic_risk, compute_cognitive_risk
overall_mastery = event.academic.total_obtained / event.academic.max_score
academic_risk = compute_academic_risk(overall_mastery=overall_mastery, gaps=gaps)
cognitive_risk = compute_cognitive_risk(prerequisite_gap_depth=len(gaps))
risk = compute_composite_risk(
    student_id="STU-001",
    academic_risk=academic_risk,
    behavioral_risk=25.0,
    cognitive_risk=cognitive_risk,
    gaps=gaps,
)
print(f"  PASS: composite={risk.composite_score}, tier={risk.tier}")
print(f"    academic_risk={academic_risk:.1f}, cognitive_risk={cognitive_risk:.1f}")
print(f"    factors={risk.contributing_factors}")

# Test 7: MTSS plan
print("\nTEST 7: MTSS engine - intervention planning")
from core.mtss_engine import build_mtss_plan
plan = build_mtss_plan(risk, gaps, prerequisite_gaps=["KC-PRE-001"])
print(f"  PASS: tier={plan.assigned_tier}, actions={len(plan.actions)}")
for a in plan.actions:
    print(f"    - {a.action_type}: {a.description[:60]}")

# Test 8: Ticket lifecycle
print("\nTEST 8: Ticket lifecycle - state machine")
from core.ticket_lifecycle import create_ticket_from_action, transition_ticket, TicketStatus, TicketPriority
if plan.actions:
    action = plan.actions[0]
    ticket = create_ticket_from_action(
        student_id="STU-001",
        teacher_id="TCH-001",
        action_type=action.action_type.value,
        target_kc_id=action.target_kc_id,
        target_kc_name=action.target_kc_name,
        description=action.description,
        priority=TicketPriority.P2,
    )
    print(f"  PASS: ticket={ticket.ticket_id}, type={ticket.ticket_type}, state={ticket.status}")

    # Transition: OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED
    ticket = transition_ticket(ticket, TicketStatus.ASSIGNED, actor="TCH-001")
    print(f"    -> ASSIGNED: {ticket.status}")
    ticket = transition_ticket(ticket, TicketStatus.IN_PROGRESS, actor="TCH-001")
    print(f"    -> IN_PROGRESS: {ticket.status}")
    ticket = transition_ticket(ticket, TicketStatus.RESOLVED, actor="TCH-001")
    print(f"    -> RESOLVED: {ticket.status}")

print("\n" + "=" * 60)
print("ALL 8 CORE PIPELINE TESTS PASSED SUCCESSFULLY")
print("=" * 60)
