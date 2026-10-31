import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.chunker import TextChunker

client = TestClient(app)


def test_chunker_unit_boundaries_and_overlap():
    """Verify TextChunker splits at natural boundaries and respects overlap."""
    chunker = TextChunker(chunk_size=400, chunk_overlap=50)

    # Text of ~1000 characters with multiple sentences
    paragraph = (
        "Project Intelligence and Risk Advisor automates document ingestion. "
        "The system analyzes delivery schedules and identifies critical blockers. "
        "Engineers can track milestone progress with deterministic accuracy. "
        "Risk detection matrices calculate likelihood and delay exposure. "
    )
    sample_text = paragraph * 3  # ~1200 characters

    chunks = chunker.split_text_into_segments(sample_text)
    assert len(chunks) >= 3

    for i, chunk in enumerate(chunks):
        assert len(chunk) > 0
        assert len(chunk) <= 450  # Boundary tolerance
        # Verify no trailing whitespace
        assert chunk == chunk.strip()

    # Check overlap between chunk 0 and chunk 1
    # End of chunk 0 text should appear near start of chunk 1
    chunk0_words = chunk0_tail = chunk[0].split()[-3:]
    assert any(w in chunks[1] for w in chunk0_tail)


def test_chunker_empty_and_whitespace():
    """Verify chunker cleanly discards whitespace-only text."""
    chunker = TextChunker(chunk_size=800, chunk_overlap=100)
    assert chunker.split_text_into_segments("") == []
    assert chunker.split_text_into_segments("   \n\n\t  ") == []


def test_upload_txt_chunking():
    """Verify text file upload returns actual text chunks with proper metadata."""
    txt_content = (
        "AI Project Intelligence & Risk Advisor Platform.\n\n"
        "Section 1: Scope of Work.\n"
        "The project will ingest multi-format engineering documents including PDF, DOCX, CSV, and TXT. "
        "All ingested documents are validated against MIME type and size boundaries.\n\n"
        "Section 2: Risk Mitigation.\n"
        "Sprint velocity slips will be identified through deterministic formula calculations. "
        "High-risk deliverables will be flagged for team lead intervention before deadlines are missed."
    ).encode("utf-8")

    files = {"file": ("architecture_charter.txt", io.BytesIO(txt_content), "text/plain")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 201
    data = response.json()

    # Verify top-level response schema as required by Step 4
    assert "document_id" in data
    assert data["filename"] == "architecture_charter.txt"
    assert data["status"] == "processed"
    assert data["extracted_characters"] == len(txt_content.decode("utf-8").strip())
    assert data["chunk_count"] > 0
    assert len(data["chunks"]) == data["chunk_count"]

    # Verify individual chunk schema
    first_chunk = data["chunks"][0]
    assert first_chunk["chunk_id"].startswith(data["document_id"])
    assert len(first_chunk["text"]) > 0
    assert first_chunk["source"] == "architecture_charter.txt"
    assert first_chunk["char_count"] == len(first_chunk["text"])
    assert first_chunk["word_count"] > 0


def test_upload_multipage_pdf_chunking():
    """Verify PDF upload preserves page numbers per chunk."""
    import pymupdf

    doc = pymupdf.open()

    # Page 1
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        "Page 1 Content: Project charter and governance guidelines for AI Project Intelligence.\n"
        "All milestones must be verified with genuine automated test execution.",
    )

    # Page 2
    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        "Page 2 Content: Detailed risk analysis and delivery forecasting model.\n"
        "ChromaDB and LangGraph multi-agent orchestration planned for Milestone 2.",
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("multipage_charter.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "processed"
    assert data["chunk_count"] >= 2
    assert len(data["chunks"]) == data["chunk_count"]

    # Verify page numbers are preserved
    page_numbers = [c["page_number"] for c in data["chunks"]]
    assert 1 in page_numbers
    assert 2 in page_numbers

    # Verify source reference
    page1_chunk = next(c for c in data["chunks"] if c["page_number"] == 1)
    assert "Page 1 Content" in page1_chunk["text"]
    assert page1_chunk["source_ref"] == "Page 1"


def test_upload_csv_chunking_with_row_references():
    """Verify CSV upload preserves row references and headers."""
    csv_lines = [
        "TaskID,Title,Owner,Priority,DueDate",
        "T-1,Setup FastAPI Ingestion,Manish,High,2026-10-15",
        "T-2,Implement Boundary Chunker,Manish,High,2026-10-16",
        "T-3,Build React Processing Results,Manish,High,2026-10-17",
        "T-4,Verify Multi-document Uploads,Manish,Medium,2026-10-18",
    ]
    csv_bytes = "\n".join(csv_lines).encode("utf-8")

    files = {"file": ("sprint_tasks.csv", io.BytesIO(csv_bytes), "text/csv")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 201
    data = response.json()

    assert data["chunk_count"] > 0
    first_chunk = data["chunks"][0]
    assert first_chunk["row_number"] == 1
    assert "TaskID" in first_chunk["text"]
    assert "T-1" in first_chunk["text"]
    assert first_chunk["source_ref"] is not None


def test_upload_docx_chunking():
    """Verify DOCX upload creates text chunks from paragraphs and tables."""
    import docx

    doc = docx.Document()
    doc.add_heading("AI Intelligence Scope & Requirements", level=1)
    doc.add_paragraph("This document details all technical specifications for document processing.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Module"
    table.cell(0, 1).text = "Target"
    table.cell(1, 0).text = "Ingestion"
    table.cell(1, 1).text = "Milestone 1 Verified"

    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()

    files = {"file": ("requirements.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["chunk_count"] > 0
    assert len(data["chunks"]) == data["chunk_count"]
    assert any("Scope & Requirements" in c["text"] for c in data["chunks"])


def test_blank_pdf_rejected_no_extractable_text():
    """Verify PDF with blank pages (no extractable text) returns 400."""
    import pymupdf

    doc = pymupdf.open()
    doc.new_page()  # Completely blank page
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("blank_scanned.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 400
    assert "no extractable text" in response.json()["detail"].lower()


def test_whitespace_only_txt_rejected():
    """Verify plain text file with whitespace only returns 400."""
    files = {"file": ("spaces.txt", io.BytesIO(b"   \n\n\t   \n  "), "text/plain")}
    response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 400
    assert "no extractable text" in response.json()["detail"].lower()
