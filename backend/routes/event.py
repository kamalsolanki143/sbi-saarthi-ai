"""
SAARTHI AI — Event Routes
Receives banking events (webhook-style) and triggers the orchestrator.
This is where the agentic pipeline begins.
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from backend.agents.orchestrator import dispatch
from backend.models.event import (
    EventCreateRequest,
    EventListResponse,
    EventResponse,
)
from backend.services.event_engine import event_engine
from backend.utils.error_handlers import EventNotFoundError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("", status_code=202)
async def receive_event(request: EventCreateRequest):
    """
    Receive a banking event and trigger the appropriate agent.
    Returns 202 Accepted immediately — processing is async.

    Used by:
      - CBS (Core Banking System) webhooks
      - Internal scheduled jobs (idle balance monitor)
      - Demo/test tool for judges
    """
    # 1. Classify event and persist
    event = event_engine.classify_and_create(request)

    logger.info(
        "event_received",
        event_id=event.event_id,
        event_type=event.event_type,
        customer_id=event.customer_id,
        agent=event.agent_assigned,
    )

    # 2. Dispatch to orchestrator (triggers agent pipeline)
    try:
        result = await dispatch(
            customer_id=event.customer_id,
            event=event,
        )

        # Return event status + first recommendation if available
        response_body: dict = {
            "status": "accepted",
            "event_id": event.event_id,
            "agent_assigned": event.agent_assigned,
            "message": f"Event processed by {event.agent_assigned} agent",
        }

        if hasattr(result, "recommendation_id"):
            # It's a Recommendation
            response_body["recommendation_id"] = result.recommendation_id
            response_body["recommendation_title"] = result.title
            response_body["action_preview_available"] = True
        elif hasattr(result, "clarifying_question"):
            # It's a FallbackResponse
            response_body["clarifying_question"] = result.clarifying_question
            response_body["quick_reply_options"] = result.question_options
            response_body["action_preview_available"] = False

        return response_body

    except Exception as e:
        logger.error("event_processing_failed", event_id=event.event_id, error=str(e))
        return {
            "status": "accepted",
            "event_id": event.event_id,
            "agent_assigned": event.agent_assigned,
            "message": "Event received. Processing encountered an issue — check audit trail.",
            "error": str(e),
        }


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get the status and details of a specific event."""
    event = event_engine.get_event(event_id)
    if not event:
        raise EventNotFoundError(message=f"Event '{event_id}' not found")

    return EventResponse(
        event_id=event.event_id,
        customer_id=event.customer_id,
        event_type=event.event_type,
        status=event.status,
        agent_assigned=event.agent_assigned,
        timestamp=event.timestamp,
        message=event.processing_result or "Event is being processed",
    )


@router.get("", response_model=EventListResponse)
async def list_events(
    customer_id: str = Query(..., description="Filter events by customer ID"),
):
    """List all events for a customer."""
    events = event_engine.get_customer_events(customer_id.upper())
    return EventListResponse(
        customer_id=customer_id.upper(),
        total=len(events),
        events=[
            EventResponse(
                event_id=e.event_id,
                customer_id=e.customer_id,
                event_type=e.event_type,
                status=e.status,
                agent_assigned=e.agent_assigned,
                timestamp=e.timestamp,
                message=e.processing_result or "Pending",
            )
            for e in events
        ],
    )
