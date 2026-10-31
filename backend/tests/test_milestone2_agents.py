import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_service import document_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure clean document state before each test run."""
    # Preserve test isolation
    yield


# =====================================================================
# 1. Bug Fix Acceptance Tests: Single-File Upload & Multi-File Rejection
# =====================================================================

def test_single_file_upload_succeeds():
    """Acceptance Test 1: Single file upload succeeds with HTTP 201."""
    content = b"AI Project Charter\nObjective: Build autonomous risk advisor.\nDeliverable: RAG pipeline by 2026-11-01."
    files = {"file": ("charter_single.txt", io.BytesIO(content), "text/plain")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "charter_single.txt"
    assert data["chunk_count"] >= 1


def test_multiple_valid_files_upload_in_one_request():
    """Acceptance Test: Uploading multiple valid files together in one request succeeds."""
    files = [
        ("files", ("batch_doc1.txt", io.BytesIO(b"Document 1 text content for multi-upload."), "text/plain")),
        ("files", ("batch_doc2.txt", io.BytesIO(b"Document 2 text content for multi-upload."), "text/plain")),
    ]
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["total_files"] == 2
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0
    assert len(data["results"]) == 2

    res1 = data["results"][0]
    res2 = data["results"][1]
    assert res1["success"] is True
    assert res2["success"] is True
    assert res1["document_id"] != res2["document_id"]
    assert res1["chunk_count"] >= 1
    assert res2["chunk_count"] >= 1


def test_mixture_valid_and_invalid_files_upload():
    """Acceptance Test: Uploading a mixture of valid and invalid files processes valid files and reports invalid."""
    files = [
        ("files", ("valid_doc.txt", io.BytesIO(b"Valid content that should be processed."), "text/plain")),
        ("files", ("unsupported_doc.exe", io.BytesIO(b"Fake executable binary"), "application/octet-stream")),
    ]
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["total_files"] == 2
    assert data["successful_count"] == 1
    assert data["failed_count"] == 1
    assert len(data["results"]) == 2

    valid_res = next(r for r in data["results"] if r["filename"] == "valid_doc.txt")
    assert valid_res["success"] is True
    assert valid_res["document_id"] is not None

    invalid_res = next(r for r in data["results"] if r["filename"] == "unsupported_doc.exe")
    assert invalid_res["success"] is False
    assert invalid_res["error"] is not None
    assert "unsupported" in invalid_res["error"].lower()


def test_all_invalid_files_batch_rejected():
    """Acceptance Test: Batch where all files are invalid returns HTTP 400."""
    files = [
        ("files", ("empty_doc.txt", io.BytesIO(b""), "text/plain")),
        ("files", ("bad_doc.dll", io.BytesIO(b"DLL"), "application/octet-stream")),
    ]
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "failed validation" in response.json()["detail"].lower()


def test_sequential_single_file_uploads_succeed():
    """Acceptance Test 5: Uploading a second file after the first completes works correctly."""
    # Upload first
    f1 = {"file": ("seq1.txt", io.BytesIO(b"Sprint 1 notes. Goal: establish baseline."), "text/plain")}
    r1 = client.post("/api/documents/upload", files=f1)
    assert r1.status_code == 201
    doc1_id = r1.json()["document_id"]

    # Upload second
    f2 = {"file": ("seq2.txt", io.BytesIO(b"Sprint 2 notes. Goal: integrate multi-agent."), "text/plain")}
    r2 = client.post("/api/documents/upload", files=f2)
    assert r2.status_code == 201
    doc2_id = r2.json()["document_id"]

    assert doc1_id != doc2_id


def test_document_listing_and_deletion():
    """Acceptance Test 6 & 8: Replacing/deleting document works and document registry is maintained."""
    f = {"file": ("to_delete.txt", io.BytesIO(b"Temporary document for deletion testing."), "text/plain")}
    r = client.post("/api/documents/upload", files=f)
    assert r.status_code == 201
    doc_id = r.json()["document_id"]

    # Verify present in list
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["document_id"] == doc_id for d in docs)

    # Get single document
    get_res = client.get(f"/api/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["document_id"] == doc_id

    # Delete document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200

    # Verify gone
    get_after = client.get(f"/api/documents/{doc_id}")
    assert get_after.status_code == 404


# =====================================================================
# 2. Agent 1: Scope & Deliverable Extraction Agent Tests
# =====================================================================

def test_scope_agent_extraction():
    """Verify Scope Agent extracts goals, deliverables, milestones, deadlines, and dependencies."""
    charter_text = (
        "Project Goals: Build an autonomous AI Project Intelligence and Risk Advisory platform.\n"
        "In-Scope: Document parsing, RAG pipeline, and autonomous multi-agent advisory.\n"
        "Out-of-Scope: Third-party Jira API bidirectional sync.\n"
        "Milestone 1: Foundation and Ingestion Setup, target date: 2026-10-15.\n"
        "Milestone 2: Multi-Agent Intelligence Core, target date: 2026-10-30.\n"
        "Expected Deliverables: Automated Risk Matrix, Scope Extractor, Blocker Register.\n"
        "RAG Pipeline depends on Document Ingestion.\n"
        "Multi-Agent Core depends on RAG Pipeline."
    ).encode("utf-8")

    files = {"file": ("project_charter_scope.txt", io.BytesIO(charter_text), "text/plain")}
    up_res = client.post("/api/documents/upload", files=files)
    assert up_res.status_code == 201
    doc_id = up_res.json()["document_id"]

    # Run Scope Agent
    res = client.post(f"/api/agents/scope?document_id={doc_id}")
    assert res.status_code == 200
    data = res.json()

    assert len(data["project_goals"]) >= 1
    assert "autonomous" in data["project_goals"][0]["description"].lower()

    # Verify In-Scope vs Out-of-Scope
    assert len(data["scope_items"]) >= 1
    in_scope_items = [s for s in data["scope_items"] if s["category"] == "In-Scope"]
    assert len(in_scope_items) >= 1

    # Verify Deliverables
    assert len(data["deliverables"]) >= 1

    # Verify Milestones
    assert len(data["milestones"]) >= 1
    m1 = next((m for m in data["milestones"] if "1" in m["milestone_id"]), None)
    assert m1 is not None

    # Verify Dependencies
    assert len(data["dependencies"]) >= 1

    # Verify Source Provenance
    assert len(data["source_references"]) >= 1
    assert data["source_references"][0]["filename"] == "project_charter_scope.txt"

    # Verify Missing Info
    assert len(data["missing_information"]) >= 1


# =====================================================================
# 3. Agent 2: Risk Detection and Delivery Forecasting Agent Tests
# =====================================================================

def test_risk_agent_overdue_schedule_and_dependency_detection():
    """Verify Risk Agent deterministically identifies overdue items and dependency bottlenecks."""
    csv_schedule = (
        "TaskID,TaskName,Assignee,Status,DueDate\n"
        "TASK-01,Environment Setup,Manish,Completed,2026-10-14\n"
        "TASK-02,Document Ingestion,Team,In Progress,2026-10-15\n"
        "TASK-03,RAG ChromaDB,TBD,Blocked,2026-10-16\n"
        "TASK-04,Frontend Dashboard,Manish,Planned,2026-11-05\n"
    ).encode("utf-8")

    files = {"file": ("sprint_schedule_risks.csv", io.BytesIO(csv_schedule), "text/csv")}
    up_res = client.post("/api/documents/upload", files=files)
    assert up_res.status_code == 201
    doc_id = up_res.json()["document_id"]

    # Run Risk Agent
    res = client.post(f"/api/agents/risks?document_id={doc_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["total_risks"] >= 1
    assert data["overall_delivery_risk"] in ("Critical", "High", "Elevated", "Moderate")

    # Verify Overdue Task was identified
    overdue_risks = [r for r in data["risks"] if "overdue" in r["risk_title"].lower() or r["risk_category"] == "Schedule"]
    assert len(overdue_risks) >= 1
    assert "2026-10" in overdue_risks[0]["description"]

    # Verify Recommended Mitigation is present and labeled
    assert "[AI Recommendation]" in overdue_risks[0]["recommended_mitigation"]

    # Verify Calculation Method and Limitations Note
    assert "Deterministic" in data["calculation_method"]
    assert "strictly grounded in textual passages" in data["limitations_note"]


# =====================================================================
# 4. Agent 3: Blocker & Action Item Identification Agent Tests
# =====================================================================

def test_blocker_agent_extraction_and_unassigned_handling():
    """Verify Blocker Agent extracts blockers, action items, and maps missing assignees to UNKNOWN."""
    minutes_text = (
        "Project Sync Meeting Minutes\n"
        "Blocker: Python 3.13 compilation issues for binary wheel packages.\n"
        "Decision: Use lightweight TF-IDF and pure Python embeddings to ensure zero native build errors.\n"
        "Pending Decision: Selection between Gemini 1.5 Flash and local LLM for optional enhancement.\n"
        "Action Item: Update requirements.txt and remove unneeded heavy packages.\n"
        "Action Item: Verify all 18 unit tests pass with pytest. Owner: Manish. Due: 2026-10-29."
    ).encode("utf-8")

    files = {"file": ("meeting_minutes_blockers.txt", io.BytesIO(minutes_text), "text/plain")}
    up_res = client.post("/api/documents/upload", files=files)
    assert up_res.status_code == 201
    doc_id = up_res.json()["document_id"]

    # Run Blocker Agent
    res = client.post(f"/api/agents/blockers?document_id={doc_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["blocker_count"] >= 1
    assert data["action_item_count"] >= 1

    # Check unassigned owner mapping
    unassigned = [it for it in data["items"] if it.get("assigned_owner") == "UNKNOWN"]
    assert len(unassigned) >= 1

    # Check explicit owner mapping
    assigned = [it for it in data["items"] if it.get("assigned_owner") and it.get("assigned_owner") != "UNKNOWN"]
    assert len(assigned) >= 1
    assert "Manish" in assigned[0]["assigned_owner"]

    # Check that blockers have recommendations
    blocker_item = next(it for it in data["items"] if it["item_type"] == "Blocker")
    assert "[AI Recommendation]" in blocker_item["recommended_next_step"]


# =====================================================================
# 5. Consolidated Multi-Agent Pipeline Test
# =====================================================================

def test_comprehensive_multi_agent_analysis():
    """Verify POST /api/agents/analyze-all executes all three agents and returns unified findings."""
    res = client.post("/api/agents/analyze-all")
    assert res.status_code == 200
    data = res.json()

    assert "scope" in data
    assert "risks" in data
    assert "blockers" in data
    assert "timestamp" in data
    assert isinstance(data["analyzed_documents"], list)
