"""
SAARTHI AI — Customer Model (MVP Priority)
Pydantic v2 model for SBI customer profile.

Maps to: database/customers.json
Used by: MITRA (onboarding), MARGDARSHAN (adoption), SAATHI (engagement),
         persona_engine.py, customer_memory.py, routes/customer.py
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ── Enums ──────────────────────────────────────────────────────────────────

class PersonaType(str, Enum):
    """
    Five customer personas defined in the SAARTHI AI system.
    Detected by persona_engine.py from transaction patterns.
    """
    FARMER = "farmer"
    STUDENT = "student"
    MERCHANT = "merchant"
    SALARIED = "salaried"
    SENIOR_CITIZEN = "senior_citizen"
    UNKNOWN = "unknown"


class KYCStatus(str, Enum):
    """KYC verification status. NOT_STARTED triggers MITRA agent."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"


class AccountType(str, Enum):
    """SBI account types. Jan Dhan has zero minimum balance."""
    SAVINGS = "savings"
    CURRENT = "current"
    SALARY = "salary"
    NRI = "nri"
    JAN_DHAN = "jan_dhan"


# ── Core Model ─────────────────────────────────────────────────────────────

class Customer(BaseModel):
    """
    Full SBI customer profile.
    Stored in database/customers.json.
    The 'mpin_hash' field stores a plain MPIN for hackathon demo —
    in production this would be an actual bcrypt/PBKDF2 hash.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "customer_id": "CUST001",
                "name": "Ramesh Kumar",
                "phone": "9876543210",
                "account_type": "salary",
                "account_number": "20001234567",
                "kyc_status": "verified",
                "persona": "salaried",
                "current_balance": 45000.00,
            }
        },
    )

    customer_id: str = Field(..., description="Unique customer ID, e.g. CUST001")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: str = Field(..., description="10-digit Indian mobile number")
    email: Optional[str] = Field(None, description="Email address (optional)")
    account_type: AccountType = Field(..., description="SBI account type")
    account_number: str = Field(..., description="Account number")
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth in YYYY-MM-DD format"
    )
    address: Optional[str] = Field(None, description="Postal address")
    kyc_status: KYCStatus = Field(KYCStatus.NOT_STARTED, description="KYC verification status")
    persona: PersonaType = Field(PersonaType.UNKNOWN, description="Detected customer persona")
    current_balance: float = Field(0.0, ge=0.0, description="Current account balance in INR")
    mpin_hash: str = Field("1234", description="MPIN (demo: plain text; production: hashed)")
    is_upi_active: bool = Field(False, description="Whether UPI is activated for this customer")
    is_yono_active: bool = Field(False, description="Whether YONO app is active")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = Field(True, description="Whether the customer account is active")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate 10-digit Indian mobile number (starts with 6-9)."""
        cleaned = re.sub(r"[\s\-\+]", "", v)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError(
                "Phone must be a valid Indian mobile number (10 digits starting with 6-9)"
            )
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address")
        return v.lower()

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        cleaned = re.sub(r"\s", "", v)
        if not re.match(r"^\d{9,18}$", cleaned):
            raise ValueError("Account number must be 9–18 digits")
        return cleaned

    @property
    def is_kyc_complete(self) -> bool:
        return self.kyc_status == KYCStatus.VERIFIED

    @property
    def needs_upi_activation(self) -> bool:
        return not self.is_upi_active and self.kyc_status == KYCStatus.VERIFIED

    @property
    def needs_yono_adoption(self) -> bool:
        return not self.is_yono_active


# ── Request / Response Models ──────────────────────────────────────────────

class CustomerCreateRequest(BaseModel):
    """Request body for POST /customers."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=100)
    phone: str
    email: Optional[str] = None
    account_type: AccountType
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\+]", "", v)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Invalid Indian mobile number")
        return cleaned


class CustomerUpdateRequest(BaseModel):
    """Request body for PUT /customers/{customer_id}."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    address: Optional[str] = None
    kyc_status: Optional[KYCStatus] = None
    is_upi_active: Optional[bool] = None
    is_yono_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    """
    Customer response — excludes sensitive fields like mpin_hash.
    Always return this instead of Customer directly in routes.
    """
    customer_id: str
    name: str
    phone: str
    email: Optional[str]
    account_type: str
    account_number: str
    kyc_status: str
    persona: str
    current_balance: float
    is_upi_active: bool
    is_yono_active: bool
    created_at: datetime
    is_active: bool

    @classmethod
    def from_customer(cls, customer: Customer) -> "CustomerResponse":
        return cls(
            customer_id=customer.customer_id,
            name=customer.name,
            phone=customer.phone,
            email=customer.email,
            account_type=customer.account_type,
            account_number=customer.account_number,
            kyc_status=customer.kyc_status,
            persona=customer.persona,
            current_balance=customer.current_balance,
            is_upi_active=customer.is_upi_active,
            is_yono_active=customer.is_yono_active,
            created_at=customer.created_at,
            is_active=customer.is_active,
        )
