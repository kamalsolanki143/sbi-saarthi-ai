"""
SAARTHI AI — Transaction Model
Pydantic v2 model for SBI banking transactions.

Maps to: database/transactions.json
Used by: persona_engine.py (pattern detection), event_engine.py (salary/idle detection),
         saathi_agent.py (spending analysis), fd_engine.py (idle balance check)
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Enums ──────────────────────────────────────────────────────────────────

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class TransactionCategory(str, Enum):
    """
    Spending categories used by persona_engine and event_engine.
    Salary/subsidy/pension credits → MARGDARSHAN triggers.
    Education/travel/shopping → SAATHI triggers.
    """
    SALARY = "salary"
    SUBSIDY = "subsidy"
    PENSION = "pension"
    SCHOLARSHIP = "scholarship"
    BUSINESS_INCOME = "business_income"
    SHOPPING = "shopping"
    FOOD = "food"
    FUEL = "fuel"
    TRAVEL = "travel"
    EDUCATION = "education"
    MEDICAL = "medical"
    UTILITIES = "utilities"
    RENT = "rent"
    EMI = "emi"
    INVESTMENT = "investment"
    TRANSFER = "transfer"
    ATM = "atm"
    OTHER = "other"


class TransactionChannel(str, Enum):
    UPI = "UPI"
    NEFT = "NEFT"
    RTGS = "RTGS"
    IMPS = "IMPS"
    POS = "POS"
    ATM = "ATM"
    BRANCH = "BRANCH"
    INTERNET_BANKING = "INTERNET_BANKING"
    DBT = "DBT"       # Direct Benefit Transfer (govt subsidies)
    PFMS = "PFMS"     # Public Financial Management System (scholarships)


# ── Core Model ─────────────────────────────────────────────────────────────

class Transaction(BaseModel):
    """SBI banking transaction record."""
    model_config = ConfigDict(use_enum_values=True)

    transaction_id: str = Field(..., description="Unique transaction ID")
    customer_id: str = Field(..., description="Customer this transaction belongs to")
    amount: float = Field(..., gt=0.0, description="Transaction amount in INR")
    transaction_type: TransactionType
    merchant: Optional[str] = Field(None, description="Merchant / sender name")
    category: TransactionCategory = Field(TransactionCategory.OTHER)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    balance_after: float = Field(..., ge=0.0, description="Account balance after this transaction")
    channel: TransactionChannel = Field(TransactionChannel.NEFT)
    description: Optional[str] = Field(None, max_length=200)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return round(v, 2)


# ── Request / Response ──────────────────────────────────────────────────────

class TransactionSummary(BaseModel):
    """Aggregated transaction summary for persona/event detection."""
    customer_id: str
    total_credits: float
    total_debits: float
    net_flow: float
    salary_credits: list[float]
    subsidy_credits: list[float]
    top_categories: list[str]
    avg_monthly_balance: float
    days_since_last_debit: int
    transaction_count: int
