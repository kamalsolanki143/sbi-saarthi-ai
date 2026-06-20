"""
SAARTHI AI — Audit Log Model
Real-time audit trail of the agentic workflow pipeline.

Maps to: database/audit_logs.json
Used by: audit_service.py, routes/audit.py (dashboard feed),
         every agent and security module

The 8 audit steps match the dashboard display:
  [Webhook Trigger Received]
  [Memory Evaluation]
  [Agent Activated]
  [Pydantic Validation]
  [Recommendation Generated]
  [Action Preview]
  [MPIN Verification]
  [Execution Complete]
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ──────────────────────────────────────────────────────────────────

class AuditStep(str, Enum):
    """
    The canonical pipeline steps shown on the SAARTHI dashboard.
    Every event processed by an agent must log entries for each relevant step.
    """
    WEBHOOK_TRIGGER = "webhook_trigger"
    MEMORY_EVALUATION = "memory_evaluation"
    AGENT_ACTIVATED = "agent_activated"
    PYDANTIC_VALIDATION = "pydantic_validation"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    ACTION_PREVIEW = "action_preview"
    MPIN_VERIFICATION = "mpin_verification"
    EXECUTION_COMPLETE = "execution_complete"

    # Additional steps
    CONFIDENCE_CHECK = "confidence_check"
    CONSENT_CHECK = "consent_check"
    FALLBACK_TRIGGERED = "fallback_triggered"
    ERROR = "error"


class AuditStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"


# Display labels for the dashboard UI
AUDIT_STEP_LABELS: dict[str, str] = {
    AuditStep.WEBHOOK_TRIGGER: "Webhook Trigger Received",
    AuditStep.MEMORY_EVALUATION: "Memory Evaluation",
    AuditStep.AGENT_ACTIVATED: "Agent Activated",
    AuditStep.PYDANTIC_VALIDATION: "Pydantic Validation",
    AuditStep.RECOMMENDATION_GENERATED: "Recommendation Generated",
    AuditStep.ACTION_PREVIEW: "Action Preview",
    AuditStep.MPIN_VERIFICATION: "MPIN Verification",
    AuditStep.EXECUTION_COMPLETE: "Execution Complete",
    AuditStep.CONFIDENCE_CHECK: "Confidence Check",
    AuditStep.CONSENT_CHECK: "Consent Check",
    AuditStep.FALLBACK_TRIGGERED: "Fallback: Clarifying Question",
    AuditStep.ERROR: "Error",
}


# ── Core Model ─────────────────────────────────────────────────────────────

class AuditLog(BaseModel):
    """
    A single entry in the audit trail for a customer interaction.
    Multiple AuditLog entries form the pipeline trace for one event.
    The dashboard displays these in chronological order with status indicators.
    """
    model_config = ConfigDict(use_enum_values=True)

    log_id: str = Field(..., description="Unique log entry ID")
    customer_id: str = Field(..., description="Customer involved in this step")
    event_id: Optional[str] = Field(None, description="Triggering event ID")
    recommendation_id: Optional[str] = Field(None, description="Related recommendation ID")
    step: AuditStep = Field(..., description="Pipeline step name")
    step_label: str = Field(..., description="Human-readable step name for dashboard")
    agent: Optional[str] = Field(None, description="Agent that executed this step")
    status: AuditStatus = Field(AuditStatus.SUCCESS)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Step-specific data (e.g. confidence score, product details)",
    )
    duration_ms: Optional[int] = Field(None, description="Step execution time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error detail if status=failed")

    @classmethod
    def create(
        cls,
        log_id: str,
        customer_id: str,
        step: AuditStep,
        agent: Optional[str] = None,
        event_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        metadata: Optional[dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> "AuditLog":
        """Factory method with auto-resolved step_label."""
        return cls(
            log_id=log_id,
            customer_id=customer_id,
            event_id=event_id,
            recommendation_id=recommendation_id,
            step=step,
            step_label=AUDIT_STEP_LABELS.get(step, step),
            agent=agent,
            status=status,
            metadata=metadata or {},
            duration_ms=duration_ms,
            error_message=error_message,
        )


# ── Response Models ─────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    """Single audit log entry for API responses."""
    log_id: str
    customer_id: str
    event_id: Optional[str]
    step: str
    step_label: str
    agent: Optional[str]
    status: str
    timestamp: datetime
    metadata: dict[str, Any]
    duration_ms: Optional[int]
    error_message: Optional[str]


class AuditTrailResponse(BaseModel):
    """Full audit trail for a customer — shown on the dashboard."""
    customer_id: str
    total_entries: int
    logs: list[AuditLogResponse]
