import { useState, useEffect } from "react";
import {
  FileText,
  Download,
  RefreshCw,
  Sparkles,
  ShieldAlert,
  ListTodo,
  Check,
  X,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  DocumentationGenerationResponse,
  generateDocumentation,
  getCurrentDocumentation,
  updateDocItemReview,
  getExportDocsUrl,
} from "../services/api";

interface Props {
  workspaceVersion?: number;
}

export function DocumentationGenerationView({ workspaceVersion }: Props) {
  const [data, setData] = useState<DocumentationGenerationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"stories" | "risks" | "actions">("stories");
  const [expandedStory, setExpandedStory] = useState<string | null>(null);

  const loadDocumentation = async (force: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      const res = force ? await generateDocumentation(undefined, true) : await getCurrentDocumentation();
      setData(res);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to generate project documentation.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocumentation(false);
  }, [workspaceVersion]);

  const handleStatusUpdate = async (
    itemType: "user_story" | "risk" | "action_item",
    itemId: string,
    status: "Approved" | "Rejected" | "Draft",
    editedFields?: Record<string, any>
  ) => {
    try {
      await updateDocItemReview({
        item_type: itemType,
        item_id: itemId,
        review_status: status,
        edited_fields: editedFields,
      });
      // Update local state
      setData((prev) => {
        if (!prev) return prev;
        if (itemType === "user_story") {
          return {
            ...prev,
            user_stories: prev.user_stories.map((s) =>
              s.story_id === itemId ? { ...s, review_status: status, ...(editedFields || {}) } : s
            ),
          };
        } else if (itemType === "risk") {
          return {
            ...prev,
            risk_register: prev.risk_register.map((r) =>
              r.risk_id === itemId ? { ...r, review_status: status, ...(editedFields || {}) } : r
            ),
          };
        } else {
          return {
            ...prev,
            action_items: prev.action_items.map((a) =>
              a.action_id === itemId ? { ...a, review_status: status, ...(editedFields || {}) } : a
            ),
          };
        }
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update review status");
    }
  };

  return (
    <div className="docgen-container card">
      {/* Header Row */}
      <div className="docgen-header">
        <div>
          <span className="section-eyebrow">Milestone 3 Autonomous Agent</span>
          <h2 className="section-title">Documentation Generation Studio</h2>
          <p className="section-desc">
            Synthesizes structured Agile user stories with Given-When-Then criteria, risk registers, and action items grounded in project documents.
          </p>
        </div>

        <div className="docgen-action-bar">
          <button
            className="btn btn-primary"
            onClick={() => loadDocumentation(true)}
            disabled={loading}
          >
            {loading ? <RefreshCw size={16} className="spin" /> : <Sparkles size={16} />}
            {loading ? "Synthesizing..." : "Generate All Documents"}
          </button>

          {data && (
            <div className="export-dropdown-wrap">
              <a
                href={getExportDocsUrl(
                  activeTab === "stories" ? "user_stories" : activeTab === "risks" ? "risk_register" : "action_items"
                )}
                download
                className="btn btn-secondary"
              >
                <Download size={15} />
                Export {activeTab === "stories" ? "Stories" : activeTab === "risks" ? "Risks" : "Actions"} (CSV)
              </a>
            </div>
          )}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Navigation Tabs */}
      <div className="docgen-tabs">
        <button
          className={`docgen-tab-btn ${activeTab === "stories" ? "active" : ""}`}
          onClick={() => setActiveTab("stories")}
        >
          <FileText size={16} />
          User Stories ({data?.user_stories.length || 0})
        </button>
        <button
          className={`docgen-tab-btn ${activeTab === "risks" ? "active" : ""}`}
          onClick={() => setActiveTab("risks")}
        >
          <ShieldAlert size={16} />
          Risk Register ({data?.risk_register.length || 0})
        </button>
        <button
          className={`docgen-tab-btn ${activeTab === "actions" ? "active" : ""}`}
          onClick={() => setActiveTab("actions")}
        >
          <ListTodo size={16} />
          Action Items ({data?.action_items.length || 0})
        </button>
      </div>

      {/* Content Area */}
      {loading && !data ? (
        <div className="loading-state">
          <RefreshCw size={32} className="spin text-accent" />
          <p>Extracting project requirements and synthesizing documentation...</p>
        </div>
      ) : !data || (data.user_story_count === 0 && data.risk_count === 0 && data.action_item_count === 0) ? (
        <div className="empty-state">
          <FileText size={42} />
          <p>No project documentation has been generated yet.</p>
          <p className="empty-state-subtext">
            Upload project charters, requirements, or meeting minutes and click "Generate All Documents".
          </p>
        </div>
      ) : (
        <div className="docgen-content">
          {/* TAB 1: USER STORIES */}
          {activeTab === "stories" && (
            <div className="stories-list">
              {data.user_stories.map((story) => (
                <div
                  key={story.story_id}
                  className={`story-card ${story.review_status === "Approved" ? "approved" : story.review_status === "Rejected" ? "rejected" : ""}`}
                >
                  <div className="story-card-header">
                    <div className="story-badge-cluster">
                      <span className="badge badge-accent font-mono">{story.story_id}</span>
                      <span className="badge badge-subtle">{story.user_actor}</span>
                      <span
                        className={`badge ${
                          story.priority === "Must Have" ? "badge-danger" : "badge-warning"
                        }`}
                      >
                        {story.priority}
                      </span>
                      <span
                        className={`badge ${
                          story.review_status === "Approved"
                            ? "badge-success"
                            : story.review_status === "Rejected"
                            ? "badge-danger"
                            : "badge-subtle"
                        }`}
                      >
                        {story.review_status}
                      </span>
                    </div>

                    <div className="story-actions">
                      {story.review_status !== "Approved" && (
                        <button
                          className="btn-icon btn-approve"
                          title="Approve User Story"
                          onClick={() => handleStatusUpdate("user_story", story.story_id, "Approved")}
                        >
                          <Check size={15} /> Approve
                        </button>
                      )}
                      {story.review_status !== "Rejected" && (
                        <button
                          className="btn-icon btn-reject"
                          title="Reject User Story"
                          onClick={() => handleStatusUpdate("user_story", story.story_id, "Rejected")}
                        >
                          <X size={15} /> Reject
                        </button>
                      )}
                      <button
                        className="btn-icon"
                        title="Toggle Acceptance Criteria"
                        onClick={() =>
                          setExpandedStory(expandedStory === story.story_id ? null : story.story_id)
                        }
                      >
                        {expandedStory === story.story_id ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                      </button>
                    </div>
                  </div>

                  {/* Formatted Story Statement */}
                  <div className="story-body">
                    <p className="story-text">
                      <span className="story-highlight font-semibold">"{story.formatted_story}"</span>
                    </p>

                    {/* Source Evidence Grounding */}
                    <div className="provenance-tag">
                      <span className="text-muted text-xs">
                        Source: <strong>{story.source_document}</strong> ({story.source_ref || "Doc"}) —{" "}
                        <em>"{story.source_evidence.slice(0, 160)}..."</em>
                      </span>
                    </div>

                    {/* Expandable Acceptance Criteria */}
                    {expandedStory === story.story_id && (
                      <div className="acceptance-criteria-panel">
                        <h4 className="criteria-heading">Given-When-Then Acceptance Criteria:</h4>
                        <ul className="criteria-list">
                          {story.acceptance_criteria.map((crit, idx) => (
                            <li
                              key={idx}
                              className={`criteria-item ${crit.includes("[AI-proposed") ? "ai-proposed" : ""}`}
                            >
                              {crit}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 2: RISK REGISTER */}
          {activeTab === "risks" && (
            <div className="risks-table-wrap">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Risk Title</th>
                    <th>Severity</th>
                    <th>Impact / Cause</th>
                    <th>Mitigation Action</th>
                    <th>Responsible</th>
                    <th>Status</th>
                    <th>Review</th>
                  </tr>
                </thead>
                <tbody>
                  {data.risk_register.map((r) => (
                    <tr
                      key={r.risk_id}
                      className={
                        r.review_status === "Approved"
                          ? "row-approved"
                          : r.review_status === "Rejected"
                          ? "row-rejected"
                          : ""
                      }
                    >
                      <td className="font-mono font-bold text-accent">{r.risk_id}</td>
                      <td>
                        <strong>{r.risk_title}</strong>
                        <div className="text-muted text-xs">{r.source_document}</div>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            r.severity === "Critical"
                              ? "badge-danger"
                              : r.severity === "High"
                              ? "badge-warning"
                              : "badge-subtle"
                          }`}
                        >
                          {r.severity}
                        </span>
                      </td>
                      <td className="text-sm">
                        <div><strong>Cause:</strong> {r.cause}</div>
                        <div><strong>Impact:</strong> {r.impact}</div>
                      </td>
                      <td className="text-sm">
                        {r.mitigation_action}
                        {r.mitigation_type === "AI-proposed" && (
                          <span className="badge badge-subtle text-xs ml-1">[AI-proposed]</span>
                        )}
                      </td>
                      <td className="text-sm">{r.responsible_party}</td>
                      <td>
                        <span className="badge badge-accent">{r.status}</span>
                      </td>
                      <td>
                        <div className="review-btn-row">
                          <button
                            className="btn-icon btn-approve"
                            title="Approve"
                            onClick={() => handleStatusUpdate("risk", r.risk_id, "Approved")}
                          >
                            <Check size={14} />
                          </button>
                          <button
                            className="btn-icon btn-reject"
                            title="Reject"
                            onClick={() => handleStatusUpdate("risk", r.risk_id, "Rejected")}
                          >
                            <X size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: ACTION ITEMS */}
          {activeTab === "actions" && (
            <div className="actions-table-wrap">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Action Description</th>
                    <th>Responsible Party</th>
                    <th>Deadline</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Source Document</th>
                    <th>Review</th>
                  </tr>
                </thead>
                <tbody>
                  {data.action_items.map((a) => (
                    <tr
                      key={a.action_id}
                      className={
                        a.review_status === "Approved"
                          ? "row-approved"
                          : a.review_status === "Rejected"
                          ? "row-rejected"
                          : ""
                      }
                    >
                      <td className="font-mono font-bold text-accent">{a.action_id}</td>
                      <td>
                        <strong>{a.action_description}</strong>
                        {a.related_blocker_or_risk && (
                          <div className="text-muted text-xs">
                            Related: {a.related_blocker_or_risk}
                          </div>
                        )}
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            a.responsible_party === "Not specified" ? "badge-warning" : "badge-subtle"
                          }`}
                        >
                          {a.responsible_party}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            a.deadline === "Not specified" ? "badge-warning" : "badge-subtle"
                          }`}
                        >
                          {a.deadline}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            a.priority === "High"
                              ? "badge-danger"
                              : a.priority === "Medium"
                              ? "badge-warning"
                              : "badge-subtle"
                          }`}
                        >
                          {a.priority}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-accent">{a.status}</span>
                      </td>
                      <td className="text-xs text-muted">{a.source_document}</td>
                      <td>
                        <div className="review-btn-row">
                          <button
                            className="btn-icon btn-approve"
                            title="Approve"
                            onClick={() => handleStatusUpdate("action_item", a.action_id, "Approved")}
                          >
                            <Check size={14} />
                          </button>
                          <button
                            className="btn-icon btn-reject"
                            title="Reject"
                            onClick={() => handleStatusUpdate("action_item", a.action_id, "Rejected")}
                          >
                            <X size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
