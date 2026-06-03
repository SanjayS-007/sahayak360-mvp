"""
Ticket Lifecycle — State machine for intervention tickets.
Tracks creation, assignment, progress, and resolution of support actions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    AWAITING_EVIDENCE = "awaiting_evidence"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    P1 = "P1"  # Critical — same day
    P2 = "P2"  # High — within 2 days
    P3 = "P3"  # Medium — within 1 week
    P4 = "P4"  # Low — scheduled review


class TicketType(str, Enum):
    MICRO_TEST_DISPATCH = "micro_test_dispatch"
    REMEDIATION_PLAN = "remediation_plan"
    PARENT_MEETING = "parent_meeting"
    SPECIALIST_REFERRAL = "specialist_referral"
    PROGRESS_CHECK = "progress_check"


class TicketEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_status: TicketStatus
    to_status: TicketStatus
    actor: str  # teacher_id or "system"
    note: Optional[str] = None


class Ticket(BaseModel):
    ticket_id: str
    student_id: str
    teacher_id: str
    ticket_type: TicketType
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    target_kc_id: str
    target_kc_name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    history: list[TicketEvent] = Field(default_factory=list)


# Valid state transitions
VALID_TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.ASSIGNED, TicketStatus.ESCALATED, TicketStatus.CLOSED},
    TicketStatus.ASSIGNED: {TicketStatus.IN_PROGRESS, TicketStatus.ESCALATED, TicketStatus.CLOSED},
    TicketStatus.IN_PROGRESS: {TicketStatus.AWAITING_EVIDENCE, TicketStatus.RESOLVED, TicketStatus.ESCALATED},
    TicketStatus.AWAITING_EVIDENCE: {TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.ESCALATED},
    TicketStatus.RESOLVED: {TicketStatus.CLOSED, TicketStatus.IN_PROGRESS},  # can reopen
    TicketStatus.ESCALATED: {TicketStatus.ASSIGNED, TicketStatus.CLOSED},
    TicketStatus.CLOSED: set(),  # terminal
}


def can_transition(current: TicketStatus, target: TicketStatus) -> bool:
    """Check if a status transition is valid."""
    return target in VALID_TRANSITIONS.get(current, set())


def transition_ticket(
    ticket: Ticket,
    new_status: TicketStatus,
    actor: str,
    note: Optional[str] = None,
) -> Ticket:
    """
    Transition a ticket to a new status.
    Raises ValueError if transition is invalid.
    """
    if not can_transition(ticket.status, new_status):
        raise ValueError(
            f"Invalid transition: {ticket.status.value} -> {new_status.value}. "
            f"Valid targets: {[s.value for s in VALID_TRANSITIONS[ticket.status]]}"
        )

    event = TicketEvent(
        from_status=ticket.status,
        to_status=new_status,
        actor=actor,
        note=note,
    )
    ticket.history.append(event)
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()

    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()

    return ticket


def create_ticket_from_action(
    student_id: str,
    teacher_id: str,
    action_type: str,
    target_kc_id: str,
    target_kc_name: str,
    description: str,
    priority: TicketPriority = TicketPriority.P3,
) -> Ticket:
    """Factory: create a new ticket from an intervention action."""
    import uuid

    type_mapping = {
        "micro_test": TicketType.MICRO_TEST_DISPATCH,
        "remedial_content": TicketType.REMEDIATION_PLAN,
        "parent_meeting": TicketType.PARENT_MEETING,
        "specialist_referral": TicketType.SPECIALIST_REFERRAL,
        "prerequisite_review": TicketType.REMEDIATION_PLAN,
        "extended_practice": TicketType.PROGRESS_CHECK,
    }
    ticket_type = type_mapping.get(action_type, TicketType.PROGRESS_CHECK)

    return Ticket(
        ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        student_id=student_id,
        teacher_id=teacher_id,
        ticket_type=ticket_type,
        priority=priority,
        target_kc_id=target_kc_id,
        target_kc_name=target_kc_name,
        description=description,
    )
