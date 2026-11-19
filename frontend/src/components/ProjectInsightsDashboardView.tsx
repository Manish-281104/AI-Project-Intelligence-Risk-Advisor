import React, { useState, useEffect, useMemo } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileText,
  ShieldAlert,
  Target,
  RefreshCw,
  FolderGit2,
  Building2,
  TrendingUp,
  ListTodo,
  ChevronRight,
  Flame,
  Search,
  Filter,
  Sparkles,
  Quote,
  X,
  PlusCircle,
  HelpCircle,
  User,
  Calendar,
  Layers,
  ArrowRight,
  AlertCircle,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import {
  getDashboardSummary,
  ProjectDashboardSummary,
  DashboardRiskItem,
  DashboardBlockerItem,
  DashboardDeliverable,
  DashboardActionItem,
  startNewProjectWorkspace,
  resetProjectWorkspace,
} from "../services/api";

interface ProjectInsightsDashboardViewProps {
  workspaceVersion?: number;
  onNavigateToTab?: (tab: "all" | "dashboard" | "ingest" | "agents" | "docgen" | "health" | "chat") => void;
  onNavigateToIngest?: () => void;
  onWorkspaceChanged?: () => void;
}

interface InsightItem {
  id: string;
  category: "updates" | "risks" | "scope_timeline" | "decisions" | "actions";
  type: "evidence" | "recommendation";
  title: string;
  description: string;
  sourceDoc?: string | null;
  sourceExcerpt?: string | null;
  badge?: string;
  severity?: "critical" | "high" | "medium" | "low" | "info";
}

export const ProjectInsightsDashboardView: React.FC<ProjectInsightsDashboardViewProps> = ({
  workspaceVersion = 0,
  onNavigateToTab,
  onNavigateToIngest,
  onWorkspaceChanged,
}) => {
  const [summary, setSummary] = useState<ProjectDashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  // Sub-Navigation Tabs
  const [subSection, setSubSection] = useState<
    "overview" | "progress" | "risks" | "blockers" | "actions" | "insights"
  >("overview");

  // Filter & Search States
  const [deliverableSearch, setDeliverableSearch] = useState<string>("");
  const [deliverableFilter, setDeliverableFilter] = useState<string>("all");

  const [riskSearch, setRiskSearch] = useState<string>("");
  const [riskSeverityFilter, setRiskSeverityFilter] = useState<string>("all");

  const [blockerSearch, setBlockerSearch] = useState<string>("");
  const [blockerFilter, setBlockerFilter] = useState<string>("all");

  const [actionSearch, setActionSearch] = useState<string>("");
  const [actionFilter, setActionFilter] = useState<string>("all");

  const [insightCategory, setInsightCategory] = useState<string>("all");

  // Modal States
  const [selectedRisk, setSelectedRisk] = useState<DashboardRiskItem | null>(null);
  const [selectedBlocker, setSelectedBlocker] = useState<DashboardBlockerItem | null>(null);
  const [selectedDeliverable, setSelectedDeliverable] = useState<DashboardDeliverable | null>(null);
  const [selectedAction, setSelectedAction] = useState<DashboardActionItem | null>(null);
  const [citationModal, setCitationModal] = useState<{
    title: string;
    source?: string | null;
    excerpt?: string | null;
    ref?: string | null;
  } | null>(null);

  // Project Workspace Manager Modal
  const [workspaceModalOpen, setWorkspaceModalOpen] = useState<boolean>(false);
  const [newProjectName, setNewProjectName] = useState<string>("");
  const [newProjectId, setNewProjectId] = useState<string>("");
  const [workspaceActionLoading, setWorkspaceActionLoading] = useState<boolean>(false);
  const [workspaceActionError, setWorkspaceActionError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboardSummary();
      setSummary(data);
      const now = new Date();
      setLastUpdated(now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    } catch (err: any) {
      setError(err.message || "Failed to load project dashboard summary from backend.");
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [workspaceVersion]);

  // Safe navigation helper
  const handleNav = (tab: "all" | "dashboard" | "ingest" | "agents" | "docgen" | "health" | "chat") => {
    if (onNavigateToTab) {
      onNavigateToTab(tab);
    } else if (tab === "ingest" && onNavigateToIngest) {
      onNavigateToIngest();
    }
  };

  // Helper to format date & check overdue
  const isOverdue = (dueDateStr?: string | null, status?: string): boolean => {
    if (!dueDateStr || dueDateStr.toUpperCase() === "UNKNOWN" || !dueDateStr.match(/\d{4}-\d{2}-\d{2}/)) {
      return false;
    }
    if (
      status &&
      (status.toLowerCase().includes("complete") ||
        status.toLowerCase().includes("resolved") ||
        status.toLowerCase().includes("closed"))
    ) {
      return false;
    }
    try {
      const dueDate = new Date(dueDateStr);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return dueDate < today;
    } catch {
      return false;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "#10b981"; // Emerald
    if (score >= 60) return "#f59e0b"; // Amber
    return "#ef4444"; // Rose
  };

  const getStatusBadgeClass = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s.includes("healthy") || s.includes("on track") || s.includes("complete") || s.includes("resolved")) {
      return "badge-status-healthy";
    }
    if (s.includes("attention") || s.includes("in progress") || s.includes("medium")) {
      return "badge-status-attention";
    }
    if (s.includes("risk") || s.includes("high") || s.includes("critical") || s.includes("open")) {
      return "badge-status-risk";
    }
    return "badge-status-neutral";
  };

  const getSeverityClass = (sev: string) => {
    const s = (sev || "").toLowerCase();
    if (s === "critical") return "sev-critical";
    if (s === "high") return "sev-high";
    if (s === "medium") return "sev-medium";
    return "sev-low";
  };

  // Switch / Create New Project Workspace
  const handleCreateNewWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    setWorkspaceActionLoading(true);
    setWorkspaceActionError(null);
    try {
      await startNewProjectWorkspace(newProjectName.trim(), newProjectId.trim() || undefined);
      setWorkspaceModalOpen(false);
      setNewProjectName("");
      setNewProjectId("");
      if (onWorkspaceChanged) onWorkspaceChanged();
      await fetchDashboardData();
    } catch (err: any) {
      setWorkspaceActionError(err.message || "Failed to initialize new project workspace.");
    } finally {
      setWorkspaceActionLoading(false);
    }
  };

  // Reset Project Workspace
  const handleResetWorkspace = async () => {
    if (!window.confirm("Are you sure you want to reset this workspace? All uploaded documents and analysis will be cleared.")) {
      return;
    }
    setWorkspaceActionLoading(true);
    setWorkspaceActionError(null);
    try {
      await resetProjectWorkspace();
      setWorkspaceModalOpen(false);
      if (onWorkspaceChanged) onWorkspaceChanged();
      await fetchDashboardData();
    } catch (err: any) {
      setWorkspaceActionError(err.message || "Failed to reset workspace.");
    } finally {
      setWorkspaceActionLoading(false);
    }
  };

  // Filtered Deliverables
  const filteredDeliverables = useMemo(() => {
    if (!summary?.scope?.key_deliverables) return [];
    return summary.scope.key_deliverables.filter((d) => {
      const matchSearch =
        deliverableSearch === "" ||
        d.name.toLowerCase().includes(deliverableSearch.toLowerCase()) ||
        d.deliverable_id.toLowerCase().includes(deliverableSearch.toLowerCase()) ||
        (d.owner && d.owner.toLowerCase().includes(deliverableSearch.toLowerCase()));

      let matchFilter = true;
      if (deliverableFilter === "completed") {
        matchFilter = d.status.toLowerCase().includes("complete") || d.status.toLowerCase().includes("done");
      } else if (deliverableFilter === "in_progress") {
        matchFilter = d.status.toLowerCase().includes("progress");
      } else if (deliverableFilter === "pending") {
        matchFilter = d.status.toLowerCase().includes("pending") || d.status.toLowerCase().includes("planned");
      } else if (deliverableFilter === "at_risk") {
        matchFilter = d.status.toLowerCase().includes("risk");
      }

      return matchSearch && matchFilter;
    });
  }, [summary, deliverableSearch, deliverableFilter]);

  // Filtered Risks
  const filteredRisks = useMemo(() => {
    if (!summary?.risks?.items) return [];
    return summary.risks.items.filter((r) => {
      const matchSearch =
        riskSearch === "" ||
        r.title.toLowerCase().includes(riskSearch.toLowerCase()) ||
        r.description.toLowerCase().includes(riskSearch.toLowerCase()) ||
        r.risk_id.toLowerCase().includes(riskSearch.toLowerCase()) ||
        r.owner.toLowerCase().includes(riskSearch.toLowerCase());

      let matchFilter = true;
      const s = r.severity.toLowerCase();
      if (riskSeverityFilter === "high") {
        matchFilter = s === "high" || s === "critical";
      } else if (riskSeverityFilter === "medium") {
        matchFilter = s === "medium";
      } else if (riskSeverityFilter === "low") {
        matchFilter = s === "low";
      }

      return matchSearch && matchFilter;
    });
  }, [summary, riskSearch, riskSeverityFilter]);

  // Filtered Blockers
  const filteredBlockers = useMemo(() => {
    if (!summary?.blockers?.items) return [];
    return summary.blockers.items.filter((b) => {
      const matchSearch =
        blockerSearch === "" ||
        b.description.toLowerCase().includes(blockerSearch.toLowerCase()) ||
        b.item_id.toLowerCase().includes(blockerSearch.toLowerCase()) ||
        b.owner.toLowerCase().includes(blockerSearch.toLowerCase());

      let matchFilter = true;
      const isResolved =
        b.status.toLowerCase().includes("resolved") || b.status.toLowerCase().includes("closed");
      if (blockerFilter === "open") matchFilter = !isResolved;
      if (blockerFilter === "resolved") matchFilter = isResolved;

      return matchSearch && matchFilter;
    });
  }, [summary, blockerSearch, blockerFilter]);

  // Filtered Actions
  const filteredActions = useMemo(() => {
    if (!summary?.action_items?.items) return [];
    return summary.action_items.items.filter((a) => {
      const matchSearch =
        actionSearch === "" ||
        a.description.toLowerCase().includes(actionSearch.toLowerCase()) ||
        a.item_id.toLowerCase().includes(actionSearch.toLowerCase()) ||
        a.owner.toLowerCase().includes(actionSearch.toLowerCase());

      let matchFilter = true;
      const isDone =
        a.status.toLowerCase().includes("complete") || a.status.toLowerCase().includes("done");
      const isUnassigned =
        !a.owner || a.owner.toUpperCase() === "UNKNOWN" || a.owner.toUpperCase() === "UNASSIGNED";

      if (actionFilter === "pending") matchFilter = !isDone;
      if (actionFilter === "completed") matchFilter = isDone;
      if (actionFilter === "high") matchFilter = a.priority.toLowerCase() === "high";
      if (actionFilter === "unassigned") matchFilter = isUnassigned;

      return matchSearch && matchFilter;
    });
  }, [summary, actionSearch, actionFilter]);

  // AI Project Insights Synthesizer (Strictly distinguishes Document Evidence vs AI Recommendations)
  const synthesizedInsights: InsightItem[] = useMemo(() => {
    if (!summary || !summary.has_documents) return [];
    const list: InsightItem[] = [];

    // 1. Important Project Updates (Evidence from Document Progress / Milestones)
    if (summary.progress && summary.progress.completed_deliverables > 0) {
      list.push({
        id: "ins-upd-1",
        category: "updates",
        type: "evidence",
        title: "Verified Delivery Milestones Achieved",
        description: `Project documents confirm ${summary.progress.completed_deliverables} of ${summary.progress.total_deliverables} deliverables have achieved verified completion (${summary.progress.completion_percentage}% progress).`,
        sourceDoc: summary.documents[0]?.filename || "Project Ingestion Record",
        badge: "Grounded Fact",
        severity: "info",
      });
    }

    if (summary.blockers && summary.blockers.resolved_count > 0) {
      list.push({
        id: "ins-upd-2",
        category: "updates",
        type: "evidence",
        title: "Blockers Successfully Resolved",
        description: `Meeting updates document ${summary.blockers.resolved_count} operational impediment(s) marked resolved, unblocking downstream integration tracks.`,
        sourceDoc: summary.documents[summary.documents.length - 1]?.filename || "Meeting Notes",
        badge: "Documented Resolution",
        severity: "info",
      });
    }

    // 2. Emerging Risks (Document Evidence + AI Mitigation Recommendations)
    if (summary.risks && summary.risks.items.length > 0) {
      summary.risks.items.forEach((r, idx) => {
        // Document Evidence of the Risk
        list.push({
          id: `ins-risk-ev-${idx}`,
          category: "risks",
          type: "evidence",
          title: `Documented Exposure: ${r.title}`,
          description: r.description,
          sourceDoc: r.source_document || summary.documents[0]?.filename,
          sourceExcerpt: r.evidence,
          badge: `${r.severity} Severity`,
          severity: r.severity.toLowerCase() === "high" ? "high" : "medium",
        });

        // AI Recommendation for the Risk
        if (r.recommended_mitigation) {
          list.push({
            id: `ins-risk-rec-${idx}`,
            category: "actions",
            type: "recommendation",
            title: `Recommended Mitigation for ${r.risk_id}`,
            description: r.recommended_mitigation,
            badge: "Suggested Action",
            severity: "info",
          });
        }
      });
    }

    // 3. Scope & Timeline Concerns (Evidence from Alerts & Missing Data)
    if (summary.health?.missing_data_alerts && summary.health.missing_data_alerts.length > 0) {
      summary.health.missing_data_alerts.forEach((alert, idx) => {
        list.push({
          id: `ins-scope-ev-${idx}`,
          category: "scope_timeline",
          type: "evidence",
          title: "Missing Project Evidence Detected",
          description: alert,
          sourceDoc: "Project Health Diagnostic Engine",
          badge: "Documentation Gap",
          severity: "medium",
        });
      });
    }

    if (summary.action_items && summary.action_items.unassigned_count > 0) {
      list.push({
        id: "ins-unassigned-ev",
        category: "decisions",
        type: "evidence",
        title: "Unassigned Critical Tasks Requiring Leadership Action",
        description: `${summary.action_items.unassigned_count} extracted action item(s) currently lack a confirmed team owner in uploaded project documentation.`,
        sourceDoc: "Deliverables & Actions Register",
        badge: "Owner Unassigned",
        severity: "high",
      });
    }

    // 4. Recommended Next Actions (AI Recommendations from Health Engine)
    if (summary.health?.recommendations && summary.health.recommendations.length > 0) {
      summary.health.recommendations.forEach((rec, idx) => {
        list.push({
          id: `ins-health-rec-${idx}`,
          category: "actions",
          type: "recommendation",
          title: `Advisory Action #${idx + 1}`,
          description: rec,
          badge: "Health Advisory",
          severity: "info",
        });
      });
    }

    return list;
  }, [summary]);

  const filteredInsights = useMemo(() => {
    if (insightCategory === "all") return synthesizedInsights;
    return synthesizedInsights.filter((item) => item.category === insightCategory);
  }, [synthesizedInsights, insightCategory]);

  // Health Score Dimensions
  const scopeInd = summary?.health?.indicators?.find((i) =>
    i.dimension.toLowerCase().includes("scope")
  );
  const timelineInd = summary?.health?.indicators?.find((i) =>
    i.dimension.toLowerCase().includes("timeline")
  );
  const blockerInd = summary?.health?.indicators?.find((i) =>
    i.dimension.toLowerCase().includes("blocker")
  );

  const overallScore = summary?.health?.overall_score ?? 0;
  // Circular gauge circumference
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeOffset = circumference - (Math.min(100, Math.max(0, overallScore)) / 100) * circumference;

  return (
    <div className="saas-dashboard-root">
      {/* =========================================================================
          1. ATTRACTIVE DASHBOARD HEADER BAR
      ========================================================================= */}
      <div className="saas-header-card">
        <div className="saas-header-main">
          <div className="saas-header-badge-row">
            <span className="saas-pill saas-pill-primary">
              <Activity size={13} /> Project Intelligence Dashboard
            </span>
            {summary?.has_documents && (
              <>
                <span className="saas-pill saas-pill-dark" title="Workspace Project ID">
                  <FolderGit2 size={13} /> {summary.project_id}
                </span>
                {summary.client && (
                  <span className="saas-pill saas-pill-dark" title="Client Organization">
                    <Building2 size={13} /> {summary.client}
                  </span>
                )}
                <span
                  className={`saas-pill ${getStatusBadgeClass(summary.health?.status || "Analyzing")}`}
                >
                  <ShieldCheck size={13} /> {summary.health?.status || "Active Workspace"}
                </span>
                <span className="saas-pill saas-pill-muted">
                  <FileText size={13} /> {summary.document_count} Doc
                  {summary.document_count === 1 ? "" : "s"} Indexed
                </span>
              </>
            )}
          </div>

          <div className="saas-title-wrap">
            <h1 className="saas-dashboard-title">
              {summary?.has_documents && summary.project_name
                ? summary.project_name
                : "Project Dashboard"}
            </h1>
            <p className="saas-dashboard-subtitle">
              Monitor project progress, health, risks, and important activities.
            </p>
          </div>
        </div>

        {/* Header Action Controls */}
        <div className="saas-header-actions">
          {lastUpdated && (
            <span className="saas-updated-label" title="Last backend data synchronization">
              <Clock size={13} /> Updated {lastUpdated}
            </span>
          )}

          <button
            className="saas-btn saas-btn-secondary"
            onClick={() => setWorkspaceModalOpen(true)}
            title="Manage or switch workspace project"
          >
            <FolderGit2 size={14} />
            <span>Switch Project</span>
          </button>

          <button
            className="saas-btn saas-btn-primary"
            onClick={() => handleNav("ingest")}
            title="Upload new or supplementary documents"
          >
            <PlusCircle size={14} />
            <span>Upload Documents</span>
          </button>

          <button
            className="saas-btn saas-btn-icon"
            onClick={fetchDashboardData}
            disabled={loading}
            title="Refresh dashboard from backend"
            aria-label="Refresh dashboard data"
          >
            <RefreshCw size={15} className={loading ? "spin" : ""} />
          </button>
        </div>
      </div>

      {/* =========================================================================
          SUB-NAVIGATION SECTION SELECTOR
      ========================================================================= */}
      <div className="saas-subnav-strip">
        <button
          className={`saas-subnav-pill ${subSection === "overview" ? "active" : ""}`}
          onClick={() => setSubSection("overview")}
        >
          <Layers size={14} /> Comprehensive Overview
        </button>
        <button
          className={`saas-subnav-pill ${subSection === "progress" ? "active" : ""}`}
          onClick={() => setSubSection("progress")}
        >
          <TrendingUp size={14} /> Project Progress ({summary?.progress?.total_deliverables || 0})
        </button>
        <button
          className={`saas-subnav-pill ${subSection === "risks" ? "active" : ""}`}
          onClick={() => setSubSection("risks")}
        >
          <ShieldAlert size={14} /> Risk Overview ({summary?.risks?.total_risks || 0})
        </button>
        <button
          className={`saas-subnav-pill ${subSection === "blockers" ? "active" : ""}`}
          onClick={() => setSubSection("blockers")}
        >
          <Flame size={14} /> Blockers ({summary?.blockers?.total_blockers || 0})
        </button>
        <button
          className={`saas-subnav-pill ${subSection === "actions" ? "active" : ""}`}
          onClick={() => setSubSection("actions")}
        >
          <ListTodo size={14} /> Action Items ({summary?.action_items?.total_actions || 0})
        </button>
        <button
          className={`saas-subnav-pill ${subSection === "insights" ? "active" : ""}`}
          onClick={() => setSubSection("insights")}
        >
          <Sparkles size={14} /> AI Project Insights ({synthesizedInsights.length})
        </button>
      </div>

      {/* =========================================================================
          LOADING SKELETON STATE
      ========================================================================= */}
      {loading && !summary && (
        <div className="saas-loading-grid">
          <div className="saas-skeleton-header pulse" />
          <div className="saas-cards-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="saas-metric-card saas-skeleton pulse" />
            ))}
          </div>
          <div className="saas-progress-section saas-skeleton pulse" style={{ height: "260px" }} />
        </div>
      )}

      {/* =========================================================================
          ERROR STATE BANNER
      ========================================================================= */}
      {error && (
        <div className="saas-alert-banner alert-danger">
          <div className="saas-alert-content">
            <AlertTriangle size={20} className="text-danger" />
            <div>
              <h4 className="saas-alert-title">Dashboard Synchronization Error</h4>
              <p className="saas-alert-desc">{error}</p>
            </div>
          </div>
          <button className="saas-btn saas-btn-secondary saas-btn-sm" onClick={fetchDashboardData}>
            Retry Connection
          </button>
        </div>
      )}

      {/* =========================================================================
          EMPTY STATE (ZERO INGESTED DOCUMENTS)
      ========================================================================= */}
      {!loading && summary && !summary.has_documents && (
        <div className="saas-empty-panel">
          <div className="saas-empty-glow" />
          <div className="saas-empty-icon-wrap">
            <FileText size={42} className="text-primary" />
          </div>
          <h2 className="saas-empty-title">Ready for Project Document Ingestion</h2>
          <p className="saas-empty-desc">
            The active workspace (<code>{summary.project_id}</code>) currently contains zero indexed documents.
            Upload your project charter, requirements specification, meeting notes, or deliverables tracker to generate instant multi-agent intelligence, deterministic health scoring, and risk forecasting.
          </p>

          <div className="saas-empty-feature-cards">
            <div className="saas-empty-feat">
              <Activity size={18} className="text-emerald" />
              <span>0–100 Deterministic Health Scoring</span>
            </div>
            <div className="saas-empty-feat">
              <ShieldAlert size={18} className="text-amber" />
              <span>Autonomous Risk & Blocker Extraction</span>
            </div>
            <div className="saas-empty-feat">
              <Sparkles size={18} className="text-cyan" />
              <span>Grounded AI Citations with Zero Hallucination</span>
            </div>
          </div>

          <div className="saas-empty-action-group">
            <button className="saas-btn saas-btn-primary saas-btn-lg" onClick={() => handleNav("ingest")}>
              <span>Upload Project Documents</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          ACTIVE SAAS DASHBOARD CONTENT
      ========================================================================= */}
      {summary && summary.has_documents && (
        <div className="saas-content-flow">
          {/* =====================================================================
              SECTION 4: PROJECT HEALTH SUMMARY CARDS (6 CARDS GRID)
          ===================================================================== */}
          <div className="saas-summary-cards-grid">
            {/* 1. Overall Project Health */}
            <div className="saas-metric-card saas-health-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Overall Project Health</span>
                <span className={`saas-pill saas-pill-sm ${getStatusBadgeClass(summary.health?.status || "At Risk")}`}>
                  {summary.health?.status || "Analyzing"}
                </span>
              </div>

              <div className="saas-gauge-row">
                {/* Donut SVG Ring */}
                <div className="saas-donut-wrap">
                  <svg className="saas-donut-svg" width="92" height="92" viewBox="0 0 92 92">
                    <circle
                      className="saas-donut-bg"
                      cx="46"
                      cy="46"
                      r={radius}
                      strokeWidth="8"
                    />
                    <circle
                      className="saas-donut-fill"
                      cx="46"
                      cy="46"
                      r={radius}
                      strokeWidth="8"
                      stroke={getScoreColor(overallScore)}
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeOffset}
                    />
                  </svg>
                  <div className="saas-donut-center">
                    <span className="saas-donut-num">{overallScore}</span>
                    <span className="saas-donut-denom">/100</span>
                  </div>
                </div>

                <div className="saas-gauge-meta">
                  <span className="saas-meta-title">{summary.health?.health_category}</span>
                  <p className="saas-meta-sub">
                    Calculated via 35% Scope + 35% Timeline + 30% Blocker formula.
                  </p>
                  <button
                    className="saas-link-btn"
                    onClick={() => handleNav("health")}
                    title="Open dedicated Project Health View"
                  >
                    <span>Health Breakdown</span>
                    <ArrowRight size={12} />
                  </button>
                </div>
              </div>
            </div>

            {/* 2. Scope Health */}
            <div className="saas-metric-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Scope Health</span>
                <span className="saas-pill saas-pill-sm saas-pill-primary">35% Weight</span>
              </div>
              <div className="saas-stat-display">
                <span className="saas-stat-num">{scopeInd?.raw_score ?? 0}</span>
                <span className="saas-stat-sub">/ 100</span>
              </div>
              <div className="saas-track-bar">
                <div
                  className="saas-track-fill bg-cyan"
                  style={{ width: `${Math.min(100, scopeInd?.raw_score ?? 0)}%` }}
                />
              </div>
              <div className="saas-card-footer-meta">
                <Target size={13} className="text-cyan" />
                <span>
                  {summary.scope?.objectives?.length || 0} Objectives • {summary.scope?.key_deliverables?.length || 0} Deliverables
                </span>
              </div>
            </div>

            {/* 3. Timeline Health */}
            <div className="saas-metric-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Timeline Health</span>
                <span className="saas-pill saas-pill-sm saas-pill-primary">35% Weight</span>
              </div>
              <div className="saas-stat-display">
                <span className="saas-stat-num">{timelineInd?.raw_score ?? 0}</span>
                <span className="saas-stat-sub">/ 100</span>
              </div>
              <div className="saas-track-bar">
                <div
                  className="saas-track-fill bg-indigo"
                  style={{ width: `${Math.min(100, timelineInd?.raw_score ?? 0)}%` }}
                />
              </div>
              <div className="saas-card-footer-meta">
                <Clock size={13} className="text-indigo" />
                <span>
                  {summary.scope?.milestones?.length || 0} Milestones Tracked
                </span>
              </div>
            </div>

            {/* 4. Active Risks */}
            <div className="saas-metric-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Active Risks</span>
                <span
                  className={`saas-pill saas-pill-sm ${
                    summary.risks?.overall_severity === "High"
                      ? "badge-status-risk"
                      : "badge-status-attention"
                  }`}
                >
                  {summary.risks?.overall_severity || "Low"} Risk
                </span>
              </div>
              <div className="saas-stat-display">
                <span className="saas-stat-num">{summary.risks?.total_risks ?? 0}</span>
                <span className="saas-stat-sub">Documented</span>
              </div>
              <div className="saas-chips-row">
                <span className="saas-chip saas-chip-danger">{summary.risks?.high_count ?? 0} High</span>
                <span className="saas-chip saas-chip-warning">{summary.risks?.medium_count ?? 0} Med</span>
                <span className="saas-chip saas-chip-info">{summary.risks?.low_count ?? 0} Low</span>
              </div>
              <div className="saas-card-footer-meta">
                <ShieldAlert size={13} className="text-amber" />
                <span>Extracted by Autonomous Risk Agent</span>
              </div>
            </div>

            {/* 5. Active Blockers */}
            <div className="saas-metric-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Active Blockers</span>
                <span className="saas-pill saas-pill-sm saas-pill-primary">30% Weight</span>
              </div>
              <div className="saas-stat-display">
                <span className="saas-stat-num text-danger">{summary.blockers?.open_count ?? 0}</span>
                <span className="saas-stat-sub">
                  Open ({blockerInd ? `Score: ${blockerInd.raw_score}` : `${summary.blockers?.total_blockers ?? 0} Total`})
                </span>
              </div>
              <div className="saas-chips-row">
                <span className="saas-chip saas-chip-success">
                  {summary.blockers?.resolved_count ?? 0} Resolved
                </span>
                <span className="saas-chip saas-chip-neutral">
                  {summary.blockers?.total_blockers ?? 0} Total
                </span>
              </div>
              <div className="saas-card-footer-meta">
                <AlertCircle size={13} className="text-danger" />
                <span>
                  {summary.blockers?.items?.some((b) => b.owner.toUpperCase() === "UNKNOWN")
                    ? "Contains unassigned blockers"
                    : "All blockers assigned to owners"}
                </span>
              </div>
            </div>

            {/* 6. Pending Actions */}
            <div className="saas-metric-card">
              <div className="saas-metric-top">
                <span className="saas-card-label">Pending Actions</span>
                <ListTodo size={16} className="text-primary" />
              </div>
              <div className="saas-stat-display">
                <span className="saas-stat-num text-primary">{summary.action_items?.pending_count ?? 0}</span>
                <span className="saas-stat-sub">
                  / {summary.action_items?.total_actions ?? 0} Total
                </span>
              </div>
              <div className="saas-chips-row">
                <span className="saas-chip saas-chip-success">
                  {summary.action_items?.completed_count ?? 0} Done
                </span>
                {summary.action_items && summary.action_items.unassigned_count > 0 && (
                  <span className="saas-chip saas-chip-danger">
                    {summary.action_items.unassigned_count} Unassigned
                  </span>
                )}
              </div>
              <div className="saas-card-footer-meta">
                <CheckCircle2 size={13} className="text-success" />
                <span>RFC 4180 / Agile Backlog groundable</span>
              </div>
            </div>
          </div>

          {/* =====================================================================
              SECTION 5: PROJECT PROGRESS
          ===================================================================== */}
          {(subSection === "overview" || subSection === "progress") && (
            <div className="saas-section-card" id="project-progress">
              <div className="saas-section-header">
                <div className="saas-header-left">
                  <div className="saas-icon-badge bg-primary-soft">
                    <TrendingUp size={18} className="text-primary" />
                  </div>
                  <div>
                    <h2 className="saas-section-title">Project Progress</h2>
                    <p className="saas-section-desc">
                      Core project goals, delivery completion percentage, and verified deliverable status.
                    </p>
                  </div>
                </div>
                {summary.progress && (
                  <span className="saas-badge-lg badge-status-primary">
                    {summary.progress.completion_percentage}% Overall Progress
                  </span>
                )}
              </div>

              {/* Main Project Goal Card */}
              {summary.scope && (
                <div className="saas-goal-banner">
                  <div className="saas-goal-tag">
                    <Target size={14} />
                    <span>Primary Project Goal</span>
                  </div>
                  <p className="saas-goal-text">{summary.scope.main_goal}</p>
                  {summary.scope.timeline_summary && (
                    <div className="saas-goal-meta">
                      <Clock size={13} />
                      <span>{summary.scope.timeline_summary}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Deliverable KPI Summary Tiles */}
              <div className="saas-progress-tiles-grid">
                <div className="saas-progress-tile">
                  <span className="saas-tile-label">Total Deliverables</span>
                  <span className="saas-tile-value">{summary.progress?.total_deliverables ?? 0}</span>
                </div>
                <div className="saas-progress-tile tile-completed">
                  <span className="saas-tile-label">Completed</span>
                  <span className="saas-tile-value text-success">
                    {summary.progress?.completed_deliverables ?? 0}
                  </span>
                </div>
                <div className="saas-progress-tile tile-progress">
                  <span className="saas-tile-label">In-Progress</span>
                  <span className="saas-tile-value text-primary">
                    {summary.progress?.in_progress_deliverables ?? 0}
                  </span>
                </div>
                <div className="saas-progress-tile tile-risk">
                  <span className="saas-tile-label">At-Risk / Pending</span>
                  <span className="saas-tile-value text-warning">
                    {summary.progress?.at_risk_deliverables ?? 0}
                  </span>
                </div>
              </div>

              {/* Visual Progress Bar */}
              <div className="saas-progress-bar-container">
                <div className="saas-bar-header">
                  <span className="saas-bar-title">Deliverables Completion Rate</span>
                  <span className="saas-bar-pct font-mono">
                    {summary.progress?.completion_percentage || 0}%
                  </span>
                </div>
                <div className="saas-bar-track">
                  <div
                    className="saas-bar-fill"
                    style={{ width: `${Math.min(100, summary.progress?.completion_percentage || 0)}%` }}
                  />
                </div>
              </div>

              {/* Deliverables Table with Search & Status Filters */}
              <div className="saas-table-wrapper">
                <div className="saas-table-toolbar">
                  <div className="saas-search-box">
                    <Search size={14} className="text-muted" />
                    <input
                      type="text"
                      placeholder="Search deliverables by name, ID, or owner..."
                      value={deliverableSearch}
                      onChange={(e) => setDeliverableSearch(e.target.value)}
                      className="saas-input"
                    />
                    {deliverableSearch && (
                      <button className="saas-clear-btn" onClick={() => setDeliverableSearch("")}>
                        <X size={13} />
                      </button>
                    )}
                  </div>

                  <div className="saas-filter-group">
                    <Filter size={13} className="text-muted" />
                    {[
                      { id: "all", label: "All" },
                      { id: "completed", label: "Completed" },
                      { id: "in_progress", label: "In Progress" },
                      { id: "pending", label: "Pending" },
                      { id: "at_risk", label: "At Risk" },
                    ].map((f) => (
                      <button
                        key={f.id}
                        className={`saas-filter-pill ${deliverableFilter === f.id ? "active" : ""}`}
                        onClick={() => setDeliverableFilter(f.id)}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                {filteredDeliverables.length === 0 ? (
                  <div className="saas-table-empty">
                    <p>No deliverables match the active search or status criteria.</p>
                    <button
                      className="saas-btn saas-btn-sm saas-btn-secondary"
                      onClick={() => {
                        setDeliverableSearch("");
                        setDeliverableFilter("all");
                      }}
                    >
                      Reset Filters
                    </button>
                  </div>
                ) : (
                  <div className="saas-table-scroll">
                    <table className="saas-data-table">
                      <thead>
                        <tr>
                          <th style={{ width: "95px" }}>ID</th>
                          <th>Deliverable Name</th>
                          <th style={{ width: "135px" }}>Status</th>
                          <th style={{ width: "150px" }}>Assigned Owner</th>
                          <th style={{ width: "130px" }}>Target Date</th>
                          <th style={{ width: "110px", textAlign: "right" }}>Citation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredDeliverables.map((deliv, idx) => (
                          <tr
                            key={idx}
                            className="saas-clickable-row"
                            onClick={() => setSelectedDeliverable(deliv)}
                            title="Click to view full deliverable details"
                          >
                            <td>
                              <code className="saas-id-tag">{deliv.deliverable_id}</code>
                            </td>
                            <td>
                              <span className="saas-name-cell">{deliv.name}</span>
                            </td>
                            <td>
                              <span className={`saas-pill saas-pill-sm ${getStatusBadgeClass(deliv.status)}`}>
                                {deliv.status}
                              </span>
                            </td>
                            <td>
                              <div className="saas-user-badge">
                                <User size={12} />
                                <span
                                  className={
                                    deliv.owner === "UNKNOWN" || deliv.owner === "Unassigned"
                                      ? "text-warning font-semibold"
                                      : ""
                                  }
                                >
                                  {deliv.owner}
                                </span>
                              </div>
                            </td>
                            <td>
                              <div className="saas-date-badge">
                                <Calendar size={12} />
                                <span>{deliv.target_date}</span>
                              </div>
                            </td>
                            <td style={{ textAlign: "right" }}>
                              <button
                                className="saas-btn-xs saas-btn-outline"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setCitationModal({
                                    title: deliv.name,
                                    source: deliv.source_ref || "Project Scope Specification",
                                    excerpt: `Deliverable ${deliv.deliverable_id}: ${deliv.name} (Assigned: ${deliv.owner}, Status: ${deliv.status}, Target: ${deliv.target_date})`,
                                    ref: deliv.source_ref,
                                  });
                                }}
                                title="Inspect document citation excerpt"
                              >
                                <Quote size={11} /> Evidence
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* =====================================================================
              SECTION 6: RISK AND BLOCKER OVERVIEW (SEPARATE SECTIONS)
          ===================================================================== */}
          {(subSection === "overview" || subSection === "risks") && (
            <div className="saas-section-card" id="risk-overview">
              <div className="saas-section-header">
                <div className="saas-header-left">
                  <div className="saas-icon-badge bg-warning-soft">
                    <ShieldAlert size={18} className="text-warning" />
                  </div>
                  <div>
                    <h2 className="saas-section-title">Risk Overview</h2>
                    <p className="saas-section-desc">
                      Documented technical and operational delivery risks with verified likelihood, impact, and mitigation steps.
                    </p>
                  </div>
                </div>
                {summary.risks && (
                  <span
                    className={`saas-badge-lg ${
                      summary.risks.overall_severity === "High"
                        ? "badge-status-risk"
                        : "badge-status-attention"
                    }`}
                  >
                    Overall: {summary.risks.overall_severity} Delivery Risk
                  </span>
                )}
              </div>

              {/* Risk Filters & Search */}
              <div className="saas-table-toolbar">
                <div className="saas-search-box">
                  <Search size={14} className="text-muted" />
                  <input
                    type="text"
                    placeholder="Search risks by title, description, or owner..."
                    value={riskSearch}
                    onChange={(e) => setRiskSearch(e.target.value)}
                    className="saas-input"
                  />
                  {riskSearch && (
                    <button className="saas-clear-btn" onClick={() => setRiskSearch("")}>
                      <X size={13} />
                    </button>
                  )}
                </div>

                <div className="saas-filter-group">
                  <Filter size={13} className="text-muted" />
                  {[
                    { id: "all", label: `All (${summary.risks?.total_risks || 0})` },
                    { id: "high", label: `High / Critical (${summary.risks?.high_count || 0})` },
                    { id: "medium", label: `Medium (${summary.risks?.medium_count || 0})` },
                    { id: "low", label: `Low (${summary.risks?.low_count || 0})` },
                  ].map((f) => (
                    <button
                      key={f.id}
                      className={`saas-filter-pill ${riskSeverityFilter === f.id ? "active" : ""}`}
                      onClick={() => setRiskSeverityFilter(f.id)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>

              {filteredRisks.length === 0 ? (
                <div className="saas-table-empty">
                  <p>No project risks match the current filter criteria.</p>
                </div>
              ) : (
                <div className="saas-risks-cards-grid">
                  {filteredRisks.map((risk, idx) => {
                    const sevClass = getSeverityClass(risk.severity);
                    return (
                      <div
                        key={idx}
                        className={`saas-risk-card ${sevClass}`}
                        onClick={() => setSelectedRisk(risk)}
                        title="Click to view full risk details"
                      >
                        <div className="saas-risk-card-top">
                          <code className="saas-id-tag">{risk.risk_id}</code>
                          <span className={`saas-pill saas-pill-sm ${sevClass}`}>
                            {risk.severity} Severity
                          </span>
                        </div>

                        <h3 className="saas-risk-title">{risk.title}</h3>
                        <p className="saas-risk-desc">{risk.description}</p>

                        <div className="saas-risk-matrix-row">
                          <div className="saas-matrix-pill">
                            <span className="matrix-lbl">Likelihood:</span>
                            <span className="matrix-val">{risk.likelihood}</span>
                          </div>
                          <div className="saas-matrix-pill">
                            <span className="matrix-lbl">Impact:</span>
                            <span className="matrix-val">{risk.impact}</span>
                          </div>
                          <div className="saas-matrix-pill">
                            <span className="matrix-lbl">Owner:</span>
                            <span className="matrix-val">{risk.owner}</span>
                          </div>
                        </div>

                        {risk.recommended_mitigation && (
                          <div className="saas-mitigation-box">
                            <div className="saas-mitigation-header">
                              <ShieldCheck size={12} />
                              <span>Recommended Mitigation:</span>
                            </div>
                            <p>{risk.recommended_mitigation}</p>
                          </div>
                        )}

                        {risk.evidence && (
                          <div className="saas-evidence-snippet">
                            <Quote size={11} className="text-muted" />
                            <span className="snippet-text">"{risk.evidence}"</span>
                            {risk.source_document && (
                              <span className="snippet-src">— {risk.source_document}</span>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* BLOCKERS OVERVIEW SECTION */}
          {(subSection === "overview" || subSection === "blockers") && (
            <div className="saas-section-card" id="blockers-overview">
              <div className="saas-section-header">
                <div className="saas-header-left">
                  <div className="saas-icon-badge bg-danger-soft">
                    <Flame size={18} className="text-danger" />
                  </div>
                  <div>
                    <h2 className="saas-section-title">Blockers</h2>
                    <p className="saas-section-desc">
                      Critical impediments delaying active progress, owner accountability, and verified resolution status.
                    </p>
                  </div>
                </div>
                <div className="saas-badge-group">
                  <span className="saas-pill saas-pill-danger">
                    {summary.blockers?.open_count || 0} Open
                  </span>
                  <span className="saas-pill saas-pill-success">
                    {summary.blockers?.resolved_count || 0} Resolved
                  </span>
                </div>
              </div>

              {/* Blocker Filters & Search */}
              <div className="saas-table-toolbar">
                <div className="saas-search-box">
                  <Search size={14} className="text-muted" />
                  <input
                    type="text"
                    placeholder="Search blockers by description or owner..."
                    value={blockerSearch}
                    onChange={(e) => setBlockerSearch(e.target.value)}
                    className="saas-input"
                  />
                  {blockerSearch && (
                    <button className="saas-clear-btn" onClick={() => setBlockerSearch("")}>
                      <X size={13} />
                    </button>
                  )}
                </div>

                <div className="saas-filter-group">
                  <Filter size={13} className="text-muted" />
                  {[
                    { id: "all", label: `All (${summary.blockers?.total_blockers || 0})` },
                    { id: "open", label: `Open / Unresolved (${summary.blockers?.open_count || 0})` },
                    { id: "resolved", label: `Resolved (${summary.blockers?.resolved_count || 0})` },
                  ].map((f) => (
                    <button
                      key={f.id}
                      className={`saas-filter-pill ${blockerFilter === f.id ? "active" : ""}`}
                      onClick={() => setBlockerFilter(f.id)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>

              {filteredBlockers.length === 0 ? (
                <div className="saas-table-empty">
                  <p>Zero active blockers found matching the current filter.</p>
                </div>
              ) : (
                <div className="saas-blockers-grid">
                  {filteredBlockers.map((b, idx) => {
                    const isResolved =
                      b.status.toLowerCase().includes("resolved") ||
                      b.status.toLowerCase().includes("closed");
                    return (
                      <div
                        key={idx}
                        className={`saas-blocker-card ${isResolved ? "blocker-resolved" : "blocker-open"}`}
                        onClick={() => setSelectedBlocker(b)}
                        title="Click to view blocker resolution details"
                      >
                        <div className="saas-blocker-header">
                          <div className="saas-blocker-id-col">
                            <code className="saas-id-tag">{b.item_id}</code>
                            <span
                              className={`saas-pill saas-pill-sm ${
                                isResolved ? "badge-status-healthy" : "badge-status-risk"
                              }`}
                            >
                              {b.status}
                            </span>
                          </div>
                          <div className="saas-blocker-meta-right">
                            <div className="saas-date-badge">
                              <Calendar size={12} />
                              <span>Due: {b.due_date}</span>
                            </div>
                          </div>
                        </div>

                        <p className="saas-blocker-desc">{b.description}</p>

                        <div className="saas-blocker-info-row">
                          <div className="saas-user-badge">
                            <User size={12} />
                            <span
                              className={
                                b.owner === "UNKNOWN" || b.owner === "Unassigned"
                                  ? "text-danger font-semibold"
                                  : ""
                              }
                            >
                              Owner: {b.owner}
                            </span>
                          </div>
                          {b.source_document && (
                            <span className="saas-doc-badge">
                              <FileText size={11} /> {b.source_document}
                            </span>
                          )}
                        </div>

                        {b.resolution && (
                          <div className="saas-blocker-res-box">
                            <strong>Resolution Action:</strong> {b.resolution}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* =====================================================================
              SECTION 7: ACTION ITEMS AND UPCOMING ACTIVITIES
          ===================================================================== */}
          {(subSection === "overview" || subSection === "actions") && (
            <div className="saas-section-card" id="action-items">
              <div className="saas-section-header">
                <div className="saas-header-left">
                  <div className="saas-icon-badge bg-primary-soft">
                    <ListTodo size={18} className="text-primary" />
                  </div>
                  <div>
                    <h2 className="saas-section-title">Action Items & Upcoming Activities</h2>
                    <p className="saas-section-desc">
                      Assigned team tasks, priorities, verification deadlines, and overdue item detection.
                    </p>
                  </div>
                </div>
                <div className="saas-badge-group">
                  <span className="saas-pill saas-pill-primary">
                    {summary.action_items?.pending_count || 0} Pending
                  </span>
                  <span className="saas-pill saas-pill-success">
                    {summary.action_items?.completed_count || 0} Completed
                  </span>
                </div>
              </div>

              {/* Action Toolbar */}
              <div className="saas-table-toolbar">
                <div className="saas-search-box">
                  <Search size={14} className="text-muted" />
                  <input
                    type="text"
                    placeholder="Search actions by description, ID, or owner..."
                    value={actionSearch}
                    onChange={(e) => setActionSearch(e.target.value)}
                    className="saas-input"
                  />
                  {actionSearch && (
                    <button className="saas-clear-btn" onClick={() => setActionSearch("")}>
                      <X size={13} />
                    </button>
                  )}
                </div>

                <div className="saas-filter-group">
                  <Filter size={13} className="text-muted" />
                  {[
                    { id: "all", label: "All" },
                    { id: "pending", label: "Pending" },
                    { id: "completed", label: "Completed" },
                    { id: "high", label: "High Priority" },
                    { id: "unassigned", label: "Unassigned" },
                  ].map((f) => (
                    <button
                      key={f.id}
                      className={`saas-filter-pill ${actionFilter === f.id ? "active" : ""}`}
                      onClick={() => setActionFilter(f.id)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>

              {filteredActions.length === 0 ? (
                <div className="saas-table-empty">
                  <p>No action items match the current filters.</p>
                </div>
              ) : (
                <div className="saas-table-scroll">
                  <table className="saas-data-table">
                    <thead>
                      <tr>
                        <th style={{ width: "95px" }}>ID</th>
                        <th>Action Description</th>
                        <th style={{ width: "150px" }}>Assigned Owner</th>
                        <th style={{ width: "100px" }}>Priority</th>
                        <th style={{ width: "140px" }}>Due Date</th>
                        <th style={{ width: "115px" }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredActions.map((act, idx) => {
                        const overdue = isOverdue(act.due_date, act.status);
                        const isDone =
                          act.status.toLowerCase().includes("complete") ||
                          act.status.toLowerCase().includes("done");
                        return (
                          <tr
                            key={idx}
                            className="saas-clickable-row"
                            onClick={() => setSelectedAction(act)}
                            title="Click to view action item details"
                          >
                            <td>
                              <code className="saas-id-tag">{act.item_id}</code>
                            </td>
                            <td>
                              <span className="saas-name-cell">{act.description}</span>
                            </td>
                            <td>
                              <div className="saas-user-badge">
                                <User size={12} />
                                <span
                                  className={
                                    act.owner === "UNKNOWN" || act.owner === "Unassigned"
                                      ? "text-warning font-semibold"
                                      : ""
                                  }
                                >
                                  {act.owner}
                                </span>
                              </div>
                            </td>
                            <td>
                              <span className={`saas-priority-tag prio-${act.priority.toLowerCase()}`}>
                                {act.priority}
                              </span>
                            </td>
                            <td>
                              <div className="saas-date-badge">
                                <Calendar size={12} />
                                <span>{act.due_date}</span>
                                {overdue && <span className="saas-chip saas-chip-danger">Overdue</span>}
                              </div>
                            </td>
                            <td>
                              <span
                                className={`saas-pill saas-pill-sm ${
                                  isDone ? "badge-status-healthy" : "badge-status-attention"
                                }`}
                              >
                                {act.status}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* =====================================================================
              SECTION 8: AI PROJECT INSIGHTS (CLEAR SEPARATION OF EVIDENCE VS RECS)
          ===================================================================== */}
          {(subSection === "overview" || subSection === "insights") && (
            <div className="saas-section-card" id="ai-project-insights">
              <div className="saas-section-header">
                <div className="saas-header-left">
                  <div className="saas-icon-badge bg-cyan-soft">
                    <Sparkles size={18} className="text-cyan" />
                  </div>
                  <div>
                    <h2 className="saas-section-title">AI Project Insights</h2>
                    <p className="saas-section-desc">
                      Useful observations synthesized from uploaded project documents, with verified evidence distinguished from algorithmic recommendations.
                    </p>
                  </div>
                </div>
                <div className="saas-legend-row">
                  <span className="saas-legend-item">
                    <span className="legend-dot bg-cyan" /> Document Evidence (Verified Fact)
                  </span>
                  <span className="saas-legend-item">
                    <span className="legend-dot bg-purple" /> AI Recommendation (Advisory)
                  </span>
                </div>
              </div>

              {/* Category Filter Pills */}
              <div className="saas-insights-category-strip">
                {[
                  { id: "all", label: "All Insights" },
                  { id: "updates", label: "Important Updates" },
                  { id: "risks", label: "Emerging Risks" },
                  { id: "scope_timeline", label: "Scope & Timeline" },
                  { id: "decisions", label: "Pending Decisions" },
                  { id: "actions", label: "Recommended Actions" },
                ].map((cat) => (
                  <button
                    key={cat.id}
                    className={`saas-subnav-pill ${insightCategory === cat.id ? "active" : ""}`}
                    onClick={() => setInsightCategory(cat.id)}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {filteredInsights.length === 0 ? (
                <div className="saas-table-empty">
                  <p>No insights categorized under this filter.</p>
                </div>
              ) : (
                <div className="saas-insights-cards-grid">
                  {filteredInsights.map((ins) => {
                    const isEvidence = ins.type === "evidence";
                    return (
                      <div
                        key={ins.id}
                        className={`saas-insight-card ${
                          isEvidence ? "insight-evidence" : "insight-recommendation"
                        }`}
                      >
                        <div className="saas-insight-top">
                          <div className="saas-insight-type-badge">
                            {isEvidence ? (
                              <>
                                <Quote size={12} className="text-cyan" />
                                <span className="text-cyan font-bold">DOCUMENT EVIDENCE</span>
                              </>
                            ) : (
                              <>
                                <Sparkles size={12} className="text-purple" />
                                <span className="text-purple font-bold">AI RECOMMENDATION</span>
                              </>
                            )}
                          </div>
                          {ins.badge && (
                            <span
                              className={`saas-pill saas-pill-sm ${
                                isEvidence ? "saas-pill-primary" : "saas-pill-purple"
                              }`}
                            >
                              {ins.badge}
                            </span>
                          )}
                        </div>

                        <h3 className="saas-insight-title">{ins.title}</h3>
                        <p className="saas-insight-desc">{ins.description}</p>

                        {isEvidence ? (
                          <div className="saas-evidence-footer">
                            <FileText size={12} className="text-muted" />
                            <span>Source: {ins.sourceDoc}</span>
                            {ins.sourceExcerpt && (
                              <button
                                className="saas-link-btn"
                                onClick={() =>
                                  setCitationModal({
                                    title: ins.title,
                                    source: ins.sourceDoc,
                                    excerpt: ins.sourceExcerpt,
                                  })
                                }
                              >
                                View Excerpt
                              </button>
                            )}
                          </div>
                        ) : (
                          <div className="saas-rec-footer">
                            <HelpCircle size={12} className="text-muted" />
                            <span>Advisory suggestion algorithmically generated from project context.</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* =====================================================================
              ACTIVE KNOWLEDGE BASE DOCUMENTS FOOTER STRIP
          ===================================================================== */}
          <div className="saas-footer-strip">
            <div className="saas-footer-left">
              <FileText size={15} className="text-primary" />
              <span className="font-semibold">
                Active Knowledge Base: {summary.document_count} Document
                {summary.document_count === 1 ? "" : "s"} Ingested
              </span>
            </div>
            <div className="saas-doc-pills-wrap">
              {summary.documents.map((d, i) => (
                <span
                  key={i}
                  className="saas-doc-chip"
                  title={`Size: ${d.file_size_kb} KB, Chunks: ${d.chunk_count}, Uploaded: ${d.uploaded_at}`}
                >
                  <span className="doc-ext font-mono">{d.file_type.toUpperCase()}</span>
                  <span className="doc-name">{d.filename}</span>
                  <span className="doc-chunks">({d.chunk_count} chunks)</span>
                </span>
              ))}
            </div>
            <button className="saas-btn saas-btn-xs saas-btn-secondary" onClick={() => handleNav("ingest")}>
              Manage Documents <ChevronRight size={12} />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          UNIVERSAL INTERACTIVE DETAIL MODALS
      ========================================================================= */}

      {/* 1. Risk Detail Modal */}
      {selectedRisk && (
        <div className="saas-modal-overlay" onClick={() => setSelectedRisk(null)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <ShieldAlert size={20} className="text-warning" />
                <h3>Risk Details: {selectedRisk.risk_id}</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setSelectedRisk(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-field">
                <label>Risk Title</label>
                <div className="field-val font-semibold">{selectedRisk.title}</div>
              </div>
              <div className="saas-modal-field">
                <label>Description</label>
                <div className="field-val">{selectedRisk.description}</div>
              </div>
              <div className="saas-modal-grid">
                <div>
                  <label>Severity</label>
                  <span className={`saas-pill ${getSeverityClass(selectedRisk.severity)}`}>
                    {selectedRisk.severity}
                  </span>
                </div>
                <div>
                  <label>Likelihood</label>
                  <div className="field-val">{selectedRisk.likelihood}</div>
                </div>
                <div>
                  <label>Impact</label>
                  <div className="field-val">{selectedRisk.impact}</div>
                </div>
                <div>
                  <label>Assigned Owner</label>
                  <div className="field-val">{selectedRisk.owner}</div>
                </div>
              </div>
              {selectedRisk.recommended_mitigation && (
                <div className="saas-modal-box bg-primary-soft">
                  <label className="text-primary font-semibold">Recommended Mitigation</label>
                  <p>{selectedRisk.recommended_mitigation}</p>
                </div>
              )}
              {selectedRisk.evidence && (
                <div className="saas-modal-box bg-dark-soft">
                  <label className="text-muted font-semibold">Verbatim Source Evidence</label>
                  <p className="italic">"{selectedRisk.evidence}"</p>
                  {selectedRisk.source_document && (
                    <span className="text-xs text-muted block mt-1">
                      Source: {selectedRisk.source_document}
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setSelectedRisk(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Blocker Detail Modal */}
      {selectedBlocker && (
        <div className="saas-modal-overlay" onClick={() => setSelectedBlocker(null)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <Flame size={20} className="text-danger" />
                <h3>Blocker Details: {selectedBlocker.item_id}</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setSelectedBlocker(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-field">
                <label>Description</label>
                <div className="field-val font-semibold">{selectedBlocker.description}</div>
              </div>
              <div className="saas-modal-grid">
                <div>
                  <label>Status</label>
                  <span className={`saas-pill ${getStatusBadgeClass(selectedBlocker.status)}`}>
                    {selectedBlocker.status}
                  </span>
                </div>
                <div>
                  <label>Assigned Owner</label>
                  <div className="field-val">{selectedBlocker.owner}</div>
                </div>
                <div>
                  <label>Due Date</label>
                  <div className="field-val">{selectedBlocker.due_date}</div>
                </div>
                <div>
                  <label>Source Document</label>
                  <div className="field-val text-xs">{selectedBlocker.source_document || "Project Registry"}</div>
                </div>
              </div>
              {selectedBlocker.resolution && (
                <div className="saas-modal-box bg-success-soft">
                  <label className="text-success font-semibold">Resolution / Recommended Action</label>
                  <p>{selectedBlocker.resolution}</p>
                </div>
              )}
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setSelectedBlocker(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Deliverable Detail Modal */}
      {selectedDeliverable && (
        <div className="saas-modal-overlay" onClick={() => setSelectedDeliverable(null)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <Target size={20} className="text-primary" />
                <h3>Deliverable: {selectedDeliverable.deliverable_id}</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setSelectedDeliverable(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-field">
                <label>Deliverable Name</label>
                <div className="field-val font-semibold">{selectedDeliverable.name}</div>
              </div>
              <div className="saas-modal-grid">
                <div>
                  <label>Status</label>
                  <span className={`saas-pill ${getStatusBadgeClass(selectedDeliverable.status)}`}>
                    {selectedDeliverable.status}
                  </span>
                </div>
                <div>
                  <label>Owner</label>
                  <div className="field-val">{selectedDeliverable.owner}</div>
                </div>
                <div>
                  <label>Target Date</label>
                  <div className="field-val">{selectedDeliverable.target_date}</div>
                </div>
                <div>
                  <label>Source Reference</label>
                  <div className="field-val text-xs">{selectedDeliverable.source_ref || "Document Table"}</div>
                </div>
              </div>
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setSelectedDeliverable(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. Action Item Detail Modal */}
      {selectedAction && (
        <div className="saas-modal-overlay" onClick={() => setSelectedAction(null)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <ListTodo size={20} className="text-primary" />
                <h3>Action Item: {selectedAction.item_id}</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setSelectedAction(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-field">
                <label>Description</label>
                <div className="field-val font-semibold">{selectedAction.description}</div>
              </div>
              <div className="saas-modal-grid">
                <div>
                  <label>Priority</label>
                  <span className={`saas-priority-tag prio-${selectedAction.priority.toLowerCase()}`}>
                    {selectedAction.priority}
                  </span>
                </div>
                <div>
                  <label>Status</label>
                  <span className={`saas-pill ${getStatusBadgeClass(selectedAction.status)}`}>
                    {selectedAction.status}
                  </span>
                </div>
                <div>
                  <label>Owner</label>
                  <div className="field-val">{selectedAction.owner}</div>
                </div>
                <div>
                  <label>Due Date</label>
                  <div className="field-val">{selectedAction.due_date}</div>
                </div>
              </div>
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setSelectedAction(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Citation / Source Evidence Modal */}
      {citationModal && (
        <div className="saas-modal-overlay" onClick={() => setCitationModal(null)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <Quote size={20} className="text-cyan" />
                <h3>Document Evidence Citation</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setCitationModal(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-field">
                <label>Entity / Topic</label>
                <div className="field-val font-semibold">{citationModal.title}</div>
              </div>
              {citationModal.source && (
                <div className="saas-modal-field">
                  <label>Source Document / Reference</label>
                  <div className="field-val font-mono text-xs">{citationModal.source}</div>
                </div>
              )}
              {citationModal.excerpt && (
                <div className="saas-modal-box bg-dark-soft">
                  <label className="text-cyan font-semibold">Verbatim Document Excerpt</label>
                  <p className="italic leading-relaxed mt-1">"{citationModal.excerpt}"</p>
                </div>
              )}
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setCitationModal(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. Project Workspace Manager Modal */}
      {workspaceModalOpen && (
        <div className="saas-modal-overlay" onClick={() => setWorkspaceModalOpen(false)}>
          <div className="saas-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="saas-modal-header">
              <div className="saas-modal-header-left">
                <FolderGit2 size={20} className="text-primary" />
                <h3>Project Workspace Management</h3>
              </div>
              <button className="saas-modal-close" onClick={() => setWorkspaceModalOpen(false)}>
                <X size={16} />
              </button>
            </div>
            <div className="saas-modal-body">
              <div className="saas-modal-box bg-dark-soft">
                <label className="text-muted font-semibold">Active Workspace Details</label>
                <div className="saas-modal-grid mt-2">
                  <div>
                    <span className="text-xs text-muted block">Project ID:</span>
                    <code className="text-xs font-mono">{summary?.project_id || "workspace_default"}</code>
                  </div>
                  <div>
                    <span className="text-xs text-muted block">Project Name:</span>
                    <span className="text-xs font-semibold">{summary?.project_name || "Default Project"}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted block">Client:</span>
                    <span className="text-xs">{summary?.client || "Not Specified"}</span>
                  </div>
                  <div>
                    <span className="text-xs text-muted block">Documents:</span>
                    <span className="text-xs">{summary?.document_count || 0} File(s)</span>
                  </div>
                </div>
              </div>

              {workspaceActionError && (
                <div className="saas-alert-banner alert-danger text-xs p-2">
                  {workspaceActionError}
                </div>
              )}

              {/* Form to Start New Project Workspace */}
              <form onSubmit={handleCreateNewWorkspace} className="saas-workspace-form">
                <h4 className="font-semibold text-sm">Start Fresh Project Workspace</h4>
                <p className="text-xs text-muted">
                  Create a new isolated project domain. This prepares a clean vector store for new documents without cross-project bleed.
                </p>

                <div className="saas-form-group">
                  <label className="text-xs">Project Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Apex ERP Modernization"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    className="saas-input"
                  />
                </div>

                <div className="saas-form-group">
                  <label className="text-xs">Custom Project ID (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. APEX-2026-01"
                    value={newProjectId}
                    onChange={(e) => setNewProjectId(e.target.value)}
                    className="saas-input font-mono"
                  />
                </div>

                <button
                  type="submit"
                  disabled={workspaceActionLoading || !newProjectName.trim()}
                  className="saas-btn saas-btn-primary w-full"
                >
                  <PlusCircle size={14} />
                  <span>{workspaceActionLoading ? "Initializing..." : "Create Project Workspace"}</span>
                </button>
              </form>

              <hr className="saas-modal-divider" />

              <div className="saas-danger-zone">
                <span className="text-xs text-danger font-semibold">Danger Zone</span>
                <p className="text-xs text-muted">
                  Reset the current workspace, purging all ingested documents, embeddings, and cached analysis.
                </p>
                <button
                  type="button"
                  disabled={workspaceActionLoading}
                  onClick={handleResetWorkspace}
                  className="saas-btn saas-btn-danger saas-btn-sm"
                >
                  <RotateCcw size={13} />
                  <span>Reset Active Workspace</span>
                </button>
              </div>
            </div>
            <div className="saas-modal-footer">
              <button className="saas-btn saas-btn-secondary" onClick={() => setWorkspaceModalOpen(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

