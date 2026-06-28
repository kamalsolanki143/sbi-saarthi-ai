"""
SAARTHI AI — Audit Routes
Serves the live audit trail for the dashboard.
Shows the real-time pipeline trace: webhook → memory → agent → validation → recommendation → preview → MPIN → execution.
"""
from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from backend.models.audit_log import AuditTrailResponse
from backend.services.audit_service import audit_service
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{customer_id}", response_model=AuditTrailResponse)
async def get_audit_trail(
    customer_id: str,
    event_id: str | None = Query(None, description="Filter by event ID"),
):
    """Get the full audit trail for a customer."""
    trail = audit_service.get_trail(
        customer_id=customer_id.upper(),
        event_id=event_id,
    )
    return trail


@router.get("/live/{customer_id}", response_model=AuditTrailResponse)
async def get_live_feed(
    customer_id: str,
    last_n: int = Query(20, ge=1, le=100, description="Number of recent entries"),
):
    """
    Live audit feed — returns the most recent N entries.
    Poll this every 2s from the dashboard for a live pipeline view.
    """
    return audit_service.get_live_feed(customer_id=customer_id.upper(), last_n=last_n)


@router.websocket("/ws/{customer_id}")
async def audit_websocket(websocket: WebSocket, customer_id: str):
    """
    WebSocket endpoint for real-time audit feed.
    The dashboard connects here for live pipeline updates.
    Sends a snapshot every 2 seconds.
    """
    await websocket.accept()
    logger.info("audit_ws_connected", customer_id=customer_id)
    import asyncio
    try:
        while True:
            trail = audit_service.get_live_feed(customer_id=customer_id.upper(), last_n=20)
            await websocket.send_json(trail.model_dump(mode="json"))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("audit_ws_disconnected", customer_id=customer_id)
