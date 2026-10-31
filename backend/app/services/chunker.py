import re
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.schemas.project import DocumentChunk


class TextChunker:
    """
    Configurable, boundary-aware text chunker for RAG pipeline ingestion.
    Splits document text along natural semantic boundaries (paragraphs, sentences, words)
    while respecting character size and overlap constraints.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        self.chunk_size = chunk_size if chunk_size is not None else getattr(settings, "CHUNK_SIZE", 800)
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else getattr(settings, "CHUNK_OVERLAP", 100)

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalize whitespace, strip non-printable characters, and clean formatting artifacts.
        """
        if not text:
            return ""
        # Replace non-breaking spaces and Windows/Mac newlines
        text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
        # Strip ASCII control characters except \n (10) and \t (9)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # Collapse 3 or more consecutive newlines into 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple spaces or tabs on individual lines
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count for text using word and punctuation tokenization."""
        if not text:
            return 0
        tokens = re.findall(r"\w+|[^\w\s]", text)
        return max(1, len(tokens))

    def split_text_into_segments(self, text: str) -> List[str]:
        """
        Split a cleaned string into text segments of approximately chunk_size characters
        with chunk_overlap characters overlap, seeking sensible boundaries such as
        paragraphs, line breaks, sentence endings, or word breaks.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        if len(cleaned) <= self.chunk_size:
            return [cleaned]

        chunks: List[str] = []
        start = 0
        text_len = len(cleaned)
        separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]

        while start < text_len:
            # If the remainder fits comfortably in one chunk
            if start + self.chunk_size >= text_len:
                chunk = cleaned[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            target_end = start + self.chunk_size

            # Search for a natural boundary in the back portion of the chunk window
            min_split = start + max(self.chunk_overlap + 1, self.chunk_size // 2)
            if min_split >= target_end:
                min_split = start + 1

            split_pos = -1
            for sep in separators:
                pos = cleaned.rfind(sep, min_split, target_end)
                if pos != -1:
                    if sep in (". ", "? ", "! ", "; ", ", "):
                        split_pos = pos + 1  # Retain trailing punctuation mark
                    else:
                        split_pos = pos
                    break

            # Fallback if no separator found in the search window
            if split_pos == -1 or split_pos <= start:
                split_pos = target_end

            chunk = cleaned[start:split_pos].strip()
            if chunk:
                chunks.append(chunk)

            # Calculate start of next chunk with configured overlap
            next_start = split_pos - self.chunk_overlap
            if next_start <= start:
                next_start = start + 1  # Guarantee forward progress

            # Snap next_start forward to a clean word boundary if nearby
            boundary_search = cleaned.find(" ", next_start, min(next_start + 30, split_pos))
            if boundary_search != -1 and boundary_search > start:
                next_start = boundary_search + 1

            start = next_start

        return chunks

    def create_chunks_from_blocks(
        self,
        blocks: List[Dict[str, Any]],
        document_id: str,
        filename: str,
        project_id: str = "proj_workspace_default",
    ) -> List[DocumentChunk]:
        """
        Create a list of DocumentChunk objects from pre-structured document blocks.
        Preserves coordinates (page numbers, row numbers, source references).
        - For page-based blocks (PDF): splits text within each page to preserve exact page references.
        - For row/paragraph-based blocks: accumulates adjacent items up to chunk_size with overlap.
        """
        chunks: List[DocumentChunk] = []
        chunk_counter = 1

        # Check if blocks have page numbers (PDF)
        has_pages = any(b.get("page_number") is not None for b in blocks)

        if has_pages:
            # Group by page number to retain exact page coordinates
            page_dict: Dict[int, List[Dict[str, Any]]] = {}
            for block in blocks:
                page_num = block.get("page_number", 1)
                page_dict.setdefault(page_num, []).append(block)

            for page_num, p_blocks in page_dict.items():
                page_text = "\n\n".join(b.get("text", "") for b in p_blocks).strip()
                if not page_text:
                    continue

                segments = self.split_text_into_segments(page_text)
                for seg in segments:
                    if not seg.strip():
                        continue
                    is_eval = bool(
                        re.search(
                            r"\b(?:Suggested\s+Agent\s+Test\s+Questions|Expected\s+Ground\s+Truth\s+for\s+Evaluator|evaluator\s+reference\s+is\s+included)\b",
                            seg,
                            re.IGNORECASE,
                        )
                    )
                    chunk_id = f"{document_id}_chunk_{chunk_counter:03d}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            project_id=project_id,
                            source=filename,
                            text=seg,
                            page_number=page_num,
                            row_number=None,
                            source_ref=f"Page {page_num}",
                            char_count=len(seg),
                            word_count=len(seg.split()),
                            token_count=self.estimate_tokens(seg),
                            is_evaluator_guidance=is_eval,
                        )
                    )
                    chunk_counter += 1

            return chunks

        # For non-page documents (DOCX, CSV, TXT), group small blocks up to chunk_size with overlap
        current_items: List[Dict[str, Any]] = []
        current_len = 0

        def emit_grouped_chunk(items: List[Dict[str, Any]]) -> None:
            nonlocal chunk_counter
            if not items:
                return
            combined_text = "\n\n".join(item["text"] for item in items).strip()
            if not combined_text:
                return

            first_item = items[0]
            last_item = items[-1]

            row_num = first_item.get("row_number")
            last_row_num = last_item.get("row_number")

            if row_num is not None and last_row_num is not None:
                if row_num == last_row_num:
                    s_ref = f"Row {row_num}"
                else:
                    s_ref = f"Rows {row_num}-{last_row_num}"
            else:
                s_ref = first_item.get("source_ref") or "Document Segment"

            is_eval = any(bool(it.get("is_evaluator_guidance", False)) for it in items) or bool(
                re.search(
                    r"\b(?:Suggested\s+Agent\s+Test\s+Questions|Expected\s+Ground\s+Truth\s+for\s+Evaluator|evaluator\s+reference\s+is\s+included)\b",
                    combined_text,
                    re.IGNORECASE,
                )
            )

            chunk_id = f"{document_id}_chunk_{chunk_counter:03d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    project_id=project_id,
                    source=filename,
                    text=combined_text,
                    page_number=None,
                    row_number=row_num,
                    source_ref=s_ref,
                    char_count=len(combined_text),
                    word_count=len(combined_text.split()),
                    token_count=self.estimate_tokens(combined_text),
                    is_evaluator_guidance=is_eval,
                )
            )
            chunk_counter += 1

        for block in blocks:
            raw_text = block.get("text", "")
            cleaned = self.clean_text(raw_text)
            if not cleaned:
                continue

            # If a single block exceeds chunk_size on its own, flush current and split the oversized block
            if len(cleaned) > self.chunk_size:
                if current_items:
                    emit_grouped_chunk(current_items)
                    current_items = []
                    current_len = 0

                segments = self.split_text_into_segments(cleaned)
                for seg in segments:
                    if not seg.strip():
                        continue
                    is_seg_eval = bool(block.get("is_evaluator_guidance", False)) or bool(
                        re.search(
                            r"\b(?:Suggested\s+Agent\s+Test\s+Questions|Expected\s+Ground\s+Truth\s+for\s+Evaluator|evaluator\s+reference\s+is\s+included)\b",
                            seg,
                            re.IGNORECASE,
                        )
                    )
                    chunk_id = f"{document_id}_chunk_{chunk_counter:03d}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            project_id=project_id,
                            source=filename,
                            text=seg,
                            page_number=block.get("page_number"),
                            row_number=block.get("row_number"),
                            source_ref=block.get("source_ref"),
                            char_count=len(seg),
                            word_count=len(seg.split()),
                            token_count=self.estimate_tokens(seg),
                            is_evaluator_guidance=is_seg_eval,
                        )
                    )
                    chunk_counter += 1
                continue

            # If adding this block exceeds chunk_size, emit current chunk and handle overlap
            if current_items and (current_len + len(cleaned) + 2 > self.chunk_size):
                emit_grouped_chunk(current_items)

                # Overlap: preserve the tail item(s) up to chunk_overlap
                overlap_items: List[Dict[str, Any]] = []
                overlap_len = 0
                for item in reversed(current_items):
                    if overlap_len + len(item["text"]) <= self.chunk_overlap or not overlap_items:
                        overlap_items.insert(0, item)
                        overlap_len += len(item["text"]) + 2
                    else:
                        break

                current_items = list(overlap_items)
                current_len = sum(len(it["text"]) + 2 for it in current_items)

            current_items.append({"text": cleaned, **{k: v for k, v in block.items() if k != "text"}})
            current_len += len(cleaned) + 2

        if current_items:
            emit_grouped_chunk(current_items)

        return chunks


text_chunker = TextChunker()
