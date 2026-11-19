from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthIndicator(BaseModel):
    dimension: str
    raw_score: float
    weight: float
    weighted_score: float
    category: str


class DashboardHealth(BaseModel):
    overall_score: float
    status: str  # "Healthy" | "Needs Attention" | "At Risk"
    health_category: str
    indicators: List[HealthIndicator] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    missing_data_alerts: List[str] = Field(default_factory=list)


class DashboardDeliverable(BaseModel):
    deliverable_id: Optional[str] = None
    name: str
    owner: str = "UNKNOWN"
    target_date: str = "UNKNOWN"
    status: str = "Pending"
    source_ref: Optional[str] = None


class DashboardMilestone(BaseModel):
    milestone_id: Optional[str] = None
    name: str
    target_date: str = "UNKNOWN"
    owner: str = "UNKNOWN"
    status: str = "Planned"


class DashboardScope(BaseModel):
    main_goal: str
    objectives: List[str] = Field(default_factory=list)
    key_deliverables: List[DashboardDeliverable] = Field(default_factory=list)
    milestones: List[DashboardMilestone] = Field(default_factory=list)
    timeline_summary: Optional[str] = None


class DashboardRiskItem(BaseModel):
    risk_id: str
    title: str
    description: str
    severity: str  # "High" | "Medium" | "Low"
    likelihood: str
    impact: str
    owner: str
    evidence: Optional[str] = None
    source_document: Optional[str] = None
    recommended_mitigation: Optional[str] = None


class DashboardRisks(BaseModel):
    total_risks: int = 0
    overall_severity: str = "Low"
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    items: List[DashboardRiskItem] = Field(default_factory=list)


class DashboardBlockerItem(BaseModel):
    item_id: str
    description: str
    owner: str
    due_date: str
    status: str
    resolution: Optional[str] = None
    evidence: Optional[str] = None
    source_document: Optional[str] = None


class DashboardBlockers(BaseModel):
    total_blockers: int = 0
    open_count: int = 0
    resolved_count: int = 0
    items: List[DashboardBlockerItem] = Field(default_factory=list)


class DashboardActionItem(BaseModel):
    item_id: str
    description: str
    owner: str
    due_date: str
    status: str
    priority: str
    evidence: Optional[str] = None
    source_document: Optional[str] = None


class DashboardActionItems(BaseModel):
    total_actions: int = 0
    pending_count: int = 0
    completed_count: int = 0
    unassigned_count: int = 0
    items: List[DashboardActionItem] = Field(default_factory=list)


class DashboardProgress(BaseModel):
    total_deliverables: int = 0
    completed_deliverables: int = 0
    in_progress_deliverables: int = 0
    at_risk_deliverables: int = 0
    completion_percentage: float = 0.0
    overall_status: str = "On Track"  # "Healthy" | "On Track" | "Needs Attention" | "At Risk"
    pending_activities: List[str] = Field(default_factory=list)


class DashboardDocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_kb: float
    uploaded_at: str
    chunk_count: int
    char_count: int


class ProjectDashboardSummary(BaseModel):
    project_id: str
    project_name: Optional[str] = None
    client: Optional[str] = None
    document_count: int = 0
    documents: List[DashboardDocumentSummary] = Field(default_factory=list)
    has_documents: bool = False
    health: Optional[DashboardHealth] = None
    scope: Optional[DashboardScope] = None
    risks: Optional[DashboardRisks] = None
    blockers: Optional[DashboardBlockers] = None
    action_items: Optional[DashboardActionItems] = None
    progress: Optional[DashboardProgress] = None
    timestamp: str
