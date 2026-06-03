"""
Dashboard routes — teacher, student, admin analytics.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from db.models import (
    AssessmentEvent,
    InterventionTicket,
    MasteryRecord,
    QuizSession,
    User,
)
from db.postgres import get_db

router = APIRouter()


class ClassOverview(BaseModel):
    total_students: int
    avg_mastery: float
    at_risk_count: int
    pending_tickets: int
    recent_events: int


class StudentSummary(BaseModel):
    student_id: str
    full_name: str
    overall_mastery: float
    gaps_count: int
    risk_tier: str
    last_assessment: str | None = None


class MasteryItem(BaseModel):
    kc_id: str
    kc_name: str
    mastery: float
    mastery_level: str
    attempts: int


@router.get("/teacher/overview", response_model=ClassOverview)
async def teacher_overview(
    class_section: str = Query(...),
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get class-level overview for teacher dashboard."""
    # Count students in this section
    students_result = await db.execute(
        select(func.count(User.id)).where(
            User.class_section == class_section,
            User.role == "student",
        )
    )
    total_students = students_result.scalar() or 0

    # Average mastery across class
    mastery_result = await db.execute(
        select(func.avg(MasteryRecord.mastery)).where(
            MasteryRecord.subject == subject,
            MasteryRecord.student_id.in_(
                select(User.user_id).where(
                    User.class_section == class_section,
                    User.role == "student",
                )
            ),
        )
    )
    avg_mastery = round(mastery_result.scalar() or 0.0, 3)

    # At-risk count (mastery < 0.40)
    risk_result = await db.execute(
        select(func.count(func.distinct(MasteryRecord.student_id))).where(
            MasteryRecord.subject == subject,
            MasteryRecord.mastery < 0.40,
            MasteryRecord.student_id.in_(
                select(User.user_id).where(
                    User.class_section == class_section,
                    User.role == "student",
                )
            ),
        )
    )
    at_risk_count = risk_result.scalar() or 0

    # Pending tickets
    tickets_result = await db.execute(
        select(func.count(InterventionTicket.id)).where(
            InterventionTicket.teacher_id == user.user_id,
            InterventionTicket.status.in_(["open", "assigned", "in_progress"]),
        )
    )
    pending_tickets = tickets_result.scalar() or 0

    # Recent events (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    events_result = await db.execute(
        select(func.count(AssessmentEvent.id)).where(
            AssessmentEvent.teacher_id == user.user_id,
            AssessmentEvent.created_at >= week_ago,
        )
    )
    recent_events = events_result.scalar() or 0

    return ClassOverview(
        total_students=total_students,
        avg_mastery=avg_mastery,
        at_risk_count=at_risk_count,
        pending_tickets=pending_tickets,
        recent_events=recent_events,
    )


@router.get("/teacher/students", response_model=list[StudentSummary])
async def teacher_student_list(
    class_section: str = Query(...),
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get per-student summary for teacher dashboard."""
    # Get students in section
    students_result = await db.execute(
        select(User).where(
            User.class_section == class_section,
            User.role == "student",
        )
    )
    students = students_result.scalars().all()

    summaries = []
    for student in students:
        # Get mastery records
        mastery_result = await db.execute(
            select(MasteryRecord).where(
                MasteryRecord.student_id == student.user_id,
                MasteryRecord.subject == subject,
            )
        )
        records = mastery_result.scalars().all()

        overall = sum(r.mastery for r in records) / len(records) if records else 0.0
        gaps = sum(1 for r in records if r.mastery < 0.65)

        # Determine risk tier
        if overall < 0.30:
            risk = "critical"
        elif overall < 0.50:
            risk = "high"
        elif overall < 0.65:
            risk = "moderate"
        else:
            risk = "low"

        summaries.append(StudentSummary(
            student_id=student.user_id,
            full_name=student.full_name,
            overall_mastery=round(overall, 3),
            gaps_count=gaps,
            risk_tier=risk,
        ))

    return sorted(summaries, key=lambda s: s.overall_mastery)


@router.get("/student/mastery", response_model=list[MasteryItem])
async def student_mastery(
    subject: str = Query(default="mathematics"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mastery breakdown for current student."""
    result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == user.user_id,
            MasteryRecord.subject == subject,
        ).order_by(MasteryRecord.mastery)
    )
    records = result.scalars().all()

    return [
        MasteryItem(
            kc_id=r.kc_id,
            kc_name=r.kc_name,
            mastery=r.mastery,
            mastery_level=r.mastery_level,
            attempts=r.attempts,
        )
        for r in records
    ]


@router.get("/admin/overview")
async def admin_overview(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Admin-level overview across all sections."""
    teachers_result = await db.execute(
        select(func.count(User.id)).where(User.role == "teacher")
    )
    students_result = await db.execute(
        select(func.count(User.id)).where(User.role == "student")
    )
    total_events = await db.execute(select(func.count(AssessmentEvent.id)))
    active_tickets = await db.execute(
        select(func.count(InterventionTicket.id)).where(
            InterventionTicket.status.in_(["open", "assigned", "in_progress"])
        )
    )

    return {
        "total_teachers": teachers_result.scalar() or 0,
        "total_students": students_result.scalar() or 0,
        "total_events": total_events.scalar() or 0,
        "active_interventions": active_tickets.scalar() or 0,
    }
