import os

# ── Confidence / Guardrails ────────────────────────────────────────────────
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
MIN_CONFIDENCE_TO_LOG: float = 0.50  # Below this → don't even log a rec attempt

# ── Agent Names ────────────────────────────────────────────────────────────
AGENT_MITRA = "mitra"
AGENT_MARGDARSHAN = "margdarshan"
AGENT_SAATHI = "saathi"
AGENT_ORCHESTRATOR = "orchestrator"
AGENT_FALLBACK = "fallback"

ALL_AGENTS = [AGENT_MITRA, AGENT_MARGDARSHAN, AGENT_SAATHI]

# ── Persona Types (must match PersonaType enum in models/customer.py) ─────
PERSONA_FARMER = "farmer"
PERSONA_STUDENT = "student"
PERSONA_MERCHANT = "merchant"
PERSONA_SALARIED = "salaried"
PERSONA_SENIOR_CITIZEN = "senior_citizen"
PERSONA_UNKNOWN = "unknown"

ALL_PERSONAS = [
    PERSONA_FARMER,
    PERSONA_STUDENT,
    PERSONA_MERCHANT,
    PERSONA_SALARIED,
    PERSONA_SENIOR_CITIZEN,
]

# ── Event Types (must match EventType enum in models/event.py) ─────────────
EVENT_SALARY_CREDIT = "salary_credit"
EVENT_SUBSIDY_CREDIT = "subsidy_credit"
EVENT_IDLE_BALANCE = "idle_balance"
EVENT_UPI_NOT_ACTIVATED = "upi_not_activated"
EVENT_YONO_NOT_ADOPTED = "yono_not_adopted"
EVENT_FD_ELIGIBLE = "fd_eligible"
EVENT_LIFE_EVENT = "life_event"
EVENT_EDUCATION_EXPENSE = "education_expense"
EVENT_FESTIVAL_PERIOD = "festival_period"
EVENT_TRAVEL_SPENDING = "travel_spending"
EVENT_SPENDING_ANOMALY = "spending_anomaly"
EVENT_KYC_INCOMPLETE = "kyc_incomplete"
EVENT_ACCOUNT_OPENED = "account_opened"

# ── Event → Agent Routing Map ──────────────────────────────────────────────
EVENT_AGENT_MAP: dict[str, str] = {
    EVENT_SALARY_CREDIT: AGENT_MARGDARSHAN,
    EVENT_SUBSIDY_CREDIT: AGENT_MARGDARSHAN,
    EVENT_IDLE_BALANCE: AGENT_MARGDARSHAN,
    EVENT_UPI_NOT_ACTIVATED: AGENT_MARGDARSHAN,
    EVENT_YONO_NOT_ADOPTED: AGENT_MARGDARSHAN,
    EVENT_FD_ELIGIBLE: AGENT_MARGDARSHAN,
    EVENT_LIFE_EVENT: AGENT_SAATHI,
    EVENT_EDUCATION_EXPENSE: AGENT_SAATHI,
    EVENT_FESTIVAL_PERIOD: AGENT_SAATHI,
    EVENT_TRAVEL_SPENDING: AGENT_SAATHI,
    EVENT_SPENDING_ANOMALY: AGENT_SAATHI,
    EVENT_KYC_INCOMPLETE: AGENT_MITRA,
    EVENT_ACCOUNT_OPENED: AGENT_MITRA,
}

# ── Network / Degradation Modes ────────────────────────────────────────────
NETWORK_MODE_VOICE = "voice"
NETWORK_MODE_COMPRESSED_TEXT = "compressed_text"
NETWORK_MODE_BASIC = "basic"

# Degradation order (index = priority, higher index = worse connection)
NETWORK_DEGRADATION_CHAIN = [
    NETWORK_MODE_VOICE,
    NETWORK_MODE_COMPRESSED_TEXT,
    NETWORK_MODE_BASIC,
]

# ── FD Engine ─────────────────────────────────────────────────────────────
FD_MIN_ELIGIBLE_BALANCE: float = 5000.0   # minimum idle balance to suggest FD
FD_IDLE_THRESHOLD_DAYS: int = 14           # days balance must sit to be "idle"

# SBI FD interest rates (in %) — matches products.json
FD_RATES: dict[str, float] = {
    "7d_to_45d": 3.50,
    "46d_to_179d": 4.75,
    "180d_to_1y": 5.50,
    "1y_to_2y": 6.80,
    "2y_to_3y": 7.00,
    "3y_to_5y": 6.50,
    "5y_to_10y": 6.50,
}
FD_SENIOR_CITIZEN_BONUS: float = 0.50     # extra 50 bps for senior citizens

# ── Recommendation ─────────────────────────────────────────────────────────
REC_DEFAULT_EXPIRY_HOURS: int = 72         # recommendations expire after 72h

# ── Redis ──────────────────────────────────────────────────────────────────
REDIS_SESSION_TTL: int = 3600              # seconds
REDIS_KEY_PREFIX_CUSTOMER = "saarthi:customer:"
REDIS_KEY_PREFIX_SESSION = "saarthi:session:"
REDIS_KEY_PREFIX_INTERACTION = "saarthi:interaction:"

# ── MPIN ──────────────────────────────────────────────────────────────────
DEFAULT_DEMO_MPIN: str = os.getenv("DEFAULT_DEMO_MPIN", "1234")
MPIN_MAX_ATTEMPTS: int = 3                 # lock after 3 failed attempts

# ── Audit Steps (must match AuditStep enum in models/audit_log.py) ─────────
AUDIT_STEP_WEBHOOK_TRIGGER = "webhook_trigger"
AUDIT_STEP_MEMORY_EVALUATION = "memory_evaluation"
AUDIT_STEP_AGENT_ACTIVATED = "agent_activated"
AUDIT_STEP_PYDANTIC_VALIDATION = "pydantic_validation"
AUDIT_STEP_RECOMMENDATION_GENERATED = "recommendation_generated"
AUDIT_STEP_ACTION_PREVIEW = "action_preview"
AUDIT_STEP_MPIN_VERIFICATION = "mpin_verification"
AUDIT_STEP_EXECUTION_COMPLETE = "execution_complete"

# ── Sarvam AI / Language ──────────────────────────────────────────────────
SUPPORTED_LANGUAGES = ["en", "hi", "ta", "te", "kn", "mr", "gu", "bn", "pa"]
DEFAULT_LANGUAGE = "hi"

# ── API Response Codes ─────────────────────────────────────────────────────
SUCCESS = "success"
ERROR = "error"
PENDING = "pending"
