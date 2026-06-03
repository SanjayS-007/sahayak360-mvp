"""
Freetext Parser — Converts teacher natural language to AST via Gemini.
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
from llm.gemini_client import generate_json

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "freetext_to_ast.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


async def parse_freetext_to_ast(
    raw_text: str,
    teacher_id: str,
    class_section: Optional[str] = None,
    subject: str = "mathematics",
) -> AssessmentEventAST:
    """
    Parse freetext teacher input into structured AST using Gemini.
    Falls back to minimal AST if parsing fails.
    """
    prompt_template = _load_prompt()
    prompt = prompt_template.replace("{input_text}", raw_text)

    try:
        parsed = await generate_json(prompt)
    except Exception as e:
        logger.warning(f"Freetext parsing failed, using minimal AST: {e}")
        return _build_minimal_ast(teacher_id, class_section, subject, raw_text)

    # Build AST from parsed data
    try:
        items = []
        for item_data in parsed.get("items", []):
            items.append(ScoreItem(
                question_id=item_data.get("question_id", "Q-00"),
                knowledge_component_id=item_data.get("knowledge_component_id", "KC-UNKNOWN"),
                knowledge_component_name=item_data.get("knowledge_component_name", "Unknown"),
                max_marks=float(item_data.get("max_marks", 0)),
                obtained_marks=float(item_data.get("obtained_marks", 0)),
                is_correct=item_data.get("is_correct", False),
            ))

        student_id = parsed.get("student_id", "STU-00")
        # Validate format
        if not student_id.startswith("STU-"):
            student_id = "STU-00"

        metadata = EventMetadata(
            student_id=student_id,
            teacher_id=teacher_id,
            department_id=parsed.get("department_id", "DEPT-MATH"),
            class_section=parsed.get("class_section") or class_section or "unknown",
            subject=parsed.get("subject") or subject,
        )

        assessment_type_str = parsed.get("assessment_type", "formative")
        try:
            assessment_type = AssessmentType(assessment_type_str)
        except ValueError:
            assessment_type = AssessmentType.FORMATIVE

        academic = AcademicPayload(
            assessment_type=assessment_type,
            max_score=float(parsed.get("max_score", 0)),
            total_obtained=float(parsed.get("total_obtained", 0)),
            items=items,
        )

        return AssessmentEventAST(
            metadata=metadata,
            channel=IngestionChannel.FREETEXT,
            academic=academic,
        )

    except Exception as e:
        logger.error(f"Failed to build AST from parsed data: {e}")
        return _build_minimal_ast(teacher_id, class_section, subject, raw_text)


def _build_minimal_ast(
    teacher_id: str,
    class_section: Optional[str],
    subject: str,
    raw_text: str,
) -> AssessmentEventAST:
    """Build minimal valid AST when parsing fails."""
    return AssessmentEventAST(
        metadata=EventMetadata(
            student_id="STU-00",
            teacher_id=teacher_id,
            department_id="DEPT-MATH",
            class_section=class_section or "unknown",
            subject=subject,
        ),
        channel=IngestionChannel.FREETEXT,
        academic=AcademicPayload(
            assessment_type=AssessmentType.FORMATIVE,
            max_score=0,
            total_obtained=0,
        ),
    )
