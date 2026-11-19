from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.agent_models import SourceCitation


# =====================================================================
# MODULE 1: Documentation Generation Agent Models
# =====================================================================

class UserStory(BaseModel):
    """Structured Agile user story grounded in project documents."""

    story_id: str = Field(..., description="Unique story ID (e.g. US-01)")
    user_actor: str = Field(..., description="User or actor persona (e.g. Student, Project Manager)")
    requirement: str = Field(..., description="Core requirement statement")
    feature: str = Field(..., description="Feature to be developed")
    expected_benefit: str = Field(..., description="Value or benefit delivered")
    formatted_story: str = Field(
        ..., description="Standard Agile format: As a [user], I want [feature], so that [benefit]."
    )
    acceptance_criteria: List[str] = Field(
        default_factory=list,
        description="Measurable Given-When-Then criteria. AI-proposed criteria are clearly tagged.",
    )
    priority: str = Field("Must Have", description="Priority: Must Have, Should Have, Could Have")
    source_document: str = Field(..., description="Source document filename")
    source_evidence: str = Field(..., description="Grounding quotation or excerpt from document")
    source_ref: Optional[str] = Field(None, description="Human-readable citation (e.g. Page 2, Row 4)")
    review_status: str = Field("Draft", description="Review state: Draft, Approved, Rejected")
    is_ai_proposed: bool = Field(False, description="Whether requirement details require user review")


class RiskRegisterEntry(BaseModel):
    """Structured Risk Register entry reusing Risk Agent intelligence."""

    risk_id: str = Field(..., description="Risk identifier (e.g. RR-01)")
    risk_title: str = Field(..., description="Concise risk title")
    risk_description: str = Field(..., description="Detailed description of the risk scenario")
    cause: str = Field(..., description="Root cause of the risk")
    impact: str = Field(..., description="Business or technical impact")
    likelihood: str = Field("Medium", description="Likelihood: Low, Medium, High")
    severity: str = Field("Medium", description="Severity: Low, Medium, High, Critical")
    responsible_party: str = Field("Not specified", description="Responsible person or team if documented")
    mitigation_action: str = Field(..., description="Actionable mitigation strategy")
    mitigation_type: str = Field("Documented", description="Documented or AI-proposed")
    status: str = Field("Open", description="Risk status: Open, Mitigated, In Review")
    source_document: str = Field(..., description="Source document filename")
    supporting_evidence: str = Field(..., description="Direct citation or excerpt from source document")
    source_ref: Optional[str] = Field(None, description="Coordinate citation")
    review_status: str = Field("Draft", description="Review state: Draft, Approved, Rejected")


class ActionItemEntry(BaseModel):
    """Structured Action Item entry extracted from meeting notes and project updates."""

    action_id: str = Field(..., description="Action identifier (e.g. ACT-01)")
    action_description: str = Field(..., description="Specific action to execute")
    responsible_party: str = Field("Not specified", description="Assigned person or team")
    deadline: str = Field("Not specified", description="Target completion deadline")
    priority: str = Field("Medium", description="Priority: High, Medium, Low")
    status: str = Field("Open", description="Status: Open, In Progress, Completed, Pending Decision")
    related_blocker_or_risk: Optional[str] = Field(None, description="Associated blocker or risk ID")
    source_document: str = Field(..., description="Source document filename")
    supporting_evidence: str = Field(..., description="Direct quotation from source document")
    source_ref: Optional[str] = Field(None, description="Coordinate citation")
    review_status: str = Field("Draft", description="Review state: Draft, Approved, Rejected")


class DocumentationGenerationResponse(BaseModel):
    """Consolidated response from the Documentation Generation Agent."""

    project_id: str = Field(..., description="Project workspace identifier")
    project_name: Optional[str] = Field(None, description="Project name")
    generated_at: str = Field(..., description="ISO 8601 generation timestamp")
    user_stories: List[UserStory] = Field(default_factory=list, description="Synthesized Agile user stories")
    risk_register: List[RiskRegisterEntry] = Field(default_factory=list, description="Structured risk register")
    action_items: List[ActionItemEntry] = Field(default_factory=list, description="Extracted actionable tasks")
    user_story_count: int = Field(0, description="Count of user stories")
    risk_count: int = Field(0, description="Count of risk register entries")
    action_item_count: int = Field(0, description="Count of action items")
    summary: str = Field("", description="Executive summary of documentation generation")


class ItemStatusUpdateRequest(BaseModel):
    """Request model for approving, rejecting, or updating review status of an item."""

    item_type: str = Field(..., description="'user_story', 'risk', or 'action_item'")
    item_id: str = Field(..., description="Identifier of the item to update")
    review_status: str = Field(..., description="'Approved', 'Rejected', or 'Draft'")
    edited_fields: Optional[Dict[str, Any]] = Field(None, description="Optional updated field values")


# =====================================================================
# MODULE 2: Project Health Scoring Models
# =====================================================================

class HealthScoreDimension(BaseModel):
    """Component dimension contributing to overall project health."""

    dimension_name: str = Field(..., description="Dimension title: Scope Clarity, Timeline Health, Blocker Health")
    weight: float = Field(..., description="Configurable decimal weight (e.g. 0.35)")
    raw_score: float = Field(..., description="Raw score between 0.0 and 100.0")
    weighted_score: float = Field(..., description="Score contribution = raw_score * weight")
    category: str = Field(..., description="Healthy, Needs Attention, At Risk, Critical, Insufficient Data")
    explanation: str = Field(..., description="Transparent mathematical breakdown and justification")
    contributing_factors: List[str] = Field(default_factory=list, description="Specific elements that contributed to score")
    critical_issues: List[str] = Field(default_factory=list, description="Issues directly pulling the score down")


class HealthSnapshot(BaseModel):
    """Historical snapshot of project health score."""

    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    project_id: str = Field(..., description="Project workspace ID")
    timestamp: str = Field(..., description="ISO 8601 calculation timestamp")
    overall_score: Optional[float] = Field(None, description="Composite health score (0-100)")
    health_category: str = Field(..., description="Healthy, Needs Attention, At Risk, Critical, Insufficient Data")
    scope_score: float = Field(..., description="Scope clarity score")
    timeline_score: float = Field(..., description="Timeline health score")
    blocker_score: float = Field(..., description="Blocker health score")


class ProjectHealthResponse(BaseModel):
    """Complete project health evaluation output."""

    project_id: str = Field(..., description="Project workspace identifier")
    project_name: Optional[str] = Field(None, description="Project name")
    calculated_at: str = Field(..., description="ISO 8601 calculation timestamp")
    overall_score: Optional[float] = Field(None, description="Composite score between 0.0 and 100.0")
    health_category: str = Field(..., description="Healthy, Needs Attention, At Risk, Critical, Insufficient Data")
    documented_status: Optional[str] = Field(None, description="Documented overall project status from status reports")
    is_insufficient_data: bool = Field(False, description="True if project lacks sufficient documents for evaluation")
    weights: Dict[str, float] = Field(..., description="Active weight configuration used")
    scope_clarity: HealthScoreDimension = Field(..., description="Scope clarity evaluation")
    timeline_health: HealthScoreDimension = Field(..., description="Timeline health evaluation")
    blocker_health: HealthScoreDimension = Field(..., description="Blocker and action health evaluation")
    critical_issues: List[str] = Field(default_factory=list, description="High-priority risks or active blockers")
    recommended_corrective_actions: List[str] = Field(default_factory=list, description="Evidence-backed corrective recommendations")
    missing_information: List[str] = Field(default_factory=list, description="Data gaps preventing more accurate scoring")
    historical_snapshots: List[HealthSnapshot] = Field(default_factory=list, description="Recent historical score trajectory")


# =====================================================================
# MODULE 3: Conversational Project Intelligence Assistant Models
# =====================================================================

class ChatRequest(BaseModel):
    """User question submitted to the Conversational Project Intelligence Assistant."""

    question: str = Field(..., min_length=1, description="Natural language question about the project")
    conversation_id: Optional[str] = Field(None, description="Optional conversation session ID")
    project_id: Optional[str] = Field(None, description="Target project ID (defaults to active workspace)")


class ChatMessage(BaseModel):
    """A single turn in the conversational dialogue."""

    message_id: str = Field(..., description="Unique message UUID")
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    timestamp: str = Field(..., description="ISO 8601 message timestamp")
    citations: List[SourceCitation] = Field(default_factory=list, description="Provenance citations for assistant response")
    has_evidence: bool = Field(True, description="Whether answer is grounded in document evidence")


class ChatResponse(BaseModel):
    """Assistant reply to a project question."""

    answer: str = Field(..., description="Grounded natural language answer")
    citations: List[SourceCitation] = Field(default_factory=list, description="Direct supporting citations")
    has_evidence: bool = Field(True, description="Whether document evidence was found")
    conversation_id: str = Field(..., description="Conversation session ID")
    project_id: str = Field(..., description="Active project workspace ID")
    timestamp: str = Field(..., description="ISO 8601 response timestamp")
    suggested_followups: List[str] = Field(default_factory=list, description="Contextual follow-up questions")


class ConversationHistoryResponse(BaseModel):
    """Full dialogue history for the active project."""

    conversation_id: str = Field(..., description="Conversation session ID")
    project_id: str = Field(..., description="Active project workspace ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chronological dialogue turns")
