"""
SAARTHI AI — FD (Fixed Deposit) Engine
Calculates Fixed Deposit recommendation parameters based on a customer's
idle balance, persona, and SBI's current interest rate table.

Used by: margdarshan_agent.py, recommendation_engine.py
Scope: FD recommendation ONLY — no loan/insurance/MF (out of scope).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.utils.constants import FD_RATES, FD_SENIOR_CITIZEN_BONUS, FD_MIN_ELIGIBLE_BALANCE
from backend.utils.formatters import format_inr, format_interest_rate
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class FDRecommendation:
    """FD recommendation parameters computed by FDEngine."""
    eligible: bool
    recommended_amount: float
    recommended_tenure_months: int
    recommended_tenure_str: str      # e.g. "1 Year"
    interest_rate: float             # % p.a.
    estimated_maturity: float
    interest_earned: float
    is_senior_citizen: bool
    ineligibility_reason: Optional[str] = None

    def to_display_dict(self) -> dict:
        return {
            "product": "SBI Fixed Deposit",
            "amount": format_inr(self.recommended_amount),
            "tenure": self.recommended_tenure_str,
            "interest_rate": format_interest_rate(self.interest_rate),
            "estimated_maturity": format_inr(self.estimated_maturity),
            "interest_earned": format_inr(self.interest_earned),
        }


class FDEngine:
    """
    Computes FD recommendations for MARGDARSHAN agent.

    Strategy:
    - Recommend depositing 60–80% of idle balance (keep 20–40% liquid)
    - Choose tenure based on persona (salaried → 1yr, senior → 3yr, merchant → 6mo)
    - Apply senior citizen bonus if applicable
    """

    PERSONA_TENURE_MAP: dict[str, int] = {
        "salaried": 12,         # 1 year — predictable income, can lock in
        "senior_citizen": 36,   # 3 years — conservative, maximise rate
        "merchant": 6,          # 6 months — needs liquidity
        "farmer": 12,           # 1 year — seasonal income pattern
        "student": 6,           # 6 months — short horizon
        "unknown": 12,
    }

    FD_AMOUNT_RATIO: float = 0.70  # Deposit 70% of idle balance

    def calculate(
        self,
        current_balance: float,
        persona: str,
        customer_id: str,
        date_of_birth: Optional[str] = None,
    ) -> FDRecommendation:
        """
        Calculate FD recommendation parameters.
        Returns FDRecommendation with eligible=False if balance is too low.
        """
        if current_balance < FD_MIN_ELIGIBLE_BALANCE:
            logger.info(
                "fd_ineligible_low_balance",
                customer_id=customer_id,
                balance=current_balance,
                threshold=FD_MIN_ELIGIBLE_BALANCE,
            )
            return FDRecommendation(
                eligible=False,
                recommended_amount=0,
                recommended_tenure_months=0,
                recommended_tenure_str="",
                interest_rate=0,
                estimated_maturity=0,
                interest_earned=0,
                is_senior_citizen=False,
                ineligibility_reason=f"Balance ₹{current_balance:,.0f} below minimum ₹{FD_MIN_ELIGIBLE_BALANCE:,.0f}",
            )

        # Determine age / senior citizen status
        is_senior = self._is_senior_citizen(date_of_birth)
        if is_senior and persona != "senior_citizen":
            persona = "senior_citizen"

        # Compute recommended amount (round to nearest 1000)
        raw_amount = current_balance * self.FD_AMOUNT_RATIO
        recommended_amount = round(raw_amount / 1000) * 1000
        recommended_amount = max(recommended_amount, 1000)  # SBI minimum FD

        # Tenure
        tenure_months = self.PERSONA_TENURE_MAP.get(persona, 12)
        tenure_str = self._months_to_string(tenure_months)

        # Interest rate
        base_rate = self._get_rate_for_tenure(tenure_months)
        interest_rate = base_rate + (FD_SENIOR_CITIZEN_BONUS if is_senior else 0.0)

        # Simple interest calculation (SBI uses compound for multi-year FDs,
        # but simple is fine for display at hackathon scope)
        interest_earned = recommended_amount * (interest_rate / 100) * (tenure_months / 12)
        estimated_maturity = recommended_amount + interest_earned

        logger.info(
            "fd_calculated",
            customer_id=customer_id,
            amount=recommended_amount,
            tenure=tenure_str,
            rate=interest_rate,
            maturity=estimated_maturity,
        )

        return FDRecommendation(
            eligible=True,
            recommended_amount=recommended_amount,
            recommended_tenure_months=tenure_months,
            recommended_tenure_str=tenure_str,
            interest_rate=interest_rate,
            estimated_maturity=round(estimated_maturity, 2),
            interest_earned=round(interest_earned, 2),
            is_senior_citizen=is_senior,
        )

    @staticmethod
    def _get_rate_for_tenure(months: int) -> float:
        """Map tenure in months to the SBI FD interest rate."""
        if months <= 1:
            return FD_RATES["7d_to_45d"]
        elif months <= 5:
            return FD_RATES["46d_to_179d"]
        elif months <= 11:
            return FD_RATES["180d_to_1y"]
        elif months <= 24:
            return FD_RATES["1y_to_2y"]
        elif months <= 36:
            return FD_RATES["2y_to_3y"]
        elif months <= 60:
            return FD_RATES["3y_to_5y"]
        else:
            return FD_RATES["5y_to_10y"]

    @staticmethod
    def _months_to_string(months: int) -> str:
        """Convert month count to human-readable string."""
        if months % 12 == 0:
            yrs = months // 12
            return f"{yrs} Year{'s' if yrs > 1 else ''}"
        if months < 12:
            return f"{months} Month{'s' if months > 1 else ''}"
        yrs = months // 12
        rem = months % 12
        return f"{yrs} Year{'s' if yrs > 1 else ''} {rem} Month{'s' if rem > 1 else ''}"

    @staticmethod
    def _is_senior_citizen(dob_str: Optional[str]) -> bool:
        """Return True if customer is 60 or older."""
        if not dob_str:
            return False
        try:
            from datetime import date
            dob = date.fromisoformat(dob_str)
            age = (date.today() - dob).days // 365
            return age >= 60
        except (ValueError, TypeError):
            return False


# ── Singleton ───────────────────────────────────────────────────────────────
fd_engine = FDEngine()
