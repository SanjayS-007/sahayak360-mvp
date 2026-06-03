"""
Sahayak 360 — Frozen AST Schema (v2.0)
Universal Assessment Event schema supporting any subject.
All data entering the system MUST conform to this contract.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class IngestionChannel(str, Enum):
    SWIPE_PWA = "SWIPE_PWA"
    VISION_SCAN = "VISION_SCAN"
    FREETEXT = "FREETEXT"
    VOICE = "VOICE"
    PET_TRACKER = "PET_TRACKER"
    PARENT_FEEDBACK = "PARENT_FEEDBACK"


class AssessmentType(str, Enum):
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    MICRO_TEST = "micro_test"
    PET_EVALUATION = "pet_evaluation"


class AthleticRating(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    F = "F"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ParticipationRating(str, Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    DISENGAGED = "disengaged"


class ScoreItem(BaseModel):
    question_id: str = Field(..., min_length=1)
    knowledge_component_id: str = Field(..., min_length=1)
    knowledge_component_name: str = Field(..., min_length=1)
    max_marks: float = Field(..., ge=0)
    obtained_marks: float = Field(..., ge=0)
    is_correct: bool = False

    @field_validator("obtained_marks")
    @classmethod
    def marks_not_exceed_max(cls, v, info):
        max_marks = info.data.get("max_marks")
        if max_marks is not None and v > max_marks:
            raise ValueError(f"obtained_marks ({v}) cannot exceed max_marks ({max_marks})")
        return v


class AcademicPayload(BaseModel):
    assessment_type: AssessmentType
    max_score: float = Field(..., ge=0)
    total_obtained: float = Field(..., ge=0)
    items: list[ScoreItem] = Field(default_factory=list)

    @field_validator("total_obtained")
    @classmethod
    def total_not_exceed_max(cls, v, info):
        max_score = info.data.get("max_score")
        if max_score is not None and v > max_score:
            raise ValueError(f"total_obtained ({v}) cannot exceed max_score ({max_score})")
        return v


class PETPayload(BaseModel):
    athletic_rating: Optional[AthleticRating] = None
    activity_tags: list[str] = Field(default_factory=list)
    raw_description: Optional[str] = None


class ParentalPayload(BaseModel):
    sentiment: Optional[Sentiment] = None
    raw_notes: Optional[str] = None
    concern_tags: list[str] = Field(default_factory=list)


class BehavioralPayload(BaseModel):
    attendance_streak: int = Field(default=0, ge=0)
    participation_rating: ParticipationRating = ParticipationRating.ACTIVE
    swipe_indicator: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class EventMetadata(BaseModel):
    student_id: str = Field(..., pattern=r"^STU-\d{2,8}$")
    teacher_id: str = Field(..., pattern=r"^TCH-\d{2,8}$")
    institution_id: str = Field(default="INST-01", pattern=r"^INST-\d{2,8}$")
    department_id: str = Field(..., pattern=r"^DEPT-\w+$")
    class_section: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    assessment_date: Optional[date] = None

    @field_validator("assessment_date")
    @classmethod
    def date_not_future(cls, v):
        if v and v > date.today():
            raise ValueError("assessment_date cannot be in the future")
        return v


class ValidationResult(BaseModel):
    sum_check_passed: bool = True
    computed_sum: float = 0.0
    declared_total: float = 0.0
    discrepancy: float = 0.0
    anomaly_flags: list[str] = Field(default_factory=list)


class AssessmentEventAST(BaseModel):
    """The universal AST contract. All ingestion channels produce this."""
    metadata: EventMetadata
    channel: IngestionChannel
    academic: AcademicPayload
    pet: Optional[PETPayload] = None
    parental: Optional[ParentalPayload] = None
    behavioral: Optional[BehavioralPayload] = None
    validation: Optional[ValidationResult] = None


# --- Request/Response models for API ---

class StructuredIngestRequest(BaseModel):
    """Direct structured JSON from SwipePWA or pre-formatted input."""
    teacher_id: str = Field(..., pattern=r"^TCH-\d{2,8}$")
    student_id: str = Field(..., pattern=r"^STU-\d{2,8}$")
    class_section: str
    subject: str
    department_id: str = Field(default="DEPT-MATH")
    assessment_type: AssessmentType = AssessmentType.FORMATIVE
    assessment_date: Optional[date] = None
    max_score: float = Field(..., ge=0)
    total_obtained: float = Field(..., ge=0)
    items: list[ScoreItem] = Field(default_factory=list)
    pet: Optional[PETPayload] = None
    parental: Optional[ParentalPayload] = None
    behavioral: Optional[BehavioralPayload] = None


class FreetextIngestRequest(BaseModel):
    """Natural language input from teacher — parsed via Gemini."""
    teacher_id: str = Field(..., pattern=r"^TCH-\d{2,8}$")
    raw_text: str = Field(..., min_length=10)
    class_section: Optional[str] = None
    subject: Optional[str] = "mathematics"


class VisionIngestRequest(BaseModel):
    """Image-based input — processed via OpenCV + Gemini Vision."""
    teacher_id: str = Field(..., pattern=r"^TCH-\d{2,8}$")
    class_section: str
    subject: str = "mathematics"


class IngestResponse(BaseModel):
    status: str = "accepted"
    event_id: Optional[str] = None
    parse_method: str = "fast_lane"
    validation: ValidationResult
    cognitive_analysis: Optional[dict] = None
    graph_mutations: list[str] = Field(default_factory=list)


class IngestErrorResponse(BaseModel):
    status: str = "rejected"
    error: str = "validation_failed"
    details: dict = Field(default_factory=dict)
