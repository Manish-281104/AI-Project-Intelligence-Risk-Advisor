from typing import List, Optional
from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    """Source provenance tracking back to uploaded documents and coordinates."""

    document_id: str = Field(..., description="Source document identifier")
    filename: str = Field(..., description="Source filename")
    chunk_id: Optional[str] = Field(None, description="Specific chunk ID if matched")
    page_number: Optional[int] = Field(None, description="PDF page number if applicable")
    row_number: Optional[int] = Field(None, description="CSV / table row number if applicable")
    source_ref: str = Field(..., description="Human-readable citation label (e.g. 'Page 2', 'Row 5')")
    excerpt: str = Field(..., description="Exact textual excerpt from the source chunk")


# =====================================================================
# AGENT 1: Scope and Deliverable Extraction Models
# =====================================================================

class PrimaryGoal(BaseModel):
    """Overarching primary project goal."""

    description: str = Field(..., description="Primary overarching project goal")
    source_references: List[str] = Field(default_factory=list, description="Grounding source citations")


class SubGoal(BaseModel):
    """Supporting sub-goal or objective."""

    id: str = Field(..., description="Sub-goal identifier (e.g. SG-01)")
    description: str = Field(..., description="Supporting objective / sub-goal description")
    source_references: List[str] = Field(default_factory=list, description="Grounding source citations")


class ProjectGoal(BaseModel):
    """Extracted high-level project goal or objective (backward-compatible)."""

    title: str = Field(..., description="Concise goal title")
    description: str = Field(..., description="Detailed goal or objective description")
    source_ref: Optional[str] = Field(None, description="Document source citation")
    confidence: str = Field("High", description="Extraction confidence (High, Medium, Low)")


class ScopeItem(BaseModel):
    """Project scope boundary item."""

    description: str = Field(..., description="Scope statement or requirement")
    category: str = Field("In-Scope", description="Scope category: 'In-Scope', 'Out-of-Scope', or 'General Scope'")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class FunctionalRequirement(BaseModel):
    """Functional system requirement extracted from specifications or requirements table."""

    req_id: str = Field(..., description="Functional requirement ID (e.g. FR-01)")
    description: str = Field(..., description="Requirement description")
    priority: str = Field("High", description="Priority level: High, Medium, Low")
    module_or_category: Optional[str] = Field(None, description="Functional module or domain")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class Deliverable(BaseModel):
    """Expected project deliverable with owner and deadline information."""

    deliverable_id: Optional[str] = Field(None, description="Deliverable identifier (e.g. D-01)")
    name: str = Field(..., description="Name of deliverable")
    description: Optional[str] = Field(None, description="Deliverable details")
    acceptance_criteria: Optional[str] = Field(None, description="Explicit acceptance criteria")
    milestone: Optional[str] = Field(None, description="Associated milestone or phase")
    target_date: Optional[str] = Field(None, description="Target delivery date or 'UNKNOWN'")
    owner: Optional[str] = Field(None, description="Assigned owner/team or 'UNKNOWN'")
    status: str = Field("Planned", description="Current status: Planned, In Progress, Completed, Not Started, Unknown")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class Milestone(BaseModel):
    """Project milestone schedule item."""

    milestone_id: str = Field(..., description="Milestone identifier (e.g. M-01, MS-01)")
    name: str = Field(..., description="Milestone name or title")
    target_date: Optional[str] = Field(None, description="Target completion date or 'UNKNOWN'")
    status: str = Field("Planned", description="Status: Planned, In Progress, Completed, At Risk, Not Started, Unknown")
    owner: Optional[str] = Field(None, description="Milestone owner / lead")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class ExplicitDeadline(BaseModel):
    """Explicitly stated deadline extracted from text."""

    milestone_or_task: str = Field(..., description="Item subject to deadline")
    due_date: str = Field(..., description="Stated deadline or date string")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class Responsibility(BaseModel):
    """Assigned responsibility, owner, or team explicitly stated in documents."""

    task: str = Field(..., description="Task or deliverable name")
    owner: Optional[str] = Field(None, description="Assigned person name or 'UNKNOWN'")
    team: Optional[str] = Field(None, description="Assigned team/role or 'UNKNOWN'")
    role: Optional[str] = Field(None, description="Role title if specified")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class Dependency(BaseModel):
    """Task or deliverable dependency relationship."""

    dependency_id: Optional[str] = Field(None, description="Dependency identifier (e.g. DEP-01)")
    dependent_item: str = Field(..., description="The task or deliverable that depends on another")
    depends_on: str = Field(..., description="The prerequisite task, deliverable, or external factor")
    related_deliverable: Optional[str] = Field(None, description="Related deliverable identifier if applicable")
    dependency_type: str = Field("Prerequisite", description="Dependency relationship type: Prerequisite, Technical, Resource")
    source_ref: Optional[str] = Field(None, description="Document source citation")


class ScopeExtractionResponse(BaseModel):
    """Validated output of the Scope and Deliverable Extraction Agent."""

    primary_goal: Optional[PrimaryGoal] = Field(None, description="Overarching primary project goal")
    sub_goals: List[SubGoal] = Field(default_factory=list, description="Supporting sub-goals / objectives")
    project_goals: List[ProjectGoal] = Field(default_factory=list, description="Project goals and objectives (backward-compatible)")
    scope_items: List[ScopeItem] = Field(default_factory=list, description="In-scope and out-of-scope boundaries")
    functional_requirements: List[FunctionalRequirement] = Field(default_factory=list, description="Functional requirements")
    deliverables: List[Deliverable] = Field(default_factory=list, description="Expected deliverables")
    milestones: List[Milestone] = Field(default_factory=list, description="Project milestones")
    deadlines: List[ExplicitDeadline] = Field(default_factory=list, description="Explicit deadlines found")
    responsibilities: List[Responsibility] = Field(default_factory=list, description="Stated task responsibilities")
    dependencies: List[Dependency] = Field(default_factory=list, description="Dependencies between tasks/deliverables")
    source_references: List[SourceCitation] = Field(default_factory=list, description="Grounding source citations")
    missing_information: List[str] = Field(default_factory=list, description="Identified data gaps and missing elements")
    summary: str = Field("", description="Executive summary of scope findings")
    primary_goal_count: int = Field(0, description="Count of primary goals")
    sub_goal_count: int = Field(0, description="Count of sub-goals")
    in_scope_count: int = Field(0, description="Count of in-scope statements")
    out_of_scope_count: int = Field(0, description="Count of out-of-scope statements")
    functional_requirement_count: int = Field(0, description="Count of functional requirements")
    deliverable_count: int = Field(0, description="Count of deliverables")
    milestone_count: int = Field(0, description="Count of milestones")
    dependency_count: int = Field(0, description="Count of dependencies")


# =====================================================================
# AGENT 2: Risk Detection and Delivery Forecasting Models
# =====================================================================

class RiskItem(BaseModel):
    """Individual project risk item grounded in document evidence."""

    risk_id: str = Field(..., description="Unique risk identifier (e.g. R-01, RSK-001)")
    risk_title: str = Field(..., description="Concise risk title")
    description: str = Field(..., description="Detailed description of the risk scenario")
    risk_category: str = Field(..., description="Category: Schedule, Resource, Dependency, Technical, Scope")
    severity: str = Field(..., description="Severity level: Low, Medium, High, Critical")
    likelihood: str = Field(..., description="Likelihood assessment: Low, Medium, High")
    impact: str = Field(..., description="Impact assessment: Low, Medium, High")
    owner: Optional[str] = Field("Unassigned", description="Assigned risk owner")
    source_severity: Optional[str] = Field(None, description="Original severity stated in source document")
    calculated_severity: Optional[str] = Field(None, description="Calculated severity from Likelihood x Impact matrix")
    affected_milestone: Optional[str] = Field(None, description="Affected milestone or deliverable, if any")
    supporting_evidence: str = Field(..., description="Verbatim or grounded factual passage from document")
    source_references: List[str] = Field(default_factory=list, description="Document filenames and coordinates")
    recommended_mitigation: str = Field(..., description="Actionable mitigation recommendation")
    confidence: str = Field("Medium", description="Confidence in assessment: High, Medium, Low")
    data_gaps: Optional[str] = Field(None, description="Limitations or missing data that prevent further precision")


class RiskDetectionResponse(BaseModel):
    """Validated output of the Risk Detection and Delivery Forecasting Agent."""

    total_risks: int = Field(0, description="Total identified risks")
    critical_count: int = Field(0, description="Count of critical risks")
    high_count: int = Field(0, description="Count of high risks")
    medium_count: int = Field(0, description="Count of medium risks")
    low_count: int = Field(0, description="Count of low risks")
    overall_delivery_risk: str = Field(
        "Moderate",
        description="Overall project delivery risk level: Low, Moderate, Elevated, High, Critical, Inconclusive"
    )
    delivery_forecast_summary: str = Field(
        ...,
        description="Qualitative delivery forecast derived strictly from document facts without invented percentages"
    )
    calculation_method: str = Field(
        ...,
        description="Deterministic calculation method and qualitative risk matrix explanation"
    )
    limitations_note: str = Field(
        ...,
        description="Explicit limitation note regarding data availability and absence of synthetic forecasting"
    )
    risks: List[RiskItem] = Field(default_factory=list, description="List of identified risk items")
    source_references: List[SourceCitation] = Field(default_factory=list, description="Source provenance citations")


# =====================================================================
# AGENT 3: Blocker and Action Item Identification Models
# =====================================================================

class DecisionItem(BaseModel):
    """Recorded project decision (approved or pending)."""

    decision_id: str = Field(..., description="Decision identifier (e.g. DEC-01)")
    decision_title: str = Field(..., description="Decision title or summary")
    status: str = Field("Approved", description="Decision status: Approved, Pending, Deferred")
    details: str = Field(..., description="Context, scope bounds, or exclusions")
    owner: Optional[str] = Field(None, description="Decision maker or accountable owner")
    date_or_deadline: Optional[str] = Field(None, description="Approval date or pending decision target date")
    source_references: List[str] = Field(default_factory=list, description="Source citations")


class BlockerActionItem(BaseModel):
    """Blocker, pending decision, or action item extracted from project documents."""

    item_id: str = Field(..., description="Unique item identifier (e.g. A-01, ACT-001, BLK-001)")
    item_type: str = Field(..., description="Item type: Blocker, Action Item, Pending Decision, Unresolved Issue")
    description: str = Field(..., description="Description of the blocker, action, or decision")
    assigned_owner: Optional[str] = Field("UNKNOWN", description="Explicit owner name or 'UNKNOWN'")
    due_date: Optional[str] = Field("UNKNOWN", description="Explicit target deadline or 'UNKNOWN'")
    status: str = Field("Open", description="Status: Open, Blocked, In Progress, Completed, Not Started, Pending Decision, Pending Review, Unknown")
    priority: str = Field("Medium", description="Priority level: Critical, High, Medium, Low")
    related_milestone: Optional[str] = Field(None, description="Related milestone or task if stated")
    supporting_evidence: str = Field(..., description="Direct quote or grounded passage from document")
    source_references: List[str] = Field(default_factory=list, description="Source citations")
    recommended_next_step: str = Field(..., description="Actionable next step for resolution")


class BlockerExtractionResponse(BaseModel):
    """Validated output of the Blocker and Action Item Identification Agent."""

    blocker_count: int = Field(0, description="Count of active blockers")
    action_item_count: int = Field(0, description="Count of actionable tasks / action register entries")
    pending_decision_count: int = Field(0, description="Count of unresolved decisions")
    approved_decision_count: int = Field(0, description="Count of approved resolved decisions")
    unassigned_count: int = Field(0, description="Count of items lacking an assigned owner")
    overdue_count: int = Field(0, description="Count of items with past deadlines")
    items: List[BlockerActionItem] = Field(default_factory=list, description="Extracted blockers and actions")
    approved_decisions: List[DecisionItem] = Field(default_factory=list, description="Approved project decisions")
    pending_decisions: List[DecisionItem] = Field(default_factory=list, description="Pending project decisions")
    source_references: List[SourceCitation] = Field(default_factory=list, description="Source citations")
    summary: str = Field("", description="Executive summary of blocker and action findings")


# =====================================================================
# Comprehensive Multi-Agent Analysis Model
# =====================================================================

class ComprehensiveAnalysisResponse(BaseModel):
    """Consolidated response combining outputs from all three autonomous agents."""

    document_ids: List[str] = Field(..., description="IDs of documents included in analysis")
    analyzed_documents: List[str] = Field(..., description="Filenames of documents analyzed")
    timestamp: str = Field(..., description="ISO 8601 analysis timestamp")
    scope: ScopeExtractionResponse = Field(..., description="Scope and deliverable findings")
    risks: RiskDetectionResponse = Field(..., description="Risk and forecasting findings")
    blockers: BlockerExtractionResponse = Field(..., description="Blocker and action item findings")
