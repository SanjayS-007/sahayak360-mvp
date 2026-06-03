"""
Rehydration Governor — Fast/Slow Lane Router.
Determines whether incoming data can be processed via fast lane (structured)
or requires slow lane (LLM parsing / vision extraction).
"""

from enum import Enum

from core.ast_schema import (
    AssessmentEventAST,
    EventMetadata,
    AcademicPayload,
    IngestionChannel,
    StructuredIngestRequest,
    FreetextIngestRequest,
    VisionIngestRequest,
)


class ProcessingLane(str, Enum):
    FAST = "fast_lane"
    SLOW = "slow_lane"


class RehydrationDecision:
    def __init__(self, lane: ProcessingLane, reason: str, ast: AssessmentEventAST = None):
        self.lane = lane
        self.reason = reason
        self.ast = ast


def route_structured(request: StructuredIngestRequest) -> RehydrationDecision:
    """
    Fast lane: structured JSON is already in parseable format.
    Directly construct AST without LLM involvement.
    """
    metadata = EventMetadata(
        student_id=request.student_id,
        teacher_id=request.teacher_id,
        institution_id="INST-01",
        department_id=request.department_id,
        class_section=request.class_section,
        subject=request.subject,
        assessment_date=request.assessment_date,
    )

    academic = AcademicPayload(
        assessment_type=request.assessment_type,
        max_score=request.max_score,
        total_obtained=request.total_obtained,
        items=request.items,
    )

    ast = AssessmentEventAST(
        metadata=metadata,
        channel=IngestionChannel.SWIPE_PWA,
        academic=academic,
        pet=request.pet,
        parental=request.parental,
        behavioral=request.behavioral,
    )

    return RehydrationDecision(
        lane=ProcessingLane.FAST,
        reason="Structured JSON — direct AST construction",
        ast=ast,
    )


def route_freetext(request: FreetextIngestRequest) -> RehydrationDecision:
    """
    Slow lane: natural language requires Gemini parsing.
    Returns decision pointing to LLM pipeline.
    """
    return RehydrationDecision(
        lane=ProcessingLane.SLOW,
        reason=f"Freetext input ({len(request.raw_text)} chars) — requires Gemini parsing",
    )


def route_vision(request: VisionIngestRequest) -> RehydrationDecision:
    """
    Slow lane: image requires OpenCV preprocessing + Gemini Vision extraction.
    """
    return RehydrationDecision(
        lane=ProcessingLane.SLOW,
        reason="Vision input — requires OpenCV + Gemini extraction",
    )


def determine_lane(channel: IngestionChannel) -> ProcessingLane:
    """Utility to check expected lane for a given channel."""
    fast_channels = {
        IngestionChannel.SWIPE_PWA,
        IngestionChannel.PET_TRACKER,
        IngestionChannel.PARENT_FEEDBACK,
    }
    return ProcessingLane.FAST if channel in fast_channels else ProcessingLane.SLOW
