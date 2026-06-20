"""
SAARTHI AI — Audit Service
Writes and reads the real-time audit trail for the dashboard.

Every step of the agentic pipeline (webhook → memory → agent →
validation → recommendation → preview → MPIN → execution)
is logged here so the dashboard shows a live trace.

Used by: all agents, security/human_in_loop.py, routes/audit.py
Maps to: database/audit_logs.json
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, Optional

from backend.models.audit_log import AuditLog, AuditStatus, AuditStep, AuditTrailResponse, AuditLogResponse
from backend.utils import json_repository as repo
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION = "audit_logs"


class AuditService:
    """
    Manages the audit trail.
    All writes are append-only — we never update or delete audit logs.
    """

    def log_step(
        self,
        customer_id: str,
        step: AuditStep,
        agent: Optional[str] = None,
        event_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
        status: AuditStatus = AuditStatus.SUCCESS,
        metadata: Optional[dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Append a single pipeline step to the audit trail.
        This is called by agents and security modules at each pipeline stage.
        """
        log_id = repo.generate_id("LOG-")
        audit_log = AuditLog.create(
            log_id=log_id,
            customer_id=customer_id,
            step=step,
            agent=agent,
            event_id=event_id,
            recommendation_id=recommendation_id,
            status=status,
            metadata=metadata or {},
            duration_ms=duration_ms,
            error_message=error_message,
        )

        # Persist to flat file
        repo.append_record(COLLECTION, audit_log.model_dump(mode="json"))

        logger.info(
            "audit_step_logged",
            log_id=log_id,
            customer_id=customer_id,
            step=step,
            status=status,
        )
        return audit_log

    def get_trail(
        self,
        customer_id: str,
        limit: Optional[int] = None,
        event_id: Optional[str] = None,
    ) -> AuditTrailResponse:
        """Retrieve the full audit trail for a customer, newest first."""
        all_logs = repo.read_all(COLLECTION)

        # Filter by customer (and optionally by event)
        filtered = [
            log for log in all_logs
            if log.get("customer_id") == customer_id
            and (event_id is None or log.get("event_id") == event_id)
        ]

        # Sort newest first
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        if limit:
            filtered = filtered[:limit]

        logs = [AuditLogResponse(**log) for log in filtered]

        return AuditTrailResponse(
            customer_id=customer_id,
            total_entries=len(logs),
            logs=logs,
        )

    def get_live_feed(self, customer_id: str, last_n: int = 20) -> AuditTrailResponse:
        """Return the most recent N audit entries — for the dashboard polling endpoint."""
        return self.get_trail(customer_id, limit=last_n)

    @contextmanager
    def timed_step(
        self,
        customer_id: str,
        step: AuditStep,
        agent: Optional[str] = None,
        event_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Generator[None, None, None]:
        """
        Context manager that automatically logs a step with its execution duration.

        Usage:
            with audit_service.timed_step(customer_id, AuditStep.AGENT_ACTIVATED, agent="margdarshan"):
                ... do work ...
        """
        start = time.monotonic()
        try:
            yield
            duration_ms = int((time.monotonic() - start) * 1000)
            self.log_step(
                customer_id=customer_id,
                step=step,
                agent=agent,
                event_id=event_id,
                recommendation_id=recommendation_id,
                status=AuditStatus.SUCCESS,
                metadata=metadata or {},
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            self.log_step(
                customer_id=customer_id,
                step=step,
                agent=agent,
                event_id=event_id,
                recommendation_id=recommendation_id,
                status=AuditStatus.FAILED,
                metadata=metadata or {},
                duration_ms=duration_ms,
                error_message=str(e),
            )
            raise


# ── Singleton ───────────────────────────────────────────────────────────────
audit_service = AuditService()
