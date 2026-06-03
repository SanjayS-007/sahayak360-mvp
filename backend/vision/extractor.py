"""
Vision Extractor — Stage 2 of the Vision pipeline.
Sends preprocessed image to Gemini Vision for data extraction.
Converts extraction result to AST.
"""

import logging
from pathlib import Path
from typing import Optional

from core.ast_schema import (
    AcademicPayload,
    AssessmentEventAST,
    AssessmentType,
    EventMetadata,
    IngestionChannel,
    ScoreItem,
)
from llm.gemini_client import generate_with_image, generate_json
from vision.opencv_preprocessor import PreprocessingResult, preprocess_answer_sheet, extract_bubble_region

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "vision_extraction.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


async def extract_from_image(
    image_bytes: bytes,
    teacher_id: str,
    class_section: str,
    subject: str = "mathematics",
    mime_type: str = "image/png",
) -> dict:
    """
    Full vision pipeline: Preprocess → Gemini Vision → Parse → Return.
    Returns: {"ast": AssessmentEventAST, "preprocessing": {...}, "raw_extraction": {...}}
    """
    # Stage 1: OpenCV preprocessing
    preprocess_result = preprocess_answer_sheet(image_bytes)

    if not preprocess_result.is_acceptable:
        logger.warning(f"Image quality too low: {preprocess_result.quality_score}")
        return {
            "error": "Image quality too low for reliable extraction",
            "quality_score": preprocess_result.quality_score,
            "preprocessing": _preprocessing_summary(preprocess_result),
        }

    # Get processed image bytes for Gemini
    processed_bytes = extract_bubble_region(image_bytes)
    if processed_bytes is None:
        processed_bytes = image_bytes  # Fallback to original

    # Stage 2: Gemini Vision extraction
    extraction_prompt = _load_prompt()
    try:
        raw_response = await generate_with_image(
            extraction_prompt, processed_bytes, mime_type
        )
    except Exception as e:
        logger.error(f"Gemini Vision extraction failed: {e}")
        return {
            "error": f"Vision extraction failed: {e}",
            "preprocessing": _preprocessing_summary(preprocess_result),
        }

    # Parse the response as JSON
    import json
    try:
        # Strip markdown fences
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        extraction = json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse vision extraction: {e}")
        return {
            "error": "Failed to parse extraction result",
            "raw_response": raw_response[:500],
            "preprocessing": _preprocessing_summary(preprocess_result),
        }

    # Stage 3: Convert extraction to AST
    ast = _extraction_to_ast(extraction, teacher_id, class_section, subject)

    return {
        "ast": ast,
        "preprocessing": _preprocessing_summary(preprocess_result),
        "raw_extraction": extraction,
        "confidence": extraction.get("extraction_confidence", 0.0),
    }


def _extraction_to_ast(
    extraction: dict,
    teacher_id: str,
    class_section: str,
    subject: str,
) -> AssessmentEventAST:
    """Convert Gemini vision extraction to AST."""
    student_info = extraction.get("student_info", {})
    assessment_info = extraction.get("assessment_info", {})
    items_data = extraction.get("items", [])

    # Build student ID from roll number or default
    roll = student_info.get("roll_number") or "00"
    student_id = f"STU-{roll.zfill(2)}" if roll.isdigit() else "STU-00"

    # Build class_section from extraction or use provided
    extracted_section = student_info.get("class_section") or class_section

    # Build score items
    items = []
    for item in items_data:
        q_num = item.get("question_number", 0)
        max_marks = float(item.get("max_marks", 1))
        obtained = float(item.get("obtained_marks", 0))

        items.append(ScoreItem(
            question_id=f"Q-{q_num:02d}",
            knowledge_component_id=f"KC-{subject.upper()[:3]}-Q{q_num:02d}",
            knowledge_component_name=f"{subject.title()} Question {q_num}",
            max_marks=max_marks,
            obtained_marks=min(obtained, max_marks),
            is_correct=obtained >= max_marks * 0.8,
        ))

    max_score = float(assessment_info.get("max_score") or sum(i.max_marks for i in items) or 0)
    total_obtained = float(
        assessment_info.get("total_obtained") or sum(i.obtained_marks for i in items) or 0
    )

    metadata = EventMetadata(
        student_id=student_id,
        teacher_id=teacher_id,
        department_id=f"DEPT-{subject.upper()[:4]}",
        class_section=extracted_section,
        subject=subject,
    )

    academic = AcademicPayload(
        assessment_type=AssessmentType.FORMATIVE,
        max_score=max_score,
        total_obtained=min(total_obtained, max_score) if max_score > 0 else total_obtained,
        items=items,
    )

    return AssessmentEventAST(
        metadata=metadata,
        channel=IngestionChannel.VISION_SCAN,
        academic=academic,
    )


def _preprocessing_summary(result: PreprocessingResult) -> dict:
    """Create a summary of preprocessing results."""
    return {
        "original_size": result.original_size,
        "deskew_angle": result.deskew_angle,
        "quality_score": result.quality_score,
        "is_acceptable": result.is_acceptable,
        "regions_detected": len(result.detected_regions),
    }
