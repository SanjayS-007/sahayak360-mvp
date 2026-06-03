"""
MTSS Engine — Multi-Tiered System of Support.
Assigns intervention tiers and generates intervention plans.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.risk_scorer import RiskAssessment, RiskTier
from core.threshold_evaluator import GapDetection, GapSeverity


class MTSSTier(str, Enum):
    TIER_1 = "tier_1"  # Universal — classroom-level
    TIER_2 = "tier_2"  # Targeted — small-group intervention
    TIER_3 = "tier_3"  # Intensive — individual intervention


class InterventionType(str, Enum):
    MICRO_TEST = "micro_test"
    REMEDIAL_CONTENT = "remedial_content"
    PEER_TUTORING = "peer_tutoring"
    PARENT_MEETING = "parent_meeting"
    SPECIALIST_REFERRAL = "specialist_referral"
    PREREQUISITE_REVIEW = "prerequisite_review"
    EXTENDED_PRACTICE = "extended_practice"


@dataclass
class InterventionAction:
    action_type: InterventionType
    target_kc_id: str
    target_kc_name: str
    priority: int  # 1=highest
    description: str
    estimated_sessions: int = 1


@dataclass
class MTSSPlan:
    student_id: str
    assigned_tier: MTSSTier
    risk_assessment: RiskAssessment
    actions: list[InterventionAction]
    escalation_note: Optional[str] = None


def assign_tier(risk: RiskAssessment) -> MTSSTier:
    """Map risk tier to MTSS tier."""
    mapping = {
        RiskTier.LOW: MTSSTier.TIER_1,
        RiskTier.MODERATE: MTSSTier.TIER_2,
        RiskTier.HIGH: MTSSTier.TIER_2,
        RiskTier.CRITICAL: MTSSTier.TIER_3,
    }
    return mapping[risk.tier]


def generate_actions(
    tier: MTSSTier,
    gaps: list[GapDetection],
    prerequisite_gaps: list[str],
) -> list[InterventionAction]:
    """Generate intervention actions based on tier and detected gaps."""
    actions = []
    priority = 1

    # Prerequisite remediation first (all tiers if applicable)
    for prereq_id in prerequisite_gaps[:3]:  # max 3 prerequisite reviews
        actions.append(InterventionAction(
            action_type=InterventionType.PREREQUISITE_REVIEW,
            target_kc_id=prereq_id,
            target_kc_name=prereq_id,  # will be enriched later
            priority=priority,
            description=f"Review prerequisite: {prereq_id}",
            estimated_sessions=2,
        ))
        priority += 1

    # Per-gap actions
    for gap in gaps[:5]:  # max 5 gap interventions
        if gap.severity == GapSeverity.CRITICAL:
            actions.append(InterventionAction(
                action_type=InterventionType.REMEDIAL_CONTENT,
                target_kc_id=gap.kc_id,
                target_kc_name=gap.kc_name,
                priority=priority,
                description=f"Intensive remediation for {gap.kc_name} (mastery: {gap.mastery:.0%})",
                estimated_sessions=3,
            ))
        elif gap.severity == GapSeverity.SEVERE:
            actions.append(InterventionAction(
                action_type=InterventionType.MICRO_TEST,
                target_kc_id=gap.kc_id,
                target_kc_name=gap.kc_name,
                priority=priority,
                description=f"Micro-test to assess current level on {gap.kc_name}",
                estimated_sessions=1,
            ))
        elif gap.severity == GapSeverity.MODERATE:
            actions.append(InterventionAction(
                action_type=InterventionType.EXTENDED_PRACTICE,
                target_kc_id=gap.kc_id,
                target_kc_name=gap.kc_name,
                priority=priority,
                description=f"Extended practice for {gap.kc_name}",
                estimated_sessions=2,
            ))
        else:
            actions.append(InterventionAction(
                action_type=InterventionType.MICRO_TEST,
                target_kc_id=gap.kc_id,
                target_kc_name=gap.kc_name,
                priority=priority,
                description=f"Quick check on {gap.kc_name}",
                estimated_sessions=1,
            ))
        priority += 1

    # Tier-specific extras
    if tier == MTSSTier.TIER_3:
        actions.append(InterventionAction(
            action_type=InterventionType.PARENT_MEETING,
            target_kc_id="OVERALL",
            target_kc_name="Overall Performance",
            priority=priority,
            description="Schedule parent-teacher meeting for comprehensive support plan",
            estimated_sessions=1,
        ))

    return actions


def build_mtss_plan(
    risk: RiskAssessment,
    gaps: list[GapDetection],
    prerequisite_gaps: list[str],
) -> MTSSPlan:
    """Build complete MTSS intervention plan."""
    tier = assign_tier(risk)
    actions = generate_actions(tier, gaps, prerequisite_gaps)

    escalation_note = None
    if tier == MTSSTier.TIER_3:
        escalation_note = (
            f"Student {risk.student_id} requires Tier 3 intensive intervention. "
            f"Composite risk: {risk.composite_score}. "
            f"Factors: {', '.join(risk.contributing_factors)}"
        )

    return MTSSPlan(
        student_id=risk.student_id,
        assigned_tier=tier,
        risk_assessment=risk,
        actions=actions,
        escalation_note=escalation_note,
    )
