"""
SAARTHI AI — JSON Repository
Flat-file persistence layer for the hackathon scope.

All database I/O goes through this module.
To swap for a real DB later: replace these functions with SQLAlchemy/Motor
equivalents — zero changes needed in services/ or routes/.

Files live under DATABASE_DIR (default: ./database/).
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────
DATABASE_DIR = Path(os.getenv("DATABASE_DIR", "./database"))

# Canonical file names
_FILES = {
    "customers": DATABASE_DIR / "customers.json",
    "transactions": DATABASE_DIR / "transactions.json",
    "products": DATABASE_DIR / "products.json",
    "consent_records": DATABASE_DIR / "consent_records.json",
    "audit_logs": DATABASE_DIR / "audit_logs.json",
    "events": DATABASE_DIR / "events.json",
    "personas": DATABASE_DIR / "personas.json",
}


# ── Low-level helpers ──────────────────────────────────────────────────────

def _load(collection: str) -> list[dict[str, Any]]:
    """Read all records from a JSON collection file."""
    path = _FILES.get(collection)
    if path is None:
        raise ValueError(f"Unknown collection: '{collection}'. Valid: {list(_FILES)}")
    if not path.exists():
        logger.warning("collection_file_missing", collection=collection, path=str(path))
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Support both {"collection": [...]} and plain [...]
    if isinstance(data, dict):
        return data.get(collection, [])
    return data


def _save(collection: str, records: list[dict[str, Any]]) -> None:
    """Write all records back to a JSON collection file."""
    path = _FILES.get(collection)
    if path is None:
        raise ValueError(f"Unknown collection: '{collection}'")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({collection: records}, f, indent=2, default=str)
    logger.debug("collection_saved", collection=collection, count=len(records))


# ── Public API ─────────────────────────────────────────────────────────────

def read_all(collection: str) -> list[dict[str, Any]]:
    """Return all records in a collection."""
    return _load(collection)


def find_by_id(collection: str, id_field: str, id_value: str) -> dict[str, Any] | None:
    """Find a single record by its ID field. Returns None if not found."""
    records = _load(collection)
    for record in records:
        if record.get(id_field) == id_value:
            return record
    return None


def find_by_field(
    collection: str, field: str, value: Any
) -> list[dict[str, Any]]:
    """Return all records where field == value."""
    records = _load(collection)
    return [r for r in records if r.get(field) == value]


def find_one_by_field(
    collection: str, field: str, value: Any
) -> dict[str, Any] | None:
    """Return the first record where field == value, or None."""
    results = find_by_field(collection, field, value)
    return results[0] if results else None


def insert(collection: str, record: dict[str, Any]) -> dict[str, Any]:
    """
    Append a new record to a collection.
    Automatically adds 'created_at' and 'updated_at' if absent.
    """
    now = datetime.now(timezone.utc).isoformat()
    if "created_at" not in record:
        record["created_at"] = now
    if "updated_at" not in record:
        record["updated_at"] = now

    records = _load(collection)
    records.append(record)
    _save(collection, records)
    logger.info("record_inserted", collection=collection, record_id=record.get(f"{collection[:-1]}_id"))
    return record


def upsert(
    collection: str,
    id_field: str,
    id_value: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Update an existing record by ID, or insert if not found.
    Always updates 'updated_at'.
    """
    records = _load(collection)
    now = datetime.now(timezone.utc).isoformat()
    updates["updated_at"] = now

    for i, record in enumerate(records):
        if record.get(id_field) == id_value:
            records[i] = {**record, **updates}
            _save(collection, records)
            logger.info("record_updated", collection=collection, id=id_value)
            return records[i]

    # Not found — insert
    new_record = {id_field: id_value, **updates, "created_at": now}
    records.append(new_record)
    _save(collection, records)
    logger.info("record_inserted_via_upsert", collection=collection, id=id_value)
    return new_record


def delete_by_id(collection: str, id_field: str, id_value: str) -> bool:
    """Delete a record by ID. Returns True if deleted, False if not found."""
    records = _load(collection)
    new_records = [r for r in records if r.get(id_field) != id_value]
    if len(new_records) == len(records):
        return False
    _save(collection, new_records)
    logger.info("record_deleted", collection=collection, id=id_value)
    return True


def append_record(collection: str, record: dict[str, Any]) -> dict[str, Any]:
    """
    Alias for insert() — semantically clearer for audit logs and events
    where we always append and never update.
    """
    return insert(collection, record)


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix, e.g., 'REC-<uuid4_short>'."""
    short_uuid = uuid.uuid4().hex[:12].upper()
    return f"{prefix}{short_uuid}" if prefix else short_uuid
