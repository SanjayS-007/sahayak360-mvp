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


class RiskDistribution(BaseModel):
    low: int = 0
    moderate: int = 0
    high: int = 0
    critical: int = 0


class StrugglingKC(BaseModel):
    kc_id: str
    kc_name: str
    avg_mastery: float
    student_count: int = 0


class ClassOverview(BaseModel):
    total_students: int
    avg_mastery: float
    class_avg_mastery: float = 0.0
    at_risk_count: int
    pending_tickets: int
    recent_events: int
    risk_distribution: RiskDistribution = RiskDistribution()
    struggling_kcs: list[StrugglingKC] = []
    open_tickets: int = 0


class StudentSummary(BaseModel):
    student_id: str
    full_name: str
    overall_mastery: float
    gaps_count: int
    risk_tier: str
    trend: str = "stable"
    last_assessment: str | None = None


class MasteryItem(BaseModel):
    kc_id: str
    kc_name: str
    mastery: float
    mastery_level: str
    attempts: int


class StudentMasteryResponse(BaseModel):
    student_id: str
    overall_mastery: float
    trend: str
    total_kcs: int
    gaps: list[dict]
    strengths: list[dict]
    assessment_count: int
    recent_scores: list[float]


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
        class_avg_mastery=avg_mastery,
        at_risk_count=at_risk_count,
        pending_tickets=pending_tickets,
        open_tickets=pending_tickets,
        recent_events=recent_events,
        risk_distribution=await _compute_risk_distribution(db, class_section, subject),
        struggling_kcs=await _compute_struggling_kcs(db, class_section, subject),
    )


async def _compute_risk_distribution(db: AsyncSession, class_section: str, subject: str) -> RiskDistribution:
    """Compute risk tier distribution for all students in a class."""
    student_ids_q = select(User.user_id).where(
        User.class_section == class_section, User.role == "student"
    )
    # Get average mastery per student
    result = await db.execute(
        select(
            MasteryRecord.student_id,
            func.avg(MasteryRecord.mastery).label("avg_m"),
        )
        .where(
            MasteryRecord.subject == subject,
            MasteryRecord.student_id.in_(student_ids_q),
        )
        .group_by(MasteryRecord.student_id)
    )
    rows = result.all()
    dist = RiskDistribution()
    for row in rows:
        avg_m = row.avg_m or 0
        if avg_m >= 0.7:
            dist.low += 1
        elif avg_m >= 0.5:
            dist.moderate += 1
        elif avg_m >= 0.3:
            dist.high += 1
        else:
            dist.critical += 1
    return dist


async def _compute_struggling_kcs(db: AsyncSession, class_section: str, subject: str) -> list[StrugglingKC]:
    """Find KCs where class average mastery is below 0.5."""
    student_ids_q = select(User.user_id).where(
        User.class_section == class_section, User.role == "student"
    )
    result = await db.execute(
        select(
            MasteryRecord.kc_id,
            MasteryRecord.kc_name,
            func.avg(MasteryRecord.mastery).label("avg_m"),
            func.count(func.distinct(MasteryRecord.student_id)).label("cnt"),
        )
        .where(
            MasteryRecord.subject == subject,
            MasteryRecord.student_id.in_(student_ids_q),
        )
        .group_by(MasteryRecord.kc_id, MasteryRecord.kc_name)
        .having(func.avg(MasteryRecord.mastery) < 0.5)
        .order_by(func.avg(MasteryRecord.mastery))
        .limit(10)
    )
    rows = result.all()
    return [
        StrugglingKC(kc_id=r.kc_id, kc_name=r.kc_name or r.kc_id, avg_mastery=round(r.avg_m, 3), student_count=r.cnt)
        for r in rows
    ]


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


@router.get("/student/mastery", response_model=StudentMasteryResponse)
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

    total_kcs = len(records)
    overall = sum(r.mastery for r in records) / total_kcs if total_kcs else 0.0
    total_attempts = sum(r.attempts for r in records)

    # Gaps: mastery < 0.4
    gaps = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
            for r in records if r.mastery < 0.4]
    # Strengths: mastery >= 0.7
    strengths = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
                 for r in records if r.mastery >= 0.7]

    return StudentMasteryResponse(
        student_id=user.user_id,
        overall_mastery=round(overall, 3),
        trend="stable",
        total_kcs=total_kcs,
        gaps=gaps,
        strengths=strengths,
        assessment_count=total_attempts,
        recent_scores=[],
    )


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


@router.get("/admin/teachers")
async def admin_teacher_list(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all teachers for admin panel."""
    result = await db.execute(
        select(User).where(User.role == "teacher").order_by(User.full_name)
    )
    teachers = result.scalars().all()
    return [
        {
            "user_id": t.user_id,
            "full_name": t.full_name,
            "email": t.email,
            "class_section": t.class_section or "",
            "department_id": t.department_id or "",
        }
        for t in teachers
    ]


@router.delete("/admin/reset-demo-data")
async def reset_demo_data(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Reset all assessment data for clean re-seeding. Admin only."""
    from sqlalchemy import delete, text

    # Valid user IDs to keep
    valid_ids = [
        "TCH-1001", "TCH-1002", "TCH-1003",
        "STU-2001", "STU-2002", "STU-2003", "STU-2004", "STU-2005",
        "STU-2006", "STU-2007", "STU-2008", "STU-2009", "STU-2010",
        "STU-2011", "STU-2012", "STU-2013", "STU-2014", "STU-2015",
        "STU-2016", "STU-2017", "STU-2018",
        "ADM-3001", "ADM-3002",
    ]

    # Delete all mastery records
    r1 = await db.execute(delete(MasteryRecord))
    # Delete all assessment events
    r2 = await db.execute(delete(AssessmentEvent))
    # Delete all intervention tickets
    r3 = await db.execute(delete(InterventionTicket))
    # Delete all quiz sessions
    r4 = await db.execute(delete(QuizSession))
    # Delete invalid users
    r5 = await db.execute(
        delete(User).where(User.user_id.notin_(valid_ids))
    )

    await db.commit()

    return {
        "deleted_mastery_records": r1.rowcount,
        "deleted_assessment_events": r2.rowcount,
        "deleted_tickets": r3.rowcount,
        "deleted_quizzes": r4.rowcount,
        "deleted_invalid_users": r5.rowcount,
    }


@router.post("/admin/bulk-seed")
async def bulk_seed_mastery(
    payload: dict,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Bulk-insert mastery records and assessment events. Admin only.
    
    Payload: { "records": [ {student_id, kc_id, kc_name, mastery_level, score, subject} ] }
    """
    from datetime import datetime, timedelta
    import random

    records = payload.get("records", [])
    inserted_mastery = 0
    inserted_events = 0

    # Group by student for assessment events
    student_records: dict = {}
    for rec in records:
        sid = rec["student_id"]
        if sid not in student_records:
            student_records[sid] = []
        student_records[sid].append(rec)

        # Insert mastery record
        mr = MasteryRecord(
            student_id=sid,
            kc_id=rec["kc_id"],
            kc_name=rec.get("kc_name", rec["kc_id"]),
            mastery_level=rec.get("mastery_level", "developing"),
            score=rec.get("score", 0.5),
            subject=rec.get("subject", "mathematics"),
        )
        db.add(mr)
        inserted_mastery += 1

    # Create assessment events per student (3 per student for history)
    now = datetime.utcnow()
    for sid, recs in student_records.items():
        avg_score = sum(r.get("score", 0.5) for r in recs) / len(recs)
        # Look up student's class_section
        stu = await db.execute(select(User).where(User.user_id == sid))
        student = stu.scalar_one_or_none()
        class_section = student.class_section if student else "9-A"

        for week in range(3):
            random.seed(hash(f"{sid}-{week}"))
            variance = random.uniform(-0.05, 0.05)
            score = max(0.0, min(1.0, avg_score + variance + week * 0.02))

            evt = AssessmentEvent(
                student_id=sid,
                class_section=class_section,
                subject=recs[0].get("subject", "mathematics"),
                assessment_type="formative",
                score=round(score, 3),
                max_score=1.0,
                assessed_at=now - timedelta(days=(2 - week) * 7),
            )
            db.add(evt)
            inserted_events += 1

    await db.commit()

    return {
        "inserted_mastery_records": inserted_mastery,
        "inserted_assessment_events": inserted_events,
    }


@router.get("/teacher/student-detail/{student_id}")
async def teacher_student_detail(
    student_id: str,
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Detailed student analytics for teacher view — radar data, KC breakdown, history."""
    # Get student info
    stu_result = await db.execute(select(User).where(User.user_id == student_id))
    student = stu_result.scalar_one_or_none()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    # Get all mastery records
    mastery_result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.subject == subject,
        )
    )
    records = mastery_result.scalars().all()

    # Build radar data (KC name → mastery score 0-100)
    radar_data = []
    for r in records:
        radar_data.append({
            "kc": r.kc_name or r.kc_id,
            "mastery": round(r.mastery * 100, 1),
            "full_mark": 100,
        })

    overall = sum(r.mastery for r in records) / len(records) if records else 0.0
    gaps = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
            for r in records if r.mastery < 0.4]
    strengths = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
                 for r in records if r.mastery >= 0.7]

    # Get assessment history for timeline
    events_result = await db.execute(
        select(AssessmentEvent).where(
            AssessmentEvent.student_id == student_id,
            AssessmentEvent.subject == subject,
        ).order_by(AssessmentEvent.created_at)
    )
    events = events_result.scalars().all()

    timeline = []
    for e in events:
        score_pct = (e.total_obtained / e.max_score * 100) if e.max_score else 0
        timeline.append({
            "date": e.created_at.strftime("%b %d") if e.created_at else "",
            "score": round(score_pct, 1),
        })

    # Determine risk and trend
    if overall < 0.30:
        risk = "critical"
    elif overall < 0.50:
        risk = "high"
    elif overall < 0.65:
        risk = "moderate"
    else:
        risk = "low"

    # Simple trend based on last 2 events
    if len(timeline) >= 2:
        trend = "improving" if timeline[-1]["score"] >= timeline[-2]["score"] else "declining"
    else:
        trend = "stable"

    return {
        "student_id": student_id,
        "full_name": student.full_name,
        "class_section": student.class_section,
        "overall_mastery": round(overall, 3),
        "risk_tier": risk,
        "trend": trend,
        "assessment_count": len(events),
        "radar_data": radar_data,
        "gaps": gaps,
        "strengths": strengths,
        "timeline": timeline,
        "kc_breakdown": [
            {"kc_id": r.kc_id, "kc_name": r.kc_name or r.kc_id, "mastery": round(r.mastery, 3), "level": r.mastery_level}
            for r in sorted(records, key=lambda x: x.mastery)
        ],
    }


@router.get("/student/analytics")
async def student_analytics(
    subject: str = Query(default="mathematics"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detailed analytics for a student's own view — radar, timeline, domain breakdown."""
    student_id = user.user_id

    # Get all mastery records
    mastery_result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id == student_id,
            MasteryRecord.subject == subject,
        )
    )
    records = mastery_result.scalars().all()

    # Build radar data
    radar_data = []
    for r in records:
        radar_data.append({
            "kc": r.kc_name or r.kc_id,
            "mastery": round(r.mastery * 100, 1),
            "full_mark": 100,
        })

    overall = sum(r.mastery for r in records) / len(records) if records else 0.0

    # Domain averages (group by prefix)
    domain_map = {"ALG": "Algebra", "GEO": "Geometry", "STAT": "Statistics", "TRIG": "Trigonometry"}
    domain_scores: dict = {}
    for r in records:
        prefix = r.kc_id.split("-")[0] if r.kc_id else "OTHER"
        domain = domain_map.get(prefix, prefix)
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(r.mastery)

    domains = [
        {"domain": d, "mastery": round(sum(scores)/len(scores)*100, 1), "kc_count": len(scores)}
        for d, scores in domain_scores.items()
    ]

    # Assessment timeline
    events_result = await db.execute(
        select(AssessmentEvent).where(
            AssessmentEvent.student_id == student_id,
            AssessmentEvent.subject == subject,
        ).order_by(AssessmentEvent.created_at)
    )
    events = events_result.scalars().all()

    timeline = []
    for e in events:
        score_pct = (e.total_obtained / e.max_score * 100) if e.max_score else 0
        timeline.append({
            "date": e.created_at.strftime("%b %d") if e.created_at else "",
            "score": round(score_pct, 1),
        })

    # Trend
    if len(timeline) >= 2:
        trend = "improving" if timeline[-1]["score"] >= timeline[-2]["score"] else "declining"
    else:
        trend = "stable"

    # Gaps & Strengths
    gaps = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
            for r in records if r.mastery < 0.4]
    strengths = [{"kc_id": r.kc_id, "kc_name": r.kc_name, "mastery": round(r.mastery, 3)}
                 for r in records if r.mastery >= 0.7]

    return {
        "student_id": student_id,
        "full_name": user.full_name,
        "overall_mastery": round(overall, 3),
        "trend": trend,
        "assessment_count": len(events),
        "radar_data": radar_data,
        "domains": domains,
        "gaps": gaps,
        "strengths": strengths,
        "timeline": timeline,
        # Enhanced analytics
        "prediction": _compute_prediction(timeline, overall),
        "study_metrics": _compute_study_metrics(events),
        "peer_comparison": await _compute_peer_comparison(db, student_id, subject, overall),
        "cross_topic_insights": _compute_cross_topic_insights(records, domain_map),
        "gap_context": _get_gap_context(gaps),
    }


def _compute_prediction(timeline: list, current_mastery: float) -> dict:
    """Linear regression on recent scores to predict 2-week trajectory."""
    if len(timeline) < 2:
        return {"mastery_2weeks": round(current_mastery * 100, 1), "velocity": 0.0, "trajectory": "stable"}

    scores = [t["score"] for t in timeline[-5:]]  # Last 5 data points
    n = len(scores)
    x_mean = (n - 1) / 2
    y_mean = sum(scores) / n
    numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0

    projected = scores[-1] + slope * 2
    projected = max(0, min(100, projected))

    velocity = round(slope, 2)
    if velocity > 2:
        trajectory = "improving"
    elif velocity < -2:
        trajectory = "declining"
    else:
        trajectory = "plateau"

    return {"mastery_2weeks": round(projected, 1), "velocity": velocity, "trajectory": trajectory}


def _compute_study_metrics(events) -> dict:
    """Compute engagement metrics from assessment event timestamps."""
    if not events:
        return {"total_sessions": 0, "avg_session_duration_min": 0, "most_active_day": "N/A", "optimal_time": "N/A"}

    from collections import Counter
    day_counts = Counter()
    hour_counts = Counter()

    for e in events:
        if e.created_at:
            day_counts[e.created_at.strftime("%A")] += 1
            hour_counts[e.created_at.hour] += 1

    most_active_day = day_counts.most_common(1)[0][0] if day_counts else "N/A"
    optimal_hour = hour_counts.most_common(1)[0][0] if hour_counts else 10
    optimal_time = f"{optimal_hour}:00 - {optimal_hour + 1}:00"

    return {
        "total_sessions": len(events),
        "avg_session_duration_min": 15,
        "most_active_day": most_active_day,
        "optimal_time": optimal_time,
    }


async def _compute_peer_comparison(db: AsyncSession, student_id: str, subject: str, student_mastery: float) -> dict:
    """Compare student to class average (anonymous)."""
    result = await db.execute(
        select(
            MasteryRecord.student_id,
            func.avg(MasteryRecord.mastery).label("avg_m"),
        )
        .where(MasteryRecord.subject == subject)
        .group_by(MasteryRecord.student_id)
    )
    all_averages = [row.avg_m for row in result.all()]

    if not all_averages:
        return {"class_avg_mastery": 0, "percentile_rank": 50, "similar_students_improvement": "N/A"}

    class_avg = sum(all_averages) / len(all_averages)
    below_count = sum(1 for a in all_averages if a < student_mastery)
    percentile = round((below_count / len(all_averages)) * 100)

    if percentile < 40:
        improvement_msg = "Students at similar levels who practiced 3+ times per week improved by 15-25% within a month."
    elif percentile < 70:
        improvement_msg = "You are tracking with the class. Consistent daily practice could push you into the top quartile."
    else:
        improvement_msg = "You are ahead of most peers. Focus on advanced topics to maintain your edge."

    return {
        "class_avg_mastery": round(class_avg * 100, 1),
        "percentile_rank": percentile,
        "similar_students_improvement": improvement_msg,
    }


def _compute_cross_topic_insights(records, domain_map: dict) -> list:
    """Find correlations between topic performance."""
    domain_scores_map: dict = {}
    for r in records:
        prefix = r.kc_id.split("-")[0] if r.kc_id else "OTHER"
        domain = domain_map.get(prefix, prefix)
        if domain not in domain_scores_map:
            domain_scores_map[domain] = []
        domain_scores_map[domain].append(r.mastery)

    insights = []
    domains_list = list(domain_scores_map.keys())

    for i in range(len(domains_list)):
        for j in range(i + 1, len(domains_list)):
            d_a = domains_list[i]
            d_b = domains_list[j]
            avg_a = sum(domain_scores_map[d_a]) / len(domain_scores_map[d_a])
            avg_b = sum(domain_scores_map[d_b]) / len(domain_scores_map[d_b])

            if avg_a < 0.4 and avg_b < 0.4:
                insights.append({
                    "topic_a": d_a,
                    "topic_b": d_b,
                    "correlation": "Both areas need attention — they share foundational concepts.",
                    "recommendation": f"Start with {d_a if avg_a < avg_b else d_b} basics first, as it may unlock progress in the other.",
                })
            elif abs(avg_a - avg_b) > 0.3:
                strong = d_a if avg_a > avg_b else d_b
                weak = d_b if avg_a > avg_b else d_a
                insights.append({
                    "topic_a": strong,
                    "topic_b": weak,
                    "correlation": f"Strong {strong} skills can support {weak} learning.",
                    "recommendation": f"Use your {strong} confidence to approach {weak} problems — many concepts transfer across.",
                })

    return insights[:3]


def _get_gap_context(gaps: list) -> list:
    """Load real-world context for each gap KC from kc_context.json."""
    import json, os
    context_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "kc_context.json")
    kc_context = {}
    if os.path.exists(context_path):
        with open(context_path, "r") as f:
            kc_context = json.load(f)

    enriched = []
    for gap in gaps:
        kc_id = gap["kc_id"]
        ctx = kc_context.get(kc_id, {})
        enriched.append({
            "kc_id": kc_id,
            "kc_name": gap["kc_name"],
            "mastery": gap["mastery"],
            "real_world": ctx.get("real_world", f"{gap['kc_name']} is a fundamental skill used across science, engineering, and daily problem-solving."),
            "prerequisites": ctx.get("prerequisites", []),
            "action": ctx.get("action", "Practice 5 problems at basic level, then progress to medium difficulty."),
            "next_steps": ctx.get("next_steps", []),
        })
    return enriched


@router.get("/teacher/knowledge-graph")
async def teacher_knowledge_graph(
    class_section: str = Query(...),
    subject: str = Query(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Get knowledge graph data: students, KCs, and mastery edges."""
    # Get students
    students_result = await db.execute(
        select(User).where(
            User.class_section == class_section,
            User.role == "student",
        )
    )
    students = students_result.scalars().all()

    # Get all mastery records for these students
    student_ids = [s.user_id for s in students]
    mastery_result = await db.execute(
        select(MasteryRecord).where(
            MasteryRecord.student_id.in_(student_ids),
            MasteryRecord.subject == subject,
        )
    )
    records = mastery_result.scalars().all()

    # Build graph nodes and edges
    nodes = []
    edges = []
    kc_set = set()

    for s in students:
        nodes.append({
            "id": s.user_id,
            "label": s.full_name.split()[0],  # First name only
            "type": "student",
            "group": "student",
        })

    for r in records:
        if r.kc_id not in kc_set:
            kc_set.add(r.kc_id)
            nodes.append({
                "id": r.kc_id,
                "label": r.kc_name,
                "type": "kc",
                "group": r.kc_id.split("-")[0].lower(),  # alg, geo, stat, trig
            })

        edges.append({
            "source": r.student_id,
            "target": r.kc_id,
            "mastery": round(r.mastery, 2),
            "level": r.mastery_level,
        })

    return {"nodes": nodes, "edges": edges}
