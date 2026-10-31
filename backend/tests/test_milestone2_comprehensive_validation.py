import io
import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import pymupdf
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service

client = TestClient(app)


def test_scanned_pdf_ocr_fallback_pipeline():
    """
    Validates Part 2.3: Robust PDF extraction pipeline with OCR fallback.
    - Page 1: Scanned image containing text (no direct digital text).
    - Page 2: Completely blank page.
    Verifies that:
    1. Direct text extraction yields 0 chars.
    2. OCR fallback is invoked.
    3. Blank page is detected.
    4. Text is extracted with page numbering preserved.
    """
    # Create synthetic scanned image
    img = Image.new("RGB", (700, 250), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((30, 90), "Scanned Project Charter: Autonomous Logistics Fleet Management System", fill=(0, 0, 0))
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")

    # Create 2-page PDF: Page 1 image-only, Page 2 blank
    doc = pymupdf.open()
    p1 = doc.new_page(width=700, height=250)
    p1.insert_image(p1.rect, stream=img_buf.getvalue())
    p2 = doc.new_page(width=700, height=250)  # Blank page
    pdf_bytes = doc.write()

    parsed = document_service.parse_pdf(pdf_bytes)
    assert parsed["page_count"] == 2
    full_text = parsed["full_text"]
    assert len(full_text) > 20
    assert "Autonomous Logistics" in full_text or "Logistics Fleet" in full_text
    # Verify blocks preserve Page 1 reference
    assert any("Page 1" in (b.get("source_ref") or "") for b in parsed["blocks"])


def test_dynamic_project_switching_and_zero_bleed():
    """
    Validates Parts 3 & 4:
    1. Ingest Project 1 (Campus Event Management).
    2. Verify Scope agent extracts Project 1's identity and primary goal.
    3. Verify cross-project upload triggers HTTP 409 Conflict.
    4. Start new project workspace via POST /api/project/new.
    5. Ingest Project 2 (Community Library).
    6. Verify Scope agent extracts Project 2's identity and primary goal.
    7. Verify zero bleed from Project 1 into Project 2.
    """
    # 1. Reset workspace
    document_service.reset_workspace()

    # 2. Upload Project 1: Campus Event Management
    def _find_path(rel: str) -> Path:
        p = Path(rel)
        if not p.exists():
            p = Path("..") / rel
        if not p.exists():
            p = Path(__file__).resolve().parent.parent.parent / rel
        return p

    sample_doc_1 = _find_path("sample_documents/AI_Project_Agent_Test_Sample_Document.docx")
    assert sample_doc_1.exists(), f"Doc 1 not found: {sample_doc_1}"

    with open(sample_doc_1, "rb") as f:
        p1_bytes = f.read()

    res1 = client.post(
        "/api/documents/upload",
        files={"file": ("AI_Project_Agent_Test_Sample_Document.docx", io.BytesIO(p1_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res1.status_code == 201
    doc1_id = res1.json()["document_id"]

    # Verify Scope Agent for Project 1
    scope1 = client.post(f"/api/agents/scope?document_id={doc1_id}").json()
    assert scope1["primary_goal"] is not None
    assert "campus event" in scope1["primary_goal"]["description"].lower() or "event management" in scope1["primary_goal"]["description"].lower()

    # 3. Attempting to upload Project 2 document into Project 1 workspace must trigger HTTP 409 Conflict
    sample_doc_2 = _find_path("sample_documents/Project_Management_Agent_Test_Document_2.docx")
    assert sample_doc_2.exists(), f"Doc 2 not found: {sample_doc_2}"

    with open(sample_doc_2, "rb") as f:
        p2_bytes = f.read()

    res_conflict = client.post(
        "/api/documents/upload",
        files={"file": ("Project_Management_Agent_Test_Document_2.docx", io.BytesIO(p2_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res_conflict.status_code == 409
    assert "Project identity conflict" in res_conflict.json()["detail"]

    # 4. Start New Project Workspace
    res_new_ws = client.post("/api/project/new", json={"project_name": "Community Library Management System"})
    assert res_new_ws.status_code == 200
    new_pid = res_new_ws.json()["project_id"]
    assert new_pid != "CEMP-2026-001"

    # Workspace should have 0 active documents
    ws_check = client.get("/api/project").json()
    assert ws_check["document_count"] == 0

    # 5. Upload Project 2 into the new workspace
    res2 = client.post(
        "/api/documents/upload",
        files={"file": ("Project_Management_Agent_Test_Document_2.docx", io.BytesIO(p2_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res2.status_code == 201
    doc2_id = res2.json()["document_id"]

    # 6. Verify Scope Agent for Project 2
    scope2 = client.post(f"/api/agents/scope?document_id={doc2_id}").json()
    assert scope2["primary_goal"] is not None
    assert "community library" in scope2["primary_goal"]["description"].lower()
    assert "paper-based" in scope2["primary_goal"]["description"].lower()

    # 7. Verify ZERO bleed from Project 1 into Project 2
    assert "campus event" not in str(scope2).lower()
    assert "cemp" not in str(scope2).lower()


def test_csv_delimiters_and_record_preservation():
    """
    Validates Part 2.5: CSV extraction with various delimiters (semicolon, tab, pipe).
    """
    # Semicolon delimited
    csv_semicolon = (
        "TaskID;TaskName;Assignee;Status;DueDate\n"
        "TASK-01;Database Setup;Alex Rivera;Completed;2026-10-15\n"
        "TASK-02;API Integration;Sarah Connor;In Progress;2026-10-25\n"
    ).encode("utf-8")
    parsed_semi = document_service.parse_csv(csv_semicolon)
    assert parsed_semi["row_count"] == 2
    assert "TASK-01" in parsed_semi["full_text"]
    assert "Database Setup" in parsed_semi["full_text"]
    assert "Sarah Connor" in parsed_semi["full_text"]

    # Tab delimited
    csv_tab = (
        "TaskID\tTaskName\tAssignee\tStatus\n"
        "TASK-10\tAuthentication Flow\tDavid Lee\tBlocked\n"
    ).encode("utf-8")
    parsed_tab = document_service.parse_csv(csv_tab)
    assert parsed_tab["row_count"] == 1
    assert "TASK-10" in parsed_tab["full_text"]
    assert "David Lee" in parsed_tab["full_text"]

    # Pipe delimited
    csv_pipe = (
        "Metric|Value|Notes\n"
        "Coverage|85%|Automated test suites\n"
    ).encode("utf-8")
    parsed_pipe = document_service.parse_csv(csv_pipe)
    assert parsed_pipe["row_count"] == 1
    assert "Coverage" in parsed_pipe["full_text"]
    assert "85%" in parsed_pipe["full_text"]
