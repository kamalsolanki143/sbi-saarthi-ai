"""
SAARTHI AI — Persona Engine
Classifies a customer into one of five personas based on transaction
and behavioural patterns:

  Farmer      (Kisan)
  Student     (Vidyarthi)
  Merchant    (Vyapari)
  Salaried    (Naukripeshaa)
  Senior Citizen (Varishtha Naagrik)

Used by: routes/customer.py, customer_memory.py,
         margdarshan_agent.py, mitra_agent.py, fd_engine.py

Persona detection uses rule-based scoring over transaction patterns.
If no clear winner, returns UNKNOWN.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from backend.models.customer import PersonaType
from backend.models.transaction import Transaction, TransactionCategory
from backend.utils.constants import (
    PERSONA_FARMER, PERSONA_MERCHANT, PERSONA_SALARIED,
    PERSONA_SENIOR_CITIZEN, PERSONA_STUDENT, PERSONA_UNKNOWN,
)
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class PersonaEngine:
    """
    Rule-based persona classifier.
    Each persona has a weighted set of signals. The persona with the
    highest score above the threshold wins.
    """

    SCORE_THRESHOLD = 2.0  # Minimum score to claim a persona

    async def classify(
        self,
        customer_id: str,
        transactions: list[dict],
        date_of_birth: Optional[str] = None,
        account_type: Optional[str] = None,
        address: Optional[str] = None,
    ) -> PersonaType:
        """
        Classify a customer's persona from available signals.
        Returns PersonaType enum value.
        """
        scores: dict[str, float] = {
            PERSONA_FARMER: 0.0,
            PERSONA_STUDENT: 0.0,
            PERSONA_MERCHANT: 0.0,
            PERSONA_SALARIED: 0.0,
            PERSONA_SENIOR_CITIZEN: 0.0,
        }

        # ── Signal 1: Age ───────────────────────────────────────────────────
        if date_of_birth:
            age = self._calculate_age(date_of_birth)
            if age is not None:
                if age >= 60:
                    scores[PERSONA_SENIOR_CITIZEN] += 3.0
                elif 18 <= age <= 25:
                    scores[PERSONA_STUDENT] += 2.0

        # ── Signal 2: Account type ──────────────────────────────────────────
        if account_type == "jan_dhan":
            scores[PERSONA_FARMER] += 2.0
        elif account_type == "current":
            scores[PERSONA_MERCHANT] += 3.0
        elif account_type == "salary":
            scores[PERSONA_SALARIED] += 2.0

        # ── Signal 3: Address (rural/urban heuristic) ───────────────────────
        if address:
            rural_keywords = ["village", "gram", "tehsil", "taluka", "dist ", "district"]
            if any(kw in address.lower() for kw in rural_keywords):
                scores[PERSONA_FARMER] += 1.5

        # ── Signal 4: Transaction patterns ─────────────────────────────────
        if transactions:
            self._score_transactions(transactions, scores)

        # ── Pick winner ─────────────────────────────────────────────────────
        best_persona = max(scores, key=lambda k: scores[k])
        best_score = scores[best_persona]

        if best_score < self.SCORE_THRESHOLD:
            logger.info(
                "persona_unclassified",
                customer_id=customer_id,
                scores=scores,
            )
            return PersonaType.UNKNOWN

        logger.info(
            "persona_classified",
            customer_id=customer_id,
            persona=best_persona,
            score=best_score,
            all_scores=scores,
        )
        return PersonaType(best_persona)

    def _score_transactions(self, transactions: list[dict], scores: dict[str, float]) -> None:
        """Apply transaction-pattern signals to the score dict."""
        salary_credits = 0
        subsidy_credits = 0
        scholarship_credits = 0
        business_income_credits = 0
        education_debits = 0
        pension_credits = 0
        total_credit_txns = 0
        unique_credit_sources = set()

        for txn in transactions:
            category = txn.get("category", "")
            txn_type = txn.get("transaction_type", "")
            merchant = txn.get("merchant", "")

            if txn_type == "credit":
                total_credit_txns += 1
                unique_credit_sources.add(merchant)

                if category == TransactionCategory.SALARY:
                    salary_credits += 1
                elif category == TransactionCategory.SUBSIDY:
                    subsidy_credits += 1
                elif category == TransactionCategory.SCHOLARSHIP:
                    scholarship_credits += 1
                elif category == TransactionCategory.BUSINESS_INCOME:
                    business_income_credits += 1
                elif category == TransactionCategory.PENSION:
                    pension_credits += 1

            elif txn_type == "debit" and category == TransactionCategory.EDUCATION:
                education_debits += 1

        # Apply scores
        if salary_credits >= 2:
            scores[PERSONA_SALARIED] += 3.0
        if subsidy_credits >= 1:
            scores[PERSONA_FARMER] += 2.5
        if scholarship_credits >= 1:
            scores[PERSONA_STUDENT] += 2.5
        if education_debits >= 2:
            scores[PERSONA_STUDENT] += 1.5
        if len(unique_credit_sources) >= 5:
            scores[PERSONA_MERCHANT] += 2.0
        if business_income_credits >= 1:
            scores[PERSONA_MERCHANT] += 2.0
        if pension_credits >= 1:
            scores[PERSONA_SENIOR_CITIZEN] += 3.0

    @staticmethod
    def _calculate_age(dob_str: str) -> Optional[int]:
        """Calculate age from a YYYY-MM-DD date string."""
        try:
            dob = date.fromisoformat(dob_str)
            today = date.today()
            return (today - dob).days // 365
        except (ValueError, TypeError):
            return None


# ── Singleton ───────────────────────────────────────────────────────────────
persona_engine = PersonaEngine()
