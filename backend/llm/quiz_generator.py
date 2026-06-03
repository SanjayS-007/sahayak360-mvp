"""
Quiz Generator — Generates assessment questions via Gemini.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

from llm.gemini_client import generate_json
from mcp.quiz_dispatcher import QuizQuestion

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "quiz_generation.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


async def generate_quiz_questions(
    target_kc_ids: list[str],
    kc_names: dict[str, str],
    mastery_levels: dict[str, float],
    num_questions: int = 5,
    student_id: str = "",
    subject: str = "mathematics",
) -> list[QuizQuestion]:
    """
    Generate quiz questions using Gemini based on target KCs and mastery levels.
    Falls back to template questions if Gemini is unavailable.
    """
    prompt_template = _load_prompt()

    # Build context string
    kc_list = ", ".join(
        f"{kc_id} ({kc_names.get(kc_id, kc_id)})" for kc_id in target_kc_ids
    )
    mastery_str = ", ".join(
        f"{kc_id}: {mastery_levels.get(kc_id, 0.5):.2f}" for kc_id in target_kc_ids
    )

    prompt = prompt_template.replace("{num_questions}", str(num_questions))
    prompt = prompt.replace("{student_id}", student_id)
    prompt = prompt.replace("{kc_list}", kc_list)
    prompt = prompt.replace("{mastery_levels}", mastery_str)
    prompt = prompt.replace("{subject}", subject)

    try:
        questions_data = await generate_json(prompt)
    except (ValueError, RuntimeError) as e:
        logger.warning(f"Gemini quiz generation failed, using fallback: {e}")
        return _generate_fallback(target_kc_ids, kc_names, mastery_levels, num_questions)

    # Parse response into QuizQuestion objects
    questions = []
    if not isinstance(questions_data, list):
        logger.warning("Gemini returned non-list for quiz, using fallback")
        return _generate_fallback(target_kc_ids, kc_names, mastery_levels, num_questions)

    for qdata in questions_data[:num_questions]:
        try:
            questions.append(QuizQuestion(
                question_id=f"Q-{uuid.uuid4().hex[:6]}",
                kc_id=qdata.get("kc_id", target_kc_ids[0] if target_kc_ids else "KC-UNKNOWN"),
                kc_name=qdata.get("kc_name", "Unknown"),
                question_text=qdata.get("question_text", "Question not generated"),
                options=qdata.get("options", ["A", "B", "C", "D"]),
                correct_answer=qdata.get("correct_answer", "A"),
                bloom_level=qdata.get("bloom_level", "understand"),
                difficulty=float(qdata.get("difficulty", 0.5)),
            ))
        except Exception as e:
            logger.warning(f"Failed to parse question: {e}")
            continue

    # If we got fewer than requested, pad with fallback
    if len(questions) < num_questions:
        fallback = _generate_fallback(
            target_kc_ids, kc_names, mastery_levels, num_questions - len(questions)
        )
        questions.extend(fallback)

    return questions


def _generate_fallback(
    target_kc_ids: list[str],
    kc_names: dict[str, str],
    mastery_levels: dict[str, float],
    num_questions: int,
) -> list[QuizQuestion]:
    """Template-based fallback when Gemini is unavailable."""
    questions = []
    for i in range(num_questions):
        kc_id = target_kc_ids[i % len(target_kc_ids)] if target_kc_ids else "KC-UNKNOWN"
        kc_name = kc_names.get(kc_id, kc_id)
        mastery = mastery_levels.get(kc_id, 0.5)
        difficulty = max(0.3, min(0.9, 1.0 - mastery))

        questions.append(QuizQuestion(
            question_id=f"Q-{uuid.uuid4().hex[:6]}",
            kc_id=kc_id,
            kc_name=kc_name,
            question_text=f"[Template] Assessment question {i+1} for: {kc_name}",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_answer="Option A",
            bloom_level="understand" if mastery < 0.5 else "apply",
            difficulty=difficulty,
        ))

    return questions
