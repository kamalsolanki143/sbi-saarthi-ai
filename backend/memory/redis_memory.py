"""
SAARTHI AI — Redis Memory
Low-level Redis client wrapper for session-level short-term memory.

All Redis I/O goes through this wrapper — never use Redis directly in agents.
Falls back gracefully if Redis is unavailable (logs warning, continues with in-memory dict).

Used by: customer_memory.py, human_in_loop.py (session state)
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

from backend.utils.constants import REDIS_SESSION_TTL
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

_REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
_REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
_REDIS_DB = int(os.getenv("REDIS_DB", 0))
_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None


class RedisMemory:
    """
    Redis client wrapper with graceful fallback to in-memory dict.
    On startup, tries to connect to Redis. If connection fails, all
    operations use a local dict (session-scoped, not distributed).
    """

    def __init__(self):
        self._client = None
        self._fallback: dict[str, str] = {}
        self._using_fallback = False
        self._connect()

    def _connect(self) -> None:
        """Attempt to connect to Redis. Fall back to in-memory on failure."""
        try:
            import redis
            client = redis.Redis(
                host=_REDIS_HOST,
                port=_REDIS_PORT,
                db=_REDIS_DB,
                password=_REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            client.ping()
            self._client = client
            logger.info("redis_connected", host=_REDIS_HOST, port=_REDIS_PORT)
        except Exception as e:
            logger.warning(
                "redis_unavailable",
                error=str(e),
                fallback="using in-memory dict (non-distributed)",
            )
            self._using_fallback = True

    # ── Core Operations ──────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[str]:
        """Get a string value by key."""
        try:
            if self._client:
                return self._client.get(key)
            return self._fallback.get(key)
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            return self._fallback.get(key)

    def set(self, key: str, value: str, ttl: int = REDIS_SESSION_TTL) -> None:
        """Set a string value with TTL (seconds)."""
        try:
            if self._client:
                self._client.setex(key, ttl, value)
            else:
                self._fallback[key] = value
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))
            self._fallback[key] = value

    def delete(self, key: str) -> None:
        """Delete a key."""
        try:
            if self._client:
                self._client.delete(key)
            else:
                self._fallback.pop(key, None)
        except Exception as e:
            logger.error("redis_delete_error", key=key, error=str(e))

    def get_json(self, key: str) -> Optional[dict[str, Any]]:
        """Get and deserialize a JSON value."""
        raw = self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: dict[str, Any], ttl: int = REDIS_SESSION_TTL) -> None:
        """Serialize and store a JSON value."""
        self.set(key, json.dumps(value, default=str), ttl)

    def hset(self, key: str, field: str, value: str) -> None:
        """Set a hash field."""
        try:
            if self._client:
                self._client.hset(key, field, value)
            else:
                existing = json.loads(self._fallback.get(key, "{}"))
                existing[field] = value
                self._fallback[key] = json.dumps(existing)
        except Exception as e:
            logger.error("redis_hset_error", key=key, field=field, error=str(e))

    def hgetall(self, key: str) -> dict[str, str]:
        """Get all fields of a hash."""
        try:
            if self._client:
                return self._client.hgetall(key) or {}
            return json.loads(self._fallback.get(key, "{}"))
        except Exception as e:
            logger.error("redis_hgetall_error", key=key, error=str(e))
            return {}

    def is_available(self) -> bool:
        """Check if Redis is connected (not using fallback)."""
        return not self._using_fallback and self._client is not None


# ── Singleton ───────────────────────────────────────────────────────────────
redis_memory = RedisMemory()
