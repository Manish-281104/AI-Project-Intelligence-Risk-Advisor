import React from "react";
import { CheckCircle2, AlertCircle, RefreshCw, ExternalLink, ShieldCheck } from "lucide-react";
import { HealthResponse } from "../services/api";

interface NavbarProps {
  health: HealthResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  apiBaseUrl: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  loading,
  error,
  onRefresh,
  apiBaseUrl,
}) => {
  const isOnline = Boolean(health && !error);

  return (
    <header className="navbar-container">
      <div className="navbar-content">
        {/* Brand */}
        <div className="navbar-brand">
          <div className="brand-logo-wrap">
            <ShieldCheck className="brand-icon" size={24} />
          </div>
          <div>
            <div className="brand-title-wrap">
              <span className="brand-title">AI Project Intelligence & Risk Advisor</span>
            </div>
            <p className="brand-subtitle">
              Automated Project Intelligence & Risk Advisory Platform
            </p>
          </div>
        </div>

        {/* Navigation & Status */}
        <div className="navbar-actions">
          {/* Quick anchor links */}
          <nav className="nav-links">
            <a href="#ingestion" className="nav-link">Documents</a>
            <a href="#ai-advisor" className="nav-link">Analysis</a>
            <a href="#modules" className="nav-link">Modules</a>
            <a
              href={`${apiBaseUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="nav-link nav-link-external"
            >
              <span>API Docs</span>
              <ExternalLink size={14} />
            </a>
          </nav>

          {/* Backend Connection Indicator */}
          <div className="connection-status-pill">
            {loading ? (
              <span className="status-pill status-loading">
                <RefreshCw size={13} className="spin-icon" />
                <span>Checking API...</span>
              </span>
            ) : isOnline ? (
              <span className="status-pill status-online" title={`Server timestamp: ${health?.timestamp}`}>
                <CheckCircle2 size={14} />
                <span>Backend Online ({health?.version})</span>
              </span>
            ) : (
              <span className="status-pill status-offline" title={error || "Server unreachable"}>
                <AlertCircle size={14} />
                <span>Backend Offline</span>
              </span>
            )}

            <button
              onClick={onRefresh}
              disabled={loading}
              className="btn-icon"
              title="Ping backend health again"
              aria-label="Refresh backend status"
            >
              <RefreshCw size={14} className={loading ? "spin-icon" : ""} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
