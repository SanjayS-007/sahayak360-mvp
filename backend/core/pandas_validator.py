"""
Pandas Cross-Field Validation Engine.
Runs deterministic math checks on validated AST payloads.
"""

import pandas as pd
from typing import Optional

from core.ast_schema import AssessmentEventAST, ValidationResult


def validate_sum_check(ast: AssessmentEventAST) -> ValidationResult:
    """Check that sum of item marks equals declared total."""
    items = ast.academic.items
    declared_total = ast.academic.total_obtained

    if not items:
        return ValidationResult(
            sum_check_passed=True,
            computed_sum=declared_total,
            declared_total=declared_total,
            discrepancy=0.0,
        )

    computed_sum = sum(item.obtained_marks for item in items)
    discrepancy = declared_total - computed_sum
    passed = abs(discrepancy) < 0.01  # float tolerance

    anomaly_flags = []
    if not passed:
        anomaly_flags.append(
            f"SUM_MISMATCH: declared={declared_total}, computed={computed_sum}, diff={discrepancy}"
        )

    return ValidationResult(
        sum_check_passed=passed,
        computed_sum=computed_sum,
        declared_total=declared_total,
        discrepancy=round(discrepancy, 2),
        anomaly_flags=anomaly_flags,
    )


def validate_marks_bounds(ast: AssessmentEventAST) -> list[str]:
    """Check that no item exceeds max and total doesn't exceed max_score."""
    flags = []
    for item in ast.academic.items:
        if item.obtained_marks > item.max_marks:
            flags.append(
                f"OVERFLOW: {item.knowledge_component_name} "
                f"obtained={item.obtained_marks} > max={item.max_marks}"
            )
    if ast.academic.total_obtained > ast.academic.max_score:
        flags.append(
            f"TOTAL_OVERFLOW: total={ast.academic.total_obtained} > max_score={ast.academic.max_score}"
        )
    return flags


def detect_statistical_anomalies(
    ast: AssessmentEventAST,
    historical_scores: Optional[pd.DataFrame] = None,
) -> list[str]:
    """
    Detect statistical outliers using Z-score against historical data.
    If no historical data, skip anomaly detection.
    """
    flags = []
    if historical_scores is None or historical_scores.empty:
        return flags

    for item in ast.academic.items:
        kc_id = item.knowledge_component_id
        pct = item.obtained_marks / item.max_marks if item.max_marks > 0 else 0

        kc_history = historical_scores[
            historical_scores["knowledge_component_id"] == kc_id
        ]
        if len(kc_history) < 3:
            continue

        mean_pct = kc_history["pct"].mean()
        std_pct = kc_history["pct"].std()

        if std_pct > 0:
            z_score = (pct - mean_pct) / std_pct
            if z_score < -2.5:
                flags.append(
                    f"STAT_ANOMALY: {item.knowledge_component_name} "
                    f"score={pct:.2f} is {abs(z_score):.1f} std below mean={mean_pct:.2f}"
                )
            elif pct == 0 and mean_pct > 0.80:
                flags.append(
                    f"ZERO_SCORE_OUTLIER: {item.knowledge_component_name} "
                    f"scored 0% but class mean is {mean_pct:.0%}"
                )

    return flags


def run_full_validation(
    ast: AssessmentEventAST,
    historical_scores: Optional[pd.DataFrame] = None,
) -> ValidationResult:
    """Run all validation checks and return combined result."""
    # 1. Sum check
    result = validate_sum_check(ast)

    # 2. Bounds check
    bounds_flags = validate_marks_bounds(ast)
    result.anomaly_flags.extend(bounds_flags)
    if bounds_flags:
        result.sum_check_passed = False

    # 3. Statistical anomaly detection
    stat_flags = detect_statistical_anomalies(ast, historical_scores)
    result.anomaly_flags.extend(stat_flags)

    return result
