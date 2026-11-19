import { useState, useEffect } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  ShieldAlert,
  History,
} from "lucide-react";
import {
  ProjectHealthResponse,
  HealthSnapshot,
  getProjectHealth,
  getHealthScoreHistory,
} from "../services/api";

interface Props {
  workspaceVersion?: number;
}

export function ProjectHealthView({ workspaceVersion }: Props) {
  const [health, setHealth] = useState<ProjectHealthResponse | null>(null);
  const [history, setHistory] = useState<HealthSnapshot[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState<boolean>(false);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getProjectHealth();
      setHealth(res);
      const hist = await getHealthScoreHistory();
      setHistory(hist);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to calculate project health.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, [workspaceVersion]);

  const getScoreColorClass = (category: string) => {
    switch (category) {
      case "Healthy":
        return "text-success border-success";
      case "Needs Attention":
        return "text-warning border-warning";
      case "At Risk":
        return "text-orange border-orange";
      case "Critical":
        return "text-danger border-danger";
      default:
        return "text-muted border-muted";
    }
  };

  const getBadgeClass = (category: string) => {
    switch (category) {
      case "Healthy":
        return "badge-success";
      case "Needs Attention":
        return "badge-warning";
      case "At Risk":
        return "badge-danger";
      case "Critical":
        return "badge-danger";
      default:
        return "badge-subtle";
    }
  };

  return (
    <div className="health-container card">
      {/* Header */}
      <div className="health-header">
        <div>
          <span className="section-eyebrow">Milestone 3 Analytics</span>
          <h2 className="section-title">Deterministic Project Health Scoring</h2>
          <p className="section-desc">
            Mathematical composite health evaluation across Scope Clarity (35%), Timeline Health (35%), and Blocker Health (30%) without synthetic or hallucinated metrics.
          </p>
        </div>

        <div className="health-actions">
          <button
            className="btn btn-secondary"
            onClick={() => setShowHistory(!showHistory)}
          >
            <History size={16} />
            {showHistory ? "Hide History" : `Score History (${history.length})`}
          </button>

          <button
            className="btn btn-primary"
            onClick={fetchHealth}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            {loading ? "Calculating..." : "Recalculate Health"}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Main Score Overview */}
      {loading && !health ? (
        <div className="loading-state">
          <RefreshCw size={32} className="spin text-accent" />
          <p>Evaluating project evidence and calculating deterministic health score...</p>
        </div>
      ) : health ? (
        <div className="health-content">
          {/* Top Score Banner */}
          <div className="health-hero-banner">
            <div className={`score-circle ${getScoreColorClass(health.health_category)}`}>
              <div className="score-value">
                {health.overall_score !== null ? health.overall_score : "N/A"}
              </div>
              <div className="score-max">/ 100</div>
            </div>

            <div className="score-info">
              <div className="score-title-row">
                <h3 className="score-category-title">{health.health_category}</h3>
                <span className={`badge ${getBadgeClass(health.health_category)}`}>
                  {health.health_category}
                </span>
                {health.is_insufficient_data && (
                  <span className="badge badge-warning">Insufficient Evidence</span>
                )}
              </div>

              <p className="score-formula-explanation">
                <strong>Formula:</strong>{" "}
                <code>
                  (Scope Clarity × {health.weights.scope_clarity * 100}%) + (Timeline Health ×{" "}
                  {health.weights.timeline_health * 100}%) + (Blocker Health ×{" "}
                  {health.weights.blocker_health * 100}%)
                </code>
              </p>

              <div className="score-timestamp text-muted text-xs">
                Calculated at: {new Date(health.calculated_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Missing Data Alert */}
          {health.is_insufficient_data && (
            <div className="alert alert-warning">
              <AlertTriangle size={18} />
              <div>
                <strong>Insufficient Data:</strong> Project evidence is incomplete for full health scoring. Missing elements:{" "}
                {health.missing_information.join(", ")}. Upload complete project schedules and risk logs to establish precision.
              </div>
            </div>
          )}

          {/* Dimension Cards (3-column grid) */}
          <div className="dimensions-grid">
            {/* Dimension 1: Scope Clarity */}
            <div className="dimension-card">
              <div className="dim-header">
                <span className="dim-title">{health.scope_clarity.dimension_name}</span>
                <span className="dim-weight">Weight: {health.scope_clarity.weight * 100}%</span>
              </div>

              <div className="dim-score-row">
                <span className="dim-score-val">{health.scope_clarity.raw_score}</span>
                <span className="text-muted text-xs">/ 100 (Contribution: +{health.scope_clarity.weighted_score})</span>
                <span className={`badge ${getBadgeClass(health.scope_clarity.category)} ml-auto`}>
                  {health.scope_clarity.category}
                </span>
              </div>

              <div className="progress-bar-wrap">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${Math.min(100, health.scope_clarity.raw_score)}%` }}
                />
              </div>

              <p className="dim-explanation text-xs text-muted">{health.scope_clarity.explanation}</p>

              <div className="dim-factors-wrap">
                <strong className="text-xs">Contributing Factors:</strong>
                <ul className="dim-factors-list">
                  {health.scope_clarity.contributing_factors.map((f, i) => (
                    <li key={i} className="text-xs text-muted">
                      ✓ {f}
                    </li>
                  ))}
                  {health.scope_clarity.critical_issues.map((issue, i) => (
                    <li key={i} className="text-xs text-danger">
                      ✗ {issue}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Dimension 2: Timeline Health */}
            <div className="dimension-card">
              <div className="dim-header">
                <span className="dim-title">{health.timeline_health.dimension_name}</span>
                <span className="dim-weight">Weight: {health.timeline_health.weight * 100}%</span>
              </div>

              <div className="dim-score-row">
                <span className="dim-score-val">{health.timeline_health.raw_score}</span>
                <span className="text-muted text-xs">/ 100 (Contribution: +{health.timeline_health.weighted_score})</span>
                <span className={`badge ${getBadgeClass(health.timeline_health.category)} ml-auto`}>
                  {health.timeline_health.category}
                </span>
              </div>

              <div className="progress-bar-wrap">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${Math.min(100, health.timeline_health.raw_score)}%` }}
                />
              </div>

              <p className="dim-explanation text-xs text-muted">{health.timeline_health.explanation}</p>

              <div className="dim-factors-wrap">
                <strong className="text-xs">Contributing Factors:</strong>
                <ul className="dim-factors-list">
                  {health.timeline_health.contributing_factors.map((f, i) => (
                    <li key={i} className="text-xs text-muted">
                      ✓ {f}
                    </li>
                  ))}
                  {health.timeline_health.critical_issues.map((issue, i) => (
                    <li key={i} className="text-xs text-danger">
                      ✗ {issue}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Dimension 3: Blocker Health */}
            <div className="dimension-card">
              <div className="dim-header">
                <span className="dim-title">{health.blocker_health.dimension_name}</span>
                <span className="dim-weight">Weight: {health.blocker_health.weight * 100}%</span>
              </div>

              <div className="dim-score-row">
                <span className="dim-score-val">{health.blocker_health.raw_score}</span>
                <span className="text-muted text-xs">/ 100 (Contribution: +{health.blocker_health.weighted_score})</span>
                <span className={`badge ${getBadgeClass(health.blocker_health.category)} ml-auto`}>
                  {health.blocker_health.category}
                </span>
              </div>

              <div className="progress-bar-wrap">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${Math.min(100, health.blocker_health.raw_score)}%` }}
                />
              </div>

              <p className="dim-explanation text-xs text-muted">{health.blocker_health.explanation}</p>

              <div className="dim-factors-wrap">
                <strong className="text-xs">Contributing Factors:</strong>
                <ul className="dim-factors-list">
                  {health.blocker_health.contributing_factors.map((f, i) => (
                    <li key={i} className="text-xs text-muted">
                      ✓ {f}
                    </li>
                  ))}
                  {health.blocker_health.critical_issues.map((issue, i) => (
                    <li key={i} className="text-xs text-danger">
                      ✗ {issue}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Action Recommendations & Critical Issues */}
          <div className="health-details-row">
            {health.critical_issues.length > 0 && (
              <div className="health-detail-box issues-box">
                <h4 className="detail-box-title text-danger">
                  <ShieldAlert size={16} /> Critical Issues Affecting Health
                </h4>
                <ul className="detail-list">
                  {health.critical_issues.map((issue, idx) => (
                    <li key={idx} className="detail-item text-danger text-sm">
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {health.recommended_corrective_actions.length > 0 && (
              <div className="health-detail-box recommendations-box">
                <h4 className="detail-box-title text-accent">
                  <CheckCircle2 size={16} /> Recommended Corrective Actions
                </h4>
                <ul className="detail-list">
                  {health.recommended_corrective_actions.map((rec, idx) => (
                    <li key={idx} className="detail-item text-sm">
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Historical Score Snapshots Panel */}
          {showHistory && (
            <div className="history-panel">
              <h4 className="detail-box-title">
                <History size={16} /> Recorded Historical Health Snapshots
              </h4>
              {history.length === 0 ? (
                <p className="text-muted text-sm">No historical snapshots recorded yet.</p>
              ) : (
                <table className="custom-table history-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Overall Score</th>
                      <th>Category</th>
                      <th>Scope Score</th>
                      <th>Timeline Score</th>
                      <th>Blocker Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((snap) => (
                      <tr key={snap.snapshot_id}>
                        <td className="text-xs font-mono">{new Date(snap.timestamp).toLocaleString()}</td>
                        <td className="font-bold">{snap.overall_score !== null ? snap.overall_score : "N/A"}</td>
                        <td>
                          <span className={`badge ${getBadgeClass(snap.health_category)}`}>
                            {snap.health_category}
                          </span>
                        </td>
                        <td>{snap.scope_score}</td>
                        <td>{snap.timeline_score}</td>
                        <td>{snap.blocker_score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
