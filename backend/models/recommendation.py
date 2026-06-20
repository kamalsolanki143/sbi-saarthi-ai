"""
SAARTHI AI — Recommendation Model (MVP Priority)
Pydantic v2 model for AI-generated banking recommendations.

Maps to: (in-memory / returned from recommendation_engine.py)
Used by: recommendation_engine.py, routes/recommendation.py,
         human_in_loop.py (Action Preview → MPIN gate),
         all three agents (mitra, margdarshan, saathi)

Every recommendation ships with:
  - why_explanation: "Why am I seeing this?" (Explainable AI requirement)
  - action_preview: Exact action details shown before MPIN screen
  - confidence_score: Must be ≥ 0.85 to reach user (confidence_checker.py enforces this)
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Enums ──────────────────────────────────────────────────────────────────

class RecommendationStatus(str, Enum):
    """Lifecycle state of a recommendation."""
    PENDING = "pending"          # Generated, not yet shown to user
    SHOWN = "shown"              # Displayed to customer
    ACTION_PREVIEW = "action_preview"  # Customer clicked — showing preview
    ACCEPTED = "accepted"        # Customer confirmed via MPIN
    REJECTED = "rejected"        # Customer declined
    EXPIRED = "expired"          # TTL elapsed without action


class ProductType(str, Enum):
    """Banking product types that can be recommended (in-scope only)."""
    FIXED_DEPOSIT = "fixed_deposit"
    UPI_ACTIVATION = "upi_activation"
    YONO_ADOPTION = "yono_adoption"
    SAVINGS_ACCOUNT = "savings_account"
    RECURRING_DEPOSIT = "recurring_deposit"
    KYC_COMPLETION = "kyc_completion"
    DIGITAL_LITERACY = "digital_literacy"


# ── Nested Models ──────────────────────────────────────────────────────────

class ActionPreview(BaseModel):
    """
    The exact action details shown to the customer BEFORE the MPIN screen.
    This is the 'Action Preview Layer' requirement — nothing is executed
    without the customer explicitly seeing and approving this.

    Example (FD):
        Product: SBI Fixed Deposit
        Amount: ₹5,000
        Tenure: 1 Year
        Interest Rate: 6.80% p.a.
    """
    model_config = ConfigDict(use_enum_values=True)

    product: str = Field(..., description="Product name, e.g. 'SBI Fixed Deposit'")
    product_type: ProductType = Field(..., description="Product type enum")
    amount: Optional[float] = Field(None, ge=0.0, description="Amount in INR")
    tenure: Optional[str] = Field(None, description="Tenure string, e.g. '1 Year'")
    interest_rate: Optional[float] = Field(
        None, ge=0.0, le=30.0, description="Interest rate % p.a."
    )
    action_label: str = Field(
        ..., description="CTA button label, e.g. 'Open Fixed Deposit'"
    )
    action_details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional product-specific details",
    )
    estimated_return: Optional[float] = Field(
        None, description="Estimated maturity amount in INR (for FD/RD)"
    )


class ExplainabilityNote(BaseModel):
    """
    Structured 'Why am I seeing this?' content.
    Part of SAARTHI AI's Explainable AI requirement.
    """
    short_reason: str = Field(
        ..., description="One-line reason shown in the recommendation card"
    )
    detailed_reason: str = Field(
        ..., description="Full paragraph shown when customer taps 'Why?'"
    )
    data_used: list[str] = Field(
        default_factory=list,
        description="List of data points used, e.g. ['Salary credit on 1 Jun', 'Balance idle 30 days']",
    )
    agent_source: str = Field(..., description="Which agent generated this: mitra/margdarshan/saathi")


# ── Core Model ─────────────────────────────────────────────────────────────

class Recommendation(BaseModel):
    """
    A validated AI recommendation ready to be shown to the customer.

    Safety guarantee: confidence_score < 0.85 → this object is never created.
    The confidence_checker.py guardrail enforces this upstream.
    """
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "recommendation_id": "REC-ABC123",
                "customer_id": "CUST001",
                "agent_source": "margdarshan",
                "product_type": "fixed_deposit",
                "title": "Earn More on Your Idle Balance",
                "description": "You have ₹45,000 sitting idle. Open an FD and earn 6.80% p.a.",
                "why_explanation": "Your salary was credited on 1 Jun but ₹45,000 hasn't moved in 30 days.",
                "confidence_score": 0.92,
            }
        },
    )

    recommendation_id: str = Field(..., description="Unique recommendation ID, e.g. REC-ABC123")
    customer_id: str = Field(..., description="Target customer ID")
    agent_source: str = Field(
        ..., description="Agent that generated this: mitra | margdarshan | saathi"
    )
    event_id: Optional[str] = Field(None, description="Triggering event ID if applicable")
    product_type: ProductType = Field(..., description="Type of product being recommended")
    title: str = Field(..., min_length=5, max_length=100, description="Short recommendation title")
    description: str = Field(..., min_length=10, description="Full recommendation description")
    why_explanation: str = Field(
        ...,
        description="Explainability text: 'Why am I seeing this?'",
        min_length=10,
    )
    explainability: Optional[ExplainabilityNote] = Field(
        None, description="Structured explainability (richer than why_explanation string)"
    )
    action_preview: ActionPreview = Field(
        ..., description="Exact action details shown before MPIN screen"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Intent confidence (0.0–1.0). Must be ≥ 0.85 to reach user.",
    )
    status: RecommendationStatus = Field(RecommendationStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(
        None, description="Recommendation expires at this time (default: 72h)"
    )
    language: str = Field("en", description="Language of recommendation text (ISO 639-1)")

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """
        Guardrail: A Recommendation object should NEVER be created
        with confidence < 0.85. The confidence_checker.py should
        catch this upstream, but we double-check here as a safety net.
        """
        from backend.utils.constants import CONFIDENCE_THRESHOLD
        if v < CONFIDENCE_THRESHOLD:
            raise ValueError(
                f"confidence_score {v:.2f} is below the required threshold "
                f"{CONFIDENCE_THRESHOLD}. Use the fallback flow instead."
            )
        return round(v, 4)

    @field_validator("agent_source")
    @classmethod
    def validate_agent_source(cls, v: str) -> str:
        from backend.utils.constants import ALL_AGENTS, AGENT_FALLBACK
        valid = ALL_AGENTS + [AGENT_FALLBACK]
        if v not in valid:
            raise ValueError(f"agent_source must be one of {valid}, got '{v}'")
        return v


# ── Request / Response Models ──────────────────────────────────────────────

class RecommendationListResponse(BaseModel):
    """Response for GET /recommendations/{customer_id}."""
    customer_id: str
    total: int
    recommendations: list[Recommendation]


class ActionPreviewResponse(BaseModel):
    """Response for POST /recommendations/{id}/action-preview."""
    recommendation_id: str
    customer_id: str
    action_preview: ActionPreview
    why_explanation: str
    next_step: str = "Verify with MPIN to proceed"


class ConfirmRecommendationRequest(BaseModel):
    """Request for POST /recommendations/{id}/confirm — triggers MPIN gate."""
    customer_id: str
    mpin: str = Field(..., min_length=4, max_length=6, description="Customer MPIN")


class FallbackResponse(BaseModel):
    """
    Returned when confidence < 0.85 — instead of a recommendation,
    the agent asks a clarifying question.
    """
    customer_id: str
    agent: str
    confidence_score: float
    clarifying_question: str
    question_options: list[str] = Field(
        default_factory=list, description="Quick-reply options for the clarifying question"
    )
    session_id: str
