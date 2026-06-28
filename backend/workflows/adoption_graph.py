"""
SAARTHI AI — MARGDARSHAN Adoption Graph
LangGraph StateGraph for the MARGDARSHAN (Digital Adoption) agent.
Wraps the digital adoption workflow (salary credit, idle balance, UPI, YONO)
into a compiled LangGraph graph.
"""
from __future__ import annotations

from typing import TypedDict, Optional, Literal, Any

from langgraph.graph import StateGraph, END

from backend.memory.customer_memory import customer_memory
from backend.services.confidence_engine import confidence_engine
from backend.guardrails.confidence_checker import check_confidence
from backend.utils.error_handlers import LowConfidenceError
from backend.guardrails.action_validator import validate_action
from backend.services.audit_service import audit_service
from backend.workflows.fallback_graph import run_fallback_graph, create_fallback_response
from backend.utils.constants import AGENT_MARGDARSHAN, AGENT_FALLBACK

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class AdoptionState(TypedDict, total=False):
    customer_id: str
    event: dict
    event_type: str  # "salary_credit" | "idle_balance" | "upi_not_activated" | "yono_not_adopted" etc.
    customer_context: dict
    intent: str
    confidence_score: float
    recommendation: Optional[Any]
    action_preview: Optional[Any]
    status: str  # tracks pipeline stage for the audit trail
    error: Optional[str]


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------

def load_memory_node(state: AdoptionState) -> AdoptionState:
    """Pull shared customer memory before doing anything else."""
    context = customer_memory.get_customer_context(state["customer_id"])
    customer_memory.set_last_agent(state["customer_id"], AGENT_MARGDARSHAN)
    
    audit_service.log_step(
        customer_id=state["customer_id"],
        step="memory_evaluation",
        agent=AGENT_MARGDARSHAN,
        metadata={"context_loaded": bool(context)},
    )
    return {**state, "customer_context": context, "status": "memory_evaluated"}


async def check_confidence_node(state: AdoptionState) -> AdoptionState:
    """Evaluate intent confidence for the incoming event."""
    result = await confidence_engine.evaluate_event(
        event_type=state["event_type"],
        source=state["event"].get("source", "webhook"),
    )
    
    audit_service.log_step(
        customer_id=state["customer_id"],
        step="confidence_check",
        agent=AGENT_MARGDARSHAN,
        metadata={"score": result.confidence},
    )
    return {
        **state,
        "confidence_score": result.confidence,
        "status": "confidence_evaluated",
    }


def route_on_confidence(state: AdoptionState) -> Literal["proceed", "fallback"]:
    """Conditional edge: confidence >= threshold -> proceed, else -> fallback."""
    from backend.guardrails.confidence_checker import assert_confidence
    try:
        assert_confidence(state["confidence_score"], state["customer_id"])
        return "proceed"
    except LowConfidenceError:
        return "fallback"


def fallback_node(state: AdoptionState) -> AdoptionState:
    """Low confidence path — defer to the existing fallback graph (clarifying question)."""
    audit_service.log_step(
        customer_id=state["customer_id"],
        step="low_confidence_fallback",
        agent=AGENT_MARGDARSHAN,
        metadata={"score": state["confidence_score"]},
    )
    
    fallback_result = run_fallback_graph(state["customer_id"], state["event"])
    clarifying_question = fallback_result.get("clarifying_question", "Maaf kijiye, main samajh nahi paaya. Kya aap thoda aur clearly bata sakte hain?")
    quick_reply_options = fallback_result.get("quick_reply_options", [])

    fallback_response = create_fallback_response(
        customer_id=state["customer_id"],
        agent=AGENT_FALLBACK,
        confidence=state["confidence_score"],
        clarifying_question=clarifying_question,
        quick_reply_options=quick_reply_options,
        session_id=state["event"].get("event_id", ""),
    )

    return {
        **state,
        "recommendation": fallback_response,
        "status": "fallback_triggered",
        "error": None,
        "action_preview": None,
    }


async def generate_recommendation_node(state: AdoptionState) -> AdoptionState:
    """Dispatch to the correct Margdarshan handler based on event_type."""
    from backend.utils import json_repository as repo
    from backend.agents.margdarshan_agent import _handle_fd_opportunity, _handle_upi_activation, _handle_yono_adoption
    from backend.models.event import Event
    from backend.utils.constants import (
        EVENT_SALARY_CREDIT,
        EVENT_IDLE_BALANCE,
        EVENT_FD_ELIGIBLE,
        EVENT_SUBSIDY_CREDIT,
        EVENT_UPI_NOT_ACTIVATED,
        EVENT_YONO_NOT_ADOPTED,
    )

    customer_record = repo.find_by_id("customers", "customer_id", state["customer_id"])
    if not customer_record:
        return {**state, "error": "Customer not found", "status": "error"}

    event_obj = Event(**state["event"])
    event_type = state["event_type"]

    try:
        if event_type in (EVENT_SALARY_CREDIT, EVENT_IDLE_BALANCE, EVENT_FD_ELIGIBLE, EVENT_SUBSIDY_CREDIT):
            recommendation = await _handle_fd_opportunity(customer_record, event_obj)
        elif event_type == EVENT_UPI_NOT_ACTIVATED:
            recommendation = _handle_upi_activation(customer_record, event_obj)
        elif event_type == EVENT_YONO_NOT_ADOPTED:
            recommendation = _handle_yono_adoption(customer_record, event_obj)
        else:
            recommendation = await _handle_fd_opportunity(customer_record, event_obj)

        audit_service.log_step(
            customer_id=state["customer_id"],
            step="recommendation_generated",
            agent=AGENT_MARGDARSHAN,
            metadata={"product_type": recommendation.product_type},
        )
        return {**state, "recommendation": recommendation, "status": "recommendation_generated"}

    except Exception as e:
        audit_service.log_step(
            customer_id=state["customer_id"],
            step="recommendation_error",
            agent=AGENT_MARGDARSHAN,
            metadata={"reason": str(e)},
        )
        return {**state, "error": str(e), "status": "error"}


def validate_action_node(state: AdoptionState) -> AdoptionState:
    """Pydantic/guardrail validation before building the Action Preview."""
    if state.get("error") or not state.get("recommendation"):
        return state

    recommendation = state["recommendation"]
    validated_action = validate_action(recommendation.action_preview, state["customer_id"])
    
    audit_service.log_step(
        customer_id=state["customer_id"],
        step="pydantic_validation",
        agent=AGENT_MARGDARSHAN,
        metadata={"validated": True},
    )
    return {**state, "action_preview": validated_action, "status": "action_validated"}


def build_action_preview_node(state: AdoptionState) -> AdoptionState:
    """Final node: surface the action preview, ready for MPIN/biometric gate downstream."""
    if state.get("error"):
        return state

    # Register with human-in-the-loop gate
    from backend.security.human_in_loop import human_in_loop_gate
    recommendation = state.get("recommendation")
    if recommendation:
        human_in_loop_gate.register_recommendation(
            recommendation_id=recommendation.recommendation_id,
            customer_id=state["customer_id"],
        )
        
        # Save to _recommendation_store
        from backend.routes.recommendation import store_recommendation
        store_recommendation(recommendation.model_dump(mode="json"))

    audit_service.log_step(
        customer_id=state["customer_id"],
        step="action_preview_ready",
        agent=AGENT_MARGDARSHAN,
        metadata={"action_preview": state.get("action_preview").model_dump(mode="json") if state.get("action_preview") else None},
    )
    return {**state, "status": "action_preview_ready"}


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_adoption_graph():
    try:
        from langgraph.graph import StateGraph, END
        
        graph = StateGraph(AdoptionState)

        graph.add_node("load_memory", load_memory_node)
        graph.add_node("check_confidence", check_confidence_node)
        graph.add_node("fallback", fallback_node)
        graph.add_node("generate_recommendation", generate_recommendation_node)
        graph.add_node("validate_action", validate_action_node)
        graph.add_node("build_action_preview", build_action_preview_node)

        graph.set_entry_point("load_memory")
        graph.add_edge("load_memory", "check_confidence")

        graph.add_conditional_edges(
            "check_confidence",
            route_on_confidence,
            {
                "proceed": "generate_recommendation",
                "fallback": "fallback",
            },
        )

        graph.add_edge("generate_recommendation", "validate_action")
        graph.add_edge("validate_action", "build_action_preview")
        graph.add_edge("build_action_preview", END)
        graph.add_edge("fallback", END)

        return graph.compile()
        
    except ImportError:
        logger = get_logger(__name__)
        logger.warning("langgraph_not_installed", note="Adoption graph running in stub mode")
        return None


# Compiled graph instance, importable by orchestrator.py
adoption_graph = build_adoption_graph()


async def run_adoption_graph(customer_id: str, event: dict) -> dict:
    """
    Entry point called by agents/orchestrator.py for any Margdarshan-routed event.

    event must include an "event_type" key matching one of:
    "salary_credit" | "idle_balance" | "upi_not_activated" | "yono_not_adopted"
    """
    initial_state: AdoptionState = {
        "customer_id": customer_id,
        "event": event,
        "event_type": event.get("event_type", ""),
        "status": "started",
    }
    if adoption_graph:
        return await adoption_graph.ainvoke(initial_state)
    return initial_state
