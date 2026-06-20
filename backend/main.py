"""
SAARTHI AI — FastAPI Application Entrypoint
Initialises the app, registers all routers, middleware, and startup hooks.

CORS: Configured for Next.js frontend on localhost:3000.
Routers: customer, event, recommendation, auth, voice, consent, audit.
Startup: Redis connection test, JSON DB file validation.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.error_handlers import register_exception_handlers
from backend.utils.logging_config import configure_logging, get_logger

# ── Configure logging before anything else ─────────────────────────────────
configure_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)


# ── Lifespan (startup / shutdown hooks) ───────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: validate database files, test Redis connection, init ChromaDB.
    Shutdown: graceful cleanup.
    """
    logger.info("saarthi_starting", version="1.0.0", env=os.getenv("APP_ENV", "development"))

    # Validate database files
    _validate_database_files()

    # Test Redis (non-blocking — falls back to in-memory if unavailable)
    from backend.memory.redis_memory import redis_memory
    if redis_memory.is_available():
        logger.info("redis_ready")
    else:
        logger.warning("redis_fallback_mode", note="Using in-memory dict for session storage")

    # Init ChromaDB
    from backend.memory.vector_memory import vector_memory
    if vector_memory.is_available():
        logger.info("chromadb_ready")
    else:
        logger.warning("chromadb_unavailable", note="Vector memory disabled")

    logger.info("saarthi_ready", message="🚀 SAARTHI AI Backend is running!")

    yield

    logger.info("saarthi_shutdown")


def _validate_database_files() -> None:
    """Ensure all required database JSON files exist."""
    from pathlib import Path
    db_dir = Path(os.getenv("DATABASE_DIR", "./database"))
    required_files = [
        "customers.json", "transactions.json", "products.json",
        "consent_records.json", "audit_logs.json", "events.json", "personas.json",
    ]
    missing = [f for f in required_files if not (db_dir / f).exists()]
    if missing:
        logger.warning("database_files_missing", missing=missing, db_dir=str(db_dir))
    else:
        logger.info("database_files_ok", db_dir=str(db_dir))


# ── App Initialisation ─────────────────────────────────────────────────────

app = FastAPI(
    title="SAARTHI AI",
    description=(
        "SAARTHI AI — From Banking Access to Banking Success. "
        "Multi-agent banking assistant for SBI with LangGraph orchestration, "
        "human-in-the-loop security, and DPDP-compliant consent management."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────

_allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_allowed_origins = [origin.strip() for origin in _allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Exception Handlers ────────────────────────────────────────────────────

register_exception_handlers(app)


# ── Router Registration ───────────────────────────────────────────────────

from backend.routes import (
    audit,
    auth,
    consent,
    customer,
    event,
    recommendation,
    voice,
)

app.include_router(customer.router, prefix="/customers", tags=["Customers"])
app.include_router(event.router, prefix="/events", tags=["Events"])
app.include_router(recommendation.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(consent.router, prefix="/consent", tags=["Consent"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(voice.router, prefix="/voice", tags=["Voice"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])


# ── Health Check ──────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """System health check — used by load balancers and the dashboard."""
    from backend.memory.redis_memory import redis_memory
    from backend.memory.vector_memory import vector_memory

    return {
        "status": "healthy",
        "service": "SAARTHI AI Backend",
        "version": "1.0.0",
        "components": {
            "redis": "connected" if redis_memory.is_available() else "fallback",
            "chromadb": "connected" if vector_memory.is_available() else "unavailable",
            "database": "json_files",
        },
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "SAARTHI AI — From Banking Access to Banking Success 🏦",
        "docs": "/docs",
        "health": "/health",
    }
