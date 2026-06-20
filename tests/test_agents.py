"""
SAARTHI AI — Test Suite: Agents
Tests for margdarshan_agent.py, mitra_agent.py, saathi_agent.py.
Run: pytest tests/test_agents.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from backend.models.event import Event, EventType, EventSource, EventStatus
from backend.models.recommendation import Recommendation, FallbackResponse


def make_event(event_type: str, customer_id: str = "CUST001", amount: float = 55000.0) -> Event:
    return Event(
        event_id="EVT-TEST001",
        customer_id=customer_id,
        event_type=event_type,
        amount=amount,
        source=EventSource.WEBHOOK,
        status=EventStatus.PENDING,
        agent_assigned="margdarshan",
    )


# ── MARGDARSHAN Tests ──────────────────────────────────────────────────────

class TestMargdarshanAgent:

    @pytest.mark.asyncio
    async def test_salary_credit_generates_fd_recommendation(self):
        """Salary credit event for salaried customer with sufficient balance → FD rec."""
        from backend.agents.margdarshan_agent import run_margdarshan
        event = make_event(EventType.SALARY_CREDIT, "CUST001")

        with patch("backend.agents.margdarshan_agent.repo.find_by_id") as mock_find, \
             patch("backend.agents.margdarshan_agent.audit_service.log_step"), \
             patch("backend.agents.margdarshan_agent.audit_service.timed_step") as mock_timed, \
             patch("backend.agents.margdarshan_agent.customer_memory.get_customer_context", return_value={}), \
             patch("backend.agents.margdarshan_agent.customer_memory.set_last_agent"), \
             patch("backend.agents.margdarshan_agent.customer_memory.log_interaction"), \
             patch("backend.agents.margdarshan_agent.confidence_engine.evaluate_event") as mock_conf, \
             patch("backend.services.consent_service.consent_service.get_consent") as mock_consent, \
             patch("backend.agents.margdarshan_agent.human_in_loop_gate.register_recommendation"):

            mock_find.return_value = {
                "customer_id": "CUST001",
                "name": "Ramesh Kumar",
                "persona": "salaried",
                "current_balance": 45000.0,
                "date_of_birth": "1985-03-15",
            }
            from backend.services.confidence_engine import ConfidenceResult
            mock_conf.return_value = ConfidenceResult(
                detected_intent="salary_credit",
                confidence=0.97,
                should_proceed=True,
                should_log=True,
            )
            from backend.models.consent import ConsentRecord
            mock_consent.return_value = ConsentRecord(
                consent_id="CON001",
                customer_id="CUST001",
                voice_processing=True,
                memory_storage=True,
                personalized_recommendations=True,
            )
            mock_timed.return_value.__enter__ = MagicMock(return_value=None)
            mock_timed.return_value.__exit__ = MagicMock(return_value=False)

            result = await run_margdarshan("CUST001", event)

        assert isinstance(result, Recommendation)
        assert result.product_type in ("fixed_deposit", "upi_activation")
        assert result.confidence_score >= 0.85
        assert result.customer_id == "CUST001"
        assert result.agent_source == "margdarshan"
        assert result.why_explanation  # Must have explainability

    @pytest.mark.asyncio
    async def test_low_confidence_returns_fallback(self):
        """If confidence < 0.85, agent returns FallbackResponse, not Recommendation."""
        from backend.agents.margdarshan_agent import run_margdarshan
        event = make_event(EventType.IDLE_BALANCE, "CUST001")

        with patch("backend.agents.margdarshan_agent.repo.find_by_id") as mock_find, \
             patch("backend.agents.margdarshan_agent.audit_service.log_step"), \
             patch("backend.agents.margdarshan_agent.audit_service.timed_step") as mock_timed, \
             patch("backend.agents.margdarshan_agent.customer_memory.get_customer_context", return_value={}), \
             patch("backend.agents.margdarshan_agent.customer_memory.set_last_agent"), \
             patch("backend.agents.margdarshan_agent.confidence_engine.evaluate_event") as mock_conf:

            mock_find.return_value = {"customer_id": "CUST001", "name": "Test", "persona": "salaried", "current_balance": 1000.0}
            from backend.services.confidence_engine import ConfidenceResult
            mock_conf.return_value = ConfidenceResult(
                detected_intent="unknown",
                confidence=0.60,   # Below 0.85 threshold
                should_proceed=False,
                should_log=True,
                clarifying_question="Kya aap FD banana chahte hain?",
                quick_reply_options=["Haan, FD", "Nahi"],
            )
            mock_timed.return_value.__enter__ = MagicMock(return_value=None)
            mock_timed.return_value.__exit__ = MagicMock(return_value=False)

            result = await run_margdarshan("CUST001", event)

        assert isinstance(result, FallbackResponse)
        assert result.confidence_score < 0.85
        assert result.clarifying_question

    @pytest.mark.asyncio
    async def test_customer_not_found_raises_error(self):
        """Missing customer raises CustomerNotFoundError."""
        from backend.agents.margdarshan_agent import run_margdarshan
        from backend.utils.error_handlers import CustomerNotFoundError
        event = make_event(EventType.SALARY_CREDIT, "CUST999")

        with patch("backend.agents.margdarshan_agent.repo.find_by_id", return_value=None), \
             patch("backend.agents.margdarshan_agent.audit_service.log_step"):
            with pytest.raises(CustomerNotFoundError):
                await run_margdarshan("CUST999", event)


# ── FD Engine Tests ────────────────────────────────────────────────────────

class TestFDEngine:

    def test_fd_calculation_salaried(self):
        from backend.services.fd_engine import fd_engine
        result = fd_engine.calculate(current_balance=45000.0, persona="salaried",
                                     customer_id="CUST001", date_of_birth="1985-03-15")
        assert result.eligible is True
        assert result.recommended_amount > 0
        assert result.recommended_amount <= 45000.0 * 0.80  # At most 80% of balance
        assert result.interest_rate >= 5.0
        assert result.estimated_maturity > result.recommended_amount

    def test_fd_ineligible_low_balance(self):
        from backend.services.fd_engine import fd_engine
        result = fd_engine.calculate(current_balance=1000.0, persona="salaried",
                                     customer_id="CUST001")
        assert result.eligible is False
        assert result.ineligibility_reason is not None

    def test_senior_citizen_gets_bonus_rate(self):
        from backend.services.fd_engine import fd_engine
        result = fd_engine.calculate(current_balance=50000.0, persona="senior_citizen",
                                     customer_id="CUST005", date_of_birth="1952-09-30")
        assert result.is_senior_citizen is True
        assert result.interest_rate >= 6.80 + 0.50  # Base + senior bonus


# ── Persona Engine Tests ───────────────────────────────────────────────────

class TestPersonaEngine:

    @pytest.mark.asyncio
    async def test_salary_transactions_classify_salaried(self):
        from backend.services.persona_engine import persona_engine
        from backend.models.customer import PersonaType
        transactions = [
            {"transaction_type": "credit", "category": "salary", "merchant": "ABC Corp"},
            {"transaction_type": "credit", "category": "salary", "merchant": "ABC Corp"},
        ]
        result = await persona_engine.classify("CUST001", transactions, account_type="salary")
        assert result == PersonaType.SALARIED

    @pytest.mark.asyncio
    async def test_subsidy_transactions_classify_farmer(self):
        from backend.services.persona_engine import persona_engine
        from backend.models.customer import PersonaType
        transactions = [
            {"transaction_type": "credit", "category": "subsidy", "merchant": "PM-KISAN"},
        ]
        result = await persona_engine.classify("CUST004", transactions,
                                               account_type="jan_dhan",
                                               address="Village Rampur, UP")
        assert result == PersonaType.FARMER

    @pytest.mark.asyncio
    async def test_age_60_plus_classifies_senior(self):
        from backend.services.persona_engine import persona_engine
        from backend.models.customer import PersonaType
        transactions = [
            {"transaction_type": "credit", "category": "pension", "merchant": "EPFO"},
        ]
        result = await persona_engine.classify("CUST005", transactions, date_of_birth="1952-09-30")
        assert result == PersonaType.SENIOR_CITIZEN


class TestAdoptionGraph:

    @pytest.mark.asyncio
    async def test_adoption_graph_salary_credit_generates_fd(self):
        from backend.workflows.adoption_graph import run_adoption_graph
        event = {
            "event_id": "EVT-TEST-GR001",
            "customer_id": "CUST001",
            "event_type": "salary_credit",
            "amount": 55000.0,
            "source": "webhook",
        }

        with patch("backend.utils.json_repository.find_by_id") as mock_find, \
             patch("backend.services.audit_service.audit_service.log_step"), \
             patch("backend.services.audit_service.audit_service.timed_step"), \
             patch("backend.memory.customer_memory.customer_memory.get_customer_context", return_value={}), \
             patch("backend.memory.customer_memory.customer_memory.set_last_agent"), \
             patch("backend.services.confidence_engine.confidence_engine.evaluate_event") as mock_conf, \
             patch("backend.services.consent_service.consent_service.get_consent") as mock_consent, \
             patch("backend.routes.recommendation.store_recommendation"), \
             patch("backend.security.human_in_loop.human_in_loop_gate.register_recommendation"):

            mock_find.return_value = {
                "customer_id": "CUST001",
                "name": "Ramesh Kumar",
                "persona": "salaried",
                "current_balance": 45000.0,
                "date_of_birth": "1985-03-15",
            }
            from backend.services.confidence_engine import ConfidenceResult
            mock_conf.return_value = ConfidenceResult(
                detected_intent="salary_credit",
                confidence=0.97,
                should_proceed=True,
                should_log=True,
            )
            from backend.models.consent import ConsentRecord
            mock_consent.return_value = ConsentRecord(
                consent_id="CON-001",
                customer_id="CUST001",
                voice_processing=True,
                memory_storage=True,
                personalized_recommendations=True,
            )

            result = await run_adoption_graph("CUST001", event)

            assert result["status"] == "action_preview_ready"
            assert result["recommendation"] is not None
            assert result["recommendation"].product_type == "fixed_deposit"

