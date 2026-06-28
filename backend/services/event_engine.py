"""
SAARTHI AI — Event Engine
Classifies raw incoming events and determines which agent should handle them.

Maps incoming payloads (from CBS webhooks or internal monitors) to:
  EventType enum → agent assignment via EVENT_AGENT_MAP

Also detects events from transaction patterns (idle balance, spending anomaly).

Used by: routes/event.py, orchestrator.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from backend.models.event import Event, EventCreateRequest, EventSource, EventStatus, EventType
from backend.utils.constants import (
    EVENT_AGENT_MAP,
    FD_IDLE_THRESHOLD_DAYS,
    FD_MIN_ELIGIBLE_BALANCE,
)
from backend.utils import json_repository as repo
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION = "events"


class EventEngine:
    """
    Classifies events and routes them to the correct agent.
    """

    def classify_and_create(
        self,
        request: EventCreateRequest,
    ) -> Event:
        """
        Receive an EventCreateRequest, classify it, assign an agent, and persist it.
        Returns the created Event object.
        """
        event_id = repo.generate_id("EVT-")
        agent = EVENT_AGENT_MAP.get(request.event_type, None)

        event = Event(
            event_id=event_id,
            customer_id=request.customer_id,
            event_type=request.event_type,
            amount=request.amount,
            metadata=request.metadata,
            source=request.source,
            timestamp=datetime.now(timezone.utc),
            processed=False,
            agent_assigned=agent,
            status=EventStatus.PENDING,
        )

        # Persist
        repo.insert(COLLECTION, event.model_dump(mode="json"))

        logger.info(
            "event_classified",
            event_id=event_id,
            event_type=request.event_type,
            customer_id=request.customer_id,
            agent_assigned=agent,
        )
        return event

    def detect_idle_balance(
        self,
        customer_id: str,
        current_balance: float,
        days_idle: int,
    ) -> Optional[Event]:
        """
        Programmatically detect if a customer's balance qualifies as 'idle'.
        Called by a scheduled job (not a webhook).
        Returns an Event if idle threshold met, else None.
        """
        if (
            current_balance >= FD_MIN_ELIGIBLE_BALANCE
            and days_idle >= FD_IDLE_THRESHOLD_DAYS
        ):
            event_id = repo.generate_id("EVT-")
            event = Event(
                event_id=event_id,
                customer_id=customer_id,
                event_type=EventType.IDLE_BALANCE,
                amount=current_balance,
                metadata={"idle_days": days_idle, "balance_threshold": FD_MIN_ELIGIBLE_BALANCE},
                source=EventSource.SYSTEM,
                agent_assigned=EVENT_AGENT_MAP[EventType.IDLE_BALANCE],
                status=EventStatus.PENDING,
            )
            repo.insert(COLLECTION, event.model_dump(mode="json"))
            logger.info("idle_balance_event_created", event_id=event_id, customer_id=customer_id)
            return event
        return None

    def get_event(self, event_id: str) -> Optional[Event]:
        """Fetch a single event by ID."""
        record = repo.find_by_id(COLLECTION, "event_id", event_id)
        if record is None:
            return None
        return Event(**record)

    def get_customer_events(self, customer_id: str) -> list[Event]:
        """Fetch all events for a customer."""
        records = repo.find_by_field(COLLECTION, "customer_id", customer_id)
        return [Event(**r) for r in records]

    def mark_processed(
        self, event_id: str, result: str, agent: str
    ) -> None:
        """Mark an event as processed after an agent completes its workflow."""
        repo.upsert(
            COLLECTION,
            "event_id",
            event_id,
            {
                "processed": True,
                "status": EventStatus.COMPLETED,
                "agent_assigned": agent,
                "processing_result": result,
            },
        )
        logger.info("event_marked_processed", event_id=event_id, agent=agent)

    def mark_failed(self, event_id: str, error: str) -> None:
        """Mark an event as failed."""
        repo.upsert(
            COLLECTION,
            "event_id",
            event_id,
            {"status": EventStatus.FAILED, "processing_result": f"Error: {error}"},
        )


# ── Singleton ───────────────────────────────────────────────────────────────
event_engine = EventEngine()
