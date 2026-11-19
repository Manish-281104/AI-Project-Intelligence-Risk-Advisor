"""
Milestone 4 Automated End-to-End Test Suite:
- Task 1: Project Insights and Risk Summary Dashboard API & Grounding
- Task 2: Incremental Document Upload Pipeline & Deduplication & Isolation
- Task 3: Conversational Project Intelligence Assistant on 7 Mandatory Queries
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service
from app.services.vector_store import vector_store
from app.services.chat_assistant_service import chat_assistant_service

client = TestClient(app)

SAMPLE_CHARTER_CONTENT = """
Project Name: Apex ERP Modernization
Client: Horizon Global Logistics
Date: 2026-10-15

Project Goal:
Modernize the legacy warehouse management system into a cloud-native ERP platform to reduce order latency by 45%.

Scope Objectives:
1. Migrate PostgreSQL database to Aurora distributed cluster.
2. Develop microservices for order routing and inventory tracking.
3. Deploy React executive operations dashboard.

Table 2: Deliverables
DEL-01 | Database Migration Script | None | Owner: Database Team | Due date: 2026-10-20 | Status: Completed
DEL-02 | Warehouse Routing Microservice | None | Owner: Backend Team | Due date: 2026-11-15 | Status: In Progress
DEL-03 | Automated Inventory Scanner App | None | Owner: Mobile Team | Due date: 2026-12-01 | Status: Pending
DEL-04 | Production Deployment Checklist | None | Owner: DevOps Lead | Due date: 2026-12-10 | Status: Planned

Table 3: Milestones
M-01 | Architecture Signoff | Planned date: 2026-10-20 | Status: Completed | Owner: Solution Architect
M-02 | Core Microservices | Planned date: 2026-11-15 | Status: In Progress | Owner: Backend Lead
M-03 | Final User Acceptance Testing | Planned date: 2026-12-05 | Status: Planned | Owner: QA Lead

Table 5: Risk Register
RISK-01 | Third-party logistics API rate limits | Technical | Impact: High | Likelihood: Medium | Evidence: Peak flash sales timeout | Owner: Dave Miller | Mitigation: Implement Redis queue with exponential backoff and batch requests
RISK-02 | Legacy database schema unindexed foreign keys | Technical | Impact: High | Likelihood: High | Evidence: Slow queries on 35 unindexed FKs | Owner: Sarah Chen | Mitigation: Run database index analyzer and apply concurrent indexing

Current Blockers:
BLOCKER-01 – Staging cloud IAM role permissions for AWS Aurora cluster are blocked. Owner: DevOps Lead. Due: 2026-11-02. Impact: Delaying automated integration test suite on staging.

Action Items:
ACTION-01 – Dave Miller to complete API schema validation for logistics endpoints by 2026-11-05.
ACTION-02 – Sarah Chen to finish Redis caching adapter benchmark tests by 2026-11-08.
ACTION-03 – Team Lead to review security audit findings for IAM roles by 2026-11-02.
"""

SAMPLE_MEETING_NOTES_CONTENT = """
Project: Apex ERP Modernization
Sprint Review & Standup Meeting Notes
Date: 2026-11-02

Progress Updates:
- Warehouse Routing Microservice core endpoints reached 85% unit test coverage.
- AWS Aurora IAM security approval was granted yesterday. Staging blocker is now resolved.
- Database index analyzer applied 35 new indexes, reducing query latency by 60%.

Updated Deliverables:
- Database Migration Script [Completed]
- Warehouse Routing Microservice [Completed]
- Automated Inventory Scanner App [In Progress]

New Action Items:
- Dave Miller: Deploy inventory scanner alpha build to pilot warehouse tablets by 2026-11-12.
- UNKNOWN: Conduct load testing with simulated 10,000 orders/sec by 2026-11-14.

New Risks:
- Tablet hardware firmware incompatibility with Bluetooth barcode scanners in older warehouse docks.
  Mitigation: Provision USB-C scanner adaptors and update Android SDK wrapper.
"""


@pytest.fixture(autouse=True)
def reset_workspace_state():
    """Ensure clean workspace state before and after each test."""
    document_service.reset_workspace()
    chat_assistant_service.clear_conversation()
    yield
    document_service.reset_workspace()
    chat_assistant_service.clear_conversation()


# ==============================================================================
# Task 1: Dashboard API Tests
# ==============================================================================

def test_dashboard_summary_empty_workspace():
    """Validates /api/dashboard/summary handles empty workspace safely with defaults."""
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["has_documents"] is False
    assert data["health"] is None
    assert data["scope"] is None
    assert data["risks"] is None
    assert data["blockers"] is None
    assert data["action_items"] is None
    assert data["progress"] is None


def test_dashboard_summary_with_documents():
    """Validates /api/dashboard/summary returns grounded metrics when documents are uploaded."""
    upload_resp = client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    assert upload_resp.status_code == 201

    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["has_documents"] is True
    assert data["project_name"] == "Apex ERP Modernization"
    assert data["client"] == "Horizon Global Logistics"
    assert data["health"] is not None
    assert data["health"]["overall_score"] > 0.0
    assert len(data["health"]["indicators"]) == 3

    # Verify Scope
    assert any(term in data["scope"]["main_goal"].lower() for term in ["warehouse", "erp", "modernize"])
    assert len(data["scope"]["key_deliverables"]) >= 3
    assert len(data["scope"]["milestones"]) >= 2

    # Verify Risks
    assert len(data["risks"]["items"]) >= 2
    assert any("rate limit" in r["title"].lower() or "api" in r["title"].lower() for r in data["risks"]["items"])

    # Verify Blockers
    assert len(data["blockers"]["items"]) >= 1
    assert any("iam" in b["description"].lower() or "permission" in b["description"].lower() for b in data["blockers"]["items"])

    # Verify Action Items
    assert len(data["action_items"]["items"]) >= 2
    assert any("dave miller" in a["owner"].lower() for a in data["action_items"]["items"])

    # Verify Progress
    assert data["progress"]["total_deliverables"] >= 3
    assert data["progress"]["completion_percentage"] > 0.0

    # Also test the alias /api/dashboard/insights
    alias_resp = client.get("/api/dashboard/insights")
    assert alias_resp.status_code == 200
    assert alias_resp.json()["project_name"] == "Apex ERP Modernization"


# ==============================================================================
# Task 2: Incremental Document Upload Pipeline Tests
# ==============================================================================

def test_incremental_document_upload_pipeline():
    """
    Validates uploading Document 1, then incrementally uploading Document 2
    without wiping or re-indexing Document 1.
    """
    # 1. Upload initial Project Charter
    resp1 = client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    assert resp1.status_code == 201
    docs_after_1 = client.get("/api/documents").json()
    assert len(docs_after_1) == 1
    doc1_id = docs_after_1[0]["document_id"]
    chunks_after_1 = vector_store.count()
    assert chunks_after_1 > 0

    # 2. Incrementally upload Meeting Notes
    resp2 = client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Sprint_Meeting_Notes.txt", io.BytesIO(SAMPLE_MEETING_NOTES_CONTENT.encode("utf-8")), "text/plain")}
    )
    assert resp2.status_code == 201
    docs_after_2 = client.get("/api/documents").json()
    assert len(docs_after_2) == 2

    # Verify original document remains intact in registry
    assert any(d["document_id"] == doc1_id for d in docs_after_2)

    # Verify chunks grew without deleting doc1's chunks
    chunks_after_2 = vector_store.count()
    assert chunks_after_2 > chunks_after_1


def test_incremental_upload_duplicate_protection():
    """Validates that re-uploading an identical file does not duplicate chunks."""
    # First upload
    client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    initial_chunks = vector_store.count()
    initial_docs = len(client.get("/api/documents").json())
    assert initial_docs == 1

    # Re-upload identical file
    resp_dup = client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    assert resp_dup.status_code == 201
    post_dup_docs = len(client.get("/api/documents").json())
    assert post_dup_docs == 1
    post_dup_chunks = vector_store.count()
    assert post_dup_chunks == initial_chunks


def test_incremental_upload_project_isolation():
    """Validates that starting a new workspace isolates Project A from Project B."""
    # Project A upload
    client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    ws_a = client.get("/api/project").json()
    assert ws_a["project_name"] == "Apex ERP Modernization"

    # Reset/Start Project B
    OTHER_PROJECT = "Project Name: Healthcare Clinic Portal\nClient: Metro Health\nGoal: Telehealth app for remote patient diagnosis."
    client.post("/api/project/new?project_name=Healthcare+Clinic+Portal")
    client.post(
        "/api/documents/upload",
        files={"files": ("Clinic_Charter.txt", io.BytesIO(OTHER_PROJECT.encode("utf-8")), "text/plain")}
    )
    ws_b = client.get("/api/project").json()
    assert "Healthcare" in ws_b["project_name"]

    # Verify only Project B documents exist
    docs_b = client.get("/api/documents").json()
    assert len(docs_b) == 1
    assert docs_b[0]["filename"] == "Clinic_Charter.txt"


# ==============================================================================
# Task 3: Conversational Project Intelligence Assistant on 7 Mandatory Queries
# ==============================================================================

def test_seven_mandatory_conversational_queries():
    """
    Validates that the conversational assistant accurately answers the 7 mandatory
    Milestone 4 queries using grounded document retrieval and citations.
    """
    # 1. Upload Project Charter
    client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )
    # 2. Incrementally Upload Meeting Notes
    client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Sprint_Meeting_Notes.txt", io.BytesIO(SAMPLE_MEETING_NOTES_CONTENT.encode("utf-8")), "text/plain")}
    )

    # Query 1: Main Goal
    q1 = client.post("/api/assistant/chat", json={"question": "What is the main goal of this project?"}).json()
    assert q1["has_evidence"] is True
    assert len(q1["citations"]) > 0
    assert any(term in q1["answer"].lower() for term in ["warehouse", "erp", "modernize", "cloud"])

    # Query 2: Biggest Risks
    q2 = client.post("/api/assistant/chat", json={"question": "What are the biggest risks?"}).json()
    assert q2["has_evidence"] is True
    assert len(q2["citations"]) > 0
    assert any(term in q2["answer"].lower() for term in ["risk", "api", "rate limit", "foreign key", "scanner"])

    # Query 3: Are we on track?
    q3 = client.post("/api/assistant/chat", json={"question": "Are we currently on track?"}).json()
    assert q3["has_evidence"] is True
    assert len(q3["citations"]) > 0
    assert any(term in q3["answer"].lower() for term in ["health", "score", "track", "progress", "healthy", "attention", "at risk"])

    # Query 4: Pending Action Items
    q4 = client.post("/api/assistant/chat", json={"question": "What are the pending action items?"}).json()
    assert q4["has_evidence"] is True
    assert len(q4["citations"]) > 0
    assert any(term in q4["answer"].lower() for term in ["action", "dave miller", "sarah chen", "conduct load"])

    # Query 5: Completed Deliverables
    q5 = client.post("/api/assistant/chat", json={"question": "Which deliverables are completed?"}).json()
    assert q5["has_evidence"] is True
    assert len(q5["citations"]) > 0
    assert any(term in q5["answer"].lower() for term in ["completed", "database migration", "warehouse routing", "deliverable"])

    # Query 6: Blockers Affecting Progress
    q6 = client.post("/api/assistant/chat", json={"question": "What blockers are affecting progress?"}).json()
    assert q6["has_evidence"] is True
    assert len(q6["citations"]) > 0
    assert any(term in q6["answer"].lower() for term in ["blocker", "iam", "permission", "resolved", "security"])

    # Query 7: Changes After Meeting Notes
    q7 = client.post("/api/assistant/chat", json={"question": "What changed after uploading the latest meeting notes?"}).json()
    assert q7["has_evidence"] is True
    assert len(q7["citations"]) > 0
    assert any(term in q7["answer"].lower() for term in ["meeting", "notes", "progress", "resolved", "update", "latest"])


def test_conversational_strict_fallback_for_absent_information():
    """Validates that questions about non-existent facts trigger an honest fallback without hallucination."""
    client.post(
        "/api/documents/upload",
        files={"files": ("Apex_Project_Charter.txt", io.BytesIO(SAMPLE_CHARTER_CONTENT.encode("utf-8")), "text/plain")}
    )

    q_absent = client.post(
        "/api/assistant/chat",
        json={"question": "What is the project manager's favorite pizza topping and vacation island?"}
    ).json()

    assert q_absent["has_evidence"] is False
    assert len(q_absent["citations"]) == 0
    assert any(term in q_absent["answer"].lower() for term in ["couldn't find enough information", "not contain", "not documented", "no mention"])
