import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service
from app.services.scope_agent import scope_agent
from app.services.risk_agent import risk_agent
from app.services.blocker_agent import blocker_agent
from app.services.chat_assistant_service import chat_assistant_service
from app.schemas.milestone3_models import ChatRequest

client = TestClient(app)

SCSP_DIR = r"C:\Users\manis\Desktop\Tests\Smart_Campus_Service_Portal"
CLMS_DIR = r"C:\Users\manis\Desktop\Tests\Community_Library_Management_System"


def test_test_a_smart_campus_project():
    """
    Test A: Smart Campus project (SCSP-2026-104)
    Upload 4 documents:
      - 01_Project_Charter.docx
      - 02_Requirements_and_Acceptance.docx
      - 03_Meeting_Minutes_and_Blockers.docx
      - 04_Status_and_Deliverables.docx
    Expected:
      - All valid documents accepted
      - Two confirmed blockers (BLOCKER-01, BLOCKER-02)
      - Two confirmed risks (RISK-01, RISK-02)
      - Three action items (ACTION-01, ACTION-02, ACTION-03)
      - Five deliverables (DEL-01 through DEL-05)
      - Overall project status: At Risk
    """
    document_service.reset_workspace()
    assert os.path.exists(SCSP_DIR), f"Smart Campus folder missing: {SCSP_DIR}"

    files_to_upload = [
        "01_Project_Charter.docx",
        "02_Requirements_and_Acceptance.docx",
        "03_Meeting_Minutes_and_Blockers.docx",
        "04_Status_and_Deliverables.docx",
    ]

    for fn in files_to_upload:
        fp = os.path.join(SCSP_DIR, fn)
        with open(fp, "rb") as f:
            resp = client.post(
                "/api/documents/upload",
                files={"files": (fn, f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )
        assert resp.status_code in (200, 201), f"Failed uploading {fn}: {resp.text}"
        data = resp.json()
        assert data["success"] is True
        assert "SCSP" in data["project_id"]

    ws = document_service.get_workspace()
    assert ws.project_id == "SCSP-2026-104"
    assert "Smart Campus" in ws.project_name

    # 1. Deliverables extraction
    scope_resp = client.post("/api/agents/scope")
    assert scope_resp.status_code == 200
    scope_data = scope_resp.json()
    delivs = scope_data["deliverables"]
    assert len(delivs) == 5, f"Expected 5 deliverables, got {len(delivs)}: {[d['deliverable_id'] for d in delivs]}"
    deliv_ids = {d["deliverable_id"] for d in delivs}
    assert deliv_ids == {"DEL-01", "DEL-02", "DEL-03", "DEL-04", "DEL-05"}

    # 2. Risk extraction
    risk_resp = client.post("/api/agents/risks")
    assert risk_resp.status_code == 200
    risk_data = risk_resp.json()
    risks = risk_data["risks"]
    assert len(risks) == 2, f"Expected 2 risks, got {len(risks)}: {[r['risk_id'] for r in risks]}"
    risk_ids = {r["risk_id"] for r in risks}
    assert risk_ids == {"RISK-01", "RISK-02"}

    # 3. Blockers and Action items extraction
    blocker_resp = client.post("/api/agents/blockers")
    assert blocker_resp.status_code == 200
    blocker_data = blocker_resp.json()
    items = blocker_data["items"]
    blockers = [i for i in items if i["item_type"] == "Blocker"]
    actions = [i for i in items if i["item_type"] == "Action Item"]
    assert len(blockers) == 2, f"Expected 2 blockers, got {len(blockers)}: {[b['item_id'] for b in blockers]}"
    assert len(actions) == 3, f"Expected 3 action items, got {len(actions)}: {[a['item_id'] for a in actions]}"

    blocker_ids = {b["item_id"] for b in blockers}
    assert blocker_ids == {"BLOCKER-01", "BLOCKER-02"}
    action_ids = {a["item_id"] for a in actions}
    assert action_ids == {"ACTION-01", "ACTION-02", "ACTION-03"}

    # 4. Overall project status query
    chat_resp = client.post("/api/assistant/chat", json={"question": "What is the overall project status?"})
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "At Risk" in chat_data["answer"]


def test_test_b_community_library_project():
    """
    Test B: Community Library project (CLMS-2026-207)
    Upload 4 documents:
      - 01_Project_Overview.docx
      - 02_Library_Requirements.docx
      - 03_Library_Meeting_Notes.docx
      - 04_Library_Deliverables_Status.docx
    Expected:
      - All valid documents accepted
      - One confirmed blocker (LIB-BLOCK-01)
      - Two confirmed risks (LIB-RISK-01, LIB-RISK-02)
      - Three action items (LIB-ACT-01, LIB-ACT-02, LIB-ACT-03)
      - Five deliverables (LIB-DEL-01 through LIB-DEL-05)
      - Overall project status: On Track
    """
    document_service.reset_workspace()
    assert os.path.exists(CLMS_DIR), f"Community Library folder missing: {CLMS_DIR}"

    files_to_upload = [
        "01_Project_Overview.docx",
        "02_Library_Requirements.docx",
        "03_Library_Meeting_Notes.docx",
        "04_Library_Deliverables_Status.docx",
    ]

    for fn in files_to_upload:
        fp = os.path.join(CLMS_DIR, fn)
        with open(fp, "rb") as f:
            resp = client.post(
                "/api/documents/upload",
                files={"files": (fn, f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )
        assert resp.status_code in (200, 201), f"Failed uploading {fn}: {resp.text}"
        data = resp.json()
        assert data["success"] is True
        assert "CLMS" in data["project_id"]

    ws = document_service.get_workspace()
    assert ws.project_id == "CLMS-2026-207"
    assert "Community Library" in ws.project_name

    # 1. Deliverables extraction
    scope_resp = client.post("/api/agents/scope")
    assert scope_resp.status_code == 200
    scope_data = scope_resp.json()
    delivs = scope_data["deliverables"]
    assert len(delivs) == 5, f"Expected 5 deliverables, got {len(delivs)}: {[d['deliverable_id'] for d in delivs]}"
    deliv_ids = {d["deliverable_id"] for d in delivs}
    assert deliv_ids == {"LIB-DEL-01", "LIB-DEL-02", "LIB-DEL-03", "LIB-DEL-04", "LIB-DEL-05"}

    # 2. Risk extraction
    risk_resp = client.post("/api/agents/risks")
    assert risk_resp.status_code == 200
    risk_data = risk_resp.json()
    risks = risk_data["risks"]
    assert len(risks) == 2, f"Expected 2 risks, got {len(risks)}: {[r['risk_id'] for r in risks]}"
    risk_ids = {r["risk_id"] for r in risks}
    assert risk_ids == {"LIB-RISK-01", "LIB-RISK-02"}

    # 3. Blockers and Action items extraction
    blocker_resp = client.post("/api/agents/blockers")
    assert blocker_resp.status_code == 200
    blocker_data = blocker_resp.json()
    items = blocker_data["items"]
    blockers = [i for i in items if i["item_type"] == "Blocker"]
    actions = [i for i in items if i["item_type"] == "Action Item"]
    assert len(blockers) == 1, f"Expected 1 blocker, got {len(blockers)}: {[b['item_id'] for b in blockers]}"
    assert len(actions) == 3, f"Expected 3 action items, got {len(actions)}: {[a['item_id'] for a in actions]}"

    blocker_ids = {b["item_id"] for b in blockers}
    assert blocker_ids == {"LIB-BLOCK-01"}
    action_ids = {a["item_id"] for a in actions}
    assert action_ids == {"LIB-ACT-01", "LIB-ACT-02", "LIB-ACT-03"}

    # 4. Overall project status query
    chat_resp = client.post("/api/assistant/chat", json={"question": "What is the overall project status?"})
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "On Track" in chat_data["answer"]


def test_test_c_project_isolation():
    """
    Test C: Project isolation
    Ensure that Smart Campus questions only return Smart Campus data,
    and Community Library questions only return Library data, with ZERO cross-project leakage.
    """
    # 1. Setup Smart Campus
    document_service.reset_workspace()
    for fn in ["01_Project_Charter.docx", "03_Meeting_Minutes_and_Blockers.docx", "04_Status_and_Deliverables.docx"]:
        with open(os.path.join(SCSP_DIR, fn), "rb") as f:
            client.post("/api/documents/upload", files={"files": (fn, f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    # Query Smart Campus
    r1 = client.post("/api/assistant/chat", json={"question": "What is the SMTP relay blocker?"}).json()
    assert "Rohan Das" in r1["answer"]
    assert "BLOCKER-01" in r1["answer"]
    assert "LIB" not in r1["answer"]

    r2 = client.post("/api/assistant/chat", json={"question": "Who owns the campus building list blocker?"}).json()
    assert "Arjun Mehta" in r2["answer"]
    assert "BLOCKER-02" in r2["answer"]
    assert "LIB" not in r2["answer"]

    r3 = client.post("/api/assistant/chat", json={"question": "What are the Smart Campus deliverables?"}).json()
    assert "DEL-01" in r3["answer"] or "DEL-02" in r3["answer"]
    assert "LIB-DEL" not in r3["answer"]

    r4 = client.post("/api/assistant/chat", json={"question": "Who is responsible for payment API integration?"}).json()
    assert r4["has_evidence"] is False
    assert "do not specify" in r4["answer"].lower()

    # 2. Switch to Community Library
    document_service.reset_workspace()
    for fn in ["01_Project_Overview.docx", "03_Library_Meeting_Notes.docx", "04_Library_Deliverables_Status.docx"]:
        with open(os.path.join(CLMS_DIR, fn), "rb") as f:
            client.post("/api/documents/upload", files={"files": (fn, f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    # Query Community Library
    r5 = client.post("/api/assistant/chat", json={"question": "What is the loan-period policy blocker?"}).json()
    assert "Priya Nair" in r5["answer"]
    assert "LIB-BLOCK-01" in r5["answer"]
    assert "SCSP" not in r5["answer"]

    r6 = client.post("/api/assistant/chat", json={"question": "Who owns catalog import validation?"}).json()
    assert "Ananya Bose" in r6["answer"]
    assert "LIB-ACT-02" in r6["answer"]

    r7 = client.post("/api/assistant/chat", json={"question": "What are the Library project deliverables?"}).json()
    assert "LIB-DEL" in r7["answer"]
    assert "Smart Campus" not in r7["answer"]

    # In CLMS workspace, asking about Smart Campus building list blocker must NOT leak
    r8 = client.post("/api/assistant/chat", json={"question": "Who is responsible for the campus building list blocker?"}).json()
    assert r8["has_evidence"] is False
    assert "do not specify" in r8["answer"].lower()
    assert "Arjun Mehta" not in r8["answer"]


def test_test_d_invalid_document_conflict():
    """
    Test D: Invalid document
    Upload a document containing a conflicting project ID.
    Must detect conflict, reject with HTTP 409 Conflict, and never associate with wrong project.
    """
    document_service.reset_workspace()
    # Ingest Smart Campus charter
    with open(os.path.join(SCSP_DIR, "01_Project_Charter.docx"), "rb") as f:
        resp = client.post("/api/documents/upload", files={"files": ("01_Project_Charter.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert resp.status_code in (200, 201)

    # Attempt to upload Community Library document into Smart Campus workspace
    with open(os.path.join(CLMS_DIR, "01_Project_Overview.docx"), "rb") as f:
        conflict_resp = client.post("/api/documents/upload", files={"files": ("01_Project_Overview.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    assert conflict_resp.status_code == 409
    assert "conflict" in conflict_resp.text.lower()
    assert "CLMS-2026-207" in conflict_resp.text


def test_test_e_missing_identity_safe_fallback():
    """
    Test E: Missing identity
    Upload a document without explicit project ID or project name.
    Empty workspace receives safe default workspace without inventing fake project.
    Active workspace safely inherits the active project identity.
    """
    # 1. Empty workspace upload of document without project ID
    document_service.reset_workspace()
    generic_text = "Standard Operating Procedure for Server Maintenance.\nSection 1: Daily reboot checks."
    resp1 = client.post("/api/documents/upload", files={"files": ("server_sop.txt", generic_text.encode("utf-8"), "text/plain")})
    assert resp1.status_code in (200, 201)
    data1 = resp1.json()
    assert data1["success"] is True
    # Fallback policy assigned default workspace ID
    assert data1["project_id"] == "proj_workspace_default"

    # 2. Active workspace upload of generic document inherits active identity
    document_service.reset_workspace()
    with open(os.path.join(SCSP_DIR, "01_Project_Charter.docx"), "rb") as f:
        client.post("/api/documents/upload", files={"files": ("01_Project_Charter.docx", f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    resp2 = client.post("/api/documents/upload", files={"files": ("server_sop.txt", generic_text.encode("utf-8"), "text/plain")})
    assert resp2.status_code in (200, 201)
    data2 = resp2.json()
    assert data2["project_id"] == "SCSP-2026-104"


def test_test_f_extraction_edge_cases():
    """
    Test F: Extraction edge cases
    - Empty documents (0 bytes) rejected
    - Corrupted PDFs rejected
    - Unsupported extensions rejected
    - Duplicate uploads deduplicated safely
    - Blank template headings filtered out
    """
    document_service.reset_workspace()

    # 1. Empty file
    r_empty = client.post("/api/documents/upload", files={"files": ("empty.txt", b"", "text/plain")})
    assert r_empty.status_code == 400

    # 2. Corrupted PDF
    r_corrupt = client.post("/api/documents/upload", files={"files": ("bad.pdf", b"%PDF-1.4 garbage data that cannot parse", "application/pdf")})
    assert r_corrupt.status_code == 400

    # 3. Unsupported extension
    r_unsupp = client.post("/api/documents/upload", files={"files": ("script.exe", b"binary", "application/octet-stream")})
    assert r_unsupp.status_code == 400

    # 4. Duplicate upload
    text = "Project ID: SCSP-2026-104\nSystem Architecture Overview.\nComponent 1: API gateway."
    r_first = client.post("/api/documents/upload", files={"files": ("arch.txt", text.encode("utf-8"), "text/plain")})
    assert r_first.status_code in (200, 201)
    assert r_first.json()["success"] is True

    r_dup = client.post("/api/documents/upload", files={"files": ("arch.txt", text.encode("utf-8"), "text/plain")})
    assert r_dup.status_code in (200, 201)
    # Processed cleanly without crashing or duplicate project collision
    assert len(document_service.list_documents()) == 1


def test_test_g_citation_accuracy():
    """
    Test G: Citation accuracy
    Verify that every important extracted fact and chatbot claim points to the correct source document and relevant evidence.
    """
    document_service.reset_workspace()
    for fn in ["01_Project_Charter.docx", "03_Meeting_Minutes_and_Blockers.docx"]:
        with open(os.path.join(SCSP_DIR, fn), "rb") as f:
            client.post("/api/documents/upload", files={"files": (fn, f.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    resp = client.post("/api/assistant/chat", json={"question": "What is the SMTP relay blocker?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_evidence"] is True
    assert len(data["citations"]) > 0
    cit = data["citations"][0]
    assert cit["filename"].endswith(".docx")
    assert len(cit["excerpt"]) > 10
