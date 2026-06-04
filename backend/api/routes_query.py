"""
AI Query routes — Natural Language to insights via Gemini + Neo4j.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from auth.dependencies import get_current_user
from db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


class NLQueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    context: str = Field(default="general")


class QueryResponse(BaseModel):
    answer: str
    data: list | dict | None = None
    cypher_used: str | None = None
    confidence: float = 0.0


@router.post("/ask", response_model=QueryResponse)
async def natural_language_query(
    req: NLQueryRequest,
    request: Request,
    user: User = Depends(get_current_user),
):
    """
    Natural language query interface.
    Converts question → Cypher via Gemini → executes on Neo4j → returns answer.
    """
    from llm.nl_to_cypher import execute_nl_query

    neo4j_driver = getattr(request.app.state, "neo4j_driver", None)
    if not neo4j_driver:
        return QueryResponse(
            answer="Knowledge graph not available. Please try again later.",
            confidence=0.0,
        )

    try:
        result = await execute_nl_query(
            question=req.question,
            user_id=user.user_id,
            role=user.role,
            class_section=user.class_section or "",
            neo4j_driver=neo4j_driver,
        )
        return QueryResponse(
            answer=result["answer"],
            data=result.get("data"),
            cypher_used=result.get("cypher_used"),
            confidence=0.8 if result.get("data") else 0.3,
        )
    except ValueError as e:
        return QueryResponse(
            answer=str(e),
            confidence=0.0,
        )
    except Exception as e:
        logger.error(f"NL query failed: {type(e).__name__}: {e}")
        return QueryResponse(
            answer=f"Query processing error: {str(e)[:200]}",
            confidence=0.0,
        )


@router.get("/student/{student_id}/insights")
async def get_student_insights(
    student_id: str,
    request: Request,
    user: User = Depends(get_current_user),
):
    """Get AI-generated insights for a specific student from the knowledge graph."""
    from services.dashboard_analytics import compute_student_profile
    from db.postgres import get_db, async_session_factory

    async with async_session_factory() as db:
        profile = await compute_student_profile(db, student_id)

    return {
        "student_id": student_id,
        "overall_mastery": profile["overall_mastery"],
        "trend": profile["trend"],
        "gaps": profile["gaps"][:5],
        "strengths": profile["strengths"][:5],
        "assessment_count": profile["assessment_count"],
    }


@router.get("/class/{class_section}/patterns")
async def get_class_patterns(
    request: Request,
    class_section: str,
    subject: str = "mathematics",
    user: User = Depends(get_current_user),
):
    """Detect class-wide learning patterns from analytics."""
    from services.dashboard_analytics import compute_class_analytics
    from db.postgres import async_session_factory

    async with async_session_factory() as db:
        analytics = await compute_class_analytics(
            db, user.user_id, class_section, subject
        )

    return {
        "class_section": class_section,
        "subject": subject,
        "total_students": analytics["total_students"],
        "class_avg_mastery": analytics["class_avg_mastery"],
        "risk_distribution": analytics["risk_distribution"],
        "struggling_kcs": analytics["struggling_kcs"][:5],
    }


@router.get("/class/{class_section}/patterns-computed")
async def get_computed_class_patterns(
    class_section: str,
    subject: str = "mathematics",
    user: User = Depends(get_current_user),
):
    """Compute AI-detected class patterns from actual mastery data — no LLM required."""
    from db.postgres import async_session_factory
    from db.models import MasteryRecord, AssessmentEvent, User as UserModel
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    import json, os

    async with async_session_factory() as db:
        # Get all students in class
        student_ids_q = select(UserModel.user_id).where(
            UserModel.class_section == class_section,
            UserModel.role == "student",
        )
        stu_result = await db.execute(student_ids_q)
        student_ids = [r[0] for r in stu_result.all()]
        total_students = len(student_ids)

        if total_students == 0:
            return {"summary": "No students found in this section.", "patterns": [], "analyzed_at": datetime.utcnow().isoformat()}

        # Get all mastery records for this class
        mastery_result = await db.execute(
            select(MasteryRecord).where(
                MasteryRecord.student_id.in_(student_ids),
                MasteryRecord.subject == subject,
            )
        )
        records = mastery_result.scalars().all()

        if not records:
            return {"summary": "Insufficient data for pattern analysis.", "patterns": [], "analyzed_at": datetime.utcnow().isoformat()}

        # --- Pattern Detection Algorithms ---
        patterns = []

        # 1. Identify class-wide struggling KCs (avg mastery < 40%)
        kc_scores: dict = {}
        student_kc_map: dict = {}
        for r in records:
            if r.kc_id not in kc_scores:
                kc_scores[r.kc_id] = {"name": r.kc_name or r.kc_id, "scores": [], "student_ids": []}
            kc_scores[r.kc_id]["scores"].append(r.mastery)
            kc_scores[r.kc_id]["student_ids"].append(r.student_id)
            # Track per-student KC mastery
            if r.student_id not in student_kc_map:
                student_kc_map[r.student_id] = {}
            student_kc_map[r.student_id][r.kc_id] = r.mastery

        for kc_id, data in kc_scores.items():
            avg = sum(data["scores"]) / len(data["scores"])
            struggling_count = sum(1 for s in data["scores"] if s < 0.4)
            if avg < 0.40 and struggling_count >= 3:
                patterns.append({
                    "insight": f"Class-wide difficulty in {data['name']}: {struggling_count}/{total_students} students scoring below 40%. Average mastery is only {round(avg*100)}%.",
                    "affected_students": struggling_count,
                    "severity": "high" if avg < 0.25 else "medium",
                    "pattern_type": "gap",
                    "kc_id": kc_id,
                })

        # 2. Detect correlation patterns (students weak in KC-A also weak in KC-B)
        kc_ids = list(kc_scores.keys())
        for i in range(len(kc_ids)):
            for j in range(i + 1, len(kc_ids)):
                kc_a, kc_b = kc_ids[i], kc_ids[j]
                # Find students who have scores for both
                weak_both = 0
                have_both = 0
                for sid in student_ids:
                    if sid in student_kc_map and kc_a in student_kc_map[sid] and kc_b in student_kc_map[sid]:
                        have_both += 1
                        if student_kc_map[sid][kc_a] < 0.4 and student_kc_map[sid][kc_b] < 0.4:
                            weak_both += 1
                if have_both >= 5 and weak_both >= 3 and weak_both / have_both >= 0.4:
                    name_a = kc_scores[kc_a]["name"]
                    name_b = kc_scores[kc_b]["name"]
                    patterns.append({
                        "insight": f"Correlated weakness: {weak_both} students struggle in both {name_a} and {name_b}. These topics may share prerequisite gaps that need addressing together.",
                        "affected_students": weak_both,
                        "severity": "medium",
                        "pattern_type": "correlation",
                        "kc_ids": [kc_a, kc_b],
                    })

        # 3. Detect declining students (recent events show score drops)
        week_ago = datetime.utcnow() - timedelta(days=14)
        events_result = await db.execute(
            select(AssessmentEvent).where(
                AssessmentEvent.student_id.in_(student_ids),
                AssessmentEvent.subject == subject,
                AssessmentEvent.created_at >= week_ago,
            ).order_by(AssessmentEvent.student_id, AssessmentEvent.created_at)
        )
        events = events_result.scalars().all()

        declining_students = []
        student_events: dict = {}
        for e in events:
            if e.student_id not in student_events:
                student_events[e.student_id] = []
            score = (e.total_obtained / e.max_score) if e.max_score else 0
            student_events[e.student_id].append(score)

        for sid, scores in student_events.items():
            if len(scores) >= 2 and scores[-1] < scores[0] - 0.1:
                declining_students.append(sid)

        if declining_students:
            patterns.append({
                "insight": f"Declining performance detected: {len(declining_students)} students show a downward trend in the last 2 weeks. Early intervention may prevent further regression.",
                "affected_students": len(declining_students),
                "severity": "high" if len(declining_students) >= 4 else "medium",
                "pattern_type": "decline",
            })

        # 4. Identify high-performing cluster (students above 80% in most KCs)
        high_performers = 0
        for sid in student_ids:
            if sid in student_kc_map:
                avg_m = sum(student_kc_map[sid].values()) / len(student_kc_map[sid])
                if avg_m >= 0.75:
                    high_performers += 1

        if high_performers >= 2 and high_performers < total_students:
            patterns.append({
                "insight": f"Achievement gap: {high_performers} students perform above 75% while {total_students - high_performers} are below. Consider differentiated instruction or peer tutoring to bridge the gap.",
                "affected_students": total_students - high_performers,
                "severity": "medium",
                "pattern_type": "cluster",
            })

        # 5. Load KC context for prerequisite-based insights
        context_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "kc_context.json")
        kc_context = {}
        if os.path.exists(context_path):
            with open(context_path, "r") as f:
                kc_context = json.load(f)

        # Check if prerequisite gaps explain current struggles
        for kc_id, data in kc_scores.items():
            if kc_id in kc_context and kc_context[kc_id].get("prerequisites"):
                prereqs = kc_context[kc_id]["prerequisites"]
                avg_kc = sum(data["scores"]) / len(data["scores"])
                if avg_kc < 0.5:
                    weak_prereq_count = 0
                    for prereq in prereqs:
                        if prereq in kc_scores:
                            prereq_avg = sum(kc_scores[prereq]["scores"]) / len(kc_scores[prereq]["scores"])
                            if prereq_avg < 0.5:
                                weak_prereq_count += 1
                    if weak_prereq_count > 0:
                        prereq_names = [kc_scores[p]["name"] for p in prereqs if p in kc_scores]
                        patterns.append({
                            "insight": f"Foundation gap: Weakness in {data['name']} may be rooted in prerequisite topics ({', '.join(prereq_names)}). Strengthening foundations first could accelerate recovery.",
                            "affected_students": sum(1 for s in data["scores"] if s < 0.5),
                            "severity": "medium",
                            "pattern_type": "prerequisite",
                        })

        # Build summary from top patterns
        patterns.sort(key=lambda p: (0 if p["severity"] == "high" else 1, -p["affected_students"]))
        patterns = patterns[:6]  # Limit to top 6

        if patterns:
            top = patterns[0]
            summary = f"Key finding: {top['insight'].split('.')[0]}. "
            summary += f"Analysis of {total_students} students across {len(kc_scores)} topics reveals {len(patterns)} actionable patterns."
        else:
            summary = f"Class of {total_students} students shows balanced performance across {len(kc_scores)} topics. No critical patterns detected."

        return {
            "summary": summary,
            "patterns": patterns,
            "total_students": total_students,
            "analyzed_at": datetime.utcnow().isoformat(),
        }
