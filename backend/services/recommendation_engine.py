"""
SAARTHI AI — Recommendation Engine
Structures raw agent output into validated Recommendation objects,
generates the 'Why am I seeing this?' explanation, and persists recommendations.

Used by: margdarshan_agent.py, mitra_agent.py, saathi_agent.py
The output of this service always passes through guardrails/action_validator.py
before being returned to the customer.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from backend.models.recommendation import (
    ActionPreview,
    ExplainabilityNote,
    ProductType,
    Recommendation,
    RecommendationStatus,
    FallbackResponse,
)
from backend.services.confidence_engine import ConfidenceResult
from backend.utils import json_repository as repo
from backend.utils.constants import REC_DEFAULT_EXPIRY_HOURS
from backend.utils.formatters import format_inr
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION = "audit_logs"  # Recommendations stored in memory / returned in-session


class RecommendationEngine:
    """
    Converts structured agent data (e.g., FDRecommendation) into a fully-formed
    Recommendation object ready for the customer-facing Action Preview Layer.
    """

    def build_fd_recommendation(
        self,
        customer_id: str,
        agent_source: str,
        fd_result: Any,          # FDRecommendation from fd_engine.py
        event_id: Optional[str] = None,
        persona: str = "unknown",
        language: str = "en",
    ) -> Recommendation:
        """
        Build a Fixed Deposit recommendation from an FDRecommendation object.
        """
        rec_id = repo.generate_id("REC-")

        why_short = f"You have {format_inr(fd_result.recommended_amount)} sitting idle"
        why_detail = (
            f"Your account balance of {format_inr(fd_result.recommended_amount)} has been "
            f"sitting idle. By opening a Fixed Deposit for {fd_result.recommended_tenure_str}, "
            f"you can earn {fd_result.interest_rate:.2f}% p.a. and get "
            f"{format_inr(fd_result.estimated_maturity)} at maturity."
        )

        if fd_result.is_senior_citizen:
            why_detail += " As a senior citizen, you get an additional 0.50% interest bonus!"

        action_preview = ActionPreview(
            product="SBI Fixed Deposit",
            product_type=ProductType.FIXED_DEPOSIT,
            amount=fd_result.recommended_amount,
            tenure=fd_result.recommended_tenure_str,
            interest_rate=fd_result.interest_rate,
            action_label="Open Fixed Deposit",
            action_details={
                "maturity_amount": fd_result.estimated_maturity,
                "interest_earned": fd_result.interest_earned,
                "is_senior_citizen_rate": fd_result.is_senior_citizen,
            },
            estimated_return=fd_result.estimated_maturity,
        )

        explainability = ExplainabilityNote(
            short_reason=why_short,
            detailed_reason=why_detail,
            data_used=[
                f"Current balance: {format_inr(fd_result.recommended_amount / 0.70)}",
                f"Balance idle for ≥14 days",
                f"Persona: {persona}",
            ],
            agent_source=agent_source,
        )

        rec = Recommendation(
            recommendation_id=rec_id,
            customer_id=customer_id,
            agent_source=agent_source,
            event_id=event_id,
            product_type=ProductType.FIXED_DEPOSIT,
            title="Earn More on Your Idle Balance",
            description=(
                f"Open an SBI Fixed Deposit of {format_inr(fd_result.recommended_amount)} "
                f"for {fd_result.recommended_tenure_str} at {fd_result.interest_rate:.2f}% p.a. "
                f"and earn {format_inr(fd_result.interest_earned)}."
            ),
            why_explanation=why_detail,
            explainability=explainability,
            action_preview=action_preview,
            confidence_score=0.92,
            status=RecommendationStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=REC_DEFAULT_EXPIRY_HOURS),
            language=language,
        )

        logger.info(
            "recommendation_built",
            rec_id=rec_id,
            customer_id=customer_id,
            product_type="fixed_deposit",
            agent=agent_source,
        )
        return rec

    def build_upi_recommendation(
        self,
        customer_id: str,
        agent_source: str,
        event_id: Optional[str] = None,
    ) -> Recommendation:
        """Build a UPI activation recommendation."""
        rec_id = repo.generate_id("REC-")

        action_preview = ActionPreview(
            product="SBI UPI",
            product_type=ProductType.UPI_ACTIVATION,
            action_label="Activate UPI Now",
            action_details={"setup_steps": 3, "time_required": "2 minutes"},
        )

        return Recommendation(
            recommendation_id=rec_id,
            customer_id=customer_id,
            agent_source=agent_source,
            event_id=event_id,
            product_type=ProductType.UPI_ACTIVATION,
            title="Start Paying Instantly with UPI",
            description="Activate SBI UPI in 2 minutes and send/receive money instantly — 24x7, zero charges.",
            why_explanation="Your account is UPI-ready but UPI hasn't been activated yet. 78% of SBI customers use UPI for daily payments.",
            action_preview=action_preview,
            confidence_score=0.93,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=REC_DEFAULT_EXPIRY_HOURS),
        )

    def build_yono_recommendation(
        self,
        customer_id: str,
        agent_source: str,
        event_id: Optional[str] = None,
    ) -> Recommendation:
        """Build a YONO adoption recommendation."""
        rec_id = repo.generate_id("REC-")

        action_preview = ActionPreview(
            product="YONO SBI",
            product_type=ProductType.YONO_ADOPTION,
            action_label="Download YONO App",
            action_details={"platform": "Android & iOS", "features": ["UPI", "FD", "Loans", "Shopping"]},
        )

        return Recommendation(
            recommendation_id=rec_id,
            customer_id=customer_id,
            agent_source=agent_source,
            event_id=event_id,
            product_type=ProductType.YONO_ADOPTION,
            title="Manage All Your Banking from One App",
            description="YONO SBI — You Only Need One app. Pay bills, open FDs, track spending, and more.",
            why_explanation="You haven't yet downloaded YONO SBI. Customers who use YONO save 45 minutes per month on banking tasks.",
            action_preview=action_preview,
            confidence_score=0.91,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=REC_DEFAULT_EXPIRY_HOURS),
        )

    def build_fallback_response(
        self,
        customer_id: str,
        agent: str,
        confidence_result: ConfidenceResult,
        session_id: str,
    ) -> FallbackResponse:
        """
        Build a FallbackResponse for when confidence < 0.85.
        This is what the agent returns instead of a Recommendation.
        """
        return FallbackResponse(
            customer_id=customer_id,
            agent=agent,
            confidence_score=confidence_result.confidence,
            clarifying_question=confidence_result.clarifying_question
            or "Kya aap thoda aur bata sakte hain?",
            question_options=confidence_result.quick_reply_options,
            session_id=session_id,
        )

    def get_customer_recommendations(
        self, customer_id: str
    ) -> list[Recommendation]:
        """
        Retrieve active recommendations for a customer.
        In production, this would query a DB. For hackathon scope,
        recommendations are stored in audit_logs as metadata and returned from cache.
        """
        # For hackathon scope, we return in-memory. The real pattern
        # would store recs in database/recommendations.json
        return []


# ── Singleton ───────────────────────────────────────────────────────────────
recommendation_engine = RecommendationEngine()
