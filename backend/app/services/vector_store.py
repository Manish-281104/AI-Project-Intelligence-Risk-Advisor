import json
import logging
import math
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from app.core.config import settings, BASE_DIR
from app.schemas.project import DocumentChunk
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class PersistentVectorStore:
    """
    Unified vector database supporting ChromaDB persistence semantics.
    Stores document chunk embeddings, maintains metadata coordinates (page, row, chunk_id),
    prevents duplicate entries, supports document-filtered and cross-document similarity search,
    and persists across backend restarts.
    """

    COLLECTION_NAME = "project_knowledge_base"

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (BASE_DIR / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.data_dir / "vector_store.json"
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load stored vectors and metadata from persistent storage."""
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text(encoding="utf-8"))
                self._entries = data.get("entries", {})
                logger.info(
                    "Loaded %d vector entries from %s", len(self._entries), self.index_file.name
                )
            except Exception as e:
                logger.warning("Failed to load vector store from disk: %s", e)
                self._entries = {}

    def _save_to_disk(self) -> None:
        """Persist vector entries to disk."""
        try:
            payload = {
                "collection": self.COLLECTION_NAME,
                "embedding_model": embedding_service.model_name,
                "dimension": embedding_service.vector_dimension,
                "entry_count": len(self._entries),
                "entries": self._entries,
            }
            self.index_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to save vector store to disk: %s", e)

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Embed and index document chunks with source coordinates.
        Avoids redundant embeddings if chunks already exist.
        """
        if not chunks:
            return 0

        added = 0
        for chunk in chunks:
            chunk_id = chunk.chunk_id
            existing = self._entries.get(chunk_id)

            # If already embedded with same text, update metadata and continue
            if existing and existing.get("text") == chunk.text and existing.get("embedding"):
                existing["metadata"] = chunk.model_dump()
                continue

            # Generate embedding
            embedding = embedding_service.embed_text(chunk.text)
            proj_id = getattr(chunk, "project_id", "proj_workspace_default") or "proj_workspace_default"

            self._entries[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": chunk.document_id,
                "project_id": proj_id,
                "text": chunk.text,
                "embedding": embedding,
                "metadata": chunk.model_dump(),
            }
            added += 1

        self._save_to_disk()
        return added

    def delete_document(self, document_id: str) -> int:
        """Remove all chunks associated with a specific document from vector index."""
        to_remove = [
            cid for cid, item in self._entries.items() if item.get("document_id") == document_id
        ]
        for cid in to_remove:
            del self._entries[cid]

        if to_remove:
            self._save_to_disk()
        return len(to_remove)

    def clear(self) -> None:
        """Clear all entries in vector store."""
        self._entries = {}
        self._save_to_disk()

    def count(self) -> int:
        """Return total indexed vectors."""
        return len(self._entries)

    def get_stats(self) -> Dict[str, Any]:
        """Return vector database collection health and statistics."""
        docs = set(item.get("document_id") for item in self._entries.values())
        projs = set(item.get("project_id", "proj_workspace_default") for item in self._entries.values())
        return {
            "collection_name": self.COLLECTION_NAME,
            "status": "ready",
            "total_chunks": len(self._entries),
            "indexed_documents_count": len(docs),
            "indexed_projects_count": len(projs),
            "embedding_model": embedding_service.model_name,
            "vector_dimension": embedding_service.vector_dimension,
            "storage_path": str(self.index_file),
        }

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two float vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 <= 0.0 or norm2 <= 0.0:
            return 0.0

        sim = dot / (norm1 * norm2)
        return max(-1.0, min(1.0, sim))

    def similarity_search(
        self,
        query: str,
        top_k: int = 6,
        document_id: Optional[str] = None,
        project_id: Optional[str] = None,
        min_score: float = 0.0,
        include_evaluator: bool = False,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Execute vector similarity search for query.
        Supports project scoping (project_id) and document filtering (document_id).
        Returns list of (DocumentChunk, similarity_score) sorted descending by relevance.
        """
        if not self._entries or not query or not query.strip():
            return []

        query_embedding = embedding_service.embed_query(query)
        scored: List[Tuple[DocumentChunk, float]] = []

        for cid, entry in self._entries.items():
            if project_id and entry.get("project_id", "proj_workspace_default") != project_id:
                continue

            if document_id and entry.get("document_id") != document_id:
                continue

            meta = entry.get("metadata", {})
            if not include_evaluator and meta.get("is_evaluator_guidance"):
                continue

            emb = entry.get("embedding")
            if not emb:
                continue

            sim = self._cosine_similarity(query_embedding, emb)

            # Bonus for exact query terms appearing in chunk text
            lower_text = entry.get("text", "").lower()
            lower_q = query.lower()
            if lower_q in lower_text:
                sim += 0.25
            else:
                q_words = [w for w in lower_q.split() if len(w) > 3]
                if q_words:
                    word_hits = sum(1 for w in q_words if w in lower_text)
                    sim += (word_hits / len(q_words)) * 0.15

            if sim >= min_score:
                chunk = DocumentChunk(**entry["metadata"])
                scored.append((chunk, round(sim, 4)))

        # Sort descending by score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


vector_store = PersistentVectorStore()

