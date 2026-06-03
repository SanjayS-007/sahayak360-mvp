"""
Quiz routes — MCP-dispatched micro-test generation and submission.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from db.models import QuizSession, User
from db.postgres import get_db
from mcp.quiz_dispatcher import dispatch_micro_test, score_quiz_submission

router = APIRouter()


class DispatchQuizRequest(BaseModel):
    student_id: str = Field(..., pattern=r"^STU-\d{2,8}$")
    target_kc_ids: list[str] = Field(..., min_length=1)
    num_questions: int = Field(default=5, ge=1, le=20)
    ticket_id: str | None = None


class QuizResponseModel(BaseModel):
    session_id: str
    questions: list[dict]
    time_limit_seconds: int = 600
    dispatched_via: str = "http"


class SubmitQuizRequest(BaseModel):
    session_id: str
    responses: list[dict]


class QuizResult(BaseModel):
    session_id: str
    score: float
    total_questions: int
    correct_count: int
    mastery_deltas: dict = Field(default_factory=dict)


@router.post("/dispatch", response_model=QuizResponseModel)
async def dispatch_quiz(
    req: DispatchQuizRequest,
    request: Request,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Teacher dispatches a micro-test to a student via MCP pipeline."""
    neo4j_driver = getattr(request.app.state, "neo4j_driver", None)
    ws_mgr = getattr(request.app.state, "ws_manager", None)

    result = await dispatch_micro_test(
        student_id=req.student_id,
        teacher_id=user.user_id,
        target_kc_ids=req.target_kc_ids,
        num_questions=req.num_questions,
        db=db,
        neo4j_driver=neo4j_driver,
        ws_manager=ws_mgr,
        gemini_client=True,  # Signals to use Gemini via quiz_generator module
        ticket_id=req.ticket_id,
    )

    return QuizResponseModel(
        session_id=result.session_id,
        questions=[q.to_student_dict() for q in result.questions],
        time_limit_seconds=600,
        dispatched_via=result.dispatched_via,
    )


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    req: SubmitQuizRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Student submits quiz responses."""
    check = await db.execute(
        select(QuizSession).where(QuizSession.session_id == req.session_id)
    )
    session = check.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    if session.student_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not your quiz session")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Quiz already submitted")

    try:
        scoring = await score_quiz_submission(req.session_id, req.responses, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return QuizResult(
        session_id=scoring["session_id"],
        score=scoring["score"],
        total_questions=scoring["total"],
        correct_count=scoring["correct_count"],
        mastery_deltas=scoring.get("mastery_deltas", {}),
    )


@router.get("/sessions")
async def list_quiz_sessions(
    status: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List quiz sessions for current user."""
    query = select(QuizSession)

    if user.role == "student":
        query = query.where(QuizSession.student_id == user.user_id)
    elif user.role == "teacher":
        query = query.where(QuizSession.teacher_id == user.user_id)

    if status:
        query = query.where(QuizSession.status == status)

    query = query.order_by(QuizSession.dispatched_at.desc()).limit(50)
    result = await db.execute(query)
    sessions = result.scalars().all()

    return [
        {
            "session_id": s.session_id,
            "student_id": s.student_id,
            "status": s.status,
            "score": s.score,
            "target_kc_ids": s.target_kc_ids,
            "dispatched_at": s.dispatched_at.isoformat() if s.dispatched_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        }
        for s in sessions
    ]
