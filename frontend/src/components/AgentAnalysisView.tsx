import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Target,
  ShieldAlert,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  Clock,
  Calendar,
  User,
  ArrowRight,
  HelpCircle,
  AlertTriangle,
  Compass,
  Filter,
  CheckSquare,
  FolderGit2,
  Building2,
} from "lucide-react";
import {
  runComprehensiveAnalysis,
  getDocuments,
  getProjectWorkspace,
  ComprehensiveAnalysisResponse,
  DocumentMetadata,
  ProjectWorkspace,
} from "../services/api";

interface AgentAnalysisViewProps {
  workspaceVersion?: number;
}

export const AgentAnalysisView: React.FC<AgentAnalysisViewProps> = ({ workspaceVersion = 0 }) => {
  const [analysisData, setAnalysisData] = useState<ComprehensiveAnalysisResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [workspace, setWorkspace] = useState<ProjectWorkspace | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string>("all");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"scope" | "risks" | "blockers">("scope");
  const [blockerFilter, setBlockerFilter] = useState<string>("all");

  const loadDocumentsList = async () => {
    try {
      const [docs, ws] = await Promise.all([
        getDocuments(),
        getProjectWorkspace().catch(() => null),
      ]);
      setDocuments(docs);
      if (ws) setWorkspace(ws);
    } catch {
      // Backend may be starting up
    }
  };

  useEffect(() => {
    loadDocumentsList();
  }, []);

  // When workspace changes (new project, reset, document added/removed), refresh metadata and invalidate active analysis
  useEffect(() => {
    if (workspaceVersion > 0) {
      loadDocumentsList();
      setAnalysisData(null);
      setSelectedDocId("all");
      setErrorMessage(null);
    }
  }, [workspaceVersion]);

  const handleRunAnalysis = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const docFilter = selectedDocId === "all" ? undefined : selectedDocId;
      const result = await runComprehensiveAnalysis(docFilter);
      setAnalysisData(result);
    } catch (err) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Analysis failed due to unexpected backend communication error.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "badge-severity-critical";
      case "high":
        return "badge-severity-high";
      case "medium":
        return "badge-severity-medium";
      default:
        return "badge-severity-low";
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "critical":
        return "risk-banner-critical";
      case "high":
        return "risk-banner-high";
      case "elevated":
        return "risk-banner-elevated";
      case "moderate":
        return "risk-banner-moderate";
      default:
        return "risk-banner-low";
    }
  };

  const filteredBlockers = analysisData?.blockers.items.filter((item) => {
    if (blockerFilter === "all") return true;
    if (blockerFilter === "approved") return false;
    return item.item_type.toLowerCase().includes(blockerFilter.toLowerCase());
  }) || [];

  return (
    <div className="agent-analysis-section" id="ai-advisor">
      {/* Header */}
      <div className="section-header">
        <span className="section-eyebrow">Project Intelligence</span>
        <h2 className="section-title">AI Risk & Intelligence Analysis</h2>
        <p className="section-desc">
          Automated analysis extracting project scope, deliverables, schedule risks, blockers, and action items
          grounded in document evidence.
        </p>
      </div>

      {/* Active Project Workspace Indicator */}
      <div className="workspace-context-bar" style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "0.75rem",
        padding: "0.8rem 1.1rem",
        marginBottom: "1rem",
        background: "rgba(15, 23, 42, 0.6)",
        border: "1px solid var(--border-color)",
        borderRadius: "var(--radius-md)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <FolderGit2 size={18} style={{ color: "var(--accent-primary)" }} />
          <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--text-primary)" }}>
            Project: {workspace?.project_name || "Workspace Project"}
          </span>
          <span className="badge badge-milestone font-mono">
            ID: {workspace?.project_id || "proj_workspace_default"}
          </span>
          {workspace?.client && (
            <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Building2 size={13} style={{ color: "var(--accent-primary)" }} />
              <span>Client: <strong>{workspace.client}</strong></span>
            </span>
          )}
        </div>
        <div style={{ fontSize: "0.8rem", color: "var(--accent-emerald)", fontWeight: 600 }}>
          <span>Unified Knowledge Base ({documents.length} docs indexed)</span>
        </div>
      </div>

      {/* Control Action Bar */}
      <div className="agent-controls-card">
        <div className="controls-left">
          <div className="control-group">
            <label htmlFor="doc-select" className="control-label">
              Document Scope:
            </label>
            <select
              id="doc-select"
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="doc-select-input"
              disabled={isLoading}
            >
              <option value="all">All Documents ({documents.length} files — Unified Project Knowledge Base)</option>
              {documents.map((doc) => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.filename} ({doc.chunk_count} chunks)
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="controls-right">
          <button
            onClick={handleRunAnalysis}
            disabled={isLoading}
            className="btn-run-analysis"
          >
            {isLoading ? (
              <>
                <RefreshCw size={17} className="spin-icon" />
                <span>Analyzing Project...</span>
              </>
            ) : (
              <>
                <Sparkles size={17} />
                <span>Run Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="error-banner">
          <AlertTriangle className="error-icon" size={20} />
          <div className="error-text">
            <strong>Advisor Error:</strong> {errorMessage}
          </div>
          <button onClick={() => setErrorMessage(null)} className="btn-dismiss">
            Dismiss
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="agent-tabs-header">
        <button
          className={`agent-tab-btn ${activeTab === "scope" ? "active" : ""}`}
          onClick={() => setActiveTab("scope")}
        >
          <Target size={17} />
          <span>Scope</span>
          {analysisData && (
            <span className="tab-pill">
              {analysisData.scope.primary_goal ? 1 : analysisData.scope.project_goals.length}
            </span>
          )}
        </button>

        <button
          className={`agent-tab-btn ${activeTab === "risks" ? "active" : ""}`}
          onClick={() => setActiveTab("risks")}
        >
          <ShieldAlert size={17} />
          <span>Risks</span>
          {analysisData && (
            <span className="tab-pill alert">{analysisData.risks.total_risks}</span>
          )}
        </button>

        <button
          className={`agent-tab-btn ${activeTab === "blockers" ? "active" : ""}`}
          onClick={() => setActiveTab("blockers")}
        >
          <AlertCircle size={17} />
          <span>Blockers & Action Items</span>
          {analysisData && (
            <span className="tab-pill">
              {analysisData.blockers.items.length + (analysisData.blockers.approved_decisions?.length || 0)}
            </span>
          )}
        </button>
      </div>

      {/* Loading Skeleton View */}
      {isLoading && (
        <div className="agent-loading-card">
          <RefreshCw size={36} className="spin-icon text-blue" />
          <h3>Executing Autonomous Multi-Agent Reasoning</h3>
          <p>
            RAG similarity retriever is searching document chunks, calculating schedule deltas against project
            deadlines, and generating validated Pydantic outputs with source citations...
          </p>
        </div>
      )}

      {/* Empty State before first run */}
      {!isLoading && !analysisData && (
        <div className="agent-empty-card">
          <div className="empty-icon-circle">
            <Compass size={40} className="text-blue" />
          </div>
          <h3>{documents.length === 0 ? "No Documents in Current Workspace" : "Multi-Agent Intelligence Ready"}</h3>
          <p>
            {documents.length === 0
              ? "Upload project documents (PDF, DOCX, CSV, TXT) in the Upload Documents section above to build your project knowledge base and run autonomous intelligence analysis."
              : "Click Run Analysis below to execute autonomous Multi-Agent reasoning (Scope, Deliverables, Schedule Risks, and Blockers) grounded in document evidence."}
          </p>
          {documents.length > 0 ? (
            <button onClick={handleRunAnalysis} className="btn-primary" style={{ marginTop: "1rem" }}>
              <Sparkles size={16} /> Run Analysis Now
            </button>
          ) : (
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "0.5rem" }}>
              Awaiting project document upload...
            </span>
          )}
        </div>
      )}

      {/* Results View */}
      {!isLoading && analysisData && (
        <div className="agent-results-wrapper">
          {/* ======================================================== */}
          {/* TAB 1: Scope & Deliverables */}
          {/* ======================================================== */}
          {activeTab === "scope" && (
            <div className="tab-panel">
              {/* Scope Metrics Row */}
              <div className="metrics-strip">
                <div className="metric-box">
                  <span className="metric-val">
                    {analysisData.scope.primary_goal ? 1 : (analysisData.scope.project_goals.length > 0 ? 1 : 0)}
                  </span>
                  <span className="metric-lbl">Primary Goal</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">{analysisData.scope.sub_goals?.length || 0}</span>
                  <span className="metric-lbl">Sub-Goals</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">
                    {analysisData.scope.scope_items.filter((i) => i.category === "In-Scope").length}
                  </span>
                  <span className="metric-lbl">In-Scope Items</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">
                    {analysisData.scope.scope_items.filter((i) => i.category === "Out-of-Scope").length}
                  </span>
                  <span className="metric-lbl">Out-of-Scope</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">{analysisData.scope.functional_requirements?.length || 0}</span>
                  <span className="metric-lbl">Requirements</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">{analysisData.scope.deliverables.length}</span>
                  <span className="metric-lbl">Deliverables</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">{analysisData.scope.milestones.length}</span>
                  <span className="metric-lbl">Milestones</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val">{analysisData.scope.dependencies.length}</span>
                  <span className="metric-lbl">Dependencies</span>
                </div>
              </div>

              {/* Summary */}
              {analysisData.scope.summary && (
                <div className="agent-summary-box">
                  <div className="summary-title">
                    <Target size={16} className="text-blue" /> Executive Scope Synthesis
                  </div>
                  <p>{analysisData.scope.summary}</p>
                </div>
              )}

              {/* Primary Project Goal Card */}
              {analysisData.scope.primary_goal && (
                <div className="primary-goal-card">
                  <div className="primary-goal-header">
                    <Target size={20} style={{ color: "var(--accent-primary)" }} />
                    <span className="primary-goal-badge">Primary Project Goal</span>
                    {analysisData.scope.primary_goal.source_references && analysisData.scope.primary_goal.source_references.length > 0 && (
                      <span className="source-citation-inline font-mono">
                        {analysisData.scope.primary_goal.source_references.join(" • ")}
                      </span>
                    )}
                  </div>
                  <p className="primary-goal-desc">{analysisData.scope.primary_goal.description}</p>
                </div>
              )}

              {/* Supporting Sub-Goals Section */}
              {analysisData.scope.sub_goals && analysisData.scope.sub_goals.length > 0 ? (
                <div className="content-card">
                  <h4 className="content-card-title">
                    <CheckCircle2 size={18} className="text-emerald" /> Supporting Sub-Goals & Objectives ({analysisData.scope.sub_goals.length})
                  </h4>
                  <div className="sub-goals-grid">
                    {analysisData.scope.sub_goals.map((sg) => (
                      <div key={sg.id} className="sub-goal-card">
                        <div className="sub-goal-header">
                          <span className="sub-goal-id-pill font-mono">{sg.id}</span>
                          {sg.source_references && sg.source_references.length > 0 && (
                            <span className="source-citation-inline font-mono">
                              {sg.source_references.join(" • ")}
                            </span>
                          )}
                        </div>
                        <p className="sub-goal-desc">{sg.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : analysisData.scope.project_goals.length > 0 && (
                <div className="content-card">
                  <h4 className="content-card-title">
                    <CheckCircle2 size={18} className="text-emerald" /> Project Goals & Objectives
                  </h4>
                  <div className="goals-grid">
                    {analysisData.scope.project_goals.map((g, idx) => (
                      <div key={idx} className="goal-item-card">
                        <div className="goal-title">{g.title}</div>
                        <p className="goal-desc">{g.description}</p>
                        {g.source_ref && (
                          <div className="source-citation-tag">
                            Source: <span>{g.source_ref}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Functional Requirements Register */}
              {analysisData.scope.functional_requirements && analysisData.scope.functional_requirements.length > 0 && (
                <div className="content-card">
                  <h4 className="content-card-title">
                    <CheckSquare size={18} className="text-blue" /> Functional Requirements Register ({analysisData.scope.functional_requirements.length})
                  </h4>
                  <div className="table-wrapper">
                    <table className="agent-data-table">
                      <thead>
                        <tr>
                          <th style={{ width: "95px" }}>ID</th>
                          <th style={{ width: "230px" }}>Requirement Name</th>
                          <th>Specification & Scope Description</th>
                          <th style={{ width: "120px" }}>Priority</th>
                          <th style={{ width: "160px" }}>Citation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisData.scope.functional_requirements.map((fr) => (
                          <tr key={fr.req_id}>
                            <td className="font-mono font-semibold" style={{ color: "var(--accent-primary)" }}>
                              {fr.req_id}
                            </td>
                            <td className="font-semibold text-primary">{fr.module_or_category || fr.req_id}</td>
                            <td>{fr.description}</td>
                            <td>
                              <span className={`status-pill ${fr.priority.toLowerCase().includes("must") || fr.priority.toLowerCase().includes("high") ? "in-progress" : "planned"}`}>
                                {fr.priority}
                              </span>
                            </td>
                            <td className="citation-cell">
                              {fr.source_ref || "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Scope Boundaries */}
              {analysisData.scope.scope_items.length > 0 && (
                <div className="content-card">
                  <h4 className="content-card-title">
                    <Compass size={18} className="text-blue" /> Scope Boundaries (In-Scope vs. Out-of-Scope)
                  </h4>
                  <div className="scope-items-list">
                    {analysisData.scope.scope_items.map((item, idx) => (
                      <div key={idx} className="scope-item-row">
                        <span
                          className={`scope-tag ${
                            item.category === "Out-of-Scope" ? "out-scope" : "in-scope"
                          }`}
                        >
                          {item.category}
                        </span>
                        <span className="scope-desc">{item.description}</span>
                        {item.source_ref && (
                          <span className="source-citation-inline">{item.source_ref}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Deliverables Table */}
              <div className="content-card">
                <h4 className="content-card-title">
                  <CheckSquare size={18} className="text-blue" /> Extracted Deliverables Register
                </h4>
                {analysisData.scope.deliverables.length === 0 ? (
                  <p className="text-muted">No explicit deliverables identified in analyzed documents.</p>
                ) : (
                  <div className="table-wrapper">
                    <table className="agent-data-table">
                      <thead>
                        <tr>
                          <th>Deliverable Name</th>
                          <th>Milestone</th>
                          <th>Assigned Owner</th>
                          <th>Target Date</th>
                          <th>Status</th>
                          <th>Citation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisData.scope.deliverables.map((d, idx) => (
                          <tr key={idx}>
                            <td className="font-semibold text-primary">{d.name}</td>
                            <td>{d.milestone || <span className="text-muted">General</span>}</td>
                            <td>
                              {d.owner && d.owner !== "UNKNOWN" ? (
                                <span className="user-tag">
                                  <User size={12} /> {d.owner}
                                </span>
                              ) : (
                                <span className="badge-unknown">UNKNOWN</span>
                              )}
                            </td>
                            <td>
                              {d.target_date && d.target_date !== "UNKNOWN" ? (
                                <span className="date-tag">
                                  <Calendar size={12} /> {d.target_date}
                                </span>
                              ) : (
                                <span className="badge-unknown">UNKNOWN</span>
                              )}
                            </td>
                            <td>
                              <span className={`status-pill ${d.status.toLowerCase().replace(/\s+/g, "-")}`}>
                                {d.status}
                              </span>
                            </td>
                            <td className="citation-cell">{d.source_ref || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Dependencies & Milestones Row */}
              <div className="two-col-grid">
                {/* Milestones */}
                <div className="content-card">
                  <h4 className="content-card-title">
                    <Clock size={18} className="text-blue" /> Project Milestones
                  </h4>
                  {analysisData.scope.milestones.length === 0 ? (
                    <p className="text-muted">No milestone schedules explicitly detailed.</p>
                  ) : (
                    <div className="milestones-timeline">
                      {analysisData.scope.milestones.map((m, idx) => (
                        <div key={idx} className="timeline-node">
                          <div className="node-icon">
                            <Clock size={14} />
                          </div>
                          <div className="node-content">
                            <div className="node-title">
                              <strong>{m.milestone_id}:</strong> {m.name}
                            </div>
                            <div className="node-meta">
                              <span>Target Date: {m.target_date || "UNKNOWN"}</span> •{" "}
                              <span>Status: {m.status}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Dependencies */}
                <div className="content-card">
                  <h4 className="content-card-title">
                    <ArrowRight size={18} className="text-blue" /> Identified Dependencies
                  </h4>
                  {analysisData.scope.dependencies.length === 0 ? (
                    <p className="text-muted">No explicit task dependency relationships detected.</p>
                  ) : (
                    <div className="dependencies-list">
                      {analysisData.scope.dependencies.map((dep, idx) => (
                        <div key={idx} className="dep-card">
                          <div className="dep-flow">
                            <span className="dep-target">{dep.dependent_item}</span>
                            <span className="dep-rel-arrow">
                              <ArrowRight size={14} /> {dep.dependency_type} on
                            </span>
                            <span className="dep-source">{dep.depends_on}</span>
                          </div>
                          {dep.source_ref && (
                            <span className="source-citation-inline">{dep.source_ref}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Missing Information Callout */}
              {analysisData.scope.missing_information.length > 0 && (
                <div className="missing-info-card">
                  <div className="missing-info-header">
                    <HelpCircle size={18} className="text-amber" />
                    <span>Identified Data Gaps & Missing Information</span>
                  </div>
                  <ul className="missing-info-list">
                    {analysisData.scope.missing_information.map((info, idx) => (
                      <li key={idx}>{info}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 2: Risks & Delivery Forecasting */}
          {/* ======================================================== */}
          {activeTab === "risks" && (
            <div className="tab-panel">
              {/* Delivery Forecast Banner */}
              <div className={`delivery-risk-banner ${getRiskLevelColor(analysisData.risks.overall_delivery_risk)}`}>
                <div className="risk-banner-left">
                  <div className="risk-level-tag">
                    <ShieldAlert size={20} />
                    <span>Overall Delivery Risk: <strong>{analysisData.risks.overall_delivery_risk.toUpperCase()}</strong></span>
                  </div>
                  <p className="risk-forecast-text">
                    {analysisData.risks.delivery_forecast_summary}
                  </p>
                </div>
              </div>

              {/* Risk Counts Strip */}
              <div className="metrics-strip">
                <div className="metric-box alert">
                  <span className="metric-val text-rose">{analysisData.risks.critical_count}</span>
                  <span className="metric-lbl">Critical Risks</span>
                </div>
                <div className="metric-box alert">
                  <span className="metric-val text-amber">{analysisData.risks.high_count}</span>
                  <span className="metric-lbl">High Risks</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-blue">{analysisData.risks.medium_count}</span>
                  <span className="metric-lbl">Medium Risks</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-emerald">{analysisData.risks.low_count}</span>
                  <span className="metric-lbl">Low Risks</span>
                </div>
              </div>

              {/* Calculation Method and Limitations Note */}
              <div className="methodology-card">
                <div className="method-col">
                  <strong>Calculation Methodology:</strong>
                  <p>{analysisData.risks.calculation_method}</p>
                </div>
                <div className="method-col">
                  <strong>Anti-Hallucination Disclosures:</strong>
                  <p>{analysisData.risks.limitations_note}</p>
                </div>
              </div>

              {/* Risk Items List */}
              <div className="risks-grid">
                {analysisData.risks.risks.length === 0 ? (
                  <div className="empty-state">
                    <ShieldAlert size={36} className="text-emerald" />
                    <p>No risks or schedule slips identified in uploaded documents.</p>
                  </div>
                ) : (
                  analysisData.risks.risks.map((risk) => (
                    <div key={risk.risk_id} className="risk-card">
                      <div className="risk-card-top">
                        <div className="risk-id-row">
                          <span className="risk-id-pill">{risk.risk_id}</span>
                          <span className="category-pill">{risk.risk_category}</span>
                          {risk.affected_milestone && (
                            <span className="milestone-pill">
                              <Clock size={11} /> {risk.affected_milestone}
                            </span>
                          )}
                        </div>
                        <div className="risk-badges-row">
                          <span className={`badge-severity ${getSeverityBadgeClass(risk.severity)}`}>
                            {risk.severity} Severity
                          </span>
                          <span className="badge-matrix">
                            Likelihood: {risk.likelihood} • Impact: {risk.impact}
                          </span>
                        </div>
                      </div>

                      <h4 className="risk-title">{risk.risk_title}</h4>
                      <p className="risk-desc">{risk.description}</p>

                      {/* Supporting Evidence */}
                      <div className="evidence-box">
                        <div className="evidence-header-label">
                          <span>Document Stated Evidence</span>
                          {risk.source_references && risk.source_references[0] && (
                            <span className="source-citation-inline">{risk.source_references[0]}</span>
                          )}
                        </div>
                        <blockquote className="evidence-quote">"{risk.supporting_evidence}"</blockquote>
                      </div>

                      {/* Mitigation Recommendation */}
                      <div className="mitigation-box">
                        <div className="mitigation-header-label">
                          <Sparkles size={13} className="text-blue" />
                          <span>AI Advisory Recommendation</span>
                        </div>
                        <p className="mitigation-text">{risk.recommended_mitigation}</p>
                      </div>

                      {risk.data_gaps && (
                        <div className="data-gaps-note">
                          <strong>Data Gap:</strong> {risk.data_gaps}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* TAB 3: Blockers & Action Items */}
          {/* ======================================================== */}
          {activeTab === "blockers" && (
            <div className="tab-panel">
              {/* Metrics Strip */}
              <div className="metrics-strip">
                <div className="metric-box alert">
                  <span className="metric-val text-rose">{analysisData.blockers.blocker_count}</span>
                  <span className="metric-lbl">Active Blockers</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-blue">{analysisData.blockers.action_item_count}</span>
                  <span className="metric-lbl">Action Register</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-amber">{analysisData.blockers.pending_decision_count}</span>
                  <span className="metric-lbl">Pending Decisions</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-emerald">
                    {analysisData.blockers.approved_decisions?.length || 0}
                  </span>
                  <span className="metric-lbl">Approved Decisions</span>
                </div>
                <div className="metric-box">
                  <span className="metric-val text-purple">{analysisData.blockers.unassigned_count}</span>
                  <span className="metric-lbl">Unassigned Items</span>
                </div>
                <div className={`metric-box ${analysisData.blockers.overdue_count > 0 ? "alert" : ""}`}>
                  <span className={`metric-val ${analysisData.blockers.overdue_count > 0 ? "text-rose" : "text-emerald"}`}>
                    {analysisData.blockers.overdue_count}
                  </span>
                  <span className="metric-lbl">Overdue Tasks</span>
                </div>
              </div>

              {/* Summary */}
              {analysisData.blockers.summary && (
                <div className="agent-summary-box">
                  <div className="summary-title">
                    <AlertCircle size={16} className="text-amber" /> Operational Blockers & Actions Overview
                  </div>
                  <p>{analysisData.blockers.summary}</p>
                </div>
              )}

              {/* Filter Row */}
              <div className="filter-button-group" style={{ marginBottom: "1rem" }}>
                <span className="filter-label">
                  <Filter size={14} /> Filter Items:
                </span>
                <button
                  className={`btn-filter ${blockerFilter === "all" ? "active" : ""}`}
                  onClick={() => setBlockerFilter("all")}
                >
                  All ({analysisData.blockers.items.length + (analysisData.blockers.approved_decisions?.length || 0)})
                </button>
                <button
                  className={`btn-filter ${blockerFilter === "blocker" ? "active" : ""}`}
                  onClick={() => setBlockerFilter("blocker")}
                >
                  Blockers Only ({analysisData.blockers.blocker_count})
                </button>
                <button
                  className={`btn-filter ${blockerFilter === "action" ? "active" : ""}`}
                  onClick={() => setBlockerFilter("action")}
                >
                  Action Register ({analysisData.blockers.action_item_count})
                </button>
                <button
                  className={`btn-filter ${blockerFilter === "decision" ? "active" : ""}`}
                  onClick={() => setBlockerFilter("decision")}
                >
                  Pending Decisions ({analysisData.blockers.pending_decision_count})
                </button>
                <button
                  className={`btn-filter ${blockerFilter === "approved" ? "active" : ""}`}
                  onClick={() => setBlockerFilter("approved")}
                >
                  Approved Decisions ({analysisData.blockers.approved_decisions?.length || 0})
                </button>
              </div>

              {/* Approved Decisions Card */}
              {analysisData.blockers.approved_decisions && analysisData.blockers.approved_decisions.length > 0 && (blockerFilter === "all" || blockerFilter === "approved") && (
                <div className="content-card" style={{ marginBottom: "1.25rem" }}>
                  <h4 className="content-card-title">
                    <CheckCircle2 size={18} className="text-emerald" /> Approved Project Decisions ({analysisData.blockers.approved_decisions.length})
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                    {analysisData.blockers.approved_decisions.map((dec) => (
                      <div
                        key={dec.decision_id}
                        style={{
                          padding: "1rem 1.25rem",
                          backgroundColor: "rgba(16, 185, 129, 0.07)",
                          border: "1px solid rgba(16, 185, 129, 0.28)",
                          borderRadius: "var(--radius-md)",
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.45rem",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.5rem" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                            <span className="item-id-pill" style={{ color: "#34d399", backgroundColor: "rgba(16, 185, 129, 0.18)" }}>
                              {dec.decision_id}
                            </span>
                            <span style={{ fontWeight: 600, color: "var(--text-primary)", fontSize: "0.92rem" }}>
                              {dec.decision_title}
                            </span>
                            <span className="status-pill completed">{dec.status}</span>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                            {dec.owner && <span>Owner: <strong>{dec.owner}</strong></span>}
                            {dec.date_or_deadline && <span>Date: <strong>{dec.date_or_deadline}</strong></span>}
                          </div>
                        </div>
                        <p style={{ margin: 0, fontSize: "0.84rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                          {dec.details}
                        </p>
                        {dec.source_references && dec.source_references.length > 0 && (
                          <div style={{ fontSize: "0.74rem", color: "#60a5fa", fontFamily: "ui-monospace, monospace" }}>
                            Source: {dec.source_references.join(" • ")}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Items List */}
              <div className="blockers-list">
                {filteredBlockers.length === 0 ? (
                  <div className="empty-state">
                    <CheckCircle2 size={36} className="text-emerald" />
                    <p>No items found for the selected filter.</p>
                  </div>
                ) : (
                  filteredBlockers.map((item) => (
                    <div
                      key={item.item_id}
                      className={`blocker-card ${item.item_type === "Blocker" ? "is-blocker" : ""}`}
                    >
                      <div className="blocker-header-row">
                        <div className="blocker-meta-left">
                          <span className="item-id-pill">{item.item_id}</span>
                          <span
                            className={`item-type-badge ${
                              item.item_type === "Blocker"
                                ? "type-blocker"
                                : item.item_type === "Pending Decision"
                                ? "type-decision"
                                : "type-action"
                            }`}
                          >
                            {item.item_type}
                          </span>
                          <span className={`priority-tag ${item.priority.toLowerCase()}`}>
                            {item.priority} Priority
                          </span>
                          <span className={`status-pill ${item.status.toLowerCase().replace(/\s+/g, "-")}`}>
                            {item.status}
                          </span>
                        </div>

                        <div className="blocker-meta-right">
                          <div className="owner-chip">
                            <User size={13} />
                            {item.assigned_owner && item.assigned_owner !== "UNKNOWN" ? (
                              <span>{item.assigned_owner}</span>
                            ) : (
                              <span className="badge-unknown">UNKNOWN (Unassigned)</span>
                            )}
                          </div>
                          <div className="due-chip">
                            <Calendar size={13} />
                            {item.due_date && item.due_date !== "UNKNOWN" ? (
                              <span>{item.due_date}</span>
                            ) : (
                              <span className="badge-unknown">No Due Date</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <p className="blocker-desc">{item.description}</p>

                      {/* Supporting Evidence */}
                      <div className="evidence-box">
                        <div className="evidence-header-label">
                          <span>Evidence from Source Document</span>
                          {item.source_references && item.source_references.length > 0 && (
                            <span className="source-citation-inline">
                              {item.source_references.join(" • ")}
                            </span>
                          )}
                        </div>
                        <blockquote className="evidence-quote">"{item.supporting_evidence}"</blockquote>
                      </div>

                      {/* AI Next Step */}
                      <div className="mitigation-box">
                        <div className="mitigation-header-label">
                          <ArrowRight size={13} className="text-blue" />
                          <span>Recommended Action Step</span>
                        </div>
                        <p className="mitigation-text">{item.recommended_next_step}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
