"""
SAARTHI AI — Redis Short-Term Memory
======================================

Manages ephemeral, session-scoped data that does not need to survive
beyond a configurable TTL:

• Conversation history (last N turns per session)
• Session-level key-value data (last_agent, flags, etc.)
• Per-customer interaction counters
• Session lifecycle (create / clear)

The store is backed by Redis (via ``redis.asyncio``) for sub-millisecond
latency.  When Redis is unreachable the service degrades gracefully —
returning empty defaults so the pipeline can still function (without
memory).

Key design
──────────
• All keys are namespaced: ``saarthi:{customer_id}:{domain}:{session_id}``
• Conversation history is stored as a Redis List (RPUSH / LRANGE).
• Session data is stored as a Redis Hash.
• Interaction count is a simple INCR counter.
• TTLs are refreshed on every write to implement sliding expiration.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import redis.asyncio as aioredis

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.memory.redis_memory")

# ─── Defaults ───────────────────────────────────────────────────────────────

_DEFAULT_REDIS_URL: str = "redis://localhost:6379/0"
_SESSION_TTL_SECONDS: int = 3600  # 1 hour
_MAX_HISTORY_TURNS: int = 50
_NAMESPACE: str = "saarthi"


# ─── Service ────────────────────────────────────────────────────────────────


class RedisMemory:
    """
    Async Redis-backed short-term memory for SAARTHI sessions.

    Parameters
    ----------
    redis_url : str | None
        Redis connection string.  Falls back to ``REDIS_URL`` env-var,
        then to ``redis://localhost:6379/0``.
    session_ttl : int
        TTL in seconds for all session-scoped keys.
    max_history_turns : int
        Maximum conversation turns retained per session.
    """

    def __init__(
        self,
        redis_url: str | None = None,
        session_ttl: int = _SESSION_TTL_SECONDS,
        max_history_turns: int = _MAX_HISTORY_TURNS,
    ) -> None:
        self._url: str = redis_url or os.getenv("REDIS_URL", _DEFAULT_REDIS_URL)
        self._ttl: int = session_ttl
        self._max_turns: int = max_history_turns
        self._client: aioredis.Redis | None = None
        logger.info(
            "RedisMemory initialised",
            extra={"url": self._sanitise_url(self._url), "ttl": session_ttl},
        )

    # ── Connection lifecycle ────────────────────────────────────────────

    async def connect(self) -> None:
        """Establish the Redis connection pool."""
        if self._client is None:
            self._client = aioredis.from_url(
                self._url,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            logger.info("Redis connection pool created")

    async def disconnect(self) -> None:
        """Close the Redis connection pool gracefully."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Redis connection pool closed")

    async def _get_client(self) -> aioredis.Redis:
        """Lazy-initialise and return the Redis client."""
        if self._client is None:
            await self.connect()
        assert self._client is not None
        return self._client

    # ── Key helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _key(customer_id: str, domain: str, session_id: str = "") -> str:
        """Build a namespaced Redis key."""
        parts = [_NAMESPACE, customer_id, domain]
        if session_id:
            parts.append(session_id)
        return ":".join(parts)

    # ── Conversation history ────────────────────────────────────────────

    async def get_conversation_history(
        self,
        customer_id: str,
        session_id: str,
    ) -> list[dict[str, str]]:
        """
        Retrieve the conversation history for a session.

        Returns a list of ``{"role": "...", "content": "..."}`` dicts,
        oldest first.
        """
        try:
            client = await self._get_client()
            key = self._key(customer_id, "history", session_id)
            raw_entries: list[str] = await client.lrange(key, 0, -1)
            return [json.loads(entry) for entry in raw_entries]
        except Exception as exc:
            logger.error(
                "Failed to read conversation history",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return []

    async def append_conversation_turn(
        self,
        customer_id: str,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Append a single turn to the conversation history.

        Automatically trims to ``max_history_turns`` and refreshes TTL.
        """
        try:
            client = await self._get_client()
            key = self._key(customer_id, "history", session_id)
            entry = json.dumps({"role": role, "content": content}, ensure_ascii=False)

            pipe = client.pipeline(transaction=True)
            pipe.rpush(key, entry)
            pipe.ltrim(key, -self._max_turns, -1)
            pipe.expire(key, self._ttl)
            await pipe.execute()
        except Exception as exc:
            logger.error(
                "Failed to append conversation turn",
                extra={
                    "customer_id": customer_id,
                    "session_id": session_id,
                    "error": str(exc),
                },
            )

    # ── Session data (hash) ─────────────────────────────────────────────

    async def get_session_data(
        self,
        customer_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Retrieve all session-level key-value pairs."""
        try:
            client = await self._get_client()
            key = self._key(customer_id, "session", session_id)
            data: dict[str, str] = await client.hgetall(key)
            return dict(data)
        except Exception as exc:
            logger.error(
                "Failed to read session data",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return {}

    async def set_session_data(
        self,
        customer_id: str,
        session_id: str,
        data: dict[str, str],
    ) -> None:
        """Merge key-value pairs into the session hash and refresh TTL."""
        try:
            client = await self._get_client()
            key = self._key(customer_id, "session", session_id)

            pipe = client.pipeline(transaction=True)
            pipe.hset(key, mapping=data)
            pipe.expire(key, self._ttl)
            await pipe.execute()
        except Exception as exc:
            logger.error(
                "Failed to write session data",
                extra={
                    "customer_id": customer_id,
                    "session_id": session_id,
                    "error": str(exc),
                },
            )

    # ── Interaction counter ─────────────────────────────────────────────

    async def get_interaction_count(self, customer_id: str) -> int:
        """Return the total interaction count for a customer."""
        try:
            client = await self._get_client()
            key = self._key(customer_id, "interactions")
            val = await client.get(key)
            return int(val) if val is not None else 0
        except Exception as exc:
            logger.error(
                "Failed to read interaction count",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return 0

    async def increment_interaction_count(self, customer_id: str) -> int:
        """Atomically increment and return the interaction count."""
        try:
            client = await self._get_client()
            key = self._key(customer_id, "interactions")
            return await client.incr(key)
        except Exception as exc:
            logger.error(
                "Failed to increment interaction count",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return 0

    # ── Session lifecycle ───────────────────────────────────────────────

    async def clear_session(
        self,
        customer_id: str,
        session_id: str,
    ) -> None:
        """Delete all keys belonging to a specific session."""
        try:
            client = await self._get_client()
            keys_to_delete = [
                self._key(customer_id, "history", session_id),
                self._key(customer_id, "session", session_id),
            ]
            if keys_to_delete:
                await client.delete(*keys_to_delete)
            logger.info(
                "Session keys cleared",
                extra={
                    "customer_id": customer_id,
                    "session_id": session_id,
                    "keys_deleted": len(keys_to_delete),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to clear session",
                extra={"customer_id": customer_id, "error": str(exc)},
            )

    # ── Health check ────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Ping Redis and report status."""
        try:
            client = await self._get_client()
            pong: bool = await client.ping()
            return {"service": "redis_memory", "status": "ok" if pong else "degraded"}
        except Exception as exc:
            return {"service": "redis_memory", "status": "error", "error": str(exc)}

    # ── Internals ───────────────────────────────────────────────────────

    @staticmethod
    def _sanitise_url(url: str) -> str:
        """Strip credentials from a Redis URL for safe logging."""
        if "@" in url:
            prefix, _, hostport = url.rpartition("@")
            scheme = prefix.split("://")[0] if "://" in prefix else "redis"
            return f"{scheme}://***@{hostport}"
        return url
