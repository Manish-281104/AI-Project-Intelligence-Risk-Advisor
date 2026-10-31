import io
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_workspace():
    """Ensure a clean project workspace before each test."""
    document_service.reset_workspace()
    yield
    document_service.reset_workspace()


def test_single_persistent_project_id_across_multiple_batches():
    """
    Test user workflow:
    1. Upload a project proposal.
    2. Upload its SRS in a separate batch.
    3. Upload meeting notes in another batch.
    4. Upload a progress report in another batch.
    5. Verify all four documents belong to one persistent project ID.
    6. Verify RAG retrieves across all four documents.
    7. Verify all three agents produce combined, evidence-grounded results.
    8. Upload a conflicting project document and verify HTTP 409 Conflict.
    """
    # -------------------------------------------------------------
    # 1. Upload Project Proposal (Batch 1)
    # -------------------------------------------------------------
    proposal_text = (
        "Project Name: Campus Event Management Portal\n"
        "Project ID: PROJ-CAMPUS-01\n"
        "Project Sponsor: Department of Computer Science\n"
        "1. Project Overview\n"
        "A web-based Campus Event Management Portal for students and event coordinators, "
        "supporting event discovery, registration, event management, capacity control, and participant list export.\n"
        "2. Project Objectives\n"
        "Provide a single portal where students can view upcoming department events.\n"
        "Allow students to register for an event and receive a registration confirmation.\n"
    )
    res1 = client.post(
        "/api/documents/upload",
        files={"file": ("project_proposal.txt", io.BytesIO(proposal_text.encode("utf-8")), "text/plain")},
    )
    assert res1.status_code == 201
    data1 = res1.json()
    project_id = data1["project_id"]
    batch1_id = data1["upload_batch_id"]
    doc1_id = data1["document_id"]
    assert project_id is not None
    assert doc1_id is not None

    # -------------------------------------------------------------
    # 2. Upload SRS in a separate batch (Batch 2)
    # -------------------------------------------------------------
    srs_text = (
        "Campus Event Management Portal (CEMP)\n"
        "Software Requirements Specification\n"
        "Section 3.1 In Scope\n"
        "Student sign-in using university email address.\n"
        "Event listing with title, date, venue, description, and available seats.\n"
        "Capacity validation during registration.\n"
        "Section 3.2 Out of Scope\n"
        "Online payment collection.\n"
        "Mobile applications for Android or iOS.\n"
        "Deliverables:\n"
        "D-01 | Student event catalogue | Students view published events | Ravi Kumar | 11 Nov 2026\n"
        "D-02 | Student registration workflow | A student can register once; capacity enforced | Sana Ali | 25 Nov 2026\n"
        "Milestones:\n"
        "M-01 | Requirements approval | 06 Nov 2026 | Completed | Ananya Rao\n"
        "M-02 | Event catalogue demo | 13 Nov 2026 | Completed | Ravi Kumar\n"
        "Dependencies:\n"
        "DEP-01 | Registration workflow | Requires student sign-in and event catalogue APIs. | D-01\n"
    )
    res2 = client.post(
        "/api/documents/upload",
        files={"file": ("system_requirements_spec.txt", io.BytesIO(srs_text.encode("utf-8")), "text/plain")},
    )
    assert res2.status_code == 201
    data2 = res2.json()
    batch2_id = data2["upload_batch_id"]
    doc2_id = data2["document_id"]
    # Critical Business Rule: SAME project ID, distinct batch ID and doc ID
    assert data2["project_id"] == project_id
    assert batch2_id != batch1_id
    assert doc2_id != doc1_id

    # -------------------------------------------------------------
    # 3. Upload Meeting Notes in another batch (Batch 3)
    # -------------------------------------------------------------
    meeting_text = (
        "Campus Event Management Portal - Meeting Notes\n"
        "Meeting Date: 27 November 2026\n"
        "Attendees: Ananya Rao, Ravi Kumar, Sana Ali, Joel Mathew.\n"
        "Blocker: The coordinator cancellation endpoint is not available. Sana Ali will provide schedule by 02 Dec 2026.\n"
        "Open question: The sponsor has not confirmed whether event cancellation emails are required.\n"
        "Action: Ravi Kumar will prepare the participant CSV export interface by 04 December 2026.\n"
        "Action: Joel Mathew will prepare registration capacity test cases by 03 December 2026.\n"
    )
    res3 = client.post(
        "/api/documents/upload",
        files={"file": ("meeting_notes_27_nov.txt", io.BytesIO(meeting_text.encode("utf-8")), "text/plain")},
    )
    assert res3.status_code == 201
    data3 = res3.json()
    batch3_id = data3["upload_batch_id"]
    doc3_id = data3["document_id"]
    assert data3["project_id"] == project_id
    assert batch3_id != batch2_id
    assert doc3_id != doc2_id

    # -------------------------------------------------------------
    # 4. Upload Progress Report in another batch (Batch 4)
    # -------------------------------------------------------------
    progress_text = (
        "Campus Event Management Portal - Progress Update\n"
        "Reporting Date: 30 November 2026\n"
        "Risk Register:\n"
        "R-01 | Registration may exceed event capacity under simultaneous requests. | Technical | High | Medium | Concurrency test incomplete | Sana Ali | Complete concurrency testing\n"
        "R-02 | Coordinator dashboard may miss planned date because cancellation endpoint is unavailable. | Schedule | High | High | Dashboard marked At Risk | Sana Ali | Complete endpoint\n"
        "R-03 | Acceptance testing may be compressed if a stable build is delivered late. | Schedule | Medium | Medium | QA has not received stable build | Ananya Rao | Deliver build\n"
    )
    res4 = client.post(
        "/api/documents/upload",
        files={"file": ("progress_update_30_nov.txt", io.BytesIO(progress_text.encode("utf-8")), "text/plain")},
    )
    assert res4.status_code == 201
    data4 = res4.json()
    batch4_id = data4["upload_batch_id"]
    doc4_id = data4["document_id"]
    assert data4["project_id"] == project_id
    assert batch4_id != batch3_id

    # -------------------------------------------------------------
    # 5. Verify Workspace Identity & Documents Collection
    # -------------------------------------------------------------
    ws_res = client.get("/api/project")
    assert ws_res.status_code == 200
    ws_data = ws_res.json()
    assert ws_data["project_id"] == project_id
    assert ws_data["document_count"] == 4
    assert set(ws_data["document_ids"]) == {doc1_id, doc2_id, doc3_id, doc4_id}

    # Verify document listing
    doc_list_res = client.get("/api/documents")
    assert doc_list_res.status_code == 200
    docs = doc_list_res.json()
    assert len(docs) == 4
    for d in docs:
        assert d["project_id"] == project_id

    # -------------------------------------------------------------
    # 6. Verify Cross-Document RAG Retrieval
    # -------------------------------------------------------------
    # Query something from document 1 (overview), document 2 (deliverables),
    # document 3 (meeting blocker), and document 4 (risks)
    analysis_res = client.post("/api/agents/analyze-all")
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()

    # Scope findings extracted from proposal and SRS
    scope = analysis["scope"]
    assert len(scope["project_goals"]) >= 1
    assert any("Campus Event Management" in g["title"] or "Campus Event Management" in g["description"] for g in scope["project_goals"])
    assert len(scope["deliverables"]) >= 2
    assert any("D-01" in d["name"] for d in scope["deliverables"])
    assert any("D-02" in d["name"] for d in scope["deliverables"])
    assert any("DEP-01" in dp["dependent_item"] for dp in scope["dependencies"])

    # Risk findings extracted from progress report and meeting notes
    risks = analysis["risks"]
    assert len(risks["risks"]) >= 3
    assert any("R-01" in r["risk_id"] for r in risks["risks"])
    assert any("R-02" in r["risk_id"] for r in risks["risks"])
    assert any("R-03" in r["risk_id"] for r in risks["risks"])

    # Blocker findings extracted from meeting notes
    blockers = analysis["blockers"]
    assert blockers["blocker_count"] >= 1
    assert any("cancellation endpoint" in b["description"].lower() for b in blockers["items"] if b["item_type"] == "Blocker")
    assert any("cancellation email" in p["description"].lower() for p in blockers["items"] if p["item_type"] == "Pending Decision")

    # -------------------------------------------------------------
    # 8. Upload Conflicting Project Document -> Must flag HTTP 409
    # -------------------------------------------------------------
    conflict_doc = (
        "Project Name: Hospital Intensive Care Management System\n"
        "Project ID: PROJ-HOSPITAL-99\n"
        "Client: Metro Health Authority\n"
        "This document describes hospital ICU bed allocation, patient telemetry, and nurse shift schedules.\n"
    )
    conflict_res = client.post(
        "/api/documents/upload",
        files={"file": ("Hospital_ICU_Spec.txt", io.BytesIO(conflict_doc.encode("utf-8")), "text/plain")},
    )
    assert conflict_res.status_code == 409, f"Expected 409 Conflict, got {conflict_res.status_code}: {conflict_res.text}"
    conflict_detail = conflict_res.json()["detail"]
    assert "Project identity conflict" in conflict_detail
    assert "Hospital Intensive Care Management System" in conflict_detail


def test_inherited_project_identity_for_generic_documents():
    """
    Test that a document without explicit project identity successfully inherits
    the workspace project ID without error.
    """
    # 1. Establish project with first document
    first_doc = (
        "Project Name: Campus Event Management Portal\n"
        "Project ID: PROJ-CAMPUS-01\n"
        "Department event system.\n"
    )
    res1 = client.post(
        "/api/documents/upload",
        files={"file": ("project_charter.txt", io.BytesIO(first_doc.encode("utf-8")), "text/plain")},
    )
    assert res1.status_code == 201
    proj_id = res1.json()["project_id"]

    # 2. Upload generic document without project title
    generic_doc = (
        "Weekly Team Sync Notes\n"
        "Discussed task backlog and unit testing progress.\n"
        "Action: Joel Mathew will write integration tests by 05 Dec 2026.\n"
    )
    res2 = client.post(
        "/api/documents/upload",
        files={"file": ("sync_notes.txt", io.BytesIO(generic_doc.encode("utf-8")), "text/plain")},
    )
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["project_id"] == proj_id
    assert data2["document"]["is_project_inherited"] is True
