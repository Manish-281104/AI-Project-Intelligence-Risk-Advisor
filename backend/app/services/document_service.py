import json
import logging
import csv
import io
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings
from app.schemas.project import DocumentMetadata, DocumentChunk, ProjectWorkspace
from app.services.chunker import text_chunker, TextChunker
from app.services.vector_store import vector_store
from app.services.ocr_service import ocr_service



class DocumentService:
    """Service handling document validation, storage, text extraction, and semantic chunking."""

    def __init__(
        self,
        upload_dir: Path | None = None,
        chunker: TextChunker | None = None,
        data_dir: Path | None = None,
    ):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.chunker = chunker or text_chunker
        self.data_dir = data_dir or (self.upload_dir.parent / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.data_dir / "documents_registry.json"
        self.workspace_file = self.data_dir / "project_workspace.json"
        self._documents: Dict[str, DocumentMetadata] = {}
        self._workspace: ProjectWorkspace = self._load_workspace()
        self._load_registry()

    def _load_workspace(self) -> ProjectWorkspace:
        """Load or initialize single persistent project workspace."""
        if self.workspace_file.exists():
            try:
                data = json.loads(self.workspace_file.read_text(encoding="utf-8"))
                return ProjectWorkspace(**data)
            except Exception as e:
                logging.warning(f"Failed to load project workspace: {e}")

        now = datetime.now(timezone.utc).isoformat()
        ws = ProjectWorkspace(
            project_id="proj_workspace_default",
            project_name=None,
            client=None,
            description=None,
            created_at=now,
            updated_at=now,
            document_ids=[],
            document_count=0,
        )
        self._save_workspace(ws)
        return ws

    def _save_workspace(self, ws: Optional[ProjectWorkspace] = None) -> None:
        """Persist project workspace metadata to disk."""
        if ws:
            self._workspace = ws
        try:
            self._workspace.updated_at = datetime.now(timezone.utc).isoformat()
            self._workspace.document_count = len(self._workspace.document_ids)
            self.workspace_file.write_text(
                json.dumps(self._workspace.model_dump(), indent=2), encoding="utf-8"
            )
        except Exception as e:
            logging.warning(f"Failed to save project workspace: {e}")

    def get_workspace(self) -> ProjectWorkspace:
        """Return current project workspace metadata."""
        self._workspace.document_count = len(self._documents)
        self._workspace.document_ids = list(self._documents.keys())
        return self._workspace

    def reset_workspace(self) -> ProjectWorkspace:
        """Reset project workspace and delete all stored documents and vectors."""
        for doc_id in list(self._documents.keys()):
            self.delete_document(doc_id)
        now = datetime.now(timezone.utc).isoformat()
        self._workspace = ProjectWorkspace(
            project_id="proj_workspace_default",
            project_name=None,
            client=None,
            description=None,
            created_at=now,
            updated_at=now,
            document_ids=[],
            document_count=0,
        )
        self._save_workspace()
        vector_store.clear()
        return self._workspace

    def start_new_workspace(
        self, project_id: Optional[str] = None, project_name: Optional[str] = None
    ) -> ProjectWorkspace:
        """
        Start a new, isolated project workspace.
        Creates a new persistent project ID, archives previous workspace data,
        clears active workspace documents, and resets active vector store chunks.
        """
        # Archive current workspace if it has documents
        if self._workspace.document_count > 0:
            archive_file = self.data_dir / "workspaces_archive.json"
            archive = {}
            if archive_file.exists():
                try:
                    archive = json.loads(archive_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            archive[self._workspace.project_id] = {
                "workspace": self._workspace.model_dump(),
                "documents": {did: self._documents[did].model_dump() for did in self._workspace.document_ids if did in self._documents},
            }
            try:
                archive_file.write_text(json.dumps(archive, indent=2), encoding="utf-8")
            except Exception as e:
                logging.warning(f"Failed to archive workspace: {e}")

        # Clear active documents
        self._documents.clear()
        self._save_registry()
        vector_store.clear()

        now = datetime.now(timezone.utc).isoformat()
        new_pid = project_id or f"proj_{uuid.uuid4().hex[:8]}"
        self._workspace = ProjectWorkspace(
            project_id=new_pid,
            project_name=project_name,
            client=None,
            description=None,
            created_at=now,
            updated_at=now,
            document_ids=[],
            document_count=0,
        )
        self._save_workspace()
        return self._workspace


    def _load_registry(self) -> None:
        """Load document metadata registry from disk if it exists."""
        if self.registry_file.exists():
            try:
                data = json.loads(self.registry_file.read_text(encoding="utf-8"))
                for doc_id, doc_dict in data.items():
                    doc_meta = DocumentMetadata(**doc_dict)
                    self._documents[doc_id] = doc_meta
                    vector_store.add_chunks(doc_meta.chunks)
                self._workspace.document_ids = list(self._documents.keys())
                self._workspace.document_count = len(self._documents)
            except Exception as e:
                logging.warning(f"Failed to load document registry: {e}")

    def _save_registry(self) -> None:
        """Persist document metadata registry to disk."""
        try:
            data = {doc_id: doc.model_dump() for doc_id, doc in self._documents.items()}
            self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logging.warning(f"Failed to save document registry: {e}")

    def list_documents(self) -> List[DocumentMetadata]:
        """Return list of all ingested documents."""
        return list(self._documents.values())

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieve document metadata by document ID."""
        return self._documents.get(document_id)

    def delete_document(self, document_id: str) -> bool:
        """Remove a document from registry, storage, and project workspace."""
        if document_id in self._documents:
            del self._documents[document_id]
            self._save_registry()
            vector_store.delete_document(document_id)
            if document_id in self._workspace.document_ids:
                self._workspace.document_ids.remove(document_id)
            if len(self._documents) == 0:
                self._workspace.project_name = None
                self._workspace.client = None
                self._workspace.project_id = "proj_workspace_default"
                self._workspace.document_ids = []
            self._save_workspace()
            for p in self.upload_dir.glob(f"{document_id}_*"):
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass
            return True
        return False

    def get_all_chunks(
        self,
        document_id: Optional[str] = None,
        project_id: Optional[str] = None,
        include_evaluator: bool = False,
    ) -> List[DocumentChunk]:
        """Return chunks for a specific document or workspace project, excluding evaluator test guides by default."""
        target_pid = project_id or self._workspace.project_id
        raw_chunks: List[DocumentChunk] = []
        if document_id:
            doc = self.get_document(document_id)
            if not doc:
                return []
            if project_id and doc.project_id != target_pid:
                return []
            raw_chunks = doc.chunks
        else:
            for doc in self._documents.values():
                if not project_id or doc.project_id == target_pid:
                    raw_chunks.extend(doc.chunks)

        if not include_evaluator:
            return [c for c in raw_chunks if not getattr(c, "is_evaluator_guidance", False)]
        return raw_chunks

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize project name or client for relaxed comparison."""
        clean = re.sub(r"[^\w\s]", "", name.lower())
        return " ".join(clean.split())

    @classmethod
    def _are_names_compatible(cls, n1: str, n2: str) -> bool:
        """Check if two project names or client names are compatible."""
        norm1 = cls._normalize_name(n1)
        norm2 = cls._normalize_name(n2)
        if not norm1 or not norm2:
            return True
        if norm1 == norm2 or norm1 in norm2 or norm2 in norm1:
            return True
        # Check abbreviation / acronym: e.g. "cemp" in "campus event management portal"
        words1 = [w for w in norm1.split() if w]
        words2 = [w for w in norm2.split() if w]
        if words1 and norm2 == "".join(w[0] for w in words1):
            return True
        if words2 and norm1 == "".join(w[0] for w in words2):
            return True
        return False

    def extract_project_identity(self, text: str, filename: str) -> Dict[str, Optional[str]]:
        """
        Extract explicit project name, project ID, and client/sponsor from document text and filename.
        """
        found_name: Optional[str] = None
        found_id: Optional[str] = None
        found_client: Optional[str] = None

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # 1. Project ID (must be formatted as key: value, supporting table row format)
        id_match = re.search(
            r"(?:^|\n|\|)\s*(?:Project\s*field\s*:\s*)?(?:Project\s*ID|Project-ID|Proj\s*ID)(?:\s*\|\s*Value)?\s*[:=\|]\s*([A-Za-z0-9\-_]+)",
            text,
            re.IGNORECASE,
        )
        if id_match:
            cand_id = id_match.group(1).strip()
            if cand_id.lower() not in ("tbd", "unknown", "none"):
                found_id = cand_id

        # 2. Client / Sponsor (must be formatted as key: value, supporting table row format)
        client_match = re.search(
            r"(?:^|\n|\|)\s*(?:Project\s*field\s*:\s*)?(?:Project\s*Sponsor|Client|Customer|Sponsor)(?:\s*\|\s*Value)?\s*[:=\|]\s*([^\n\r\|]+)",
            text,
            re.IGNORECASE,
        )
        if client_match:
            cand_client = client_match.group(1).strip(" .-_|")
            # Ensure not a narrative statement like "The sponsor has not confirmed..."
            is_narrative = bool(
                re.search(r"\b(has|have|had|not|will|is|was|confirmed|required|agreed|discussed|open question)\b", cand_client, re.IGNORECASE)
            )
            if cand_client and len(cand_client) > 2 and not is_narrative and cand_client.lower() not in ("tbd", "unknown", "none"):
                found_client = cand_client

        # 3. Project Name (must be formatted as key: value, supporting table row format)
        name_match = re.search(
            r"(?:^|\n|\|)\s*(?:Project\s*field\s*:\s*)?(?:Project\s*Name|System\s*Name|Project\s*Title)(?:\s*\|\s*Value)?\s*[:=\|]\s*([^\n\r\|]+)",
            text,
            re.IGNORECASE,
        )
        if name_match:
            cand_name = name_match.group(1).strip(" .-_|")
            if cand_name and len(cand_name) > 3 and cand_name.lower() not in ("tbd", "unknown", "none"):
                found_name = cand_name

        # If not found via key-value, check early lines (headers / title)
        if not found_name:
            for line in lines[:8]:
                clean_l = re.sub(r"^#+\s*", "", line).strip()
                if re.match(r"^(?:Sample\s+Project\s+Test\s+Document|Test\s+Fixture|Table\s+\d+|ID\s*\|)", clean_l, re.IGNORECASE):
                    continue
                if re.search(r"\b(?:Portal|System|Platform|Application|Manager|Dashboard|Tool)\b", clean_l, re.IGNORECASE):
                    if len(clean_l) < 80 and not re.search(r"Overview|Section|Chapter|Table|Status", clean_l, re.IGNORECASE):
                        # Strip document type suffixes like "- Meeting Notes", "- Progress Update"
                        clean_l = re.sub(r"\s*-\s*(?:Meeting\s+Notes|Progress\s+Update|Status\s+Report|SRS|Requirements).*", "", clean_l, flags=re.IGNORECASE).strip()
                        found_name = clean_l
                        break

        # Check filename if it explicitly designates a distinct project
        fn_base = Path(filename).stem
        clean_fn = re.sub(r"[_\-]+", " ", fn_base).strip()
        is_generic_fn = bool(
            re.search(
                r"^(?:meeting[-_ ]notes|sprint[-_ ]tasks|progress[-_ ]update|requirements|architecture|sync[-_ ]notes|charter|document|sample|spec|test|notes|charter[-_ ]single)",
                clean_fn,
                re.IGNORECASE,
            )
        )
        if not found_name and not is_generic_fn and len(clean_fn) > 3:
            if re.search(
                r"\b(?:Portal|System|Platform|Application|Manager|Dashboard|Tool|App|Project|Service|Engine|Tracker|ICU|Hospital|Flight|Banking|Ecommerce|Inventory|Hotel|Library|Lab|Analytics)\b",
                clean_fn,
                re.IGNORECASE,
            ):
                found_name = clean_fn


        return {
            "project_name": found_name,
            "project_id": found_id,
            "client": found_client,
        }

    def validate_project_consistency(
        self, text: str, filename: str
    ) -> Tuple[str, Optional[str], Optional[str], bool]:
        """
        Compare extracted document identifiers against existing workspace project info.
        Raises HTTPException(409) if document explicitly conflicts with workspace project.
        Returns (project_id, project_name, client, is_inherited).
        """
        extracted = self.extract_project_identity(text, filename)
        ext_name = extracted["project_name"]
        ext_id = extracted["project_id"]
        ext_client = extracted["client"]

        ws = self._workspace

        # If workspace currently has 0 documents, adopt new document identity without conflict
        if len(self._documents) == 0:
            ws.project_name = ext_name
            ws.client = ext_client
            if ext_id:
                ws.project_id = ext_id
            self._save_workspace(ws)
            return (
                ws.project_id,
                ws.project_name,
                ws.client,
                ext_name is None and ext_id is None and ext_client is None,
            )

        conflicts = []
        # Check Project ID Conflict
        if ext_id and ws.project_id != "proj_workspace_default" and ext_id != ws.project_id:
            conflicts.append(f"Project ID '{ext_id}' which conflicts with workspace Project ID '{ws.project_id}'")

        # Check Project Name Conflict
        if ext_name and ws.project_name:
            if not self._are_names_compatible(ext_name, ws.project_name):
                conflicts.append(f"project '{ext_name}' which conflicts with workspace project '{ws.project_name}'")

        # Check Client / Sponsor Conflict
        if ext_client and ws.client:
            if not self._are_names_compatible(ext_client, ws.client):
                conflicts.append(f"client/sponsor '{ext_client}' which conflicts with workspace client '{ws.client}'")

        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Project identity conflict: Document '{filename}' explicitly identifies "
                    + "; ".join(conflicts)
                    + ". All documents in this workspace must belong to the same project."
                ),
            )

        # If document has no explicit identity, it inherits the workspace's identity
        is_inherited = False
        if not ext_name and not ext_id and not ext_client:
            is_inherited = True

        # If workspace project name or client was not yet established, adopt them from this document
        updated = False
        if ext_name and not ws.project_name:
            ws.project_name = ext_name
            updated = True
        if ext_client and not ws.client:
            ws.client = ext_client
            updated = True
        if ext_id and ws.project_id == "proj_workspace_default":
            ws.project_id = ext_id
            updated = True

        if updated:
            self._save_workspace(ws)

        return (ws.project_id, ws.project_name, ws.client, is_inherited)



    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal or invalid characters."""
        base_name = Path(filename).name
        clean_name = re.sub(r"[^\w\-.]", "_", base_name)
        return clean_name or "uploaded_document"

    def validate_file_basics(self, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Validate file extension, emptiness, and file size limits.
        Returns (sanitized_filename, extension).
        """
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing or empty.",
            )

        sanitized = self.sanitize_filename(filename)
        ext = Path(sanitized).suffix.lower()

        if ext not in settings.ALLOWED_EXTENSIONS:
            allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats are: {allowed}.",
            )

        file_size = len(content)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty (0 bytes). Please upload a valid document.",
            )

        if file_size > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed limit "
                    f"of {settings.MAX_FILE_SIZE_MB} MB."
                ),
            )

        return sanitized, ext

    def parse_pdf(self, content: bytes) -> Dict[str, Any]:
        """Extract text and metadata from PDF bytes using PyMuPDF with OCR fallback."""
        if not content.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed PDF: File header does not match valid PDF signature.",
            )

        try:
            import pymupdf  # PyMuPDF
        except ImportError:
            try:
                import fitz as pymupdf
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="PyMuPDF library is not installed on backend.",
                )

        try:
            doc = pymupdf.open(stream=content, filetype="pdf")
            page_count = len(doc)
            blocks: List[Dict[str, Any]] = []
            pages_text: List[str] = []

            for page_index in range(page_count):
                page = doc[page_index]
                text = page.get_text() or ""
                cleaned_page = self.chunker.clean_text(text)

                # Check character quality: if page has >= 25 characters, keep direct text
                if len(cleaned_page.strip()) >= 25:
                    blocks.append({
                        "text": cleaned_page,
                        "page_number": page_index + 1,
                        "row_number": None,
                        "source_ref": f"Page {page_index + 1}",
                        "is_ocr": False,
                    })
                    pages_text.append(cleaned_page)
                else:
                    # Page has minimal or no direct text character layer: attempt OCR fallback
                    ocr_extracted = ""
                    if ocr_service.is_available():
                        try:
                            pix = page.get_pixmap(dpi=200)
                            img = Image.open(io.BytesIO(pix.tobytes("png")))
                            if not ocr_service.is_image_blank(img):
                                raw_ocr, _ = ocr_service.extract_text_from_image(img)
                                ocr_extracted = self.chunker.clean_text(raw_ocr)
                        except Exception as e:
                            logging.warning(f"OCR fallback failed on page {page_index + 1}: {e}")

                    # Prefer OCR result if it extracted readable characters
                    if len(ocr_extracted.strip()) > len(cleaned_page.strip()):
                        blocks.append({
                            "text": ocr_extracted,
                            "page_number": page_index + 1,
                            "row_number": None,
                            "source_ref": f"Page {page_index + 1} (OCR)",
                            "is_ocr": True,
                        })
                        pages_text.append(ocr_extracted)
                    elif cleaned_page.strip():
                        # Keep whatever direct text was present
                        blocks.append({
                            "text": cleaned_page,
                            "page_number": page_index + 1,
                            "row_number": None,
                            "source_ref": f"Page {page_index + 1}",
                            "is_ocr": False,
                        })
                        pages_text.append(cleaned_page)

            full_text = "\n\n".join(pages_text).strip()
            doc.close()

            return {
                "page_count": page_count,
                "paragraph_count": None,
                "row_count": None,
                "column_count": None,
                "columns": None,
                "blocks": blocks,
                "full_text": full_text,
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF document. It may be encrypted or corrupted: {str(exc)}",
            )

    def parse_docx(self, content: bytes) -> Dict[str, Any]:
        """Extract text and metadata from DOCX bytes using python-docx."""
        if not content.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed DOCX: File does not match valid Microsoft Word XML package format.",
            )

        try:
            import docx
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="python-docx library is not installed on backend.",
            )

        try:
            file_stream = io.BytesIO(content)
            doc = docx.Document(file_stream)

            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            blocks: List[Dict[str, Any]] = []

            eval_active = False
            for p_idx, p_text in enumerate(paragraphs, 1):
                cleaned = self.chunker.clean_text(p_text)
                if not cleaned:
                    continue
                if re.search(r"^(?:12\.\s*Suggested\s+Agent\s+Test\s+Questions|13\.\s*Expected\s+Ground\s+Truth|Suggested\s+Agent\s+Test\s+Questions|Expected\s+Ground\s+Truth)", cleaned, re.IGNORECASE):
                    eval_active = True
                is_eval = eval_active or bool(
                    re.search(
                        r"\b(?:Suggested\s+Agent\s+Test\s+Questions|Expected\s+Ground\s+Truth\s+for\s+Evaluator|evaluator\s+reference\s+is\s+included)\b",
                        cleaned,
                        re.IGNORECASE,
                    )
                )
                blocks.append({
                    "text": cleaned,
                    "page_number": None,
                    "row_number": p_idx,
                    "source_ref": f"Paragraph {p_idx}",
                    "is_evaluator_guidance": is_eval,
                })

            # Also extract table cells text with header awareness
            table_row_count = 0
            for t_idx, table in enumerate(doc.tables, 1):
                if not table.rows:
                    continue
                
                # Extract rows with merged cell deduplication
                table_matrix = []
                for row in table.rows:
                    seen_cells = []
                    for cell in row.cells:
                        txt = cell.text.strip()
                        if not seen_cells or txt != seen_cells[-1]:
                            seen_cells.append(txt)
                    table_matrix.append(seen_cells)
                
                if not table_matrix:
                    continue

                # Header detection: first row has multiple non-empty cells and more rows follow
                has_headers = len(table_matrix) > 1 and len(table_matrix[0]) > 1 and all(bool(c) for c in table_matrix[0])
                headers = table_matrix[0] if has_headers else []

                for r_idx, row_cells in enumerate(table_matrix, 1):
                    non_empty = [c for c in row_cells if c]
                    if not non_empty:
                        continue
                    table_row_count += 1
                    
                    if has_headers and r_idx > 1:
                        row_parts = []
                        for c_idx, cell_text in enumerate(row_cells):
                            if cell_text:
                                col_header = headers[c_idx] if c_idx < len(headers) else f"Col {c_idx+1}"
                                row_parts.append(f"{col_header}: {cell_text}")
                        row_line = " | ".join(row_parts)
                    else:
                        row_line = " | ".join(non_empty)

                    cleaned_row = self.chunker.clean_text(row_line)
                    if cleaned_row:
                        blocks.append({
                            "text": cleaned_row,
                            "page_number": None,
                            "row_number": table_row_count,
                            "source_ref": f"Table {t_idx}, Row {r_idx}",
                        })

            full_text = "\n\n".join(b["text"] for b in blocks).strip()

            return {
                "page_count": None,
                "paragraph_count": len(paragraphs),
                "row_count": table_row_count if table_row_count else None,
                "column_count": None,
                "columns": None,
                "blocks": blocks,
                "full_text": full_text,
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse DOCX document: {str(exc)}",
            )

    def parse_csv(self, content: bytes) -> Dict[str, Any]:
        """Extract structured text and metadata from CSV bytes."""
        text_content: str = ""
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if not text_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode CSV text using supported encodings (UTF-8, Latin-1).",
            )

        try:
            # Detect delimiter using sniffer or common separator counts
            sample = text_content[:2048]
            delimiter = ","
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
                delimiter = dialect.delimiter
            except Exception:
                if ";" in sample and sample.count(";") > sample.count(","):
                    delimiter = ";"
                elif "\t" in sample and sample.count("\t") > sample.count(","):
                    delimiter = "\t"
                elif "|" in sample and sample.count("|") > sample.count(","):
                    delimiter = "|"

            stream = io.StringIO(text_content)
            reader = csv.reader(stream, delimiter=delimiter)
            rows = [r for r in reader if any(cell.strip() for cell in r)]


            if not rows:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV file contains no rows or data.",
                )

            headers = [h.strip() for h in rows[0]] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            row_count = len(data_rows)
            col_count = len(headers)

            blocks: List[Dict[str, Any]] = []
            for r_idx, row in enumerate(data_rows, 1):
                if headers:
                    row_parts = [
                        f"{headers[i]}: {cell.strip()}"
                        for i, cell in enumerate(row)
                        if i < len(headers) and cell.strip()
                    ]
                    row_str = f"Row {r_idx}: " + " | ".join(row_parts)
                else:
                    row_str = f"Row {r_idx}: " + ", ".join(cell.strip() for cell in row if cell.strip())

                cleaned = self.chunker.clean_text(row_str)
                if cleaned:
                    blocks.append({
                        "text": cleaned,
                        "page_number": None,
                        "row_number": r_idx,
                        "source_ref": f"Row {r_idx}",
                    })

            full_text = "\n".join(b["text"] for b in blocks).strip()

            return {
                "page_count": None,
                "paragraph_count": None,
                "row_count": row_count,
                "column_count": col_count,
                "columns": headers[:20],
                "blocks": blocks,
                "full_text": full_text,
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse CSV structure: {str(exc)}",
            )

    def parse_txt(self, content: bytes) -> Dict[str, Any]:
        """Extract text and metadata from plain-text bytes."""
        text_content: str = ""
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if not text_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to decode text file. Ensure it is valid UTF-8 or ASCII.",
            )

        cleaned_full = self.chunker.clean_text(text_content)
        lines = [ln.strip() for ln in cleaned_full.splitlines() if ln.strip()]

        raw_paras = [p.strip() for p in cleaned_full.split("\n\n") if p.strip()]
        if not raw_paras:
            raw_paras = lines

        blocks: List[Dict[str, Any]] = []
        for p_idx, para in enumerate(raw_paras, 1):
            cleaned_p = self.chunker.clean_text(para)
            if cleaned_p:
                blocks.append({
                    "text": cleaned_p,
                    "page_number": None,
                    "row_number": p_idx,
                    "source_ref": f"Section {p_idx}",
                })

        return {
            "page_count": None,
            "paragraph_count": len(raw_paras),
            "row_count": len(lines),
            "column_count": None,
            "columns": None,
            "blocks": blocks,
            "full_text": cleaned_full,
        }

    async def process_uploaded_file(
        self, upload_file: UploadFile, upload_batch_id: Optional[str] = None
    ) -> DocumentMetadata:
        """
        Validate, save, parse, and chunk an uploaded document.
        Validates project workspace consistency.
        Raises HTTPException if file is invalid, contains no extractable text, or conflicts with workspace project.
        """
        raw_bytes = await upload_file.read()
        return self.process_bytes(raw_bytes, upload_file.filename or "", upload_batch_id)

    def process_bytes(
        self, raw_bytes: bytes, filename: str, upload_batch_id: Optional[str] = None
    ) -> DocumentMetadata:
        """
        Process document bytes directly with validation, parsing, chunking, and vector indexing.
        """
        sanitized_filename, ext = self.validate_file_basics(filename, raw_bytes)

        # Generate unique document ID
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Save to disk in designated local uploads directory
        save_name = f"{doc_id}_{sanitized_filename}"
        dest_path = self.upload_dir / save_name
        dest_path.write_bytes(raw_bytes)

        # Dispatch to format-specific parser
        if ext == ".pdf":
            parsed = self.parse_pdf(raw_bytes)
        elif ext == ".docx":
            parsed = self.parse_docx(raw_bytes)
        elif ext == ".csv":
            parsed = self.parse_csv(raw_bytes)
        elif ext == ".txt":
            parsed = self.parse_txt(raw_bytes)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported extension: {ext}",
            )

        full_text = parsed.get("full_text", "")
        blocks = parsed.get("blocks", [])

        # Validate project identity consistency across the workspace
        proj_id, proj_name, client_name, is_inherited = self.validate_project_consistency(
            full_text, sanitized_filename
        )

        # Chunk the extracted text blocks with unified project workspace ID
        chunks = self.chunker.create_chunks_from_blocks(
            blocks, doc_id, sanitized_filename, project_id=proj_id
        )

        # Verify that usable text was extracted
        char_count = len(full_text)
        if char_count == 0 or len(chunks) == 0 or not full_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Document '{sanitized_filename}' contains no extractable text. "
                    "Please ensure the document contains readable text characters rather than blank pages or image-only scans."
                ),
            )

        word_count = len(full_text.split())

        # Create sanitized preview snippet (max 350 characters)
        cleaned_snippet = " ".join(full_text.split())[:350]
        if len(full_text) > 350:
            cleaned_snippet += "..."

        file_size_bytes = len(raw_bytes)
        file_size_kb = round(file_size_bytes / 1024, 2)
        uploaded_at = datetime.now(timezone.utc).isoformat()

        notes = (
            f"Successfully parsed and chunked {ext.upper()} document for project '{proj_name or proj_id}' "
            f"({file_size_kb} KB, {word_count} words, {len(chunks)} chunks). "
            f"Chunk size: ~{self.chunker.chunk_size} chars, Overlap: ~{self.chunker.chunk_overlap} chars. "
            "Chunks ready for ChromaDB vector embeddings and unified project retrieval."
        )

        metadata = DocumentMetadata(
            document_id=doc_id,
            project_id=proj_id,
            project_name=proj_name,
            client=client_name,
            is_project_inherited=is_inherited,
            upload_batch_id=upload_batch_id,
            filename=sanitized_filename,
            file_type=ext,
            file_size_bytes=file_size_bytes,
            file_size_kb=file_size_kb,
            uploaded_at=uploaded_at,
            page_count=parsed.get("page_count"),
            paragraph_count=parsed.get("paragraph_count"),
            row_count=parsed.get("row_count"),
            column_count=parsed.get("column_count"),
            columns=parsed.get("columns"),
            char_count=char_count,
            word_count=word_count,
            preview_snippet=cleaned_snippet,
            chunk_count=len(chunks),
            chunks=chunks,
            full_text=full_text,
            status="processed",
            notes=notes,
        )

        self._documents[doc_id] = metadata
        self._save_registry()
        vector_store.add_chunks(chunks)

        # Update workspace document index
        if doc_id not in self._workspace.document_ids:
            self._workspace.document_ids.append(doc_id)
        self._workspace.document_count = len(self._workspace.document_ids)
        self._save_workspace()

        return metadata

    def get_document_full_text(self, document_id: Optional[str] = None) -> str:
        """Return clean full text for a document or workspace."""
        if document_id:
            doc = self.get_document(document_id)
            return (doc.full_text or "") if doc else ""
        return "\n\n".join(doc.full_text for doc in self._documents.values() if doc.full_text)


document_service = DocumentService()
