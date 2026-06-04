"""
SQLAlchemy models for PostgreSQL.
"""

from datetime import date, datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(String(20), unique=True, nullable=False)  # INST-XX
    name = Column(String(200), nullable=False)
    type = Column(String(50), default="school")
    created_at = Column(DateTime, default=datetime.utcnow)

    departments = relationship("Department", back_populates="institution")


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(String(30), unique=True, nullable=False)  # DEPT-MATH
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"))
    name = Column(String(100), nullable=False)
    subject = Column(String(50), nullable=False)

    institution = relationship("Institution", back_populates="departments")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), unique=True, nullable=False)  # TCH-XX or STU-XX
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(SAEnum("teacher", "student", "admin", "parent", name="user_role"), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"))
    department_id = Column(String(30), nullable=True)
    class_section = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssessmentEvent(Base):
    __tablename__ = "assessment_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(30), unique=True, nullable=False)
    student_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    teacher_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    institution_id = Column(String(20), nullable=False)
    department_id = Column(String(30), nullable=False)
    class_section = Column(String(20), nullable=False)
    subject = Column(String(50), nullable=False)
    channel = Column(String(30), nullable=False)
    assessment_type = Column(String(30), nullable=False)
    assessment_date = Column(Date, nullable=True)
    max_score = Column(Float, nullable=False)
    total_obtained = Column(Float, nullable=False)
    items = Column(JSON, default=list)  # list of score items
    validation_result = Column(JSON, nullable=True)
    cognitive_analysis = Column(JSON, nullable=True)
    pet_data = Column(JSON, nullable=True)
    behavioral_data = Column(JSON, nullable=True)
    parental_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MasteryRecord(Base):
    __tablename__ = "mastery_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    kc_id = Column(String(50), nullable=False)
    kc_name = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False)
    mastery = Column(Float, default=0.0)
    mastery_level = Column(String(20), default="not_attempted")
    attempts = Column(Integer, default=0)
    last_event_id = Column(String(30), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class InterventionTicket(Base):
    __tablename__ = "intervention_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(20), unique=True, nullable=False)
    student_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    teacher_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    ticket_type = Column(String(30), nullable=False)
    priority = Column(String(5), nullable=False)
    status = Column(String(30), default="open")
    target_kc_id = Column(String(50), nullable=False)
    target_kc_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    history = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(30), unique=True, nullable=False)
    student_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    teacher_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    ticket_id = Column(String(20), nullable=True)
    target_kc_ids = Column(JSON, default=list)
    questions = Column(JSON, default=list)
    responses = Column(JSON, default=list)
    status = Column(String(20), default="pending")  # pending, active, completed, expired
    score = Column(Float, nullable=True)
    dispatched_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(20), ForeignKey("users.user_id"), nullable=False)
    type = Column(String(30), nullable=False)  # practice_result, risk_alert, badge, quiz, ticket, weekly
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
