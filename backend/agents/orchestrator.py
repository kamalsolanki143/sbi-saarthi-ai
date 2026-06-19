"""
SAARTHI AI — Agent Orchestrator
=================================

Central controller that wires the LangGraph pipeline:

1. **Consent validation** — blocks processing if mandatory consents
   are missing.
2. **Memory loading** — hydrates ``MemoryContext`` from Redis + Vector.
3. **Confidence scoring** — classifies intent and scores confidence.
4. **Persona detection** — profiles the customer archetype.
5. **Event detection** — identifies banking-event triggers.
6. **Agent routing** — dispatches to Mitra, Margdarshan, Saathi, or
   Fallback based on intent + event + confidence (< 85 → fallback).
7. **Audit trail** — persists an immutable ``AuditEntry`` per turn.
8. **Memory persistence** — writes conversation turn back to stores.

The orchestrator is the **only** module that instantiates service objects
and composes the LangGraph ``StateGraph``.  Workflow graphs (onboarding,
adoption, engagement, fallback) are registered as sub-graphs.

Agent Hook Design
─────────────────
This module does NOT contain Mitra / Margdarshan / Saathi business
logic.  It exposes orchestration hooks (``AgentHook`` protocol) so each
agent can be plugged in as an independent module.
"""

from __future__ import annotations

import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from backend.memory.customer_memory import CustomerMemory
from backend.memory.redis_memory import RedisMemory
from backend.memory.vector_memory import VectorMemory
from backend.models.state import (
    AgentRequest,
    AgentResponse,
    AgentType,
    AuditEntry,
    ConsentCategory,
    ConsentStatus,
    EventType,
    GuardrailStatus,
    IntentCategory,
    NetworkMode,
    SAARTHIState,
    create_initial_state,
)
from backend.services.confidence_engine import ConfidenceEngine
from backend.services.event_engine import EventEngine
from backend.services.gemini_service import GeminiService
from backend.services.persona_engine import PersonaEngine

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.agents.orchestrator")

# ─── Confidence threshold ──────────────────────────────────────────────────

_CONFIDENCE_THRESHOLD: float = 85.0


class _ConsentRequiredError(Exception):
    """Raised when mandatory consent is missing and the pipeline must halt."""
    pass


# ─── Agent Hook Protocol ───────────────────────────────────────────────────


@runtime_checkable
class AgentHook(Protocol):
    """
    Interface contract for specialist agent implementations.

    Any class satisfying this protocol can be registered with the
    orchestrator.  The orchestrator will call ``handle`` with a
    structured ``AgentRequest`` and expect an ``AgentResponse``.
    """

    async def handle(self, request: AgentRequest) -> AgentResponse:
        """Process a customer request and return a response."""
        ...


# ─── Default (stub) agent hook ──────────────────────────────────────────────


class DefaultAgentHook:
    """
    Passthrough agent used when no specialist is registered for a
    given ``AgentType``.  Returns a polite deferral message.
    """

    def __init__(self, agent_type: AgentType) -> None:
        self._agent_type = agent_type

    async def handle(self, request: AgentRequest) -> AgentResponse:
        """Return a generic deferral response."""
        return AgentResponse(
            agent=self._agent_type,
            response_text=(
                "I understand your query.  Let me connect you with a "
                "specialist who can help you further.  Please hold on."
            ),
            confidence=50.0,
            metadata={"handler": "default_hook"},
        )


# ─── Orchestrator ───────────────────────────────────────────────────────────


class Orchestrator:
    """
    Composes and drives the SAARTHI processing pipeline.

    Parameters
    ----------
    gemini_service : GeminiService
        Central LLM gateway.
    redis_memory : RedisMemory
        Short-term memory backend.
    vector_memory : VectorMemory
        Long-term memory backend.
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        redis_memory: RedisMemory,
        vector_memory: VectorMemory,
    ) -> None:
        # ── Services ───────────────────────────────────────────────────
        self._gemini: GeminiService = gemini_service
        self._confidence_engine: ConfidenceEngine = ConfidenceEngine(gemini_service)
        self._persona_engine: PersonaEngine = PersonaEngine(gemini_service)
        self._event_engine: EventEngine = EventEngine(gemini_service)
        self._customer_memory: CustomerMemory = CustomerMemory(redis_memory, vector_memory)

        # ── Agent registry ─────────────────────────────────────────────
        self._agent_hooks: dict[AgentType, AgentHook] = {}

        logger.info("Orchestrator initialised")

    # ── Agent registration ──────────────────────────────────────────────

    def register_agent(self, agent_type: AgentType, hook: AgentHook) -> None:
        """
        Register a specialist agent hook.

        Parameters
        ----------
        agent_type : AgentType
            The agent slot to fill.
        hook : AgentHook
            An object implementing the ``AgentHook`` protocol.
        """
        self._agent_hooks[agent_type] = hook
        logger.info(
            "Agent hook registered",
            extra={"agent_type": agent_type.value},
        )

    def _get_agent_hook(self, agent_type: AgentType) -> AgentHook:
        """Retrieve a registered hook or return the default."""
        return self._agent_hooks.get(
            agent_type,
            DefaultAgentHook(agent_type),
        )

    # ── Main pipeline ───────────────────────────────────────────────────

    async def process(
        self,
        customer_id: str,
        query: str,
        language: str = "en",
        network_mode: NetworkMode = NetworkMode.TEXT_MODE,
        consent_status: ConsentStatus | None = None,
        session_id: str | None = None,
    ) -> SAARTHIState:
        """
        Execute the full SAARTHI pipeline for a single customer turn.

        Parameters
        ----------
        customer_id : str
            Unique customer identifier.
        query : str
            Natural-language customer input.
        language : str
            ISO language code.
        network_mode : NetworkMode
            Current network quality mode.
        consent_status : ConsentStatus | None
            Pre-existing consent state; defaults to empty.
        session_id : str | None
            Session identifier; auto-generated if not provided.

        Returns
        -------
        SAARTHIState
            Fully populated pipeline state.
        """
        pipeline_start = time.monotonic()

        # ── 1. Initialise state ────────────────────────────────────────
        state: SAARTHIState = create_initial_state(
            customer_id=customer_id,
            query=query,
            language=language,
            network_mode=network_mode,
            session_id=session_id,
        )
        if consent_status is not None:
            state["consent_status"] = consent_status

        logger.info(
            "Pipeline started",
            extra={
                "customer_id": customer_id,
                "session_id": state["session_id"],
                "language": language,
                "network_mode": network_mode.value,
            },
        )

        try:
            # ── 2. Consent validation ──────────────────────────────────
            state = await self._validate_consent(state)

            # ── 3. Load memory context ─────────────────────────────────
            state = await self._load_memory(state)

            # ── 4. Confidence scoring ──────────────────────────────────
            state = await self._score_confidence(state)

            # ── 5. Persona detection ───────────────────────────────────
            state = await self._detect_persona(state)

            # ── 6. Event detection ─────────────────────────────────────
            state = await self._detect_events(state)

            # ── 7. Route to agent ──────────────────────────────────────
            state = await self._route_and_execute(state)

            # ── 8. Guardrail check ─────────────────────────────────────
            state = await self._apply_guardrails(state)

            # ── 9. Persist memory ──────────────────────────────────────
            state = await self._persist_memory(state)

        except _ConsentRequiredError:
            # Consent block is expected — state already has the response set.
            logger.info(
                "Pipeline halted — consent required",
                extra={"customer_id": customer_id},
            )

        except Exception as exc:
            logger.error(
                "Pipeline error",
                extra={
                    "customer_id": customer_id,
                    "error": str(exc),
                    "type": type(exc).__name__,
                },
            )
            state["error"] = str(exc)
            state["guardrail_status"] = GuardrailStatus.ESCALATED

        # ── 10. Audit trail ────────────────────────────────────────────
        elapsed_ms = (time.monotonic() - pipeline_start) * 1000
        state = self._create_audit_entry(state, elapsed_ms)

        logger.info(
            "Pipeline completed",
            extra={
                "customer_id": customer_id,
                "session_id": state["session_id"],
                "agent": state.get("agent", AgentType.FALLBACK).value,
                "intent": state.get("intent", IntentCategory.UNKNOWN).value,
                "confidence": state.get("confidence", 0.0),
                "elapsed_ms": round(elapsed_ms, 2),
                "has_error": state.get("error") is not None,
            },
        )

        return state

    # ── Pipeline steps ──────────────────────────────────────────────────

    async def _validate_consent(self, state: SAARTHIState) -> SAARTHIState:
        """
        Ensure mandatory consents are present.

        Voice consent is required in VOICE_MODE.  Memory consent gates
        all memory operations downstream.  If consent is absent the
        pipeline is BLOCKED: a consent-required response is returned
        and no further processing occurs.
        """
        consent: ConsentStatus = state.get("consent_status", ConsentStatus())
        network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)

        if network_mode == NetworkMode.VOICE_MODE:
            if not consent.is_granted(ConsentCategory.VOICE_CONSENT):
                logger.warning(
                    "Voice consent not granted in VOICE_MODE",
                    extra={"customer_id": state.get("customer_id")},
                )

        if not consent.is_granted(ConsentCategory.MEMORY_CONSENT):
            logger.warning(
                "Memory consent not granted — blocking pipeline",
                extra={"customer_id": state.get("customer_id")},
            )
            state["response"] = (
                "To assist you securely, I need your consent to store "
                "your data as per DPDP Act guidelines.  Would you like "
                "to grant consent for data storage and personalisation?"
            )
            state["agent"] = AgentType.FALLBACK
            state["guardrail_status"] = GuardrailStatus.PASSED
            state["consent_status"] = consent
            raise _ConsentRequiredError("Memory consent not granted")

        state["consent_status"] = consent
        return state

    async def _load_memory(self, state: SAARTHIState) -> SAARTHIState:
        """Load customer memory context from Redis + Vector stores."""
        try:
            memory_context = await self._customer_memory.load_context(
                customer_id=state.get("customer_id", ""),
                session_id=state.get("session_id", ""),
                query=state.get("query", ""),
            )
            state["memory_context"] = memory_context

            # Apply language from memory if not explicitly set
            if memory_context.language_preference and state.get("language") == "en":
                state["language"] = memory_context.language_preference

        except Exception as exc:
            logger.error(
                "Memory loading failed — continuing with empty context",
                extra={"error": str(exc)},
            )

        return state

    async def _score_confidence(self, state: SAARTHIState) -> SAARTHIState:
        """Classify intent and score confidence."""
        confidence_result = await self._confidence_engine.classify(state)

        state["confidence_result"] = confidence_result
        state["intent"] = confidence_result.intent
        state["confidence"] = confidence_result.confidence

        return state

    async def _detect_persona(self, state: SAARTHIState) -> SAARTHIState:
        """Detect customer persona archetype."""
        consent: ConsentStatus = state.get("consent_status", ConsentStatus())

        if not consent.is_granted(ConsentCategory.PERSONALIZATION_CONSENT):
            logger.info("Persona detection skipped — PERSONALIZATION_CONSENT not granted")
            return state

        persona_result = await self._persona_engine.detect(state)

        state["persona_result"] = persona_result
        state["persona"] = persona_result.persona

        return state

    async def _detect_events(self, state: SAARTHIState) -> SAARTHIState:
        """Detect banking events from query and context."""
        event_result = await self._event_engine.detect(state)

        state["event_result"] = event_result
        state["event_type"] = event_result.event_type

        return state

    async def _route_and_execute(self, state: SAARTHIState) -> SAARTHIState:
        """
        Determine the target agent and execute the request.

        Routing rules
        ─────────────
        1. If an event was detected, the event's recommended agent wins.
        2. If confidence ≥ 85, the confidence engine's recommendation wins.
        3. Otherwise → Fallback.

        Explicit overrides:
        • ACCOUNT_OPENING → MITRA
        • SALARY_CREDIT   → MARGDARSHAN
        • SCHOOL_FEE      → SAATHI
        """
        confidence_result = state.get("confidence_result")
        event_result = state.get("event_result")
        confidence: float = state.get("confidence", 0.0)
        intent = state.get("intent", IntentCategory.UNKNOWN)

        # ── Determine target agent ─────────────────────────────────────
        agent: AgentType = AgentType.FALLBACK

        # Priority 1: explicit intent overrides
        if intent == IntentCategory.ACCOUNT_OPENING and confidence >= _CONFIDENCE_THRESHOLD:
            agent = AgentType.MITRA
        elif (
            event_result is not None
            and event_result.event_type == EventType.SALARY_CREDIT
        ):
            agent = AgentType.SAATHI
        elif (
            event_result is not None
            and event_result.event_type == EventType.SCHOOL_FEE_DETECTED
        ):
            agent = AgentType.SAATHI
        # Priority 2: event-driven routing
        elif (
            event_result is not None
            and event_result.event_type != EventType.NONE
        ):
            agent = event_result.recommended_agent
        # Priority 3: confidence-based routing
        elif confidence >= _CONFIDENCE_THRESHOLD and confidence_result is not None:
            agent = confidence_result.recommended_agent
        # Priority 4: fallback
        else:
            agent = AgentType.FALLBACK

        state["agent"] = agent

        logger.info(
            "Agent routed",
            extra={
                "agent": agent.value,
                "intent": intent.value if hasattr(intent, "value") else str(intent),
                "confidence": confidence,
                "event": (
                    event_result.event_type.value
                    if event_result
                    else "none"
                ),
            },
        )

        # ── Execute agent hook ─────────────────────────────────────────
        hook = self._get_agent_hook(agent)
        persona_result = state.get("persona_result")
        memory_context = state.get("memory_context")

        from backend.models.state import MemoryContext, PersonaResult

        request = AgentRequest(
            customer_id=state.get("customer_id", ""),
            query=state.get("query", ""),
            intent=intent if isinstance(intent, IntentCategory) else IntentCategory.UNKNOWN,
            persona=persona_result if persona_result else PersonaResult(),
            memory_context=memory_context if memory_context else MemoryContext(),
            network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
            language=state.get("language", "en"),
            session_id=state.get("session_id", ""),
        )

        try:
            agent_response: AgentResponse = await hook.handle(request)
        except Exception as exc:
            logger.error(
                "Agent execution failed",
                extra={"agent": agent.value, "error": str(exc)},
            )
            agent_response = AgentResponse(
                agent=agent,
                response_text=(
                    "I apologize, but I'm having trouble processing your "
                    "request right now.  Please try again shortly."
                ),
                confidence=0.0,
                metadata={"error": str(exc)},
            )

        state["agent_response"] = agent_response
        state["response"] = agent_response.response_text
        state["action_required"] = agent_response.action_required

        return state

    async def _apply_guardrails(self, state: SAARTHIState) -> SAARTHIState:
        """
        Post-generation guardrail checks.

        Checks for:
        • Empty responses
        • Responses that might contain sensitive information leaks
        • Excessively long responses for low-bandwidth mode
        """
        response: str = state.get("response", "")
        network_mode: NetworkMode = state.get("network_mode", NetworkMode.TEXT_MODE)

        if not response.strip():
            state["guardrail_status"] = GuardrailStatus.ESCALATED
            state["response"] = (
                "I wasn't able to generate a response.  Let me connect "
                "you with a human agent for assistance."
            )
            logger.warning("Empty response — escalating to human agent")
            return state

        # Check for sensitive data patterns (account numbers, PINs)
        sensitive_patterns = ["account number:", "pin:", "password:", "cvv:"]
        response_lower = response.lower()
        for pattern in sensitive_patterns:
            if pattern in response_lower:
                state["guardrail_status"] = GuardrailStatus.BLOCKED
                state["response"] = (
                    "For your security, I cannot display sensitive "
                    "information in this format.  Please use our secure "
                    "banking channels."
                )
                logger.warning(
                    "Guardrail triggered — sensitive data detected",
                    extra={"pattern": pattern},
                )
                return state

        # Low-bandwidth response truncation
        if network_mode == NetworkMode.LOW_BANDWIDTH_MODE and len(response) > 500:
            state["response"] = response[:497] + "..."
            logger.info("Response truncated for low-bandwidth mode")

        state["guardrail_status"] = GuardrailStatus.PASSED
        return state

    async def _persist_memory(self, state: SAARTHIState) -> SAARTHIState:
        """Write the current turn to memory stores (consent-gated)."""
        try:
            await self._customer_memory.save_turn(state)

            # Persist persona update if detected
            persona_result = state.get("persona_result")
            if persona_result and persona_result.persona.value != "unknown":
                consent: ConsentStatus = state.get("consent_status", ConsentStatus())
                await self._customer_memory.save_profile_update(
                    customer_id=state.get("customer_id", ""),
                    updates={
                        "persona": persona_result.persona.value,
                        "persona_confidence": persona_result.confidence,
                    },
                    consent=consent,
                )
        except Exception as exc:
            logger.error(
                "Memory persistence failed",
                extra={"error": str(exc)},
            )

        return state

    def _create_audit_entry(
        self,
        state: SAARTHIState,
        elapsed_ms: float,
    ) -> SAARTHIState:
        """
        Create an immutable audit log entry for compliance.

        Appends to the ``audit_logs`` list in state.
        """
        entry = AuditEntry(
            customer_id=state.get("customer_id", "unknown"),
            agent_selected=state.get("agent", AgentType.FALLBACK),
            intent=state.get("intent", IntentCategory.UNKNOWN),
            confidence=state.get("confidence", 0.0),
            event_trigger=state.get("event_type", EventType.NONE),
            consent_status=state.get("consent_status", ConsentStatus()),
            guardrail_status=state.get("guardrail_status", GuardrailStatus.PASSED),
            response_generated=bool(state.get("response")),
            network_mode=state.get("network_mode", NetworkMode.TEXT_MODE),
            execution_time_ms=round(elapsed_ms, 2),
            error=state.get("error"),
        )

        existing_logs: list[AuditEntry] = state.get("audit_logs", [])
        existing_logs.append(entry)
        state["audit_logs"] = existing_logs

        logger.info(
            "Audit entry created",
            extra={
                "audit_id": entry.audit_id,
                "customer_id": entry.customer_id,
                "agent": entry.agent_selected.value,
                "execution_time_ms": entry.execution_time_ms,
            },
        )

        return state

    # ── Diagnostics ─────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Aggregate health status across all sub-services."""
        memory_health = await self._customer_memory.health_check()
        gemini_health = self._gemini.health_check()

        registered_agents = [at.value for at in self._agent_hooks]

        return {
            "service": "orchestrator",
            "status": (
                "ok"
                if memory_health.get("status") == "ok"
                and gemini_health.get("status") == "ok"
                else "degraded"
            ),
            "gemini": gemini_health,
            "memory": memory_health,
            "registered_agents": registered_agents,
        }
