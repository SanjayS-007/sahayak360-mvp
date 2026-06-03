"""
MCP Quiz Dispatcher — Model Context Protocol quiz generation and dispatch.
Coordinates between:
  - Gemini (question generation)
  - Neo4j (prerequisite context)
  - WebSocket (real-time delivery to student)
  - PostgreSQL (session persistence)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.knowledge_dag import get_student_gaps, get_prerequisite_chain
from core.threshold_evaluator import GapDetection
from db.models import QuizSession, MasteryRecord


class QuizQuestion:
    """Generated quiz question."""

    def __init__(
        self,
        question_id: str,
        kc_id: str,
        kc_name: str,
        question_text: str,
        options: list[str],
        correct_answer: str,
        bloom_level: str = "understand",
        difficulty: float = 0.5,
    ):
        self.question_id = question_id
        self.kc_id = kc_id
        self.kc_name = kc_name
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer
        self.bloom_level = bloom_level
        self.difficulty = difficulty

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "kc_id": self.kc_id,
            "kc_name": self.kc_name,
            "question_text": self.question_text,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "bloom_level": self.bloom_level,
            "difficulty": self.difficulty,
        }

    def to_student_dict(self) -> dict:
        """Student-facing version (no correct_answer)."""
        return {
            "question_id": self.question_id,
            "kc_id": self.kc_id,
            "question_text": self.question_text,
            "options": self.options,
            "bloom_level": self.bloom_level,
        }


class MCPDispatchResult:
    """Result of a quiz dispatch operation."""

    def __init__(self):
        self.session_id: str = ""
        self.student_id: str = ""
        self.questions: list[QuizQuestion] = []
        self.dispatched_via: str = "http"  # "http" or "websocket"
        self.ws_delivered: bool = False


async def dispatch_micro_test(
    student_id: str,
    teacher_id: str,
    target_kc_ids: list[str],
    num_questions: int,
    db: AsyncSession,
    neo4j_driver=None,
    ws_manager=None,
    gemini_client=None,
    ticket_id: Optional[str] = None,
) -> MCPDispatchResult:
    """
    Full MCP quiz dispatch pipeline:
    1. Fetch student context (mastery state, prerequisites)
    2. Generate questions (Gemini or fallback template)
    3. Create quiz session
    4. Dispatch via WebSocket (if student online) or queue for HTTP poll
    """
    result = MCPDispatchResult()
    result.session_id = f"QZ-{uuid.uuid4().hex[:8].upper()}"
    result.student_id = student_id

    # Step 1: Gather student context for question generation
    context = await _gather_student_context(db, student_id, target_kc_ids)

    # Step 2: Generate questions
    if gemini_client:
        questions = await _generate_questions_gemini(
            gemini_client, target_kc_ids, context, num_questions
        )
    else:
        questions = _generate_fallback_questions(target_kc_ids, context, num_questions)
    result.questions = questions

    # Step 3: Persist quiz session
    session = QuizSession(
        session_id=result.session_id,
        student_id=student_id,
        teacher_id=teacher_id,
        ticket_id=ticket_id,
        target_kc_ids=target_kc_ids,
        questions=[q.to_dict() for q in questions],
        status="pending",
    )
    db.add(session)
    await db.flush()

    # Step 4: Dispatch via WebSocket if student is online
    if ws_manager:
        delivered = await ws_manager.send_to_student(student_id, {
            "type": "quiz_dispatch",
            "session_id": result.session_id,
            "questions": [q.to_student_dict() for q in questions],
            "time_limit_seconds": 600,
            "teacher_id": teacher_id,
        })
        if delivered:
            result.dispatched_via = "websocket"
            result.ws_delivered = True
            session.status = "active"

    return result


async def score_quiz_submission(
    session_id: str,
    responses: list[dict],
    db: AsyncSession,
) -> dict:
    """
    Score a completed quiz and compute mastery deltas.
    Returns: {score, correct_count, total, mastery_deltas}
    """
    stmt = select(QuizSession).where(QuizSession.session_id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise ValueError(f"Quiz session {session_id} not found")

    questions = session.questions or []
    correct_count = 0
    per_kc_results: dict[str, list[bool]] = {}

    for response in responses:
        qid = response.get("question_id")
        answer = response.get("answer")
        question = next((q for q in questions if q["question_id"] == qid), None)

        if question:
            is_correct = answer == question.get("correct_answer")
            if is_correct:
                correct_count += 1
            kc_id = question["kc_id"]
            per_kc_results.setdefault(kc_id, []).append(is_correct)

    total = len(questions)
    score = correct_count / total if total > 0 else 0.0

    # Update session
    session.responses = responses
    session.status = "completed"
    session.score = score
    session.completed_at = datetime.utcnow()

    # Compute per-KC mastery deltas
    mastery_deltas = {}
    for kc_id, results in per_kc_results.items():
        kc_score = sum(1 for r in results if r) / len(results)
        mastery_deltas[kc_id] = round(kc_score, 3)

    return {
        "session_id": session_id,
        "score": round(score, 3),
        "correct_count": correct_count,
        "total": total,
        "mastery_deltas": mastery_deltas,
        "per_kc_results": {k: sum(v) / len(v) for k, v in per_kc_results.items()},
    }


# --- Private helpers ---

async def _gather_student_context(
    db: AsyncSession, student_id: str, target_kc_ids: list[str]
) -> dict:
    """Gather mastery context for question generation."""
    stmt = select(MasteryRecord).where(
        MasteryRecord.student_id == student_id,
        MasteryRecord.kc_id.in_(target_kc_ids),
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return {
        "student_id": student_id,
        "current_mastery": {r.kc_id: r.mastery for r in records},
        "kc_names": {r.kc_id: r.kc_name for r in records},
        "target_kc_ids": target_kc_ids,
    }


async def _generate_questions_gemini(
    client, target_kc_ids: list[str], context: dict, num_questions: int
) -> list[QuizQuestion]:
    """Generate questions using Gemini API via quiz_generator module."""
    from llm.quiz_generator import generate_quiz_questions

    try:
        return await generate_quiz_questions(
            target_kc_ids=target_kc_ids,
            kc_names=context.get("kc_names", {}),
            mastery_levels=context.get("current_mastery", {}),
            num_questions=num_questions,
            student_id=context.get("student_id", ""),
        )
    except Exception:
        return _generate_fallback_questions(target_kc_ids, context, num_questions)


def _generate_fallback_questions(
    target_kc_ids: list[str], context: dict, num_questions: int
) -> list[QuizQuestion]:
    """
    Template-based fallback question generation.
    Used when Gemini is unavailable or for testing.
    """
    questions = []
    kc_names = context.get("kc_names", {})

    for i in range(min(num_questions, len(target_kc_ids) * 2)):
        kc_id = target_kc_ids[i % len(target_kc_ids)]
        kc_name = kc_names.get(kc_id, kc_id)
        mastery = context.get("current_mastery", {}).get(kc_id, 0.5)

        # Adjust difficulty based on current mastery
        difficulty = max(0.3, min(0.9, 1.0 - mastery))

        questions.append(QuizQuestion(
            question_id=f"Q-{uuid.uuid4().hex[:6]}",
            kc_id=kc_id,
            kc_name=kc_name,
            question_text=f"[Auto-generated] Assessment question for: {kc_name} (difficulty: {difficulty:.1f})",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_answer="Option A",
            bloom_level="understand" if mastery < 0.5 else "apply",
            difficulty=difficulty,
        ))

    return questions
