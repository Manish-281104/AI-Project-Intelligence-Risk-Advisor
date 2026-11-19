import { useState, useEffect } from "react";
import {
  checkHealth,
  HealthResponse,
  API_BASE_URL,
} from "./services/api";
import { Navbar } from "./components/Navbar";
import { FileUpload } from "./components/FileUpload";
import { ProjectInsightsDashboardView } from "./components/ProjectInsightsDashboardView";
import { AgentAnalysisView } from "./components/AgentAnalysisView";
import { DocumentationGenerationView } from "./components/DocumentationGenerationView";
import { ProjectHealthView } from "./components/ProjectHealthView";
import { ConversationalAssistantView } from "./components/ConversationalAssistantView";
import { TopNavigation } from "./components/TopNavigation";

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [dashboardTab, setDashboardTab] = useState<"all" | "dashboard" | "ingest" | "agents" | "docgen" | "health" | "chat">("all");
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

  useEffect(() => {
    fetchHealthData();
  }, []);

  return (
    <div className="app-layout">
      {/* Navigation Header */}
      <Navbar
        health={health}
        loading={loadingHealth}
        error={healthError}
        onRefresh={() => {
          fetchHealthData();
        }}
        apiBaseUrl={API_BASE_URL}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <div className="hero-badge-wrap">
            </div>
            <h1 className="hero-title">
              AI Project Intelligence &<br />
              <span className="text-gradient">Risk Advisory Platform</span>
            </h1>

            <div className="hero-stats-row">
              <div className="stat-pill active">
                <span className="stat-number">4</span>
                <span className="stat-label">AI Agents (Scope, Risks, Blockers, DocGen)</span>
              </div>
              <div className="stat-pill active">
                <span className="stat-number">100%</span>
                <span className="stat-label">Deterministic Health Scoring (0–100)</span>
              </div>
              <div className="stat-pill active">
                <span className="stat-number">RAG</span>
                <span className="stat-label">Conversational Assistant with Citations</span>
              </div>
              <div className="stat-pill active">
                <span className="stat-number">4</span>
                <span className="stat-label">Formats (PDF, DOCX, CSV, TXT)</span>
              </div>
            </div>
          </div>
        </section>

        {/* Modern Enterprise SaaS Primary Navigation Bar */}
        <TopNavigation
          activeTab={dashboardTab}
          onSelectTab={(tab) => setDashboardTab(tab)}
        />

        {/* SECTION: Milestone 4 Executive Project Insights & Risk Summary Dashboard */}
        {(dashboardTab === "all" || dashboardTab === "dashboard") && (
          <section className="section-wrapper" id="dashboard">
            <ProjectInsightsDashboardView
              workspaceVersion={workspaceVersion}
              onNavigateToTab={(tab) => setDashboardTab(tab)}
              onNavigateToIngest={() => setDashboardTab("ingest")}
              onWorkspaceChanged={() => setWorkspaceVersion((v) => v + 1)}
            />
          </section>
        )}

        {/* SECTION 1: Document Ingestion Component */}
        {(dashboardTab === "all" || dashboardTab === "ingest") && (
          <section className="section-wrapper" id="ingestion">
            <FileUpload onWorkspaceChanged={() => setWorkspaceVersion((v) => v + 1)} />
          </section>
        )}

        {/* SECTION 2: Conversational Project Intelligence Assistant */}
        {(dashboardTab === "all" || dashboardTab === "chat") && (
          <section className="section-wrapper">
            <ConversationalAssistantView workspaceVersion={workspaceVersion} />
          </section>
        )}

        {/* SECTION 3: Project Health Scoring */}
        {(dashboardTab === "all" || dashboardTab === "health") && (
          <section className="section-wrapper">
            <ProjectHealthView workspaceVersion={workspaceVersion} />
          </section>
        )}

        {/* SECTION 4: Documentation Generation Studio */}
        {(dashboardTab === "all" || dashboardTab === "docgen") && (
          <section className="section-wrapper">
            <DocumentationGenerationView workspaceVersion={workspaceVersion} />
          </section>
        )}

        {/* SECTION 5: Autonomous Multi-Agent Analysis View (Scope, Risks, Blockers) */}
        {(dashboardTab === "all" || dashboardTab === "agents") && (
          <section className="section-wrapper" id="ai-advisor">
            <AgentAnalysisView workspaceVersion={workspaceVersion} />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer-container">
        <div className="footer-content">
          <p>© 2026 AI Project Intelligence & Risk Advisor — Milestone 4 Final Release</p>
          <p className="footer-subtext">
            Autonomous Multi-Agent Documentation Generation, Deterministic Health Scoring, Conversational Assistant, and Executive Intelligence Dashboard
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
