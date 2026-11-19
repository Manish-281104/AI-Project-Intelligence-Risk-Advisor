import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.document_service import document_service
from app.services.docgen_agent import docgen_agent
from app.services.health_scoring_service import health_scoring_service
from app.services.chat_assistant_service import chat_assistant_service

client = TestClient(app)

SAMPLE_CHARTER = b"""Project Name: Campus Event Management Portal (CEMP)
Client: Greenfield University
1. Project Overview & Primary Goal
The primary overarching goal is to build an automated, web-based Campus Event Management Portal that enables students and faculty to discover, register for, and manage academic events.

2. Scope Boundaries
In-Scope: Student event registration, calendar view, attendance verification, and automated email confirmation.
Out-of-Scope: Third-party commercial ticketing, payment gateway processing, and external vendor catering.

3. Functional Requirements
FR-01: The system shall allow students to browse published campus events. Priority: High.
FR-02: The system shall allow event organizers to create and publish event schedules. Priority: High.
FR-03: The system shall provide QR-code attendance check-in for registered participants. Priority: High.
FR-04: The system shall generate PDF certificates of participation after event completion. Priority: Medium.

4. Deliverables and Schedule
D-01: Requirements Specification Document (Target: 2026-10-15, Owner: Manish)
D-02: Core Event Registration Engine (Target: 2026-10-25, Owner: Development Team)
D-03: Automated QR Attendance Scanner (Target: 2026-10-30, Owner: Manish)
"""

SAMPLE_MINUTES = b"""Meeting Title: CEMP Sprint 2 Standup and Risk Review
Date: October 28, 2026

Risks and Impediments:
1. Vendor API Integration Delay: The third-party campus student directory API documentation is incomplete, creating a high schedule risk for authentication integration.
2. Server Provisioning: University IT has not yet approved the staging Docker cluster deployment.

Action Items:
1. Finalize payment API fallback and test mock endpoint. Assigned to: Backend Team. Due Date: Friday.
2. Approve staging Docker deployment. Assigned to: IT Director. Due Date: 2026-11-02.
3. Update user registration wireframe. Assigned to: UNKNOWN. Due Date: UNKNOWN.

Pending Decisions:
DEC-01: Single-Sign-On Provider Selection (OAuth2 vs SAML2). Details: Deciding between Azure AD and Google Workspace. Target: 2026-10-30.
"""


@pytest.fixture(autouse=True)
def setup_workspace():
    """Ensure clean test workspace with sample documents."""
    document_service.reset_workspace()
    # Ingest test documents
    client.post(
        "/api/documents/upload",
        files={"file": ("project_charter.txt", io.BytesIO(SAMPLE_CHARTER), "text/plain")},
    )
    client.post(
        "/api/documents/upload",
        files={"file": ("meeting_minutes.txt", io.BytesIO(SAMPLE_MINUTES), "text/plain")},
    )
    yield
    document_service.reset_workspace()


# =====================================================================
# 1. MODULE 1: Documentation Generation Agent Tests
# =====================================================================

def test_generate_user_stories():
    """Verify synthesis of Agile user stories with Given-When-Then acceptance criteria."""
    response = client.post("/api/agents/generate-user-stories?force=true")
    assert response.status_code == 200
    stories = response.json()
    assert len(stories) >= 3

    # Check structure of stories
    first_story = stories[0]
    assert "story_id" in first_story
    assert first_story["story_id"].startswith("US-")
    assert "user_actor" in first_story
    assert len(first_story["user_actor"]) > 0
    assert "formatted_story" in first_story
    assert first_story["formatted_story"].startswith("As a ")
    assert ", I want " in first_story["formatted_story"]
    assert ", so that " in first_story["formatted_story"]
    assert "acceptance_criteria" in first_story
    assert len(first_story["acceptance_criteria"]) >= 2
    # Check Given-When-Then formatting
    assert any("Given " in c for c in first_story["acceptance_criteria"])
    assert any("When " in c for c in first_story["acceptance_criteria"])
    assert any("Then " in c for c in first_story["acceptance_criteria"])
    assert first_story["review_status"] == "Draft"
    assert "source_document" in first_story
    assert "source_evidence" in first_story


def test_generate_risk_register():
    """Verify structured risk register generation distinguishing documented from AI mitigation."""
    response = client.post("/api/agents/generate-risk-register?force=true")
    assert response.status_code == 200
    risks = response.json()
    assert len(risks) >= 1

    first_risk = risks[0]
    assert "risk_id" in first_risk
    assert first_risk["risk_id"].startswith("RR-")
    assert "risk_title" in first_risk
    assert "cause" in first_risk
    assert "impact" in first_risk
    assert "likelihood" in first_risk
    assert "severity" in first_risk
    assert "mitigation_action" in first_risk
    assert "mitigation_type" in first_risk
    assert first_risk["status"] == "Open"
    assert "supporting_evidence" in first_risk
    assert first_risk["review_status"] == "Draft"


def test_generate_action_items():
    """Verify action item extraction with responsible party and deadline handling."""
    response = client.post("/api/agents/generate-action-items?force=true")
    assert response.status_code == 200
    actions = response.json()
    assert len(actions) >= 2

    # Check unassigned / missing deadline handling
    assert any(a["responsible_party"] != "" for a in actions)
    assert any(a["deadline"] != "" for a in actions)
    for a in actions:
        assert a["action_id"].startswith("ACT-")
        assert a["review_status"] == "Draft"
        assert len(a["action_description"]) > 0


def test_doc_item_review_approval_and_editing():
    """Verify approving and editing a generated documentation item."""
    # First generate docs
    gen_res = client.post("/api/agents/generate-docs?force=true")
    assert gen_res.status_code == 200
    docs = gen_res.json()
    assert len(docs["user_stories"]) > 0

    target_story = docs["user_stories"][0]
    story_id = target_story["story_id"]

    # Approve item
    update_res = client.post(
        "/api/agents/doc-item/update",
        json={
            "item_type": "user_story",
            "item_id": story_id,
            "review_status": "Approved",
            "edited_fields": {"priority": "Must Have"},
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["success"] is True

    # Retrieve docs and verify status
    get_res = client.get("/api/agents/documentation")
    assert get_res.status_code == 200
    updated_stories = get_res.json()["user_stories"]
    matched = next(s for s in updated_stories if s["story_id"] == story_id)
    assert matched["review_status"] == "Approved"


def test_export_documentation_csv():
    """Verify CSV export for user stories, risk register, and action items."""
    # Ensure generated
    client.post("/api/agents/generate-docs?force=true")

    # Export stories
    res_stories = client.get("/api/agents/export-docs?export_type=user_stories&format=csv")
    assert res_stories.status_code == 200
    assert "text/csv" in res_stories.headers["content-type"]
    assert "Story ID" in res_stories.text
    assert "US-01" in res_stories.text

    # Export risk register
    res_risks = client.get("/api/agents/export-docs?export_type=risk_register&format=csv")
    assert res_risks.status_code == 200
    assert "Risk ID" in res_risks.text
    assert "RR-01" in res_risks.text

    # Export action items
    res_actions = client.get("/api/agents/export-docs?export_type=action_items&format=csv")
    assert res_actions.status_code == 200
    assert "Action ID" in res_actions.text
    assert "ACT-01" in res_actions.text


# =====================================================================
# 2. MODULE 2: Project Health Scoring Tests
# =====================================================================

def test_project_health_calculation_deterministic():
    """Verify deterministic mathematical health score calculation (Scope 35%, Timeline 35%, Blocker 30%)."""
    response = client.get("/api/health-score")
    assert response.status_code == 200
    data = response.json()

    assert "overall_score" in data
    assert data["overall_score"] is not None
    assert 0.0 <= data["overall_score"] <= 100.0

    # Verify formula: overall = round((scope * 0.35) + (timeline * 0.35) + (blocker * 0.30), 1)
    scope_w = data["scope_clarity"]["weighted_score"]
    timeline_w = data["timeline_health"]["weighted_score"]
    blocker_w = data["blocker_health"]["weighted_score"]
    expected_overall = round(scope_w + timeline_w + blocker_w, 1)
    assert abs(data["overall_score"] - expected_overall) <= 0.2

    # Verify health categories
    assert data["health_category"] in ("Healthy", "Needs Attention", "At Risk", "Critical")
    assert len(data["scope_clarity"]["contributing_factors"]) > 0
    assert len(data["historical_snapshots"]) >= 1


def test_project_health_custom_weights():
    """Verify health score responds properly to custom user-configured dimension weights."""
    custom_weights = {"scope_clarity": 0.50, "timeline_health": 0.25, "blocker_health": 0.25}
    response = client.post("/api/health-score", json=custom_weights)
    assert response.status_code == 200
    data = response.json()

    assert data["weights"]["scope_clarity"] == 0.5
    assert data["weights"]["timeline_health"] == 0.25
    assert data["weights"]["blocker_health"] == 0.25


def test_project_health_insufficient_data_empty_workspace():
    """Verify empty workspace returns Insufficient Data rather than fabricated score."""
    document_service.reset_workspace()
    response = client.get("/api/health-score")
    assert response.status_code == 200
    data = response.json()

    assert data["is_insufficient_data"] is True
    assert data["health_category"] == "Insufficient Data"
    assert data["overall_score"] is None
    assert len(data["missing_information"]) > 0


def test_health_score_history_persistence():
    """Verify that multiple health calculations persist in history snapshots."""
    client.get("/api/health-score")
    client.get("/api/health-score")
    history_res = client.get("/api/health-score/history")
    assert history_res.status_code == 200
    snapshots = history_res.json()
    assert len(snapshots) >= 1
    assert "snapshot_id" in snapshots[0]
    assert "timestamp" in snapshots[0]


# =====================================================================
# 3. MODULE 3: Conversational Assistant Tests
# =====================================================================

def test_conversational_assistant_grounded_qa():
    """Verify assistant answers grounded project questions with source citations."""
    queries = [
        "What are our biggest risks?",
        "What are the current blockers?",
        "Who is responsible for the payment API?",
        "What is the current project health?",
        "What deliverables are pending?",
    ]

    for q in queries:
        response = client.post("/api/assistant/chat", json={"question": q})
        assert response.status_code == 200
        data = response.json()
        assert len(data["answer"]) > 0
        assert data["has_evidence"] is True
        assert len(data["citations"]) > 0
        assert "filename" in data["citations"][0]
        assert len(data["suggested_followups"]) > 0


def test_conversational_assistant_strict_fallback_no_evidence():
    """Verify assistant strictly refuses to answer when information is not in uploaded documents."""
    unrelated_question = "What is the orbital trajectory of the Mars rover cryptocurrency blockchain?"
    response = client.post("/api/assistant/chat", json={"question": unrelated_question})
    assert response.status_code == 200
    data = response.json()
    # Must use official fallback phrasing
    assert "couldn't find enough information" in data["answer"].lower()
    assert data["has_evidence"] is False
    assert len(data["citations"]) == 0


def test_conversational_assistant_conversation_history_and_clear():
    """Verify assistant records dialogue turns and allows clearing."""
    client.post("/api/assistant/chat", json={"question": "What is our primary goal?"})
    hist_res = client.get("/api/assistant/history")
    assert hist_res.status_code == 200
    messages = hist_res.json()["messages"]
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    # Clear conversation
    clear_res = client.post("/api/assistant/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["success"] is True

    # Check history is now empty
    hist_after = client.get("/api/assistant/history")
    assert len(hist_after.json()["messages"]) == 0
