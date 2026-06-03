"""
Mastery Updater — Bayesian Knowledge Tracing (BKT) inspired mastery update.
Updates student mastery based on new evidence from assessment events.
"""

from dataclasses import dataclass
from typing import Optional

from core.ast_schema import ScoreItem
from core.knowledge_dag import MasteryLevel, mastery_to_level


@dataclass
class BKTParams:
    """Bayesian Knowledge Tracing parameters per KC."""
    p_learn: float = 0.10   # probability of learning per opportunity
    p_guess: float = 0.20   # probability of guessing correctly
    p_slip: float = 0.10    # probability of slipping (knowing but answering wrong)
    p_transit: float = 0.10  # transition probability


@dataclass
class MasteryUpdate:
    kc_id: str
    prior_mastery: float
    posterior_mastery: float
    delta: float
    new_level: MasteryLevel
    evidence: str  # "correct" or "incorrect"


DEFAULT_BKT = BKTParams()


def bayesian_update(
    prior: float,
    is_correct: bool,
    params: BKTParams = DEFAULT_BKT,
) -> float:
    """
    Single Bayesian update step.
    P(L_n | obs) using BKT formula.
    """
    if is_correct:
        # P(L | correct) = P(correct|L) * P(L) / P(correct)
        p_correct_given_l = 1.0 - params.p_slip
        p_correct_given_not_l = params.p_guess
        p_correct = p_correct_given_l * prior + p_correct_given_not_l * (1 - prior)

        if p_correct == 0:
            posterior = prior
        else:
            posterior = (p_correct_given_l * prior) / p_correct
    else:
        # P(L | incorrect) = P(incorrect|L) * P(L) / P(incorrect)
        p_incorrect_given_l = params.p_slip
        p_incorrect_given_not_l = 1.0 - params.p_guess
        p_incorrect = p_incorrect_given_l * prior + p_incorrect_given_not_l * (1 - prior)

        if p_incorrect == 0:
            posterior = prior
        else:
            posterior = (p_incorrect_given_l * prior) / p_incorrect

    # Apply learning transition
    posterior = posterior + (1 - posterior) * params.p_transit

    return round(min(max(posterior, 0.0), 1.0), 4)


def update_from_score_item(
    item: ScoreItem,
    current_mastery: float,
    params: BKTParams = DEFAULT_BKT,
) -> MasteryUpdate:
    """Update mastery for a single KC based on a score item."""
    # Use proportional correctness for partial credit
    if item.max_marks > 0:
        pct = item.obtained_marks / item.max_marks
        # Treat > 80% as correct, < 40% as incorrect, middle as partial
        if pct >= 0.80:
            is_correct = True
        elif pct <= 0.40:
            is_correct = False
        else:
            # Partial credit: weighted average of correct/incorrect updates
            posterior_correct = bayesian_update(current_mastery, True, params)
            posterior_incorrect = bayesian_update(current_mastery, False, params)
            posterior = pct * posterior_correct + (1 - pct) * posterior_incorrect
            return MasteryUpdate(
                kc_id=item.knowledge_component_id,
                prior_mastery=current_mastery,
                posterior_mastery=round(posterior, 4),
                delta=round(posterior - current_mastery, 4),
                new_level=mastery_to_level(posterior),
                evidence=f"partial_{pct:.0%}",
            )
    else:
        is_correct = item.is_correct

    posterior = bayesian_update(current_mastery, is_correct, params)

    return MasteryUpdate(
        kc_id=item.knowledge_component_id,
        prior_mastery=current_mastery,
        posterior_mastery=posterior,
        delta=round(posterior - current_mastery, 4),
        new_level=mastery_to_level(posterior),
        evidence="correct" if is_correct else "incorrect",
    )


def batch_update_mastery(
    items: list[ScoreItem],
    current_masteries: dict[str, float],
    params: BKTParams = DEFAULT_BKT,
) -> list[MasteryUpdate]:
    """
    Process all items from an assessment and update masteries.
    Returns list of mastery updates.
    """
    updates = []
    for item in items:
        current = current_masteries.get(item.knowledge_component_id, 0.1)
        update = update_from_score_item(item, current, params)
        updates.append(update)
        # Update running mastery for subsequent items on same KC
        current_masteries[item.knowledge_component_id] = update.posterior_mastery

    return updates
