"""
SAARTHI AI — Customer Routes
GET/POST/PUT customer profiles and persona classification.
Thin handlers — all business logic in services/persona_engine.py.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query

from backend.models.customer import (
    Customer,
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    PersonaType,
)
from backend.services.persona_engine import persona_engine
from backend.utils import json_repository as repo
from backend.utils.error_handlers import CustomerNotFoundError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

COLLECTION = "customers"


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """Fetch a customer profile by ID."""
    record = repo.find_by_id(COLLECTION, "customer_id", customer_id.upper())
    if not record:
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")
    customer = Customer(**record)
    return CustomerResponse.from_customer(customer)


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(request: CustomerCreateRequest):
    """Create a new SBI customer account."""
    customer_id = f"CUST{uuid.uuid4().hex[:6].upper()}"
    now = datetime.now(timezone.utc)

    customer = Customer(
        customer_id=customer_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        account_type=request.account_type,
        account_number=f"20{uuid.uuid4().int % 10**9:09d}",
        date_of_birth=request.date_of_birth,
        address=request.address,
        created_at=now,
        updated_at=now,
    )

    repo.insert(COLLECTION, customer.model_dump(mode="json"))

    # Trigger MITRA agent for new customer onboarding event
    from backend.models.event import EventCreateRequest, EventSource, EventType
    from backend.services.event_engine import event_engine
    onboarding_event = event_engine.classify_and_create(
        EventCreateRequest(
            customer_id=customer_id,
            event_type=EventType.ACCOUNT_OPENED,
            source=EventSource.SYSTEM,
        )
    )

    logger.info("customer_created", customer_id=customer_id)
    return CustomerResponse.from_customer(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, request: CustomerUpdateRequest):
    """Update customer profile fields."""
    record = repo.find_by_id(COLLECTION, "customer_id", customer_id.upper())
    if not record:
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")

    updates = request.model_dump(exclude_none=True)
    updated = repo.upsert(COLLECTION, "customer_id", customer_id.upper(), updates)
    return CustomerResponse.from_customer(Customer(**updated))


@router.get("/{customer_id}/persona")
async def get_customer_persona(customer_id: str):
    """
    Classify (or re-classify) a customer's persona.
    Runs persona_engine over the customer's transaction history.
    """
    record = repo.find_by_id(COLLECTION, "customer_id", customer_id.upper())
    if not record:
        raise CustomerNotFoundError(message=f"Customer '{customer_id}' not found")

    transactions = repo.find_by_field("transactions", "customer_id", customer_id.upper())

    persona = await persona_engine.classify(
        customer_id=customer_id.upper(),
        transactions=transactions,
        date_of_birth=record.get("date_of_birth"),
        account_type=record.get("account_type"),
        address=record.get("address"),
    )

    # Persist the detected persona
    repo.upsert(COLLECTION, "customer_id", customer_id.upper(), {"persona": persona.value})

    return {
        "customer_id": customer_id.upper(),
        "persona": persona.value,
        "persona_display": persona.value.replace("_", " ").title(),
    }


@router.get("")
async def list_customers(limit: int = Query(20, ge=1, le=100)):
    """List all customers (for internal/dashboard use)."""
    records = repo.read_all(COLLECTION)[:limit]
    customers = [Customer(**r) for r in records]
    return {
        "total": len(customers),
        "customers": [CustomerResponse.from_customer(c) for c in customers],
    }
