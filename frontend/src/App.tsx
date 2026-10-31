import { useState, useEffect } from "react";
import {
  checkHealth,
  getModules,
  HealthResponse,
  ModuleItem,
  API_BASE_URL,
} from "./services/api";
import { Navbar } from "./components/Navbar";
import { FileUpload } from "./components/FileUpload";
import { AgentAnalysisView } from "./components/AgentAnalysisView";
import { ModuleCard } from "./components/ModuleCard";
import { Cpu, Layers } from "lucide-react";

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [modules, setModules] = useState<ModuleItem[]>([]);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [loadingModules, setLoadingModules] = useState<boolean>(true);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [moduleFilter, setModuleFilter] = useState<"all" | "active" | "planned">("all");
  const [workspaceVersion, setWorkspaceVersion] = useState<number>(0);

  const fetchHealthData = async () => {
    setLoadingHealth(true);
    setHealthError(null);
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch (err) {
      if (err instanceof Error) {
        setHealthError(err.message);
      } else {
        setHealthError("Failed to reach FastAPI backend server.");
      }
      setHealth(null);
    } finally {
      setLoadingHealth(false);
    }
  };

  const fetchModulesData = async () => {
    setLoadingModules(true);
    try {
      const data = await getModules();
      setModules(data.modules);
    } catch {
      setModules([]);
    } finally {
      setLoadingModules(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    fetchModulesData();
  }, []);

  const filteredModules = modules.filter((m) => {
    if (moduleFilter === "active") return m.status === "Partially Implemented" || m.status === "Implemented and Verified";
    if (moduleFilter === "planned") return m.status === "Planned";
    return true;
  });

  return (
    <div className="app-layout">
      {/* Navigation Header */}
      <Navbar
        health={health}
        loading={loadingHealth}
        error={healthError}
        onRefresh={() => {
          fetchHealthData();
          fetchModulesData();
        }}
        apiBaseUrl={API_BASE_URL}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <div className="hero-badge-wrap">
              <span className="badge badge-hero">
                <Cpu size={14} />
                Autonomous Project Intelligence
              </span>
            </div>
            <h1 className="hero-title">
              AI Project Intelligence &<br />
              <span className="text-gradient">Risk Advisory Platform</span>
            </h1>

            <div className="hero-stats-row">
              <div className="stat-pill active">
                <span className="stat-number">3</span>
                <span className="stat-label">AI Agents (Scope, Risks, Blockers)</span>
              </div>
              <div className="stat-pill active">
                <span className="stat-number">4</span>
                <span className="stat-label">Formats (PDF, DOCX, CSV, TXT)</span>
              </div>
            </div>
          </div>
        </section>

        {/* Document Ingestion Component */}
        <section className="section-wrapper">
          <FileUpload onWorkspaceChanged={() => setWorkspaceVersion((v) => v + 1)} />
        </section>

        {/* Autonomous Agent Analysis View */}
        <section className="section-wrapper">
          <AgentAnalysisView workspaceVersion={workspaceVersion} />
        </section>

        {/* Modules Section */}
        <section className="section-wrapper" id="modules">
          <div className="modules-header-row">
            <div>
              <span className="section-eyebrow">System Architecture</span>
              <h2 className="section-title">Core System Modules</h2>
              <p className="section-desc">
                Current operational status of system capabilities and planned features.
              </p>
            </div>

            {/* Filter Buttons */}
            <div className="filter-button-group">
              <button
                className={`btn-filter ${moduleFilter === "all" ? "active" : ""}`}
                onClick={() => setModuleFilter("all")}
              >
                All Modules ({modules.length})
              </button>
              <button
                className={`btn-filter ${moduleFilter === "active" ? "active" : ""}`}
                onClick={() => setModuleFilter("active")}
              >
                Active ({modules.filter(m => m.status === "Partially Implemented" || m.status === "Implemented and Verified").length})
              </button>
              <button
                className={`btn-filter ${moduleFilter === "planned" ? "active" : ""}`}
                onClick={() => setModuleFilter("planned")}
              >
                Upcoming ({modules.filter(m => m.status === "Planned").length})
              </button>
            </div>
          </div>

          {/* Module Cards Grid */}
          {loadingModules ? (
            <div className="loading-grid">
              <p>Loading module statuses from FastAPI...</p>
            </div>
          ) : filteredModules.length > 0 ? (
            <div className="modules-grid">
              {filteredModules.map((module) => (
                <ModuleCard key={module.id} module={module} />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <Layers size={36} />
              <p>No modules match the selected filter or backend is offline.</p>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="footer-container">
        <div className="footer-content">
          <p>© 2026 AI Project Intelligence & Risk Advisor</p>
          <p className="footer-subtext">
            Evidence-Grounded Autonomous Project Intelligence & Risk Forecasting
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
