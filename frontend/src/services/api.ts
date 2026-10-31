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

