"""
SAARTHI AI — Event Model (MVP Priority)
Pydantic v2 model for banking events that trigger agent workflows.

Maps to: database/events.json
Used by: event_engine.py, orchestrator.py, routes/event.py,
         MARGDARSHAN (salary/idle), MITRA (KYC), SAATHI (life events)

Event lifecycle:
  Webhook → event_engine classifies → orchestrator routes → agent processes →
  recommendation generated → audit trail logged
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Enums ──────────────────────────────────────────────────────────────────

class EventType(str, Enum):
    """
    All event types SAARTHI AI can process.
    Each maps to a specific agent via EVENT_AGENT_MAP in constants.py.

    MARGDARSHAN handles: salary_credit, subsidy_credit, idle_balance,
                         upi_not_activated, yono_not_adopted, fd_eligible
    SAATHI handles:      life_event, education_expense, festival_period,
                         travel_spending, spending_anomaly
    MITRA handles:       kyc_incomplete, account_opened
    """
    SALARY_CREDIT = "salary_credit"
    SUBSIDY_CREDIT = "subsidy_credit"
    IDLE_BALANCE = "idle_balance"
    UPI_NOT_ACTIVATED = "upi_not_activated"
    YONO_NOT_ADOPTED = "yono_not_adopted"
    FD_ELIGIBLE = "fd_eligible"
    LIFE_EVENT = "life_event"
    EDUCATION_EXPENSE = "education_expense"
    FESTIVAL_PERIOD = "festival_period"
    TRAVEL_SPENDING = "travel_spending"
    SPENDING_ANOMALY = "spending_anomaly"
    KYC_INCOMPLETE = "kyc_incomplete"
    ACCOUNT_OPENED = "account_opened"


class EventSource(str, Enum):
    """Origin of the event."""
    WEBHOOK = "webhook"     # External system (CBS, UPI switch, etc.)
    SYSTEM = "system"       # Internally generated (scheduled jobs, balance monitor)
    MANUAL = "manual"       # Test/demo events injected via API


class EventStatus(str, Enum):
    """Processing status of the event."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    IGNORED = "ignored"     # Event received but no action warranted


# ── Core Model ─────────────────────────────────────────────────────────────

class Event(BaseModel):
    """
    A banking event that may trigger an agentic workflow.
    Created either by external webhooks (CBS, UPI system) or internal monitors.
    """
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "event_id": "EVT001",
                "customer_id": "CUST001",
                "event_type": "salary_credit",
                "amount": 55000.00,
                "source": "webhook",
            }
        },
    )

    event_id: str = Field(..., description="Unique event ID")
    customer_id: str = Field(..., description="Customer this event belongs to")
    event_type: EventType = Field(..., description="Type of banking event")
    amount: Optional[float] = Field(None, ge=0.0, description="Amount in INR if applicable")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific payload (employer, scheme name, idle days, etc.)",
    )
    source: EventSource = Field(EventSource.WEBHOOK, description="Origin of the event")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred",
    )
    processed: bool = Field(False, description="Whether this event has been processed by an agent")
    agent_assigned: Optional[str] = Field(
        None, description="Which agent handled this event (e.g. 'margdarshan')"
    )
    processing_result: Optional[str] = Field(
        None, description="Short description of what the agent did"
    )
    status: EventStatus = Field(EventStatus.PENDING)

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("customer_id cannot be empty")
        return v.strip().upper()


# ── Request / Response Models ──────────────────────────────────────────────

class EventCreateRequest(BaseModel):
    """
    Request body for POST /events.
    Used by external systems (CBS webhook) and internal schedulers.
    """
    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    customer_id: str = Field(..., description="Customer ID")
    event_type: EventType = Field(..., description="Type of event")
    amount: Optional[float] = Field(None, ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: EventSource = Field(EventSource.WEBHOOK)

    @field_validator("customer_id")
    @classmethod
    def normalise_customer_id(cls, v: str) -> str:
        return v.strip().upper()


class EventResponse(BaseModel):
    """Response returned after an event is accepted."""
    event_id: str
    customer_id: str
    event_type: str
    status: str
    agent_assigned: Optional[str]
    timestamp: datetime
    message: str


class EventListResponse(BaseModel):
    """List of events for a customer."""
    customer_id: str
    total: int
    events: list[EventResponse]
