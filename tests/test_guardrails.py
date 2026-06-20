"""
SAARTHI AI — Test Suite: Guardrails
Tests for confidence threshold, consent blocking, action validation.
Run: pytest tests/test_guardrails.py -v
"""
import pytest
from unittest.mock import MagicMock

from backend.models.recommendation import ActionPreview, ProductType
from backend.services.confidence_engine import ConfidenceResult


class TestConfidenceChecker:

    def test_passes_above_threshold(self):
        from backend.guardrails.confidence_checker import check_confidence
        result = ConfidenceResult(
            detected_intent="fd_enquiry", confidence=0.92,
            should_proceed=True, should_log=True,
        )
        # Should NOT raise
        check_confidence(result, "CUST001")

    def test_raises_below_threshold(self):
        from backend.guardrails.confidence_checker import check_confidence
        from backend.utils.error_handlers import LowConfidenceError
        result = ConfidenceResult(
            detected_intent="unknown", confidence=0.70,
            should_proceed=False, should_log=True,
            clarifying_question="Kya aap FD kholna chahte hain?",
        )
        with pytest.raises(LowConfidenceError):
            check_confidence(result, "CUST001")

    def test_exact_threshold_passes(self):
        from backend.guardrails.confidence_checker import check_confidence
        result = ConfidenceResult(
            detected_intent="fd_enquiry", confidence=0.85,
            should_proceed=True, should_log=True,
        )
        check_confidence(result, "CUST001")  # Should not raise

    def test_one_below_threshold_fails(self):
        from backend.guardrails.confidence_checker import check_confidence
        from backend.utils.error_handlers import LowConfidenceError
        result = ConfidenceResult(
            detected_intent="fd_enquiry", confidence=0.849,
            should_proceed=False, should_log=True,
        )
        with pytest.raises(LowConfidenceError):
            check_confidence(result, "CUST001")


class TestConsentValidator:

    def _make_consent(self, voice=False, memory=False, personalise=False):
        from backend.models.consent import ConsentRecord
        return ConsentRecord(
            consent_id="CON-TEST",
            customer_id="CUST001",
            voice_processing=voice,
            memory_storage=memory,
            personalized_recommendations=personalise,
        )

    def test_voice_blocked_without_consent(self):
        from backend.guardrails.consent_validator import require_voice_consent
        from backend.utils.error_handlers import ConsentRequiredError
        consent = self._make_consent(voice=False)
        with pytest.raises(ConsentRequiredError):
            require_voice_consent(consent, "CUST001")

    def test_voice_passes_with_consent(self):
        from backend.guardrails.consent_validator import require_voice_consent
        consent = self._make_consent(voice=True)
        require_voice_consent(consent, "CUST001")  # Should not raise

    def test_memory_blocked_without_consent(self):
        from backend.guardrails.consent_validator import require_memory_consent
        from backend.utils.error_handlers import ConsentRequiredError
        consent = self._make_consent(memory=False)
        with pytest.raises(ConsentRequiredError):
            require_memory_consent(consent, "CUST001")

    def test_personalisation_blocked_without_consent(self):
        from backend.guardrails.consent_validator import require_personalisation_consent
        from backend.utils.error_handlers import ConsentRequiredError
        consent = self._make_consent(personalise=False)
        with pytest.raises(ConsentRequiredError):
            require_personalisation_consent(consent, "CUST001")

    def test_none_consent_blocks_voice(self):
        from backend.guardrails.consent_validator import require_voice_consent
        from backend.utils.error_handlers import ConsentRequiredError
        with pytest.raises(ConsentRequiredError):
            require_voice_consent(None, "CUST001")


class TestActionValidator:

    def _make_preview(self, product="SBI Fixed Deposit", product_type=ProductType.FIXED_DEPOSIT,
                      amount=10000.0, tenure="1 Year", interest_rate=6.8):
        return ActionPreview(
            product=product, product_type=product_type, amount=amount,
            tenure=tenure, interest_rate=interest_rate,
            action_label="Open FD",
        )

    def test_valid_fd_passes(self):
        from backend.guardrails.action_validator import validate_action
        preview = self._make_preview()
        validate_action(preview, "CUST001")  # Should not raise

    def test_loan_product_blocked(self):
        from backend.guardrails.action_validator import validate_action
        from backend.utils.error_handlers import ValidationError
        preview = ActionPreview(
            product="SBI Home Loan",
            product_type=ProductType.FIXED_DEPOSIT,  # Mismatched but product name triggers check
            action_label="Apply for Loan",
        )
        with pytest.raises(ValidationError):
            validate_action(preview, "CUST001")

    def test_fd_missing_amount_blocked(self):
        from backend.guardrails.action_validator import validate_action
        from backend.utils.error_handlers import ValidationError
        preview = ActionPreview(
            product="SBI Fixed Deposit",
            product_type=ProductType.FIXED_DEPOSIT,
            # amount missing!
            tenure="1 Year",
            interest_rate=6.8,
            action_label="Open FD",
        )
        with pytest.raises(ValidationError):
            validate_action(preview, "CUST001")

    def test_upi_without_amount_passes(self):
        from backend.guardrails.action_validator import validate_action
        preview = ActionPreview(
            product="SBI UPI", product_type=ProductType.UPI_ACTIVATION,
            action_label="Activate UPI",
        )
        validate_action(preview, "CUST001")  # UPI doesn't need amount


class TestHumanInLoop:

    def test_full_chain_passes(self):
        """Valid chain: register → preview → mpin → execute."""
        from backend.security.human_in_loop import HumanInLoopGate
        gate = HumanInLoopGate()
        gate.register_recommendation("REC-001", "CUST001")
        gate.advance_to_preview("REC-001", "CUST001")
        gate.advance_to_mpin("REC-001", "CUST001")
        gate.advance_to_execute("REC-001", "CUST001")
        assert gate.is_cleared_for_execution("REC-001")

    def test_skip_preview_raises(self):
        """Trying to MPIN without preview step → violation."""
        from backend.security.human_in_loop import HumanInLoopGate
        from backend.utils.error_handlers import HumanInLoopViolationError
        gate = HumanInLoopGate()
        gate.register_recommendation("REC-002", "CUST001")
        # Skip advance_to_preview
        with pytest.raises(HumanInLoopViolationError):
            gate.advance_to_mpin("REC-002", "CUST001")

    def test_execute_without_mpin_raises(self):
        """Trying to execute without MPIN verification → violation."""
        from backend.security.human_in_loop import HumanInLoopGate
        from backend.utils.error_handlers import HumanInLoopViolationError
        gate = HumanInLoopGate()
        gate.register_recommendation("REC-003", "CUST001")
        gate.advance_to_preview("REC-003", "CUST001")
        # Skip advance_to_mpin
        with pytest.raises(HumanInLoopViolationError):
            gate.advance_to_execute("REC-003", "CUST001")

    def test_unregistered_recommendation_raises(self):
        """Assert on unregistered rec ID → violation."""
        from backend.security.human_in_loop import HumanInLoopGate
        from backend.utils.error_handlers import HumanInLoopViolationError
        gate = HumanInLoopGate()
        with pytest.raises(HumanInLoopViolationError):
            gate.assert_cleared_for_execution("REC-GHOST", "CUST001")
