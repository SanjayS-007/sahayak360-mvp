"""
Dashboard Analytics Service — Computes aggregated data for dashboards.
Provides class-level, student-level, and institutional analytics.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    AssessmentEvent,
    InterventionTicket,
    MasteryRecord,
    QuizSession,
    User,
)


async def compute_class_analytics(
    db: AsyncSession,
    teacher_id: str,
    class_section: str,
    subject: str = "mathematics",
    days: int = 30,
) -> dict:
    """Compute comprehensive class analytics for teacher dashboard."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get student IDs in section
    student_ids_query = select(User.user_id).where(
        User.class_section == class_section,
        User.role == "student",
    )

    # Total students
    total_result = await db.execute(
        select(func.count()).select_from(student_ids_query.subquery())
    )
    total_students = total_result.scalar() or 0

    # Mastery distribution
    mastery_result = await db.execute(
        select(
            MasteryRecord.student_id,
            func.avg(MasteryRecord.mastery).label("avg_mastery"),
        )
        .where(
            MasteryRecord.student_id.in_(student_ids_query),
            MasteryRecord.subject == subject,
        )
        .group_by(MasteryRecord.student_id)
    )
    student_masteries = mastery_result.all()

    # Classify students by risk
    risk_distribution = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for _, avg_mastery in student_masteries:
        if avg_mastery >= 0.65:
            risk_distribution["low"] += 1
        elif avg_mastery >= 0.50:
            risk_distribution["moderate"] += 1
        elif avg_mastery >= 0.30:
            risk_distribution["high"] += 1
        else:
            risk_distribution["critical"] += 1

    # Top struggling KCs across the class
    kc_result = await db.execute(
        select(
            MasteryRecord.kc_id,
            MasteryRecord.kc_name,
            func.avg(MasteryRecord.mastery).label("avg_mastery"),
            func.count(MasteryRecord.id).label("student_count"),
        )
        .where(
            MasteryRecord.student_id.in_(student_ids_query),
            MasteryRecord.subject == subject,
        )
        .group_by(MasteryRecord.kc_id, MasteryRecord.kc_name)
        .having(func.avg(MasteryRecord.mastery) < 0.65)
        .order_by(func.avg(MasteryRecord.mastery))
        .limit(10)
    )
    struggling_kcs = [
        {
            "kc_id": row.kc_id,
            "kc_name": row.kc_name,
            "avg_mastery": round(row.avg_mastery, 3),
            "student_count": row.student_count,
        }
        for row in kc_result.all()
    ]

    # Recent activity count
    events_result = await db.execute(
        select(func.count(AssessmentEvent.id)).where(
            AssessmentEvent.teacher_id == teacher_id,
            AssessmentEvent.class_section == class_section,
            AssessmentEvent.created_at >= cutoff,
        )
    )
    recent_events = events_result.scalar() or 0

    # Open tickets count
    tickets_result = await db.execute(
        select(func.count(InterventionTicket.id)).where(
            InterventionTicket.teacher_id == teacher_id,
            InterventionTicket.status.in_(["open", "assigned", "in_progress"]),
        )
    )
    open_tickets = tickets_result.scalar() or 0

    # Class average mastery
    class_avg = (
        sum(m for _, m in student_masteries) / len(student_masteries)
        if student_masteries
        else 0.0
    )

    return {
        "total_students": total_students,
        "class_avg_mastery": round(class_avg, 3),
        "risk_distribution": risk_distribution,
        "struggling_kcs": struggling_kcs,
        "recent_events": recent_events,
        "open_tickets": open_tickets,
        "period_days": days,
    }


async def compute_student_profile(
    db: AsyncSession,
    student_id: str,
    subject: str = "mathematics",
) -> dict:
    """Compute detailed student analytics profile."""
    # Mastery records
    mastery_result = await db.execute(
        select(MasteryRecord)
        .where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.subject == subject,
        )
        .order_by(MasteryRecord.mastery)
    )
    records = mastery_result.scalars().all()

    # Assessment history
    events_result = await db.execute(
        select(AssessmentEvent)
        .where(AssessmentEvent.student_id == student_id)
        .order_by(AssessmentEvent.created_at.desc())
        .limit(20)
    )
    events = events_result.scalars().all()

    # Quiz history
    quiz_result = await db.execute(
        select(QuizSession)
        .where(
            QuizSession.student_id == student_id,
            QuizSession.status == "completed",
        )
        .order_by(QuizSession.completed_at.desc())
        .limit(10)
    )
    quizzes = quiz_result.scalars().all()

    # Compute trend (last 5 events)
    recent_scores = [
        e.total_obtained / e.max_score if e.max_score > 0 else 0
        for e in events[:5]
    ]
    trend = "stable"
    if len(recent_scores) >= 3:
        if recent_scores[0] > recent_scores[-1] + 0.1:
            trend = "improving"
        elif recent_scores[0] < recent_scores[-1] - 0.1:
            trend = "declining"

    # Overall mastery
    overall = sum(r.mastery for r in records) / len(records) if records else 0.0

    # Gaps
    gaps = [
        {"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": r.mastery}
        for r in records
        if r.mastery < 0.65
    ]

    # Strengths
    strengths = [
        {"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": r.mastery}
        for r in records
        if r.mastery >= 0.85
    ]

    return {
        "student_id": student_id,
        "overall_mastery": round(overall, 3),
        "trend": trend,
        "total_kcs": len(records),
        "gaps": gaps,
        "strengths": strengths,
        "assessment_count": len(events),
        "quiz_count": len(quizzes),
        "recent_scores": recent_scores,
    }


async def compute_mastery_heatmap(
    db: AsyncSession,
    class_section: str,
    subject: str = "mathematics",
) -> list[dict]:
    """
    Generate mastery heatmap data: students × KCs matrix.
    Used by the heatmap visualization component.
    """
    # Get students
    students_result = await db.execute(
        select(User.user_id, User.full_name).where(
            User.class_section == class_section,
            User.role == "student",
        )
    )
    students = students_result.all()

    # Get all KCs for the subject in this class
    kcs_result = await db.execute(
        select(MasteryRecord.kc_id, MasteryRecord.kc_name)
        .where(
            MasteryRecord.subject == subject,
            MasteryRecord.student_id.in_([s.user_id for s in students]),
        )
        .distinct()
    )
    kcs = kcs_result.all()

    # Build heatmap matrix
    heatmap = []
    for student in students:
        mastery_result = await db.execute(
            select(MasteryRecord.kc_id, MasteryRecord.mastery).where(
                MasteryRecord.student_id == student.user_id,
                MasteryRecord.subject == subject,
            )
        )
        mastery_map = {row.kc_id: row.mastery for row in mastery_result.all()}

        heatmap.append({
            "student_id": student.user_id,
            "student_name": student.full_name,
            "masteries": {kc.kc_id: mastery_map.get(kc.kc_id, 0.0) for kc in kcs},
        })

    return heatmap
