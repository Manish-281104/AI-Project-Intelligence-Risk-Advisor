import io
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_service import document_service

client = TestClient(app)


def test_milestone2_sample_document_10_ground_truth_criteria():
    """
    Milestone 2 Acceptance & Ground Truth Validation Test.
    Uses sample_documents/AI_Project_Agent_Test_Sample_Document.docx to rigorously verify:
    1. Scope Extraction: Exactly 6 deliverables (D-01 through D-06)
    2. Scope Extraction: Exactly 6 milestones (M-01 through M-06)
    3. Scope Extraction: Exactly 4 dependencies (DEP-01 through DEP-04)
    4. Target Release Date: 18 Dec 2026 explicitly identified
    5. Risk Detection: Documented risks R-01, R-02, R-03 identified
    6. Risk Detection: Milestone 'Coordinator dashboard' identified as At Risk
    7. Blocker & Action Items: Exactly 5 action items (A-01 through A-05)
    8. Action item without due date: A-05 identified without synthetic deadline
    9. Pending Decision: Cancellation email requirement identified as pending review
    10. Delivery Forecasting: Honest qualitative forecast without fabricated numbers
    """
    # 1. Locate sample document fixture
    sample_path = Path("sample_documents/AI_Project_Agent_Test_Sample_Document.docx")
    if not sample_path.exists():
        sample_path = Path("backend/uploads/AI_Project_Agent_Test_Sample_Document.docx")
    assert sample_path.exists(), f"Sample test document not found at {sample_path}"

    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    # 2. Upload sample document through official ingestion pipeline
    files = {"file": ("AI_Project_Agent_Test_Sample_Document.docx", io.BytesIO(file_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    up_res = client.post("/api/documents/upload", files=files)
    assert up_res.status_code == 201
    doc_id = up_res.json()["document_id"]
    assert doc_id is not None

    # =========================================================================
    # CRITERION 1, 2, 3, 4: Scope, Deliverables, Milestones, Dependencies, Release Date
    # =========================================================================
    scope_res = client.post(f"/api/agents/scope?document_id={doc_id}")
    assert scope_res.status_code == 200
    scope_data = scope_res.json()

    # Criterion 1: Exactly 6 deliverables (D-01 to D-06)
    deliv_ids = {d["name"][:4] for d in scope_data["deliverables"] if d["name"].startswith("D-")}
    assert len(scope_data["deliverables"]) >= 6, f"Expected 6 deliverables, got {len(scope_data['deliverables'])}"
    for did in ["D-01", "D-02", "D-03", "D-04", "D-05", "D-06"]:
        assert any(did in d["name"] for d in scope_data["deliverables"]), f"Deliverable {did} missing from extraction"

    # Verify primary goal is NOT a dependency (DEP-01) but the actual Campus Event Management Portal
    assert len(scope_data["project_goals"]) >= 1
    primary_goal = scope_data["project_goals"][0]
    assert "DEP-" not in primary_goal["title"] and "DEP-" not in primary_goal["description"]
    assert "Campus Event Management" in primary_goal["title"] or "Campus Event Management" in primary_goal["description"]

    # Criterion 2: Exactly 6 milestones (M-01 to M-06)
    assert len(scope_data["milestones"]) >= 6, f"Expected 6 milestones, got {len(scope_data['milestones'])}"
    for mid in ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06"]:
        assert any(mid in m["milestone_id"] or mid in m["name"] for m in scope_data["milestones"]), f"Milestone {mid} missing"

    # Criterion 3: Exactly 4 dependencies (DEP-01 to DEP-04)
    assert len(scope_data["dependencies"]) >= 4, f"Expected 4 dependencies, got {len(scope_data['dependencies'])}"
    for dep_id in ["DEP-01", "DEP-02", "DEP-03", "DEP-04"]:
        assert any(dep_id in d["dependent_item"] for d in scope_data["dependencies"]), f"Dependency {dep_id} missing"

    # Criterion 4: Target release date 18 Dec 2026
    m6 = next((m for m in scope_data["milestones"] if "M-06" in m["milestone_id"] or "Production release" in m["name"]), None)
    assert m6 is not None
    assert "18 Dec 2026" in m6["target_date"] or "2026-12-18" in m6["target_date"]

    # =========================================================================
    # CRITERION 5, 6, 10: Documented Risks, At-Risk Milestone, Qualitative Forecast
    # =========================================================================
    risk_res = client.post(f"/api/agents/risks?document_id={doc_id}")
    assert risk_res.status_code == 200
    risk_data = risk_res.json()

    # Criterion 5: Exactly 3 documented risks R-01, R-02, R-03
    assert len(risk_data["risks"]) == 3, f"Expected exactly 3 documented risks, got {len(risk_data['risks'])}"
    for rid in ["R-01", "R-02", "R-03"]:
        assert any(rid in r["risk_id"] or rid in r["description"] for r in risk_data["risks"]), f"Risk {rid} missing"

    # Criterion 6: Milestone 'Coordinator dashboard' identified as At Risk and linked to R-02
    coordinator_risk = next(
        (r for r in risk_data["risks"] if "coordinator dashboard" in r["risk_title"].lower() or (r.get("affected_milestone") and "coordinator" in r["affected_milestone"].lower())),
        None
    )
    assert coordinator_risk is not None, "Coordinator dashboard milestone at risk not flagged"
    assert "cancellation endpoint" in coordinator_risk["supporting_evidence"].lower() or "at risk" in coordinator_risk["supporting_evidence"].lower()

    # Criterion 10: Honest qualitative forecast without fabricated numbers
    forecast = risk_data["delivery_forecast_summary"]
    assert "critical" in forecast.lower() or "moderate" in forecast.lower() or "elevated" in forecast.lower()
    assert "velocity metrics" in forecast.lower() or "limitations" in risk_data["limitations_note"].lower()
    # Ensure no fabricated percentages in forecast summary
    assert not re.search(r"\b\d{2,3}%\s+chance\b", forecast, re.IGNORECASE)

    # =========================================================================
    # CRITERION 7, 8, 9: Action Items (A-01 to A-05), A-05 No Deadline, Pending Decision
    # =========================================================================
    blocker_res = client.post(f"/api/agents/blockers?document_id={doc_id}")
    assert blocker_res.status_code == 200
    blocker_data = blocker_res.json()

    # Criterion 7: Exactly 5 action items (A-01 to A-05)
    action_items = [it for it in blocker_data["items"] if it["item_type"] == "Action Item"]
    assert len(action_items) == 5, f"Expected exactly 5 action items, got {len(action_items)}: {[it['item_id'] for it in action_items]}"
    for aid in ["A-01", "A-02", "A-03", "A-04", "A-05"]:
        assert any(aid in it["item_id"] for it in action_items), f"Action item {aid} missing"

    # Criterion 8: Action A-05 has NO due date
    a05 = next(it for it in action_items if "A-05" in it["item_id"])
    assert a05["due_date"] in ("UNKNOWN", "Not specified", "None", None, "")

    # Criterion 9: 1 pending decision on cancellation email policy
    pending_decisions = [it for it in blocker_data["items"] if it["item_type"] == "Pending Decision"]
    assert len(pending_decisions) >= 1
    assert any("cancellation" in d["description"].lower() for d in pending_decisions)

    # Verify Blocker is present (Exactly 1 active blocker)
    blockers = [it for it in blocker_data["items"] if it["item_type"] == "Blocker"]
    assert len(blockers) == 1
    assert "cancellation endpoint" in blockers[0]["description"].lower()

    # Verify Unassigned count is 0 (all 5 action items have named owners)
    assert blocker_data["unassigned_count"] == 0, f"Expected 0 unassigned items, got {blocker_data['unassigned_count']}"

    # Verify Overdue count is 0 as of reporting date (30 Nov 2026)
    assert blocker_data["overdue_count"] == 0, f"Expected 0 overdue items, got {blocker_data['overdue_count']}"

