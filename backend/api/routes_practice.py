"""
Practice routes — progressive difficulty practice system.
"""

import json
import random
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from db.models import MasteryRecord, User, Notification
from db.postgres import get_db
from api.routes_gamification import award_xp

router = APIRouter()

# Load question bank
_questions_path = os.path.join(os.path.dirname(__file__), "..", "data", "practice_questions.json")
with open(_questions_path, "r", encoding="utf-8") as f:
    QUESTION_BANK = json.load(f)


class PracticeRequest(BaseModel):
    kc_id: str
    difficulty: Optional[str] = None  # auto-select based on mastery if None
    count: int = 5


class AnswerSubmission(BaseModel):
    kc_id: str
    difficulty: str
    answers: list  # [{question_id, selected_index}]


def _get_difficulty_for_mastery(mastery: float) -> str:
    """Progressive difficulty: pick level based on current mastery."""
    if mastery < 0.4:
        return "basic"
    elif mastery < 0.7:
        return "medium"
    else:
        return "advanced"


@router.post("/generate")
async def generate_practice(
    req: PracticeRequest,
    user: User = Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    """Generate practice questions for a KC at appropriate difficulty."""
    # Determine difficulty
    difficulty = req.difficulty
    if not difficulty:
        # Auto from mastery
        result = await db.execute(
            select(MasteryRecord.mastery).where(
                MasteryRecord.student_id == user.user_id,
                MasteryRecord.kc_id == req.kc_id,
            )
        )
        mastery_val = result.scalar() or 0.0
        difficulty = _get_difficulty_for_mastery(mastery_val)

    # Get questions from bank
    kc_questions = QUESTION_BANK.get(req.kc_id, {})
    available = kc_questions.get(difficulty, [])

    if not available:
        raise HTTPException(404, f"No questions available for {req.kc_id} at {difficulty} level")

    # Pick random subset
    count = min(req.count, len(available))
    selected = random.sample(available, count)

    # Strip correct_index and explanation for client
    questions_for_client = []
    for q in selected:
        questions_for_client.append({
            "id": q["id"],
            "text": q["text"],
            "options": q["options"],
        })

    return {
        "kc_id": req.kc_id,
        "difficulty": difficulty,
        "questions": questions_for_client,
        "count": count,
    }


@router.post("/submit")
async def submit_practice(
    submission: AnswerSubmission,
    user: User = Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    """Submit practice answers, score, and update mastery."""
    kc_questions = QUESTION_BANK.get(submission.kc_id, {})
    available = kc_questions.get(submission.difficulty, [])

    if not available:
        raise HTTPException(404, "Question set not found")

    # Build lookup
    q_map = {q["id"]: q for q in available}

    correct = 0
    total = len(submission.answers)
    results = []

    for ans in submission.answers:
        q = q_map.get(ans.get("question_id"))
        if not q:
            continue
        is_correct = ans.get("selected_index") == q["correct_index"]
        if is_correct:
            correct += 1
        results.append({
            "question_id": q["id"],
            "correct": is_correct,
            "correct_index": q["correct_index"],
            "explanation": q["explanation"],
        })

    score = correct / total if total > 0 else 0

    # Update mastery record
    result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == user.user_id,
            MasteryRecord.kc_id == submission.kc_id,
        )
    )
    mastery_rec = result.scalar_one_or_none()

    mastery_delta = score * 0.1  # practice gives up to +10% mastery boost
    new_mastery = 0.0

    if mastery_rec:
        new_mastery = min(1.0, mastery_rec.mastery + mastery_delta)
        mastery_rec.mastery = new_mastery
        mastery_rec.attempts = (mastery_rec.attempts or 0) + 1
        mastery_rec.updated_at = datetime.utcnow()
        # Update level
        if new_mastery >= 0.8:
            mastery_rec.mastery_level = "mastered"
        elif new_mastery >= 0.6:
            mastery_rec.mastery_level = "proficient"
        elif new_mastery >= 0.4:
            mastery_rec.mastery_level = "developing"
        else:
            mastery_rec.mastery_level = "beginning"
    else:
        new_mastery = mastery_delta
        level = "beginning"
        if new_mastery >= 0.4:
            level = "developing"
        mastery_rec = MasteryRecord(
            student_id=user.user_id,
            kc_id=submission.kc_id,
            kc_name=submission.kc_id.replace("-", " ").title(),
            subject="Mathematics",
            mastery=new_mastery,
            mastery_level=level,
            attempts=1,
            updated_at=datetime.utcnow(),
        )
        db.add(mastery_rec)

    # Create notification for the student
    notif = Notification(
        user_id=user.user_id,
        type="practice_result",
        title=f"Practice Complete: {submission.kc_id.replace('-', ' ').title()}",
        message=f"You scored {correct}/{total} ({int(score*100)}%) at {submission.difficulty} level. Mastery: {int(new_mastery*100)}%",
        data={"kc_id": submission.kc_id, "score": score, "difficulty": submission.difficulty},
    )
    db.add(notif)

    # Award XP (10 base + 5 per correct + bonus for difficulty)
    diff_bonus = {"basic": 0, "medium": 5, "advanced": 10}.get(submission.difficulty, 0)
    xp_earned = 10 + (correct * 5) + (diff_bonus * correct)
    new_badges = await award_xp(db, user.user_id, xp_earned, correct, total, score)

    await db.commit()

    # Suggest next difficulty
    next_difficulty = submission.difficulty
    if score >= 0.8 and submission.difficulty != "advanced":
        next_difficulty = "medium" if submission.difficulty == "basic" else "advanced"
    elif score < 0.4 and submission.difficulty != "basic":
        next_difficulty = "basic" if submission.difficulty == "medium" else "medium"

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "results": results,
        "mastery_after": new_mastery,
        "next_difficulty": next_difficulty,
        "xp_earned": xp_earned,
        "badges_earned": [{"name": b["name"], "icon": b["icon"]} for b in new_badges],
        "message": "Great job!" if score >= 0.8 else "Keep practicing!" if score >= 0.5 else "Review the explanations and try again.",
    }


@router.get("/available-kcs")
async def get_available_kcs(
    user: User = Depends(require_role("student")),
):
    """List KCs that have practice questions available."""
    kcs = []
    for kc_id, levels in QUESTION_BANK.items():
        total_q = sum(len(qs) for qs in levels.values())
        kcs.append({"kc_id": kc_id, "levels": list(levels.keys()), "total_questions": total_q})
    return {"kcs": kcs}
