"""
Data Ingestion routes — structured, freetext, and vision channels.
"""

import logging
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role
from core.ast_schema import (
    AcademicPayload,
    AssessmentEventAST,
    EventMetadata,
    FreetextIngestRequest,
    IngestionChannel,
    IngestResponse,
    StructuredIngestRequest,
    ValidationResult,
    VisionIngestRequest,
)
from core.pandas_validator import run_full_validation
from core.rehydration_governor import route_freetext, route_vision
from core.threshold_evaluator import needs_intervention
from db.models import User
from db.postgres import get_db
from services.ingestion_orchestrator import orchestrate_structured_ingest

router = APIRouter()


@router.post("/structured", response_model=IngestResponse)
async def ingest_structured(
    req: StructuredIngestRequest,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Fast lane: ingest structured JSON assessment data."""
    try:
        result = await orchestrate_structured_ingest(req, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if result.validation and not result.validation.sum_check_passed:
        if result.validation.discrepancy > 5:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "validation_failed",
                    "anomaly_flags": result.validation.anomaly_flags,
                    "discrepancy": result.validation.discrepancy,
                },
            )

    return IngestResponse(
        status="accepted",
        event_id=result.event_id,
        parse_method=result.lane,
        validation=result.validation or ValidationResult(),
        cognitive_analysis={
            "gaps_detected": len(result.gaps),
            "needs_intervention": needs_intervention(result.gaps),
            "mastery_updates": len(result.mastery_updates),
            "risk_tier": result.risk.tier.value if result.risk else "unknown",
            "tickets_created": result.tickets_created,
        },
        graph_mutations=result.graph_mutations,
    )


@router.post("/freetext", response_model=IngestResponse)
async def ingest_freetext(
    req: FreetextIngestRequest,
    user: User = Depends(require_role("teacher", "admin")),
    db: AsyncSession = Depends(get_db),
):
    """Slow lane: natural language input parsed via Gemini into AST then orchestrated."""
    from llm.freetext_parser import parse_freetext_to_ast

    decision = route_freetext(req)

    # Parse via Gemini
    try:
        ast = await parse_freetext_to_ast(
            raw_text=req.raw_text,
            teacher_id=req.teacher_id,
            class_section=req.class_section or "unknown",
            subject=req.subject or "mathematics",
        )
    except Exception as e:
        logger.warning(f"Gemini freetext parsing unavailable: {e}")
        return IngestResponse(
            status="queued",
            event_id=None,
            parse_method="ai_unavailable",
            validation=ValidationResult(),
            graph_mutations=[],
        )

    # Build a StructuredIngestRequest from the parsed AST and run through orchestrator
    structured_req = StructuredIngestRequest(
        teacher_id=ast.metadata.teacher_id,
        student_id=ast.metadata.student_id,
        class_section=ast.metadata.class_section,
        subject=ast.metadata.subject,
        department_id=ast.metadata.department_id,
        assessment_type=ast.academic.assessment_type,
        max_score=ast.academic.max_score,
        total_obtained=ast.academic.total_obtained,
        items=ast.academic.items,
    )

    try:
        result = await orchestrate_structured_ingest(structured_req, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return IngestResponse(
        status="accepted",
        event_id=result.event_id,
        parse_method=decision.lane.value,
        validation=result.validation or ValidationResult(),
        cognitive_analysis={
            "gaps_detected": len(result.gaps),
            "needs_intervention": needs_intervention(result.gaps),
            "mastery_updates": len(result.mastery_updates),
            "risk_tier": result.risk.tier.value if result.risk else "unknown",
            "tickets_created": result.tickets_created,
            "source": "freetext_gemini_parse",
        },
        graph_mutations=result.graph_mutations,
    )


@router.post("/vision")
async def ingest_vision(
    file: UploadFile = File(...),
    teacher_id: str = Form(...),
    class_section: str = Form(...),
    subject: str = Form(default="mathematics"),
    user: User = Depends(require_role("teacher", "admin")),
):
    """Slow lane: image upload for OMR/handwriting extraction via OpenCV + Gemini Vision."""
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only PNG/JPEG images accepted")

    from vision.extractor import extract_from_image

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")

    result = await extract_from_image(
        image_bytes=image_bytes,
        teacher_id=teacher_id,
        class_section=class_section,
        subject=subject,
        mime_type=file.content_type or "image/png",
    )

    if "error" in result:
        raise HTTPException(status_code=422, detail=result)

    # Run extracted AST through orchestrator with a fresh DB session
    from db.postgres import async_session_factory

    ast = result["ast"]
    structured_req = StructuredIngestRequest(
        teacher_id=ast.metadata.teacher_id,
        student_id=ast.metadata.student_id,
        class_section=ast.metadata.class_section,
        subject=ast.metadata.subject,
        department_id=ast.metadata.department_id,
        assessment_type=ast.academic.assessment_type,
        max_score=ast.academic.max_score,
        total_obtained=ast.academic.total_obtained,
        items=ast.academic.items,
    )

    async with async_session_factory() as db_session:
        try:
            orchestration_result = await orchestrate_structured_ingest(structured_req, db_session)
            await db_session.commit()
        except ValueError as e:
            await db_session.rollback()
            raise HTTPException(status_code=422, detail=str(e))

    return {
        "status": "accepted",
        "event_id": orchestration_result.event_id,
        "parse_method": "slow_lane_vision",
        "filename": file.filename,
        "preprocessing": result.get("preprocessing"),
        "extraction_confidence": result.get("confidence", 0.0),
        "items_extracted": len(ast.academic.items) if ast.academic and ast.academic.items else 0,
    }
