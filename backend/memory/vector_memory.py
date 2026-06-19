"""
SAARTHI AI — Vector Long-Term Memory
======================================

Stores and retrieves long-lived customer data using vector similarity:

• **Interaction embeddings** — past queries and responses indexed for
  semantic retrieval so agents can reference relevant prior context.
• **Customer profiles** — structured metadata (persona, preferences,
  account type) stored alongside embedding documents.
• **Product interests** — interest signals extracted from interactions
  for cross-sell / up-sell recommendation flows.

Backend
───────
ChromaDB (local persistent mode) is the default vector store.  The
service is designed behind an abstract interface so Pinecone, Weaviate,
or pgvector can be swapped in via a thin adapter.

Embedding model
───────────────
ChromaDB's default ``all-MiniLM-L6-v2`` sentence-transformer is used.
To use Gemini embeddings, subclass and override ``_embed()``.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

# ─── Logger ─────────────────────────────────────────────────────────────────

logger = logging.getLogger("saarthi.memory.vector_memory")

# ─── Defaults ───────────────────────────────────────────────────────────────

_DEFAULT_PERSIST_DIR: str = "./data/chromadb"
_INTERACTIONS_COLLECTION: str = "saarthi_interactions"
_PROFILES_COLLECTION: str = "saarthi_profiles"
_MAX_SIMILARITY_RESULTS: int = 5


# ─── Service ────────────────────────────────────────────────────────────────


class VectorMemory:
    """
    ChromaDB-backed long-term semantic memory for SAARTHI.

    Parameters
    ----------
    persist_directory : str | None
        Path to the ChromaDB persistence directory.  Falls back to
        ``CHROMA_PERSIST_DIR`` env-var, then ``./data/chromadb``.
    max_results : int
        Maximum number of similarity results returned per query.
    """

    def __init__(
        self,
        persist_directory: str | None = None,
        max_results: int = _MAX_SIMILARITY_RESULTS,
    ) -> None:
        self._persist_dir: str = (
            persist_directory
            or os.getenv("CHROMA_PERSIST_DIR", _DEFAULT_PERSIST_DIR)
        )
        self._max_results: int = max_results

        self._client: chromadb.ClientAPI = chromadb.PersistentClient(
            path=self._persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Ensure collections exist
        self._interactions = self._client.get_or_create_collection(
            name=_INTERACTIONS_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        self._profiles = self._client.get_or_create_collection(
            name=_PROFILES_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            "VectorMemory initialised",
            extra={"persist_dir": self._persist_dir},
        )

    # ── Interaction storage ─────────────────────────────────────────────

    async def store_interaction(
        self,
        customer_id: str,
        query: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Embed and store a query-response pair for future retrieval.

        Parameters
        ----------
        customer_id : str
            Customer identifier used for filtering.
        query : str
            The customer's query text.
        response : str
            The agent's response text.
        metadata : dict[str, Any] | None
            Additional metadata (session_id, agent, intent, etc.).
        """
        doc_id: str = uuid.uuid4().hex
        document: str = f"Query: {query}\nResponse: {response}"

        meta: dict[str, str] = {
            "customer_id": customer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "interaction",
        }
        if metadata:
            for k, v in metadata.items():
                meta[k] = str(v) if not isinstance(v, str) else v

        try:
            self._interactions.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[meta],
            )
            logger.debug(
                "Interaction stored",
                extra={"customer_id": customer_id, "doc_id": doc_id},
            )
        except Exception as exc:
            logger.error(
                "Failed to store interaction in vector memory",
                extra={"customer_id": customer_id, "error": str(exc)},
            )

    async def search_relevant_context(
        self,
        customer_id: str,
        query: str,
    ) -> dict[str, Any]:
        """
        Retrieve the most semantically relevant past interactions.

        Parameters
        ----------
        customer_id : str
            Filter to this customer's interactions only.
        query : str
            The current query used as the similarity anchor.

        Returns
        -------
        dict[str, Any]
            A dictionary with ``"relevant_interactions"`` (list of past
            documents) and ``"relevance_scores"`` (list of floats).
        """
        if not query.strip():
            return {"relevant_interactions": [], "relevance_scores": []}

        try:
            results = self._interactions.query(
                query_texts=[query],
                n_results=self._max_results,
                where={"customer_id": customer_id},
            )

            documents: list[str] = results.get("documents", [[]])[0]
            distances: list[float] = results.get("distances", [[]])[0]

            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score (0-1)
            scores: list[float] = [
                round(max(0.0, 1.0 - d / 2.0), 4) for d in distances
            ]

            return {
                "relevant_interactions": documents,
                "relevance_scores": scores,
            }

        except Exception as exc:
            logger.error(
                "Vector similarity search failed",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return {"relevant_interactions": [], "relevance_scores": []}

    # ── Customer profile ────────────────────────────────────────────────

    async def get_customer_profile(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve the stored customer profile.

        Returns an empty dict if no profile exists yet.
        """
        try:
            results = self._profiles.get(
                ids=[f"profile_{customer_id}"],
                include=["documents", "metadatas"],
            )

            docs = results.get("documents", [])
            if docs and docs[0]:
                return json.loads(docs[0])
            return {}

        except Exception as exc:
            logger.error(
                "Failed to retrieve customer profile",
                extra={"customer_id": customer_id, "error": str(exc)},
            )
            return {}

    async def update_customer_profile(
        self,
        customer_id: str,
        updates: dict[str, Any],
    ) -> None:
        """
        Merge ``updates`` into the existing customer profile document.

        Creates the profile document if it does not exist.
        """
        existing = await self.get_customer_profile(customer_id)
        merged = {**existing, **updates}
        merged["updated_at"] = datetime.now(timezone.utc).isoformat()

        doc_id = f"profile_{customer_id}"
        document = json.dumps(merged, default=str, ensure_ascii=False)

        try:
            self._profiles.upsert(
                ids=[doc_id],
                documents=[document],
                metadatas=[{"customer_id": customer_id, "type": "profile"}],
            )
            logger.info(
                "Customer profile updated",
                extra={
                    "customer_id": customer_id,
                    "updated_keys": list(updates.keys()),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to update customer profile",
                extra={"customer_id": customer_id, "error": str(exc)},
            )

    # ── Product interests ───────────────────────────────────────────────

    async def get_product_interests(
        self,
        customer_id: str,
    ) -> list[str]:
        """
        Retrieve the list of product interest signals for a customer.
        """
        profile = await self.get_customer_profile(customer_id)
        interests = profile.get("product_interests", [])
        if isinstance(interests, list):
            return interests
        return []

    async def add_product_interest(
        self,
        customer_id: str,
        interest: str,
    ) -> None:
        """
        Append a product interest if not already recorded.
        """
        current = await self.get_product_interests(customer_id)
        if interest not in current:
            current.append(interest)
            await self.update_customer_profile(
                customer_id=customer_id,
                updates={"product_interests": current},
            )

    # ── Health check ────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """Report vector store status."""
        try:
            interaction_count = self._interactions.count()
            profile_count = self._profiles.count()
            return {
                "service": "vector_memory",
                "status": "ok",
                "interactions_stored": interaction_count,
                "profiles_stored": profile_count,
            }
        except Exception as exc:
            return {
                "service": "vector_memory",
                "status": "error",
                "error": str(exc),
            }
