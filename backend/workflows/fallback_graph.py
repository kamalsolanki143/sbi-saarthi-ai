"""
SAARTHI AI — Fallback Graph (Safety-Critical LangGraph Workflow)
Implements the confidence < 0.85 clarifying-question flow.

This graph is triggered when confidence_checker.py catches a LowConfidenceError.
Instead of proceeding with a potentially unsafe recommendation, the agent
asks a targeted clarifying question and awaits the customer's response.

Pipeline:
  Low Confidence Detected
  → Generate Clarifying Question
  → Present to Customer
  → Await Response
  → Re-evaluate Confidence
  → Route: proceed / fallback again / escalate

This is a safety-critical workflow — do NOT add bypass nodes.
"""
from __future__ import annotations

from typing import Any, TypedDict

from backend.models.recommendation import FallbackResponse
from backend.utils.constants import AGENT_FALLBACK, CONFIDENCE_THRESHOLD
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


# ── State ──────────────────────────────────────────────────────────────────

class FallbackState(TypedDict):
    customer_id: str
    original_input: str
    detected_intent: str
    confidence: float
    clarifying_question: str
    quick_reply_options: list[str]
    customer_response: str | None
    re_evaluated_confidence: float | None
    final_intent: str | None
    should_proceed: bool
    iteration: int  # Limit clarifying question loops to 2


# ── Node Functions ─────────────────────────────────────────────────────────

def generate_clarifying_question(state: FallbackState) -> FallbackState:
    """
    Generate a contextual clarifying question based on partial intent.
    This is a safety node — it only asks, never acts.
    """
    logger.info(
        "fallback_generating_question",
        customer_id=state["customer_id"],
        intent=state["detected_intent"],
        confidence=state["confidence"],
        iteration=state["iteration"],
    )

    # After 2 iterations, escalate to a human agent / generic help
    if state["iteration"] >= 2:
        return {
            **state,
            "clarifying_question": (
                "Mujhe aapki madad karne mein thodi takleef aa rahi hai. "
                "Kya aap apni SBI branch se sampark kar sakte hain ya "
                "SBI helpline 1800-11-2211 pe call kar sakte hain?"
            ),
            "quick_reply_options": ["SBI Branch", "Helpline Call Karein"],
            "should_proceed": False,
        }

    # Use confidence_engine clarifying question (already computed upstream)
    return state


def await_customer_response(state: FallbackState) -> FallbackState:
    """
    Placeholder node representing the async wait for customer response.
    In production: this would be handled by the WebSocket/session layer.
    The session manager calls back into the graph with the customer's response.
    """
    # Customer response is injected into state by the session layer
    return state


async def re_evaluate_intent(state: FallbackState) -> FallbackState:
    """
    Re-evaluate intent confidence after the customer's clarifying response.
    If confidence >= 0.85, mark should_proceed=True.
    Otherwise, increment iteration for another round.
    """
    from backend.services.confidence_engine import confidence_engine

    customer_response = state.get("customer_response", "")
    if not customer_response:
        return {**state, "should_proceed": False}

    result = await confidence_engine.evaluate_text_input(
        customer_input=customer_response,
        customer_id=state["customer_id"],
        context=f"Previous intent: {state['detected_intent']}",
    )

    should_proceed = result.confidence >= CONFIDENCE_THRESHOLD
    logger.info(
        "fallback_re_evaluated",
        customer_id=state["customer_id"],
        new_confidence=result.confidence,
        should_proceed=should_proceed,
    )

    return {
        **state,
        "re_evaluated_confidence": result.confidence,
        "final_intent": result.detected_intent,
        "should_proceed": should_proceed,
        "iteration": state["iteration"] + 1,
        "clarifying_question": result.clarifying_question if not should_proceed else None,
        "quick_reply_options": result.quick_reply_options if not should_proceed else [],
    }


# ── Graph Builder ──────────────────────────────────────────────────────────

def build_fallback_graph():
    """
    Build the LangGraph StateGraph for the fallback flow.
    Returns the compiled graph.

    NOTE: This uses LangGraph's StateGraph API.
    Kamal's orchestration decisions will extend this graph.
    """
    try:
        from langgraph.graph import StateGraph, END

        graph = StateGraph(FallbackState)

        graph.add_node("generate_question", generate_clarifying_question)
        graph.add_node("await_response", await_customer_response)
        graph.add_node("re_evaluate", re_evaluate_intent)

        graph.set_entry_point("generate_question")
        graph.add_edge("generate_question", "await_response")
        graph.add_edge("await_response", "re_evaluate")

        # Conditional edge: if confident → END; if not → loop back
        def should_loop(state: FallbackState) -> str:
            if state["should_proceed"]:
                return "end"
            if state["iteration"] >= 2:
                return "end"
            return "generate_question"

        graph.add_conditional_edges("re_evaluate", should_loop, {"end": END, "generate_question": "generate_question"})

        return graph.compile()

    except ImportError:
        logger.warning("langgraph_not_installed", note="Fallback graph running in stub mode")
        return None


def create_fallback_response(
    customer_id: str,
    agent: str,
    confidence: float,
    clarifying_question: str,
    quick_reply_options: list[str],
    session_id: str,
) -> FallbackResponse:
    """
    Convenience function to create a FallbackResponse directly.
    Used when the graph is not needed (e.g., first clarifying question).
    """
    return FallbackResponse(
        customer_id=customer_id,
        agent=agent,
        confidence_score=confidence,
        clarifying_question=clarifying_question,
        question_options=quick_reply_options,
        session_id=session_id,
    )


# ── Singleton compiled graph ─────────────────────────────────────────────
fallback_graph = build_fallback_graph()


def run_fallback_graph(customer_id: str, event: dict) -> dict:
    """
    Entry point called by other graphs/agents to run the fallback clarifying question flow.
    """
    initial_state = {
        "customer_id": customer_id,
        "original_input": event.get("text_input", ""),
        "detected_intent": event.get("event_type", ""),
        "confidence": event.get("confidence", 0.0),
        "clarifying_question": "Maaf kijiye, main samajh nahi paaya. Kya aap thoda aur clearly bata sakte hain?",
        "quick_reply_options": ["Balance check", "FD khulwana hai", "UPI activate karna hai", "Help chahiye"],
        "customer_response": None,
        "re_evaluated_confidence": None,
        "final_intent": None,
        "should_proceed": False,
        "iteration": 0,
    }
    if fallback_graph:
        return fallback_graph.invoke(initial_state)
    return initial_state

