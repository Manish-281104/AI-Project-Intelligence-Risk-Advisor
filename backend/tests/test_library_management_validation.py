import io
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_service import document_service

client = TestClient(app)


def test_library_management_system_full_validation():
    """
    Rigorously validates the 14 Ground Truth requirements for
    Project_Management_Agent_Test_Document_2.docx:
    - Project: LIB-2026-008, Community Library Management System, Greenfield Community Library
    - Primary Goal: Exactly 1
    - Sub-Goals: Exactly 5 (SG-01 to SG-05)
    - In-Scope Items: Exactly 8
    - Out-of-Scope Items: Exactly 4
    - Functional Requirements: Exactly 8 (FR-01 to FR-08)
    - Deliverables: Exactly 9 (D-01 to D-09)
    - Milestones: Exactly 6 (M-01 to M-06)
    - Dependencies: Exactly 4 (DEP-01 to DEP-04)
    - Documented Risks: Exactly 4 (R-01 to R-04)
    - Calculated Severity: High = 4, Critical = 0
    - Active Blockers: Exactly 1 (BLK-01)
    - Action Register: Exactly 5 (A-01 to A-05)
    - Pending Decisions: Exactly 1
    - Approved Decisions: Exactly 1
    - Unassigned Items: Exactly 0
    - Overdue Tasks: Exactly 0 (relative to 20 October 2026)
    - Project Isolation: Zero bleed from Campus Event Management Portal
    """
    # 1. Reset workspace to ensure complete isolation
    document_service.reset_workspace()

    # 2. Locate test document
    sample_path = Path("sample_documents/Project_Management_Agent_Test_Document_2.docx")
    if not sample_path.exists():
        sample_path = Path("../sample_documents/Project_Management_Agent_Test_Document_2.docx")
    if not sample_path.exists():
        sample_path = Path(__file__).resolve().parent.parent.parent / "sample_documents" / "Project_Management_Agent_Test_Document_2.docx"
    assert sample_path.exists(), f"Sample test document not found at {sample_path}"

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    # 3. Upload document
    files = {
        "file": (
            "Project_Management_Agent_Test_Document_2.docx",
            io.BytesIO(file_bytes),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    up_res = client.post("/api/documents/upload", files=files)
    assert up_res.status_code == 201
    up_data = up_res.json()
    doc_id = up_data["document_id"]
    assert doc_id is not None

    # Verify project identity extracted from document metadata
    ws_res = client.get("/api/project")
    assert ws_res.status_code == 200
    ws_data = ws_res.json()
    assert ws_data["project_id"] == "LIB-2026-008"
    assert ws_data["project_name"] == "Community Library Management System"
    assert ws_data["client"] == "Greenfield Community Library"

    # =========================================================================
    # AGENT 1: Scope, Goals, Sub-Goals, Deliverables, Milestones, Dependencies
    # =========================================================================
    scope_res = client.post(f"/api/agents/scope?document_id={doc_id}")
    assert scope_res.status_code == 200
    scope_data = scope_res.json()

    # Metric 1: Primary Goal == 1
    assert scope_data["primary_goal"] is not None
    assert "community library management system" in scope_data["primary_goal"]["description"].lower()
    assert "paper-based" in scope_data["primary_goal"]["description"].lower()
    # Ensure goal count in project_goals is exactly 1 (not 19 or counting sub-goals)
    assert len(scope_data["project_goals"]) == 1

    # Metric 2: Sub-Goals == 5 (SG-01 to SG-05)
    assert len(scope_data["sub_goals"]) == 5, f"Expected 5 sub-goals, got {len(scope_data['sub_goals'])}"
    sub_ids = [sg["id"] for sg in scope_data["sub_goals"]]
    assert sub_ids == ["SG-01", "SG-02", "SG-03", "SG-04", "SG-05"]

    # Metric 3: In-Scope == 8
    in_scope_items = [it for it in scope_data["scope_items"] if it["category"] == "In-Scope"]
    assert len(in_scope_items) == 8, f"Expected 8 in-scope items, got {len(in_scope_items)}"

    # Metric 4: Out-of-Scope == 4
    out_scope_items = [it for it in scope_data["scope_items"] if it["category"] == "Out-of-Scope"]
    assert len(out_scope_items) == 4, f"Expected 4 out-of-scope items, got {len(out_scope_items)}"

    # Metric 5: Functional Requirements == 8 (FR-01 to FR-08)
    assert len(scope_data["functional_requirements"]) == 8, f"Expected 8 FRs, got {len(scope_data['functional_requirements'])}"
    fr_ids = [fr["req_id"] for fr in scope_data["functional_requirements"]]
    for i in range(1, 9):
        assert f"FR-0{i}" in fr_ids

    # Metric 6: Deliverables == 9 (D-01 to D-09)
    assert len(scope_data["deliverables"]) == 9, f"Expected 9 deliverables, got {len(scope_data['deliverables'])}"
    deliv_identifiers = [f"{d.get('deliverable_id', '')} {d.get('name', '')}" for d in scope_data["deliverables"]]
    for i in range(1, 10):
        assert any(f"D-0{i}" in ident for ident in deliv_identifiers), f"Missing D-0{i}"

    # Metric 7: Milestones == 6 (M-01 to M-06)
    assert len(scope_data["milestones"]) == 6, f"Expected 6 milestones, got {len(scope_data['milestones'])}"
    ms_ids = [m["milestone_id"] for m in scope_data["milestones"]]
    for i in range(1, 7):
        assert f"M-0{i}" in ms_ids

    # Metric 8: Dependencies == 4 (DEP-01 to DEP-04)
    assert len(scope_data["dependencies"]) == 4, f"Expected 4 dependencies, got {len(scope_data['dependencies'])}"
    dep_identifiers = [f"{dep.get('dependency_id', '')} {dep.get('dependent_item', '')}" for dep in scope_data["dependencies"]]
    for i in range(1, 5):
        assert any(f"DEP-0{i}" in ident for ident in dep_identifiers), f"Missing DEP-0{i}"

    # Verify no bleed from other projects
    assert "Campus Event" not in str(scope_data)

    # =========================================================================
    # AGENT 2: Risk Detection & Qualitative Forecasting
    # =========================================================================
    risk_res = client.post(f"/api/agents/risks?document_id={doc_id}")
    assert risk_res.status_code == 200
    risk_data = risk_res.json()

    # Metric 9: Documented Risks == 4 (R-01 to R-04)
    assert len(risk_data["risks"]) == 4, f"Expected 4 documented risks, got {len(risk_data['risks'])}"
    risk_ids = [r["risk_id"] for r in risk_data["risks"]]
    for i in range(1, 5):
        assert f"R-0{i}" in risk_ids

    # Metric 10: Calculated Severity: High = 4, Critical = 0
    assert risk_data["critical_count"] == 0, f"Expected 0 critical risks, got {risk_data['critical_count']}"
    assert risk_data["high_count"] == 4, f"Expected 4 high risks, got {risk_data['high_count']}"

    # Verify qualitative forecast
    assert not re.search(r"\b\d{2,3}%\s+chance\b", risk_data["delivery_forecast_summary"])
    assert "Campus Event" not in str(risk_data)

    # =========================================================================
    # AGENT 3: Blockers, Action Register, and Decisions
    # =========================================================================
    blocker_res = client.post(f"/api/agents/blockers?document_id={doc_id}")
    assert blocker_res.status_code == 200
    blocker_data = blocker_res.json()

    # Metric 11: Active Blockers == 1 (BLK-01: Email service credentials, Meera Nair, 21 Oct 2026)
    assert blocker_data["blocker_count"] == 1, f"Expected 1 active blocker, got {blocker_data['blocker_count']}"
    blocker_item = next(it for it in blocker_data["items"] if it["item_type"] == "Blocker")
    assert "BLK-01" in blocker_item["item_id"]
    assert "email" in blocker_item["description"].lower()
    assert "Meera Nair" in blocker_item["assigned_owner"]
    assert "21 Oct 2026" in blocker_item["due_date"] or "2026-10-21" in blocker_item["due_date"]

    # Metric 12: Action Register == 5 (A-01 to A-05 from Table 6)
    action_items = [it for it in blocker_data["items"] if it["item_type"] == "Action Item"]
    assert len(action_items) == 5, f"Expected 5 action items, got {len(action_items)}"
    action_ids = [it["item_id"] for it in action_items]
    for i in range(1, 6):
        assert f"A-0{i}" in action_ids

    # Metric 13: Pending Decisions == 1
    assert blocker_data["pending_decision_count"] == 1, f"Expected 1 pending decision, got {blocker_data['pending_decision_count']}"
    pending_items = [it for it in blocker_data["items"] if it["item_type"] == "Pending Decision"]
    assert len(pending_items) == 1
    assert "cancel" in pending_items[0]["description"].lower()
    assert "reservation" in pending_items[0]["description"].lower()
    assert "Meera Nair" in pending_items[0]["assigned_owner"]

    # Metric 14: Approved Decisions == 1
    assert len(blocker_data["approved_decisions"]) == 1, f"Expected 1 approved decision, got {len(blocker_data['approved_decisions'])}"
    app_dec = blocker_data["approved_decisions"][0]
    assert "authentication" in app_dec["decision_title"].lower() or "auth" in app_dec["decision_title"].lower()
    assert "email" in app_dec["details"].lower()

    # Unassigned Items == 0
    assert blocker_data["unassigned_count"] == 0, f"Expected 0 unassigned items, got {blocker_data['unassigned_count']}"

    # Overdue Tasks == 0 (relative to 20 October 2026 reporting date)
    assert blocker_data["overdue_count"] == 0, f"Expected 0 overdue tasks, got {blocker_data['overdue_count']}"
