import math
import re
from typing import List, Tuple, Optional, Dict, Set
from app.schemas.project import DocumentChunk
from app.services.document_service import document_service
from app.services.vector_store import vector_store


class SemanticRetriever:
    """
    Semantic and lexical hybrid retrieval engine for RAG pipeline.
    Combines dense vector similarity from vector_store with lexical BM25/TF-IDF matching,
    coordinate tracking (page, row, chunk_id), and multi-query domain retrieval.
    """

    STOP_WORDS: Set[str] = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
        "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
        "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
        "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
        "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
        "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
        "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
        "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    }

    def tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text into lowercase word tokens and bigrams."""
        words = re.findall(r"\b[a-zA-Z0-9_\-\.\/]{2,}\b", text.lower())
        tokens = [w for w in words if w not in self.STOP_WORDS]
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        return tokens + bigrams

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute normalized term frequency vector."""
        tf: Dict[str, float] = {}
        if not tokens:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        total = float(len(tokens))
        for t in tf:
            tf[t] /= total
        return tf

    def retrieve(
        self,
        query: str,
        top_k: int = 8,
        document_id: Optional[str] = None,
        project_id: Optional[str] = None,
        min_similarity: float = 0.01,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve top-k most semantically relevant document chunks for the query.
        Uses vector_store dense retrieval blended with lexical TF-IDF cosine ranking,
        scoped to the project workspace.
        """
        target_pid = project_id or document_service.get_workspace().project_id
        chunks = document_service.get_all_chunks(document_id=document_id, project_id=target_pid)
        if not chunks:
            return []

        # 1. Try dense vector similarity from vector store first
        vector_results = vector_store.similarity_search(
            query=query, top_k=top_k * 2, document_id=document_id, project_id=target_pid
        )

        query_tokens = self.tokenize(query)
        if not query_tokens and vector_results:
            return vector_results[:top_k]
        if not query_tokens:
            return [(c, 0.5) for c in chunks[:top_k]]

        # 2. Compute TF-IDF lexical scores for precision
        query_tf = self._compute_tf(query_tokens)
        doc_count = len(chunks)
        df: Dict[str, int] = {}
        chunk_tfs: List[Dict[str, float]] = []

        for c in chunks:
            c_tokens = self.tokenize(c.text)
            c_tf = self._compute_tf(c_tokens)
            chunk_tfs.append(c_tf)
            for term in c_tf:
                df[term] = df.get(term, 0) + 1

        query_vec: Dict[str, float] = {}
        for term, tf_val in query_tf.items():
            idf = math.log((doc_count + 1.0) / (df.get(term, 0) + 1.0)) + 1.0
            query_vec[term] = tf_val * idf

        q_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1.0

        # Build map of vector scores
        vec_score_map = {c.chunk_id: score for c, score in vector_results}

        scored_chunks: List[Tuple[DocumentChunk, float]] = []
        for idx, chunk in enumerate(chunks):
            c_tf = chunk_tfs[idx]
            c_vec: Dict[str, float] = {}
            dot_product = 0.0

            for term, tf_val in c_tf.items():
                idf = math.log((doc_count + 1.0) / (df.get(term, 0) + 1.0)) + 1.0
                weight = tf_val * idf
                c_vec[term] = weight
                if term in query_vec:
                    dot_product += query_vec[term] * weight

            c_norm = math.sqrt(sum(v * v for v in c_vec.values())) or 1.0
            lexical_sim = dot_product / (q_norm * c_norm)

            # Bonus for exact query phrase in chunk
            lower_chunk = chunk.text.lower()
            if query.lower() in lower_chunk:
                lexical_sim += 0.35
            else:
                for q_word in query.lower().split():
                    if len(q_word) > 3 and q_word in lower_chunk:
                        lexical_sim += 0.05

            # Combine dense vector score and lexical score (hybrid score)
            dense_sim = vec_score_map.get(chunk.chunk_id, 0.0)
            hybrid_score = round(0.55 * dense_sim + 0.45 * lexical_sim, 4)

            if hybrid_score >= min_similarity:
                scored_chunks.append((chunk, hybrid_score))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        if not scored_chunks:
            return [(c, 0.1) for c in chunks[:top_k]]

        return scored_chunks[:top_k]

    def retrieve_multi(
        self,
        queries: List[str],
        top_k: int = 14,
        document_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Execute multiple targeted domain queries, merge chunk results, deduplicate,
        and return the consolidated most relevant evidence within the project workspace.
        """
        target_pid = project_id or document_service.get_workspace().project_id
        chunk_score_map: Dict[str, Tuple[DocumentChunk, float]] = {}

        for q in queries:
            results = self.retrieve(
                query=q, top_k=top_k, document_id=document_id, project_id=target_pid
            )
            for chunk, score in results:
                cid = chunk.chunk_id
                if cid not in chunk_score_map or score > chunk_score_map[cid][1]:
                    chunk_score_map[cid] = (chunk, score)

        merged = list(chunk_score_map.values())
        merged.sort(key=lambda x: x[1], reverse=True)

        if not merged:
            chunks = document_service.get_all_chunks(
                document_id=document_id, project_id=target_pid
            )
            return [(c, 0.1) for c in chunks[:top_k]]

        return merged[:top_k]

    def format_context_for_prompt(self, scored_chunks: List[Tuple[DocumentChunk, float]]) -> str:
        """
        Format retrieved chunks into a structured prompt context block
        retaining coordinate citations (Page, Row, Chunk ID).
        """
        if not scored_chunks:
            return "No relevant document passages were retrieved."

        lines: List[str] = []
        for i, (chunk, score) in enumerate(scored_chunks, 1):
            ref = chunk.source_ref or f"Chunk #{chunk.chunk_id}"
            coord_details = []
            if chunk.page_number is not None:
                coord_details.append(f"Page {chunk.page_number}")
            if chunk.row_number is not None:
                coord_details.append(f"Row {chunk.row_number}")
            coord_str = ", ".join(coord_details) if coord_details else ref

            lines.append(
                f"--- [Passage {i}] Source: '{chunk.source}' | Ref: {coord_str} | ID: {chunk.chunk_id} (Relevance: {score:.2f}) ---"
            )
            lines.append(chunk.text.strip())
            lines.append("")

        return "\n".join(lines).strip()


semantic_retriever = SemanticRetriever()
