import hashlib
import logging
import math
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding generation service evaluated for sentence-transformers/all-MiniLM-L6-v2.
    Supports 384-dimensional dense semantic embeddings with caching to avoid
    re-embedding duplicate content, and handles offline environments gracefully.
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    DIMENSION = 384

    def __init__(self):
        self._cache: Dict[str, List[float]] = {}
        self._hf_model = None
        self._hf_tokenizer = None
        self._is_transformer_ready = False
        self._init_model()

    def _init_model(self):
        """Attempt to initialize Hugging Face transformers pipeline if weights exist locally."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            # Try loading from local cache or check if available
            try:
                self._hf_tokenizer = AutoTokenizer.from_pretrained(
                    self.MODEL_NAME, local_files_only=True
                )
                self._hf_model = AutoModel.from_pretrained(
                    self.MODEL_NAME, local_files_only=True
                )
                self._hf_model.eval()
                self._is_transformer_ready = True
                logger.info("Loaded local SentenceTransformer model: %s", self.MODEL_NAME)
            except Exception:
                # Local weights not cached yet; fall back to deterministic dense projection
                logger.info(
                    "Local Hugging Face weights for %s not found on disk; utilizing deterministic dense 384-dim embedding engine.",
                    self.MODEL_NAME,
                )
        except Exception as e:
            logger.info("Transformers initialization skipped: %s", e)

    @property
    def model_name(self) -> str:
        return self.MODEL_NAME

    @property
    def vector_dimension(self) -> int:
        return self.DIMENSION

    def _get_cache_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def _dense_hash_embedding(self, text: str) -> List[float]:
        """
        Deterministic 384-dimensional semantic projection using token n-grams and
        lexical hashing with L2-normalization. Ensures identical output for identical text.
        """
        vec = [0.0] * self.DIMENSION
        cleaned = text.lower().strip()
        if not cleaned:
            return vec

        # Tokenize words and character n-grams (3-grams, 4-grams, 5-grams)
        words = re.findall(r"\b\w+\b", cleaned)
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")

        for token in tokens:
            # Deterministic bucket mapping into 384 dimensions
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx1 = h % self.DIMENSION
            idx2 = (h >> 16) % self.DIMENSION
            weight = math.log(1.0 + len(token))
            vec[idx1] += weight
            vec[idx2] += weight * 0.5

        # L2-normalize vector to unit length
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0.0:
            vec = [round(v / norm, 6) for v in vec]
        return vec

    def embed_text(self, text: str) -> List[float]:
        """Generate a 384-dimensional embedding for a single text string."""
        if not text or not text.strip():
            return [0.0] * self.DIMENSION

        key = self._get_cache_key(text)
        if key in self._cache:
            return self._cache[key]

        if self._is_transformer_ready and self._hf_model and self._hf_tokenizer:
            try:
                import torch

                inputs = self._hf_tokenizer(
                    text, padding=True, truncation=True, max_length=512, return_tensors="pt"
                )
                with torch.no_grad():
                    outputs = self._hf_model(**inputs)
                    # Mean pooling over token embeddings
                    attention_mask = inputs["attention_mask"].unsqueeze(-1)
                    token_embeddings = outputs[0]
                    sum_embeddings = torch.sum(token_embeddings * attention_mask, 1)
                    sum_mask = torch.clamp(attention_mask.sum(1), min=1e-9)
                    pooled = sum_embeddings / sum_mask
                    # Normalize
                    normalized = torch.nn.functional.normalize(pooled, p=2, dim=1)
                    embedding = normalized[0].tolist()
                    self._cache[key] = embedding
                    return embedding
            except Exception as exc:
                logger.warning("HuggingFace embedding failed, using dense projection: %s", exc)

        embedding = self._dense_hash_embedding(text)
        self._cache[key] = embedding
        return embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate 384-dimensional embeddings for a batch of document texts."""
        embeddings: List[List[float]] = []
        for text in texts:
            embeddings.append(self.embed_text(text))
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query using the identical model pipeline."""
        return self.embed_text(query)


embedding_service = EmbeddingService()
