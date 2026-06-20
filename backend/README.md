# SAARTHI AI — Backend README

## Quick Start

```bash
# 1. Clone / navigate to project root
cd "muskan personal/Saarthi Ai"

# 2. Create virtualenv
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit env vars
cp .env.example .env
# Fill in GEMINI_API_KEY at minimum

# 5. Start Redis + any other services
docker-compose up -d

# 6. Run the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 7. Interactive API docs
open http://localhost:8000/docs
```

## Run Tests

```bash
pytest tests/ -v
# Individual suites:
pytest tests/test_guardrails.py -v   # Safety-critical guardrail tests
pytest tests/test_agents.py -v       # Agent pipeline tests
pytest tests/test_memory.py -v       # Memory layer tests
pytest tests/test_api.py -v          # API integration tests
```

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app init, routers, middleware
├── agents/
│   ├── orchestrator.py        # LangGraph event router
│   ├── margdarshan_agent.py   # Digital adoption (MVP)
│   ├── mitra_agent.py         # Customer acquisition
│   └── saathi_agent.py        # Customer engagement
├── guardrails/
│   ├── confidence_checker.py  # 85% threshold enforcement ⛔
│   ├── consent_validator.py   # DPDP consent blocking ⛔
│   ├── action_validator.py    # Out-of-scope product blocking ⛔
│   └── pydantic_validation.py # LLM output validation
├── security/
│   ├── human_in_loop.py       # State machine: Rec→Preview→MPIN→Execute ⛔
│   ├── mpin_gate.py           # MPIN verification + lockout
│   └── biometric_gate.py      # Biometric stub
├── memory/
│   ├── customer_memory.py     # Cross-agent shared memory
│   ├── redis_memory.py        # Redis wrapper + fallback
│   └── vector_memory.py       # ChromaDB semantic memory
├── services/
│   ├── gemini_service.py      # Gemini AI client
│   ├── confidence_engine.py   # Intent confidence scoring
│   ├── audit_service.py       # Audit trail + timed_step context mgr
│   ├── persona_engine.py      # Customer persona classification
│   ├── event_engine.py        # Event lifecycle management
│   ├── fd_engine.py           # FD recommendation calculator
│   ├── consent_service.py     # DPDP consent management
│   ├── recommendation_engine.py # Recommendation builder
│   ├── sarvam_service.py      # Voice (STT/TTS/Translation via Sarvam AI)
│   └── network_fallback_service.py # Connectivity degradation
├── routes/
│   ├── customer.py            # GET/POST/PUT customer profiles
│   ├── event.py               # POST /events → triggers agents
│   ├── recommendation.py      # GET recs, action-preview, confirm
│   ├── consent.py             # Grant/revoke DPDP consent
│   ├── auth.py                # Sessions, MPIN verify, biometric
│   ├── voice.py               # Sarvam AI voice processing
│   └── audit.py               # Pipeline audit trail + WebSocket
├── ocr/
│   ├── document_parser.py     # Tesseract OCR wrapper
│   ├── kyc_processor.py       # Aadhaar/PAN field extraction
│   └── lead_extractor.py      # Lead qualification signals
├── workflows/
│   └── fallback_graph.py      # LangGraph confidence<85% flow
├── models/                    # Pydantic v2 data models
└── utils/                     # Constants, formatters, logging, repo
tests/
├── test_agents.py             # Agent pipeline tests
├── test_guardrails.py         # Safety-critical guardrail tests (15 tests)
├── test_memory.py             # Memory + consent gating tests
└── test_api.py                # API integration tests
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | System health + Redis/ChromaDB status |
| GET | `/customers/{id}` | Customer profile (no MPIN leak) |
| POST | `/customers` | Create new customer |
| GET | `/customers/{id}/persona` | Run persona classification |
| **POST** | **`/events`** | **Trigger agent pipeline (main entrypoint)** |
| GET | `/recommendations/{customer_id}` | Get active recommendations |
| GET | `/recommendations/{id}/why` | Explainability (Why am I seeing this?) |
| POST | `/recommendations/{id}/action-preview` | Show action preview (human-in-loop step 2) |
| POST | `/recommendations/{id}/confirm` | MPIN verify + execute (step 3+4) |
| GET | `/consent/{customer_id}` | Get consent state |
| POST | `/consent/{customer_id}/grant` | Grant permissions |
| POST | `/consent/{customer_id}/revoke` | Revoke permissions |
| POST | `/auth/session` | Create session |
| POST | `/auth/mpin/verify` | Verify MPIN |
| POST | `/voice/process` | Process voice/text input |
| GET | `/audit/{customer_id}` | Full audit trail |
| WS | `/audit/ws/{customer_id}` | Real-time pipeline feed |

---

## Human-in-the-Loop Flow (Safety-Critical)

```
POST /events  →  Agent generates Recommendation
                          ↓
POST /recommendations/{id}/action-preview  →  Customer sees exact action
                          ↓
Customer enters MPIN
                          ↓
POST /recommendations/{id}/confirm  →  MPIN verified  →  Execution unlocked
```

**AI NEVER directly executes a transaction.** Every execution requires the full 4-step chain enforced by `human_in_loop.py`.

---

## Confidence Fallback Logic

If intent confidence < **0.85** (set in `constants.py`):
- Agent does NOT generate a recommendation
- A `FallbackResponse` with a clarifying question is returned
- Max 2 clarifying question loops before human escalation

---

## For Frontend Integration (Krrish)

1. Base URL: `http://localhost:8000`
2. Interactive docs: `http://localhost:8000/docs`
3. Start with `GET /health` to verify backend is up
4. Demo event trigger: `POST /events` with `{"customer_id": "CUST001", "event_type": "salary_credit", "amount": 55000, "source": "manual"}`
5. Grant consent first for personalization: `POST /consent/CUST001/grant` with `{"personalized_recommendations": true, "memory_storage": true}`
6. MPIN for demo customers: `1234` (configurable in `database/customers.json`)
