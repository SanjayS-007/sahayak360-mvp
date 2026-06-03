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
        logger.error(f"NL query failed: {e}")
        return QueryResponse(
            answer="An error occurred processing your query. Please rephrase.",
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
