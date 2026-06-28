"""
SAARTHI AI — Vector Memory
ChromaDB wrapper for long-term semantic memory.
Stores customer interaction summaries as embeddings for context-aware conversations.

Used by: customer_memory.py, saathi_agent.py (spending pattern lookups)
"""
from __future__ import annotations

import os
from typing import Any, Optional

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "saarthi_customer_memory")


class VectorMemory:
    """
    ChromaDB-backed vector store for semantic search over customer history.
    Falls back gracefully if ChromaDB is unavailable.
    """

    def __init__(self):
        self._client = None
        self._collection = None
        self._available = False
        self._init()

    def _init(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            self._available = True
            logger.info(
                "chroma_connected",
                persist_dir=_PERSIST_DIR,
                collection=_COLLECTION_NAME,
            )
        except Exception as e:
            logger.warning(
                "chroma_unavailable",
                error=str(e),
                note="Vector memory disabled — agents will use Redis context only",
            )

    def store_interaction(
        self,
        customer_id: str,
        interaction_text: str,
        metadata: Optional[dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> None:
        """Store an interaction summary as a vector embedding."""
        if not self._available or not self._collection:
            return

        import uuid
        doc_id = doc_id or str(uuid.uuid4())
        meta = {"customer_id": customer_id, **(metadata or {})}

        try:
            self._collection.upsert(
                ids=[doc_id],
                documents=[interaction_text],
                metadatas=[meta],
            )
            logger.debug("vector_stored", customer_id=customer_id, doc_id=doc_id)
        except Exception as e:
            logger.error("vector_store_error", error=str(e), customer_id=customer_id)

    def search_similar(
        self,
        customer_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Semantic search for past interactions similar to the query.
        Returns top_k results with text and metadata.
        """
        if not self._available or not self._collection:
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"customer_id": {"$eq": customer_id}},
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [
                {"text": doc, "metadata": meta}
                for doc, meta in zip(docs, metas)
            ]
        except Exception as e:
            logger.error("vector_search_error", error=str(e), customer_id=customer_id)
            return []

    def is_available(self) -> bool:
        return self._available


# ── Singleton ───────────────────────────────────────────────────────────────
vector_memory = VectorMemory()
