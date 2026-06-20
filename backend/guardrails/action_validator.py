"""
SAARTHI AI — Action Validator (Guardrail)
Validates ActionPreview objects before they reach the customer-facing
Action Preview Layer.

Every action shown to the customer MUST pass this validator.
It checks that the action is complete, coherent, and within allowed scope.

Scope constraints enforced here:
  ✅ Fixed Deposit — ALLOWED
  ✅ UPI Activation — ALLOWED
  ✅ YONO Adoption — ALLOWED
  ✅ KYC Completion — ALLOWED
  ❌ Loan — NOT ALLOWED (compliance boundary)
  ❌ Insurance — NOT ALLOWED
  ❌ Mutual Funds / SIP — NOT ALLOWED

Used by: human_in_loop.py (before Action Preview is shown)
"""
from __future__ import annotations

from backend.models.recommendation import ActionPreview, ProductType
from backend.utils.error_handlers import ValidationError as SaarthiValidationError
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

# Products that SAARTHI AI is explicitly NOT allowed to recommend
OUT_OF_SCOPE_PRODUCTS = {"loan", "insurance", "mutual_fund", "sip", "credit_card"}

# Required fields for each product type (beyond the base ActionPreview fields)
PRODUCT_REQUIRED_FIELDS: dict[str, list[str]] = {
    ProductType.FIXED_DEPOSIT: ["amount", "tenure", "interest_rate"],
    ProductType.UPI_ACTIVATION: [],         # No financial fields needed
    ProductType.YONO_ADOPTION: [],
    ProductType.SAVINGS_ACCOUNT: [],
    ProductType.RECURRING_DEPOSIT: ["amount", "tenure"],
    ProductType.KYC_COMPLETION: [],
    ProductType.DIGITAL_LITERACY: [],
}


def validate_action(action: ActionPreview, customer_id: str) -> ActionPreview:
    """
    Validate an ActionPreview object before it reaches the Action Preview screen.

    Raises:
        SaarthiValidationError: If the action is invalid or out of scope.

    Returns:
        The validated ActionPreview (unchanged) if all checks pass.
    """
    # 1. Scope check — block out-of-scope products
    _check_scope(action, customer_id)

    # 2. Required fields for the product type
    _check_required_fields(action, customer_id)

    # 3. Financial sanity checks for monetary actions
    if action.amount is not None:
        _check_financial_sanity(action, customer_id)

    logger.info(
        "action_validated",
        customer_id=customer_id,
        product=action.product,
        product_type=action.product_type,
        amount=action.amount,
    )
    return action


def _check_scope(action: ActionPreview, customer_id: str) -> None:
    """Ensure product is within SAARTHI AI's allowed scope."""
    product_lower = action.product.lower()
    for blocked in OUT_OF_SCOPE_PRODUCTS:
        if blocked in product_lower:
            logger.error(
                "action_out_of_scope",
                customer_id=customer_id,
                product=action.product,
                blocked_keyword=blocked,
            )
            raise SaarthiValidationError(
                message=f"Product '{action.product}' is out of scope for SAARTHI AI",
                detail=(
                    f"SAARTHI AI does not handle {blocked} products. "
                    "Please consult an SBI branch for this product."
                ),
            )


def _check_required_fields(action: ActionPreview, customer_id: str) -> None:
    """Verify product-type-specific required fields are present."""
    required = PRODUCT_REQUIRED_FIELDS.get(action.product_type, [])
    missing = []
    for field in required:
        value = getattr(action, field, None)
        if value is None:
            missing.append(field)

    if missing:
        logger.error(
            "action_missing_fields",
            customer_id=customer_id,
            product_type=action.product_type,
            missing_fields=missing,
        )
        raise SaarthiValidationError(
            message=f"ActionPreview for {action.product_type} is missing required fields: {missing}",
            detail=f"Cannot show Action Preview without: {', '.join(missing)}",
        )


def _check_financial_sanity(action: ActionPreview, customer_id: str) -> None:
    """Sanity check on amounts and rates."""
    errors = []

    if action.amount is not None and action.amount <= 0:
        errors.append(f"amount must be positive, got {action.amount}")

    if action.interest_rate is not None:
        if not (0.0 < action.interest_rate <= 20.0):
            errors.append(
                f"interest_rate {action.interest_rate}% is outside expected range (0-20%)"
            )

    if errors:
        logger.error(
            "action_financial_sanity_failed",
            customer_id=customer_id,
            errors=errors,
        )
        raise SaarthiValidationError(
            message="ActionPreview failed financial sanity checks",
            detail="; ".join(errors),
        )
