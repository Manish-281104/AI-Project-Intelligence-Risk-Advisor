import React, { useState, useEffect, useRef } from "react";
import {
  LayoutDashboard,
  FileText,
  Activity,
  MessageSquare,
  ChevronDown,
} from "lucide-react";

export type NavTabKey =
  | "all"
  | "dashboard"
  | "ingest"
  | "agents"
  | "docgen"
  | "health"
  | "chat";

interface NavTabItem {
  id: NavTabKey;
  label: string;
  icon?: React.ReactNode;
}

interface TopNavigationProps {
  activeTab: NavTabKey;
  onSelectTab: (tab: NavTabKey) => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  activeTab,
  onSelectTab,
}) => {
  const [windowWidth, setWindowWidth] = useState<number>(
    typeof window !== "undefined" ? window.innerWidth : 1440
  );
  const [moreMenuOpen, setMoreMenuOpen] = useState<boolean>(false);
  const moreMenuRef = useRef<HTMLDivElement>(null);

  // Monitor window resize for responsive strategy
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Close More dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        moreMenuRef.current &&
        !moreMenuRef.current.contains(event.target as Node)
      ) {
        setMoreMenuOpen(false);
      }
    };
    if (moreMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [moreMenuOpen]);

  // Tab definitions matching the exact image provided:
  // 1. All Sections (no icon)
  // 2. Project Dashboard (LayoutDashboard icon)
  // 3. Document Ingestion (no icon)
  // 4. Agent Intelligence (no icon)
  // 5. Documentation Studio (FileText icon)
  // 6. Project Health (0–100) (Activity icon)
  // 7. AI Assistant (MessageSquare icon)
  const allTabs: NavTabItem[] = [
    { id: "all", label: "All Sections" },
    {
      id: "dashboard",
      label: "Project Dashboard",
      icon: <LayoutDashboard size={17} className="enterprise-tab-icon" />,
    },
    { id: "ingest", label: "Document Ingestion" },
    { id: "agents", label: "Agent Intelligence" },
    {
      id: "docgen",
      label: "Documentation Studio",
      icon: <FileText size={17} className="enterprise-tab-icon" />,
    },
    {
      id: "health",
      label: "Project Health (0–100)",
      icon: <Activity size={17} className="enterprise-tab-icon" />,
    },
    {
      id: "chat",
      label: "AI Assistant",
      icon: <MessageSquare size={17} className="enterprise-tab-icon" />,
    },
  ];

  // Responsive strategy:
  // >=1024px: Show all tabs in a single row with intelligent shrinking and overflow hidden
  // <1024px: Show primary tabs and collapse remaining into a "More" dropdown menu
  const isCompact = windowWidth < 1024;
  const visibleTabs = isCompact ? allTabs.slice(0, 4) : allTabs;
  const overflowTabs = isCompact ? allTabs.slice(4) : [];

  const isMoreActive = isCompact && overflowTabs.some((t) => t.id === activeTab);
  const activeOverflowItem = isMoreActive
    ? overflowTabs.find((t) => t.id === activeTab)
    : null;

  return (
    <div className="enterprise-nav-wrapper">
      <nav
        className="enterprise-nav-bar"
        role="tablist"
        aria-label="Application Sections"
      >
        {visibleTabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              className={`enterprise-nav-tab ${isActive ? "active" : ""}`}
              onClick={() => onSelectTab(tab.id)}
            >
              {tab.icon && <span className="tab-icon-wrap">{tab.icon}</span>}
              <span className="tab-label">{tab.label}</span>
            </button>
          );
        })}

        {/* More dropdown menu for screens < 1024px */}
        {isCompact && overflowTabs.length > 0 && (
          <div className="enterprise-more-wrap" ref={moreMenuRef}>
            <button
              className={`enterprise-nav-tab enterprise-more-btn ${
                isMoreActive ? "active" : ""
              }`}
              onClick={() => setMoreMenuOpen((prev) => !prev)}
              aria-haspopup="true"
              aria-expanded={moreMenuOpen}
            >
              <span className="tab-label">
                {activeOverflowItem ? activeOverflowItem.label : "More"}
              </span>
              <ChevronDown
                size={15}
                className={`enterprise-chevron ${moreMenuOpen ? "open" : ""}`}
              />
            </button>

            {moreMenuOpen && (
              <div
                className="enterprise-more-dropdown"
                role="menu"
                aria-orientation="vertical"
              >
                {overflowTabs.map((tab) => {
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      role="menuitem"
                      className={`enterprise-dropdown-item ${
                        isActive ? "active" : ""
                      }`}
                      onClick={() => {
                        onSelectTab(tab.id);
                        setMoreMenuOpen(false);
                      }}
                    >
                      {tab.icon && (
                        <span className="dropdown-icon-wrap">{tab.icon}</span>
                      )}
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </nav>
    </div>
  );
};
