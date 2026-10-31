import io
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns API info and docs link."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "online"
    assert "documentation" in data


def test_health_endpoint():
    """Verify GET /api/health returns 200 and honest status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "storage_ready" in data
    assert data["storage_ready"] is True
    assert "planned" in data["ai_pipeline_status"].lower()


def test_modules_endpoint():
    """Verify GET /api/modules returns exactly nine modules with correct statuses."""
    response = client.get("/api/modules")
    assert response.status_code == 200
    data = response.json()
    assert data["total_modules"] == 9
    modules = data["modules"]
    assert len(modules) == 9

    # Verify Module 1 is Partially Implemented
    mod1 = next(m for m in modules if m["id"] == 1)
    assert mod1["name"] == "Document Ingestion and Knowledge Base Construction"
    assert mod1["status"] == "Partially Implemented"

    # Verify Module 9 is Partially Implemented
    mod9 = next(m for m in modules if m["id"] == 9)
    assert mod9["name"] == "Project Insights and Risk Summary Dashboard"
    assert mod9["status"] == "Partially Implemented"

    # Verify Module 2 (RAG Pipeline) is Planned
    mod2 = next(m for m in modules if m["id"] == 2)
    assert mod2["status"] == "Planned"


def test_upload_txt_file():
    """Verify uploading a plain text file."""
    txt_content = b"AI Project Intelligence & Risk Advisor\nSprint 1 kickoff meeting notes.\nGoals: Ingestion pipeline."
    files = {"file": ("project_charter.txt", io.BytesIO(txt_content), "text/plain")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    doc = data["document"]
    assert doc["filename"] == "project_charter.txt"
    assert doc["file_type"] == ".txt"
    assert doc["word_count"] > 0
    assert "AI Project Intelligence" in doc["preview_snippet"]


def test_upload_csv_file():
    """Verify uploading a structured CSV sprint schedule."""
    csv_content = (
        b"TaskID,TaskName,Assignee,Status,DueDate\n"
        b"TASK-101,Setup Backend API,Manish,Completed,2026-10-15\n"
        b"TASK-102,Document Ingestion,Manish,Completed,2026-10-16\n"
        b"TASK-103,RAG ChromaDB,DevTeam,Planned,2026-10-25\n"
    )
    files = {"file": ("sprint_schedule.csv", io.BytesIO(csv_content), "text/csv")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    doc = data["document"]
    assert doc["file_type"] == ".csv"
    assert doc["row_count"] == 3
    assert doc["column_count"] == 5
    assert "TaskID" in doc["columns"]


def test_upload_docx_file():
    """Verify uploading a valid DOCX file created with python-docx."""
    import docx

    doc = docx.Document()
    doc.add_heading("AI Project Intelligence Scope Document", level=1)
    doc.add_paragraph("This document outlines the scope of work and risk mitigation strategies.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Risk"
    table.cell(0, 1).text = "Mitigation"
    table.cell(1, 0).text = "Delayed Milestone"
    table.cell(1, 1).text = "Agile backlog reprioritization"

    buffer = io.BytesIO()
    doc.save(buffer)
    docx_bytes = buffer.getvalue()

    files = {"file": ("scope_statement.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    doc_res = data["document"]
    assert doc_res["file_type"] == ".docx"
    assert doc_res["paragraph_count"] >= 1
    assert "Scope Document" in doc_res["preview_snippet"]


def test_upload_pdf_file():
    """Verify uploading a valid PDF document generated with PyMuPDF."""
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "AI Project Intelligence & Risk Advisor Charter\nExecutive Summary of Requirements.")
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("project_charter.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    doc_res = data["document"]
    assert doc_res["file_type"] == ".pdf"
    assert doc_res["page_count"] == 1
    assert "AI Project Intelligence" in doc_res["preview_snippet"]


def test_upload_empty_file_rejected():
    """Verify empty 0-byte file upload is rejected with HTTP 400."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_unsupported_extension_rejected():
    """Verify unsupported file types (.exe, .jpg) are rejected with HTTP 400."""
    files = {"file": ("malicious_script.exe", io.BytesIO(b"MZfakeexecutable"), "application/octet-stream")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()


def test_upload_corrupted_pdf_rejected():
    """Verify invalid PDF with bad magic bytes is rejected."""
    files = {"file": ("fake.pdf", io.BytesIO(b"Not A Valid PDF Body"), "application/pdf")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "malformed pdf" in response.json()["detail"].lower()
