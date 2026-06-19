"""
SAARTHI AI — Customer Memory (Unified Facade)
===============================================

Provides a single entry-point for all memory operations consumed by
the orchestrator and workflow graphs.  Internally delegates to:

• **RedisMemory** — fast session-scoped short-term store (conversation
  history, ephemeral flags, TTL-controlled data).
• **VectorMemory** — long-term semantic store for product interests,
  behavioural patterns, and similarity-based retrieval.

The facade enforces **consent gating**: memory writes are silently
skipped when the customer has not granted ``MEMORY_CONSENT``.

Thread-safety
─────────────
All public methods are ``async``.  The facade itself is stateless and
safe to share across concurrent requests.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.memory.redis_memory import RedisMemory
from backend.memory.vector_memory import VectorMemory
from backend.models.state import (
    ConsentCategory,
    ConsentStatus,
    MemoryContext,
    SAARTHIState,
)

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.memory.customer_memory")


# ─── Facade ─────────────────────────────────────────────────────────────────


class CustomerMemory:
    """
    Unified memory layer for customer state across sessions.

    Parameters
    ----------
    redis_memory : RedisMemory
        Short-term / session memory backend.
    vector_memory : VectorMemory
        Long-term semantic memory backend.
    """

    def __init__(
        self,
        redis_memory: RedisMemory,
        vector_memory: VectorMemory,
    ) -> None:
        self._redis: RedisMemory = redis_memory
        self._vector: VectorMemory = vector_memory
        logger.info("CustomerMemory facade initialised")

    # ── Retrieval ───────────────────────────────────────────────────────

    async def load_context(
        self,
        customer_id: str,
        session_id: str,
        query: str = "",
    ) -> MemoryContext:
        """
        Build a ``MemoryContext`` snapshot for the current turn.

        Merges data from both Redis (recent conversation, session data)
        and the vector store (historical interests, behavioural signals).

        Parameters
        ----------
        customer_id : str
            Unique customer identifier.
        session_id : str
            Current session identifier.
        query : str
            Current user query (used for similarity search in the vector
            store).

        Returns
        -------
        MemoryContext
            Populated context object.
        """
        start = time.monotonic()

        # Short-term: conversation history + session profile
        conversation_history = await self._redis.get_conversation_history(
            customer_id=customer_id,
            session_id=session_id,
        )
        session_profile = await self._redis.get_session_data(
            customer_id=customer_id,
            session_id=session_id,
        )

        # Long-term: customer profile + semantic matches
        customer_profile = await self._vector.get_customer_profile(
            customer_id=customer_id,
        )
        product_interests = await self._vector.get_product_interests(
            customer_id=customer_id,
        )
        behavioral_context = await self._vector.search_relevant_context(
            customer_id=customer_id,
            query=query,
        )

        # Merge session profile into customer profile (session overrides)
        merged_profile: dict[str, Any] = {**customer_profile, **session_profile}

        # Interaction count from Redis counter
        interaction_count = await self._redis.get_interaction_count(
            customer_id=customer_id,
        )

        # Last agent from session
        last_agent_str = session_profile.get("last_agent")
        from backend.models.state import AgentType

        last_agent = None
        if last_agent_str:
            try:
                last_agent = AgentType(last_agent_str)
            except ValueError:
                pass

        language = merged_profile.get("language_preference", "en")

        context = MemoryContext(
            conversation_history=conversation_history,
            customer_profile=merged_profile,
            product_interests=product_interests,
            language_preference=language,
            interaction_count=interaction_count,
            last_agent=last_agent,
            behavioral_context=behavioral_context,
        )

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Memory context loaded",
            extra={
                "customer_id": customer_id,
                "session_id": session_id,
                "history_turns": len(conversation_history),
                "interests": len(product_interests),
                "interaction_count": interaction_count,
                "elapsed_ms": round(elapsed, 2),
            },
        )
        return context

    # ── Persistence ─────────────────────────────────────────────────────

    async def save_turn(
        self,
        state: SAARTHIState,
    ) -> None:
        """
        Persist the current conversation turn to memory stores.

        Consent-gated: skipped entirely if ``MEMORY_CONSENT`` is not
        granted.

        Parameters
        ----------
        state : SAARTHIState
            Pipeline state after response generation.
        """
        customer_id: str = state.get("customer_id", "")
        session_id: str = state.get("session_id", "")
        consent: ConsentStatus = state.get("consent_status", ConsentStatus())

        if not consent.is_granted(ConsentCategory.MEMORY_CONSENT):
            logger.info(
                "Memory write skipped — MEMORY_CONSENT not granted",
                extra={"customer_id": customer_id},
            )
            return

        start = time.monotonic()

        query: str = state.get("query", "")
        response: str = state.get("response", "")
        agent = state.get("agent")

        # ── Short-term writes ──────────────────────────────────────────
        await self._redis.append_conversation_turn(
            customer_id=customer_id,
            session_id=session_id,
            role="user",
            content=query,
        )
        if response:
            await self._redis.append_conversation_turn(
                customer_id=customer_id,
                session_id=session_id,
                role="model",
                content=response,
            )

        await self._redis.increment_interaction_count(
            customer_id=customer_id,
        )

        if agent is not None:
            await self._redis.set_session_data(
                customer_id=customer_id,
                session_id=session_id,
                data={"last_agent": agent.value if hasattr(agent, "value") else str(agent)},
            )

        # ── Long-term writes ──────────────────────────────────────────
        await self._vector.store_interaction(
            customer_id=customer_id,
            query=query,
            response=response,
            metadata={
                "session_id": session_id,
                "agent": agent.value if agent and hasattr(agent, "value") else "unknown",
                "intent": state.get("intent", "unknown"),
            },
        )

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Turn persisted to memory",
            extra={
                "customer_id": customer_id,
                "session_id": session_id,
                "elapsed_ms": round(elapsed, 2),
            },
        )

    async def save_profile_update(
        self,
        customer_id: str,
        updates: dict[str, Any],
        consent: ConsentStatus,
    ) -> None:
        """
        Persist profile updates (persona, language pref, etc.).

        Parameters
        ----------
        customer_id : str
            Customer identifier.
        updates : dict[str, Any]
            Key-value pairs to merge into the stored profile.
        consent : ConsentStatus
            Current consent state.
        """
        if not consent.is_granted(ConsentCategory.MEMORY_CONSENT):
            logger.info(
                "Profile update skipped — MEMORY_CONSENT not granted",
                extra={"customer_id": customer_id},
            )
            return

        await self._vector.update_customer_profile(
            customer_id=customer_id,
            updates=updates,
        )

        logger.info(
            "Customer profile updated",
            extra={
                "customer_id": customer_id,
                "updated_keys": list(updates.keys()),
            },
        )

    # ── Session lifecycle ───────────────────────────────────────────────

    async def clear_session(
        self,
        customer_id: str,
        session_id: str,
    ) -> None:
        """
        Flush all short-term (Redis) data for a completed session.

        Long-term (vector) data is intentionally retained.
        """
        await self._redis.clear_session(
            customer_id=customer_id,
            session_id=session_id,
        )
        logger.info(
            "Session memory cleared",
            extra={"customer_id": customer_id, "session_id": session_id},
        )

    # ── Diagnostics ─────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Aggregate health status of both memory backends."""
        redis_health = await self._redis.health_check()
        vector_health = await self._vector.health_check()
        return {
            "service": "customer_memory",
            "redis": redis_health,
            "vector": vector_health,
            "status": (
                "ok"
                if redis_health.get("status") == "ok"
                and vector_health.get("status") == "ok"
                else "degraded"
            ),
        }
