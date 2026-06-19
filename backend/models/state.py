"""
SAARTHI AI — Centralized State Model

Defines the canonical LangGraph state (SAARTHIState) and all supporting
domain types consumed by the orchestrator, workflows, engines, and memory
layer.  Every field is strongly typed; no optional-by-omission patterns.

Design decisions
────────────────
• SAARTHIState is a TypedDict so LangGraph can merge partial updates via
  its reducer semantics.  Pydantic models are used for *embedded* rich
  objects (audit entries, consent records, memory snapshots) where
  validation matters.
• Enums use str-mixin so JSON serialisation works without custom encoders.
• All timestamps are UTC-aware datetime objects.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Domain Enums
# ═══════════════════════════════════════════════════════════════════════════


class AgentType(str, Enum):
    """Supported specialist agents in the SAARTHI platform."""

    MITRA = "mitra"
    MARGDARSHAN = "margdarshan"
    SAATHI = "saathi"
    FALLBACK = "fallback"


class PersonaType(str, Enum):
    """Customer persona archetypes for personalisation."""

    STUDENT = "student"
    FARMER = "farmer"
    MERCHANT = "merchant"
    SALARIED = "salaried"
    SENIOR_CITIZEN = "senior_citizen"
    UNKNOWN = "unknown"


class EventType(str, Enum):
    """Banking events that trigger proactive engagement."""

    SALARY_CREDIT = "salary_credit"
    SUBSIDY_CREDIT = "subsidy_credit"
    IDLE_BALANCE_DETECTED = "idle_balance_detected"
    SCHOOL_FEE_DETECTED = "school_fee_detected"
    FESTIVAL_SPENDING_DETECTED = "festival_spending_detected"
    NONE = "none"


class NetworkMode(str, Enum):
    """Adaptive network quality modes for rural/bandwidth-constrained users."""

    VOICE_MODE = "voice_mode"
    TEXT_MODE = "text_mode"
    LOW_BANDWIDTH_MODE = "low_bandwidth_mode"


class ConsentCategory(str, Enum):
    """Granular consent categories per DPDP Act compliance."""

    VOICE_CONSENT = "voice_consent"
    MEMORY_CONSENT = "memory_consent"
    PERSONALIZATION_CONSENT = "personalization_consent"


class IntentCategory(str, Enum):
    """Top-level intent buckets derived from customer queries."""

    ACCOUNT_OPENING = "account_opening"
    BALANCE_INQUIRY = "balance_inquiry"
    FUND_TRANSFER = "fund_transfer"
    BILL_PAYMENT = "bill_payment"
    CARD_SERVICES = "card_services"
    FD_RECOMMENDATION = "fd_recommendation"
    DIGITAL_ADOPTION = "digital_adoption"
    ACCOUNT_SERVICES = "account_services"
    SAVINGS_AWARENESS = "savings_awareness"
    CUSTOMER_ENGAGEMENT = "customer_engagement"
    COMPLAINT = "complaint"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"


class GuardrailStatus(str, Enum):
    """Result of guardrail checks applied before response delivery."""

    PASSED = "passed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


class Priority(str, Enum):
    """Event / action priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Sub-Models (embedded inside state)
# ═══════════════════════════════════════════════════════════════════════════


class ConsentRecord(BaseModel):
    """Immutable record of a single consent grant or denial."""

    category: ConsentCategory
    granted: bool
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(
        default="system",
        description="Origin of consent capture: 'voice', 'app', 'ivr', 'system'.",
    )


class ConsentStatus(BaseModel):
    """Aggregated consent state for a customer session."""

    voice_consent: bool = False
    memory_consent: bool = False
    personalization_consent: bool = False
    records: list[ConsentRecord] = Field(default_factory=list)

    @property
    def all_granted(self) -> bool:
        """Return True only if every consent category is granted."""
        return self.voice_consent and self.memory_consent and self.personalization_consent

    def is_granted(self, category: ConsentCategory) -> bool:
        """Check whether a specific consent category is currently granted."""
        mapping: dict[ConsentCategory, bool] = {
            ConsentCategory.VOICE_CONSENT: self.voice_consent,
            ConsentCategory.MEMORY_CONSENT: self.memory_consent,
            ConsentCategory.PERSONALIZATION_CONSENT: self.personalization_consent,
        }
        return mapping[category]

    def grant(self, category: ConsentCategory, source: str = "system") -> None:
        """Record a consent grant and update the aggregate flag."""
        record = ConsentRecord(category=category, granted=True, source=source)
        self.records.append(record)
        if category == ConsentCategory.VOICE_CONSENT:
            self.voice_consent = True
        elif category == ConsentCategory.MEMORY_CONSENT:
            self.memory_consent = True
        elif category == ConsentCategory.PERSONALIZATION_CONSENT:
            self.personalization_consent = True

    def revoke(self, category: ConsentCategory, source: str = "system") -> None:
        """Record a consent revocation and update the aggregate flag."""
        record = ConsentRecord(category=category, granted=False, source=source)
        self.records.append(record)
        if category == ConsentCategory.VOICE_CONSENT:
            self.voice_consent = False
        elif category == ConsentCategory.MEMORY_CONSENT:
            self.memory_consent = False
        elif category == ConsentCategory.PERSONALIZATION_CONSENT:
            self.personalization_consent = False


class ConfidenceResult(BaseModel):
    """Output of the confidence engine after intent classification."""

    intent: IntentCategory = IntentCategory.UNKNOWN
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Confidence score as a percentage (0–100).",
    )
    recommended_agent: AgentType = AgentType.FALLBACK
    reasoning: str = Field(
        default="",
        description="Human-readable explanation of the classification decision.",
    )

    @property
    def is_confident(self) -> bool:
        """Return True when confidence meets the 85 % routing threshold."""
        return self.confidence >= 85.0


class PersonaResult(BaseModel):
    """Output of the persona engine after customer profiling."""

    persona: PersonaType = PersonaType.UNKNOWN
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Persona classification confidence (0–100).",
    )
    signals: list[str] = Field(
        default_factory=list,
        description="Evidence signals that contributed to the classification.",
    )


class EventResult(BaseModel):
    """Output of the event engine after banking-event detection."""

    event_type: EventType = EventType.NONE
    recommended_agent: AgentType = AgentType.FALLBACK
    priority: Priority = Priority.LOW
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary event-specific metadata (amounts, dates, etc.).",
    )


class MemoryContext(BaseModel):
    """Snapshot of customer memory retrieved for the current turn."""

    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    customer_profile: dict[str, Any] = Field(default_factory=dict)
    product_interests: list[str] = Field(default_factory=list)
    language_preference: str = Field(default="en")
    interaction_count: int = Field(default=0)
    last_agent: AgentType | None = None
    behavioral_context: dict[str, Any] = Field(default_factory=dict)


class AuditEntry(BaseModel):
    """Single immutable audit log entry for compliance and explainability."""

    audit_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    customer_id: str
    agent_selected: AgentType
    intent: IntentCategory
    confidence: float
    event_trigger: EventType = EventType.NONE
    consent_status: ConsentStatus = Field(default_factory=ConsentStatus)
    guardrail_status: GuardrailStatus = GuardrailStatus.PASSED
    response_generated: bool = False
    network_mode: NetworkMode = NetworkMode.TEXT_MODE
    execution_time_ms: float = 0.0
    error: str | None = None


class HumanInLoopAction(BaseModel):
    """Structured payload for actions that require human confirmation."""

    action_type: str = Field(
        description="Descriptive action label, e.g. 'fund_transfer', 'account_opening'.",
    )
    action_preview: dict[str, Any] = Field(
        default_factory=dict,
        description="Human-readable preview of the proposed action.",
    )
    requires_mpin: bool = False
    requires_biometric: bool = False
    requires_human_confirmation: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ═══════════════════════════════════════════════════════════════════════════
# Agent Interface Contract
# ═══════════════════════════════════════════════════════════════════════════


class AgentRequest(BaseModel):
    """Standard request payload sent to any specialist agent."""

    customer_id: str
    query: str
    intent: IntentCategory
    persona: PersonaResult
    memory_context: MemoryContext
    network_mode: NetworkMode = NetworkMode.TEXT_MODE
    language: str = "en"
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)


class AgentResponse(BaseModel):
    """Standard response payload returned by any specialist agent."""

    agent: AgentType
    response_text: str
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    action_required: HumanInLoopAction | None = None
    follow_up_questions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# LangGraph State — the single source of truth flowing through every node
# ═══════════════════════════════════════════════════════════════════════════


class SAARTHIState(TypedDict, total=False):
    """
    Canonical LangGraph state for the SAARTHI AI orchestration pipeline.

    Every workflow node reads from and writes to this dict.  Fields use
    ``total=False`` so nodes can emit partial updates; LangGraph merges
    them via shallow-dict reduction.

    Serialisable fields use Pydantic ``.model_dump()`` before persistence
    and ``.model_validate()`` on retrieval.
    """

    # ── Identity & session ──────────────────────────────────────────────
    customer_id: str
    session_id: str
    query: str
    language: str

    # ── Classification outputs ──────────────────────────────────────────
    intent: IntentCategory
    confidence: float
    confidence_result: ConfidenceResult
    persona: PersonaType
    persona_result: PersonaResult

    # ── Routing ─────────────────────────────────────────────────────────
    agent: AgentType
    event_type: EventType
    event_result: EventResult

    # ── Memory ──────────────────────────────────────────────────────────
    memory_context: MemoryContext

    # ── Response ────────────────────────────────────────────────────────
    response: str
    agent_response: AgentResponse
    action_required: HumanInLoopAction | None

    # ── Compliance & governance ─────────────────────────────────────────
    consent_status: ConsentStatus
    audit_logs: list[AuditEntry]
    guardrail_status: GuardrailStatus

    # ── Infrastructure ──────────────────────────────────────────────────
    network_mode: NetworkMode
    timestamp: datetime
    error: str | None


# ═══════════════════════════════════════════════════════════════════════════
# Factory helper
# ═══════════════════════════════════════════════════════════════════════════


def create_initial_state(
    customer_id: str,
    query: str,
    language: str = "en",
    network_mode: NetworkMode = NetworkMode.TEXT_MODE,
    session_id: str | None = None,
) -> SAARTHIState:
    """
    Build a fully-initialised SAARTHIState with safe defaults.

    This is the **only** sanctioned way to create a new pipeline state.
    Down-stream nodes may mutate individual keys but must never replace
    the state object itself.
    """
    return SAARTHIState(
        customer_id=customer_id,
        session_id=session_id or uuid.uuid4().hex,
        query=query,
        language=language,
        intent=IntentCategory.UNKNOWN,
        confidence=0.0,
        confidence_result=ConfidenceResult(),
        persona=PersonaType.UNKNOWN,
        persona_result=PersonaResult(),
        agent=AgentType.FALLBACK,
        event_type=EventType.NONE,
        event_result=EventResult(),
        memory_context=MemoryContext(),
        response="",
        agent_response=AgentResponse(agent=AgentType.FALLBACK, response_text=""),
        action_required=None,
        consent_status=ConsentStatus(),
        audit_logs=[],
        guardrail_status=GuardrailStatus.PASSED,
        network_mode=network_mode,
        timestamp=datetime.now(timezone.utc),
        error=None,
    )