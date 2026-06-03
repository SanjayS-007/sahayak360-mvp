"""
ABC Risk Scorer — Academic, Behavioral, Cognitive EWS (Early Warning System).
Computes a composite risk score for each student based on multi-dimensional signals.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.ast_schema import BehavioralPayload, ParticipationRating
from core.threshold_evaluator import GapDetection, GapSeverity


class RiskTier(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ABCScores:
    """Individual dimension scores (0-100)."""
    academic: float = 0.0
    behavioral: float = 0.0
    cognitive: float = 0.0  # prerequisite gap depth


@dataclass
class RiskAssessment:
    student_id: str
    composite_score: float  # 0-100 (higher = more at-risk)
    tier: RiskTier
    abc_scores: ABCScores
    contributing_factors: list[str]
    urgency_rank: int = 0


# Weights for composite scoring
WEIGHTS = {
    "academic": 0.50,
    "behavioral": 0.25,
    "cognitive": 0.25,
}


def compute_academic_risk(
    overall_mastery: float,
    gaps: list[GapDetection],
    trend_declining: bool = False,
) -> float:
    """
    Academic risk: 0-100 (100 = maximum risk).
    Based on mastery level and gap severity distribution.
    """
    # Base risk from overall mastery (inverse)
    base_risk = (1.0 - overall_mastery) * 60

    # Gap severity contribution
    severity_weights = {
        GapSeverity.MILD: 2,
        GapSeverity.MODERATE: 5,
        GapSeverity.SEVERE: 10,
        GapSeverity.CRITICAL: 15,
    }
    gap_risk = sum(severity_weights.get(g.severity, 0) for g in gaps)
    gap_risk = min(gap_risk, 30)  # cap at 30

    # Trend penalty
    trend_penalty = 10 if trend_declining else 0

    return min(100, base_risk + gap_risk + trend_penalty)


def compute_behavioral_risk(
    behavioral: Optional[BehavioralPayload],
    attendance_pct: Optional[float] = None,
) -> float:
    """
    Behavioral risk: 0-100.
    Based on attendance, participation, and engagement indicators.
    """
    if behavioral is None:
        return 25.0  # neutral if no data

    risk = 0.0

    # Attendance risk
    if attendance_pct is not None:
        if attendance_pct < 0.75:
            risk += 40
        elif attendance_pct < 0.85:
            risk += 20
        elif attendance_pct < 0.95:
            risk += 10

    # Participation risk
    participation_risk = {
        ParticipationRating.ACTIVE: 0,
        ParticipationRating.PASSIVE: 20,
        ParticipationRating.DISENGAGED: 40,
    }
    risk += participation_risk.get(behavioral.participation_rating, 20)

    # Swipe indicator (engagement proxy)
    if behavioral.swipe_indicator is not None:
        if behavioral.swipe_indicator < 0.3:
            risk += 20
        elif behavioral.swipe_indicator < 0.5:
            risk += 10

    return min(100, risk)


def compute_cognitive_risk(
    prerequisite_gap_depth: int,
    bloom_regression_count: int = 0,
) -> float:
    """
    Cognitive risk: 0-100.
    Based on depth of prerequisite gaps and bloom-level regression.
    """
    # Each unmastered prerequisite adds risk
    depth_risk = min(60, prerequisite_gap_depth * 20)

    # Bloom regression (student scoring lower on higher-order questions)
    bloom_risk = min(40, bloom_regression_count * 15)

    return min(100, depth_risk + bloom_risk)


def compute_composite_risk(
    student_id: str,
    academic_risk: float,
    behavioral_risk: float,
    cognitive_risk: float,
    gaps: list[GapDetection],
) -> RiskAssessment:
    """Compute weighted composite risk and assign tier."""
    abc = ABCScores(
        academic=round(academic_risk, 1),
        behavioral=round(behavioral_risk, 1),
        cognitive=round(cognitive_risk, 1),
    )

    composite = (
        WEIGHTS["academic"] * academic_risk
        + WEIGHTS["behavioral"] * behavioral_risk
        + WEIGHTS["cognitive"] * cognitive_risk
    )
    composite = round(composite, 1)

    # Assign tier
    if composite >= 75:
        tier = RiskTier.CRITICAL
    elif composite >= 55:
        tier = RiskTier.HIGH
    elif composite >= 35:
        tier = RiskTier.MODERATE
    else:
        tier = RiskTier.LOW

    # Contributing factors
    factors = []
    if academic_risk >= 60:
        factors.append("academic_performance_low")
    if behavioral_risk >= 50:
        factors.append("behavioral_concerns")
    if cognitive_risk >= 50:
        factors.append("deep_prerequisite_gaps")
    if any(g.severity == GapSeverity.CRITICAL for g in gaps):
        factors.append("critical_gap_present")

    return RiskAssessment(
        student_id=student_id,
        composite_score=composite,
        tier=tier,
        abc_scores=abc,
        contributing_factors=factors,
    )
