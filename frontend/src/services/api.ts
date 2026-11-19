/**
 * API Service for AI Project Intelligence & Risk Advisor.
 * Connects to the FastAPI backend.
 */

// Fallback to local FastAPI development server if VITE_API_BASE_URL is not set
export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string) || "http://127.0.0.1:8000";

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
  storage_ready: boolean;
  ai_pipeline_status: string;
  message: string;
}

export interface ModuleItem {
  id: number;
  key: string;
  name: string;
  category: string;
  description: string;
  status: "Implemented and Verified" | "Partially Implemented" | "Planned";
  milestone: string;
  notes: string;
}

export interface ModulesResponse {
  total_modules: number;
  implemented_count: number;
  partially_implemented_count: number;
  planned_count: number;
  modules: ModuleItem[];
}

export interface DocumentChunk {
  chunk_id: string;
  document_id: string;
  project_id?: string | null;
  source: string;
  text: string;
  page_number?: number | null;
  row_number?: number | null;
  source_ref?: string | null;
  char_count: number;
  word_count: number;
}

export interface DocumentMetadata {
  document_id: string;
  project_id?: string | null;
  project_name?: string | null;
  client?: string | null;
  is_project_inherited?: boolean;
  upload_batch_id?: string | null;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  file_size_kb: number;
  uploaded_at: string;
  page_count?: number | null;
  paragraph_count?: number | null;
  row_count?: number | null;
  column_count?: number | null;
  columns?: string[] | null;
  char_count: number;
  word_count: number;
  preview_snippet: string;
  chunk_count: number;
  chunks: DocumentChunk[];
  status: string;
  notes: string;
}

export interface FileUploadResultItem {
  filename: string;
  success: boolean;
  status: string;
  document_id?: string | null;
  project_id?: string | null;
  upload_batch_id?: string | null;
  extracted_characters: number;
  chunk_count: number;
  chunks: DocumentChunk[];
  document?: DocumentMetadata | null;
  error?: string | null;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  total_files?: number;
  successful_count?: number;
  failed_count?: number;
  document_id?: string | null;
  project_id?: string | null;
  project_name?: string | null;
  client?: string | null;
  upload_batch_id?: string | null;
  filename?: string | null;
  status: string;
  extracted_characters: number;
  chunk_count: number;
  chunks: DocumentChunk[];
  document?: DocumentMetadata | null;
  results?: FileUploadResultItem[];
}

export interface ProjectWorkspace {
  project_id: string;
  project_name?: string | null;
  client?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
  document_ids: string[];
  document_count: number;
}

// =====================================================================
// Milestone 2 Autonomous Agent Interfaces
// =====================================================================

export interface SourceCitation {
  document_id: string;
  filename: string;
  chunk_id?: string | null;
  page_number?: number | null;
  row_number?: number | null;
  source_ref: string;
  excerpt: string;
}

export interface PrimaryGoal {
  description: string;
  source_references: string[];
}

export interface SubGoal {
  id: string;
  description: string;
  source_references: string[];
}

export interface ProjectGoal {
  title: string;
  description: string;
  source_ref?: string | null;
  confidence: string;
}

export interface ScopeItem {
  description: string;
  category: "In-Scope" | "Out-of-Scope" | "General Scope";
  source_ref?: string | null;
}

export interface FunctionalRequirement {
  req_id: string;
  description: string;
  priority: string;
  module_or_category?: string | null;
  source_ref?: string | null;
}

export interface Deliverable {
  deliverable_id?: string | null;
  name: string;
  description?: string | null;
  acceptance_criteria?: string | null;
  milestone?: string | null;
  target_date?: string | null;
  owner?: string | null;
  status: string;
  source_ref?: string | null;
}

export interface Milestone {
  milestone_id: string;
  name: string;
  target_date?: string | null;
  status: string;
  owner?: string | null;
  source_ref?: string | null;
}

export interface ExplicitDeadline {
  milestone_or_task: string;
  due_date: string;
  source_ref?: string | null;
}

export interface Responsibility {
  task: string;
  owner?: string | null;
  team?: string | null;
  role?: string | null;
  source_ref?: string | null;
}

export interface Dependency {
  dependency_id?: string | null;
  dependent_item: string;
  depends_on: string;
  related_deliverable?: string | null;
  dependency_type: string;
  source_ref?: string | null;
}

export interface ScopeExtractionResponse {
  primary_goal?: PrimaryGoal | null;
  sub_goals: SubGoal[];
  project_goals: ProjectGoal[];
  scope_items: ScopeItem[];
  functional_requirements: FunctionalRequirement[];
  deliverables: Deliverable[];
  milestones: Milestone[];
  deadlines: ExplicitDeadline[];
  responsibilities: Responsibility[];
  dependencies: Dependency[];
  source_references: SourceCitation[];
  missing_information: string[];
  summary: string;
  primary_goal_count: number;
  sub_goal_count: number;
  in_scope_count: number;
  out_of_scope_count: number;
  functional_requirement_count: number;
  deliverable_count: number;
  milestone_count: number;
  dependency_count: number;
}

export interface RiskItem {
  risk_id: string;
  risk_title: string;
  description: string;
  risk_category: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  likelihood: "High" | "Medium" | "Low";
  impact: "High" | "Medium" | "Low";
  owner?: string | null;
  source_severity?: string | null;
  calculated_severity?: string | null;
  affected_milestone?: string | null;
  supporting_evidence: string;
  source_references: string[];
  recommended_mitigation: string;
  confidence: string;
  data_gaps?: string | null;
}

export interface RiskDetectionResponse {
  total_risks: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  overall_delivery_risk: "Critical" | "High" | "Elevated" | "Moderate" | "Low" | "Inconclusive";
  delivery_forecast_summary: string;
  calculation_method: string;
  limitations_note: string;
  risks: RiskItem[];
  source_references: SourceCitation[];
}

export interface DecisionItem {
  decision_id: string;
  decision_title: string;
  status: string;
  details: string;
  owner?: string | null;
  date_or_deadline?: string | null;
  source_references: string[];
}

export interface BlockerActionItem {
  item_id: string;
  item_type: "Blocker" | "Action Item" | "Pending Decision" | "Unresolved Issue";
  description: string;
  assigned_owner?: string | null;
  due_date?: string | null;
  status: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  related_milestone?: string | null;
  supporting_evidence: string;
  source_references: string[];
  recommended_next_step: string;
}

export interface BlockerExtractionResponse {
  blocker_count: number;
  action_item_count: number;
  pending_decision_count: number;
  approved_decision_count: number;
  unassigned_count: number;
  overdue_count: number;
  items: BlockerActionItem[];
  approved_decisions: DecisionItem[];
  pending_decisions: DecisionItem[];
  source_references: SourceCitation[];
  summary: string;
}

export interface ComprehensiveAnalysisResponse {
  document_ids: string[];
  analyzed_documents: string[];
  timestamp: string;
  scope: ScopeExtractionResponse;
  risks: RiskDetectionResponse;
  blockers: BlockerExtractionResponse;
}

// =====================================================================
// API Client Functions
// =====================================================================

export async function checkHealth(): Promise<HealthResponse> {
  const url = `${API_BASE_URL}/api/health`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Health check failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function getModules(): Promise<ModulesResponse> {
  const url = `${API_BASE_URL}/api/modules`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Modules fetch failed with HTTP ${response.status}`);
  }
  return response.json();
}

export class UploadApiError extends Error {
  status: number;
  isConflict: boolean;

  constructor(message: string, status: number) {
    super(message);
    this.name = "UploadApiError";
    this.status = status;
    this.isConflict = status === 409;
  }
}

export async function uploadDocument(files: File | File[]): Promise<UploadResponse> {
  const url = `${API_BASE_URL}/api/documents/upload`;
  const formData = new FormData();
  if (Array.isArray(files)) {
    for (const file of files) {
      formData.append("files", file);
    }
  } else {
    formData.append("file", files);
  }

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMessage = data.detail || `Upload failed with HTTP ${response.status}`;
    throw new UploadApiError(errorMessage, response.status);
  }
  return data as UploadResponse;
}

export async function getDocuments(): Promise<DocumentMetadata[]> {
  const url = `${API_BASE_URL}/api/documents`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to list documents: HTTP ${response.status}`);
  }
  return response.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const url = `${API_BASE_URL}/api/documents/${docId}`;
  const response = await fetch(url, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`Failed to delete document: HTTP ${response.status}`);
  }
}

export async function runScopeAgent(documentId?: string): Promise<ScopeExtractionResponse> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const url = `${API_BASE_URL}/api/agents/scope${query}`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Scope agent failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function runRiskAgent(documentId?: string): Promise<RiskDetectionResponse> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const url = `${API_BASE_URL}/api/agents/risks${query}`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Risk agent failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function runBlockerAgent(documentId?: string): Promise<BlockerExtractionResponse> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const url = `${API_BASE_URL}/api/agents/blockers${query}`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Blocker agent failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function runComprehensiveAnalysis(documentId?: string): Promise<ComprehensiveAnalysisResponse> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const url = `${API_BASE_URL}/api/agents/analyze-all${query}`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Comprehensive analysis failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function getProjectWorkspace(): Promise<ProjectWorkspace> {
  const url = `${API_BASE_URL}/api/project`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to get project workspace: HTTP ${response.status}`);
  }
  return response.json();
}

export async function resetProjectWorkspace(): Promise<{ success: boolean; message: string; project_id: string }> {
  const url = `${API_BASE_URL}/api/project/reset`;
  const response = await fetch(url, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`Failed to reset project workspace: HTTP ${response.status}`);
  }
  return response.json();
}

export async function startNewProjectWorkspace(
  projectName?: string,
  projectId?: string
): Promise<{ success: boolean; message: string; project_id: string; project_name?: string }> {
  const url = `${API_BASE_URL}/api/project/new`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_name: projectName, project_id: projectId }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to start new project workspace: HTTP ${response.status}`);
  }
  return response.json();
}

// =====================================================================
// MILESTONE 3: Documentation Generation Interfaces & API
// =====================================================================

export interface UserStory {
  story_id: string;
  user_actor: string;
  requirement: string;
  feature: string;
  expected_benefit: string;
  formatted_story: string;
  acceptance_criteria: string[];
  priority: string;
  source_document: string;
  source_evidence: string;
  source_ref?: string | null;
  review_status: "Draft" | "Approved" | "Rejected";
  is_ai_proposed?: boolean;
}

export interface RiskRegisterEntry {
  risk_id: string;
  risk_title: string;
  risk_description: string;
  cause: string;
  impact: string;
  likelihood: string;
  severity: string;
  responsible_party: string;
  mitigation_action: string;
  mitigation_type: string;
  status: string;
  source_document: string;
  supporting_evidence: string;
  source_ref?: string | null;
  review_status: "Draft" | "Approved" | "Rejected";
}

export interface ActionItemEntry {
  action_id: string;
  action_description: string;
  responsible_party: string;
  deadline: string;
  priority: string;
  status: string;
  related_blocker_or_risk?: string | null;
  source_document: string;
  supporting_evidence: string;
  source_ref?: string | null;
  review_status: "Draft" | "Approved" | "Rejected";
}

export interface DocumentationGenerationResponse {
  project_id: string;
  project_name?: string | null;
  generated_at: string;
  user_stories: UserStory[];
  risk_register: RiskRegisterEntry[];
  action_items: ActionItemEntry[];
  user_story_count: number;
  risk_count: number;
  action_item_count: number;
  summary: string;
}

export interface ItemStatusUpdateRequest {
  item_type: "user_story" | "risk" | "action_item";
  item_id: string;
  review_status: "Draft" | "Approved" | "Rejected";
  edited_fields?: Record<string, any>;
}

export async function generateDocumentation(
  documentId?: string,
  force: boolean = false
): Promise<DocumentationGenerationResponse> {
  const query = new URLSearchParams();
  if (documentId) query.set("document_id", documentId);
  if (force) query.set("force", "true");
  const url = `${API_BASE_URL}/api/agents/generate-docs?${query.toString()}`;
  const response = await fetch(url, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Documentation generation failed with HTTP ${response.status}`);
  }
  return response.json();
}

export async function getCurrentDocumentation(): Promise<DocumentationGenerationResponse> {
  const url = `${API_BASE_URL}/api/agents/documentation`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to fetch documentation with HTTP ${response.status}`);
  }
  return response.json();
}

export async function updateDocItemReview(
  req: ItemStatusUpdateRequest
): Promise<{ success: boolean; message: string }> {
  const url = `${API_BASE_URL}/api/agents/doc-item/update`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Item update failed with HTTP ${response.status}`);
  }
  return response.json();
}

export function getExportDocsUrl(exportType: string, format: string = "csv"): string {
  return `${API_BASE_URL}/api/agents/export-docs?export_type=${encodeURIComponent(exportType)}&format=${encodeURIComponent(format)}`;
}

// =====================================================================
// MILESTONE 3: Project Health Scoring Interfaces & API
// =====================================================================

export interface HealthScoreDimension {
  dimension_name: string;
  weight: number;
  raw_score: number;
  weighted_score: number;
  category: "Healthy" | "Needs Attention" | "At Risk" | "Critical" | "Insufficient Data";
  explanation: string;
  contributing_factors: string[];
  critical_issues: string[];
}

export interface HealthSnapshot {
  snapshot_id: string;
  project_id: string;
  timestamp: string;
  overall_score?: number | null;
  health_category: string;
  scope_score: number;
  timeline_score: number;
  blocker_score: number;
}

export interface ProjectHealthResponse {
  project_id: string;
  project_name?: string | null;
  calculated_at: string;
  overall_score?: number | null;
  health_category: "Healthy" | "Needs Attention" | "At Risk" | "Critical" | "Insufficient Data";
  is_insufficient_data: boolean;
  weights: Record<string, number>;
  scope_clarity: HealthScoreDimension;
  timeline_health: HealthScoreDimension;
  blocker_health: HealthScoreDimension;
  critical_issues: string[];
  recommended_corrective_actions: string[];
  missing_information: string[];
  historical_snapshots: HealthSnapshot[];
}

export async function getProjectHealth(
  documentId?: string,
  weights?: Record<string, number>
): Promise<ProjectHealthResponse> {
  const query = new URLSearchParams();
  if (documentId) query.set("document_id", documentId);
  const url = `${API_BASE_URL}/api/health-score?${query.toString()}`;
  const response = await fetch(url, {
    method: weights ? "POST" : "GET",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: weights ? JSON.stringify(weights) : undefined,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Failed to calculate project health: HTTP ${response.status}`);
  }
  return response.json();
}

export async function getHealthScoreHistory(): Promise<HealthSnapshot[]> {
  const url = `${API_BASE_URL}/api/health-score/history`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to fetch health history: HTTP ${response.status}`);
  }
  return response.json();
}

// =====================================================================
// MILESTONE 3: Conversational Assistant Interfaces & API
// =====================================================================

export interface ChatMessage {
  message_id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  citations: SourceCitation[];
  has_evidence: boolean;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
  project_id?: string;
}

export interface ChatResponse {
  answer: string;
  citations: SourceCitation[];
  has_evidence: boolean;
  conversation_id: string;
  project_id: string;
  timestamp: string;
  suggested_followups: string[];
}

export interface ConversationHistoryResponse {
  conversation_id: string;
  project_id: string;
  messages: ChatMessage[];
}

export async function chatWithAssistant(req: ChatRequest): Promise<ChatResponse> {
  const url = `${API_BASE_URL}/api/assistant/chat`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Chat request failed: HTTP ${response.status}`);
  }
  return response.json();
}

export async function getAssistantHistory(conversationId?: string): Promise<ConversationHistoryResponse> {
  const query = conversationId ? `?conversation_id=${encodeURIComponent(conversationId)}` : "";
  const url = `${API_BASE_URL}/api/assistant/history${query}`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to fetch chat history: HTTP ${response.status}`);
  }
  return response.json();
}

export async function clearAssistantConversation(
  conversationId?: string
): Promise<{ success: boolean; message: string }> {
  const query = conversationId ? `?conversation_id=${encodeURIComponent(conversationId)}` : "";
  const url = `${API_BASE_URL}/api/assistant/clear${query}`;
  const response = await fetch(url, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Failed to clear conversation: HTTP ${response.status}`);
  }
  return response.json();
}

// =====================================================================
// Milestone 4 Project Insights & Risk Summary Dashboard
// =====================================================================

export interface HealthIndicator {
  dimension: string;
  raw_score: number;
  weight: number;
  weighted_score: number;
  category: string;
}

export interface DashboardHealth {
  overall_score: number;
  status: "Healthy" | "Needs Attention" | "At Risk" | string;
  health_category: string;
  indicators: HealthIndicator[];
  recommendations: string[];
  missing_data_alerts: string[];
}

export interface DashboardDeliverable {
  deliverable_id: string;
  name: string;
  owner: string;
  target_date: string;
  status: string;
  source_ref?: string | null;
}

export interface DashboardMilestone {
  milestone_id: string;
  name: string;
  target_date: string;
  owner: string;
  status: string;
}

export interface DashboardScope {
  main_goal: string;
  objectives: string[];
  key_deliverables: DashboardDeliverable[];
  milestones: DashboardMilestone[];
  timeline_summary?: string | null;
}

export interface DashboardRiskItem {
  risk_id: string;
  title: string;
  description: string;
  severity: "High" | "Medium" | "Low" | string;
  likelihood: string;
  impact: string;
  owner: string;
  evidence?: string | null;
  source_document?: string | null;
  recommended_mitigation?: string | null;
}

export interface DashboardRisks {
  total_risks: number;
  overall_severity: string;
  high_count: number;
  medium_count: number;
  low_count: number;
  items: DashboardRiskItem[];
}

export interface DashboardBlockerItem {
  item_id: string;
  description: string;
  owner: string;
  due_date: string;
  status: string;
  resolution?: string | null;
  evidence?: string | null;
  source_document?: string | null;
}

export interface DashboardBlockers {
  total_blockers: number;
  open_count: number;
  resolved_count: number;
  items: DashboardBlockerItem[];
}

export interface DashboardActionItem {
  item_id: string;
  description: string;
  owner: string;
  due_date: string;
  status: string;
  priority: string;
  evidence?: string | null;
  source_document?: string | null;
}

export interface DashboardActionItems {
  total_actions: number;
  pending_count: number;
  completed_count: number;
  unassigned_count: number;
  items: DashboardActionItem[];
}

export interface DashboardProgress {
  total_deliverables: number;
  completed_deliverables: number;
  in_progress_deliverables: number;
  at_risk_deliverables: number;
  completion_percentage: number;
  overall_status: string;
  pending_activities: string[];
}

export interface DashboardDocumentSummary {
  document_id: string;
  filename: string;
  file_type: string;
  file_size_kb: number;
  uploaded_at: string;
  chunk_count: number;
  char_count: number;
}

export interface ProjectDashboardSummary {
  project_id: string;
  project_name?: string | null;
  client?: string | null;
  document_count: number;
  documents: DashboardDocumentSummary[];
  has_documents: boolean;
  health?: DashboardHealth | null;
  scope?: DashboardScope | null;
  risks?: DashboardRisks | null;
  blockers?: DashboardBlockers | null;
  action_items?: DashboardActionItems | null;
  progress?: DashboardProgress | null;
  timestamp: string;
}

export async function getDashboardSummary(documentId?: string): Promise<ProjectDashboardSummary> {
  const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
  const url = `${API_BASE_URL}/api/dashboard/summary${query}`;
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Failed to fetch project dashboard summary: HTTP ${response.status}`);
  }
  return response.json();
}


