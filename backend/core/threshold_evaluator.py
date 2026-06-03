"""
Threshold Evaluator — Deterministic gap detection engine.
Evaluates mastery against configurable thresholds per KC/subject.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.ast_schema import AssessmentEventAST, ScoreItem
from core.knowledge_dag import MasteryLevel, mastery_to_level


class GapSeverity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class ThresholdConfig:
    """Per-subject/grade threshold configuration."""
    mastery_threshold: float = 0.65
    proficiency_threshold: float = 0.85
    critical_threshold: float = 0.30
    severe_threshold: float = 0.40
    moderate_threshold: float = 0.55


@dataclass
class GapDetection:
    kc_id: str
    kc_name: str
    mastery: float
    severity: GapSeverity
    gap_points: float  # how far below threshold
    recommendation: str


DEFAULT_THRESHOLDS = ThresholdConfig()


def classify_severity(mastery: float, config: ThresholdConfig = DEFAULT_THRESHOLDS) -> GapSeverity:
    """Classify gap severity based on mastery level."""
    if mastery >= config.mastery_threshold:
        return GapSeverity.NONE
    elif mastery >= config.moderate_threshold:
        return GapSeverity.MILD
    elif mastery >= config.severe_threshold:
        return GapSeverity.MODERATE
    elif mastery >= config.critical_threshold:
        return GapSeverity.SEVERE
    else:
        return GapSeverity.CRITICAL


def generate_recommendation(severity: GapSeverity, kc_name: str) -> str:
    """Generate action recommendation based on gap severity."""
    recommendations = {
        GapSeverity.NONE: f"{kc_name}: On track, continue practice",
        GapSeverity.MILD: f"{kc_name}: Minor gap — targeted practice needed",
        GapSeverity.MODERATE: f"{kc_name}: Moderate gap — focused intervention required",
        GapSeverity.SEVERE: f"{kc_name}: Severe gap — immediate remediation needed",
        GapSeverity.CRITICAL: f"{kc_name}: Critical gap — prerequisite review + intensive support",
    }
    return recommendations[severity]


def evaluate_single_item(
    item: ScoreItem,
    config: ThresholdConfig = DEFAULT_THRESHOLDS,
) -> GapDetection:
    """Evaluate a single score item against thresholds."""
    mastery = item.obtained_marks / item.max_marks if item.max_marks > 0 else 0.0
    severity = classify_severity(mastery, config)
    gap_points = max(0, config.mastery_threshold - mastery)

    return GapDetection(
        kc_id=item.knowledge_component_id,
        kc_name=item.knowledge_component_name,
        mastery=round(mastery, 3),
        severity=severity,
        gap_points=round(gap_points, 3),
        recommendation=generate_recommendation(severity, item.knowledge_component_name),
    )


def evaluate_assessment(
    ast: AssessmentEventAST,
    config: ThresholdConfig = DEFAULT_THRESHOLDS,
) -> list[GapDetection]:
    """Evaluate all items in an assessment event."""
    gaps = []
    for item in ast.academic.items:
        detection = evaluate_single_item(item, config)
        if detection.severity != GapSeverity.NONE:
            gaps.append(detection)
    return sorted(gaps, key=lambda g: g.mastery)


def compute_overall_mastery(ast: AssessmentEventAST) -> float:
    """Compute overall mastery percentage for the assessment."""
    if ast.academic.max_score == 0:
        return 0.0
    return round(ast.academic.total_obtained / ast.academic.max_score, 3)


def needs_intervention(gaps: list[GapDetection]) -> bool:
    """Determine if the student needs MTSS intervention based on gaps."""
    severe_count = sum(
        1 for g in gaps if g.severity in (GapSeverity.SEVERE, GapSeverity.CRITICAL)
    )
    return severe_count >= 1 or len(gaps) >= 3
