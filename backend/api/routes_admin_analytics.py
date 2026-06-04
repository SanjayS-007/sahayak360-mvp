"""
Admin Analytics routes — school-wide decision support endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_role
from db.session import get_db
from db.models import (
    User,
    MasteryRecord,
    InterventionTicket,
    AssessmentEvent,
)

router = APIRouter()


@router.get("/risk-heatmap")
async def risk_heatmap(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Risk heatmap: section × subject matrix."""
    # Get all students grouped by class_section with risk stats
    students = await db.execute(
        select(
            User.class_section,
            func.count(User.id).label("total"),
            func.sum(case((MasteryRecord.mastery_level == "below_basic", 1), else_=0)).label("at_risk"),
        )
        .outerjoin(MasteryRecord, MasteryRecord.student_id == User.user_id)
        .where(User.role == "student")
        .group_by(User.class_section)
    )
    rows = students.all()

    sections = []
    for row in rows:
        section = row.class_section or "Unknown"
        total = row.total or 1
        at_risk = row.at_risk or 0
        risk_pct = round((at_risk / max(total, 1)) * 100)
        sections.append({
            "section": section,
            "total_students": total,
            "at_risk_count": at_risk,
            "risk_percentage": risk_pct,
            "subjects": {
                "mathematics": risk_pct,  # Primary subject in our system
            },
        })

    return {"sections": sections}


@router.get("/section-comparison")
async def section_comparison(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Compare sections by average mastery."""
    result = await db.execute(
        select(
            User.class_section,
            func.count(func.distinct(User.id)).label("student_count"),
            func.avg(MasteryRecord.p_mastery).label("avg_mastery"),
        )
        .outerjoin(MasteryRecord, MasteryRecord.student_id == User.user_id)
        .where(User.role == "student")
        .group_by(User.class_section)
    )
    rows = result.all()

    sections = []
    for row in rows:
        sections.append({
            "section": row.class_section or "Unknown",
            "student_count": row.student_count,
            "avg_mastery": round(float(row.avg_mastery or 0), 3),
        })

    return {"sections": sorted(sections, key=lambda x: x["avg_mastery"], reverse=True)}


@router.get("/effectiveness")
async def intervention_effectiveness(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Intervention effectiveness by type."""
    # Count tickets by type and status
    result = await db.execute(
        select(
            InterventionTicket.ticket_type,
            func.count(InterventionTicket.id).label("total"),
            func.sum(case((InterventionTicket.status == "resolved", 1), else_=0)).label("resolved"),
        )
        .group_by(InterventionTicket.ticket_type)
    )
    rows = result.all()

    by_type = []
    for row in rows:
        total = row.total or 1
        resolved = row.resolved or 0
        # Estimate improvement based on resolution rate (actual would need before/after mastery)
        est_improvement = round((resolved / max(total, 1)) * 18, 1)
        by_type.append({
            "type": (row.ticket_type or "unknown").replace("_", " ").title(),
            "total_created": total,
            "resolved": resolved,
            "resolution_rate": round(resolved / max(total, 1), 2),
            "estimated_improvement": est_improvement,
        })

    overall_total = sum(t["total_created"] for t in by_type) or 1
    overall_resolved = sum(t["resolved"] for t in by_type)

    return {
        "by_type": sorted(by_type, key=lambda x: x["estimated_improvement"], reverse=True),
        "overall_resolution_rate": round(overall_resolved / overall_total, 2),
        "total_interventions": overall_total,
        "total_resolved": overall_resolved,
    }


@router.get("/teacher-workload")
async def teacher_workload(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Teacher workload distribution."""
    result = await db.execute(
        select(
            User.user_id,
            User.full_name,
            User.class_section,
            func.count(InterventionTicket.id).label("total_tickets"),
            func.sum(
                case((InterventionTicket.priority.in_(["P1", "P2"]), 1), else_=0)
            ).label("urgent_tickets"),
        )
        .outerjoin(
            InterventionTicket,
            and_(
                InterventionTicket.teacher_id == User.user_id,
                InterventionTicket.status.in_(["open", "assigned", "in_progress"]),
            ),
        )
        .where(User.role == "teacher")
        .group_by(User.user_id, User.full_name, User.class_section)
    )
    rows = result.all()

    teachers = []
    for row in rows:
        teachers.append({
            "teacher_id": row.user_id,
            "name": row.full_name,
            "class_section": row.class_section,
            "open_tickets": row.total_tickets or 0,
            "urgent_tickets": row.urgent_tickets or 0,
        })

    return {"teachers": sorted(teachers, key=lambda x: x["open_tickets"], reverse=True)}
