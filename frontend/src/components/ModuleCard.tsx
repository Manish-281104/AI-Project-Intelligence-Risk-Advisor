import React from "react";
import {
  FileText,
  Database,
  Crosshair,
  AlertTriangle,
  ListTodo,
  FileCheck,
  TrendingUp,
  MessageSquare,
  LayoutDashboard,
  CheckCircle,
  Clock,
  Sparkles,
} from "lucide-react";
import { ModuleItem } from "../services/api";

interface ModuleCardProps {
  module: ModuleItem;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ module }) => {
  // Select icon based on module id
  const getModuleIcon = (id: number) => {
    switch (id) {
      case 1:
        return <FileText className="module-icon" size={20} />;
      case 2:
        return <Database className="module-icon" size={20} />;
      case 3:
        return <Crosshair className="module-icon" size={20} />;
      case 4:
        return <AlertTriangle className="module-icon" size={20} />;
      case 5:
        return <ListTodo className="module-icon" size={20} />;
      case 6:
        return <FileCheck className="module-icon" size={20} />;
      case 7:
        return <TrendingUp className="module-icon" size={20} />;
      case 8:
        return <MessageSquare className="module-icon" size={20} />;
      case 9:
        return <LayoutDashboard className="module-icon" size={20} />;
      default:
        return <Sparkles className="module-icon" size={20} />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Implemented and Verified":
        return (
          <span className="badge badge-success">
            <CheckCircle size={12} />
            <span>Implemented & Verified</span>
          </span>
        );
      case "Partially Implemented":
        return (
          <span className="badge badge-partial">
            <Sparkles size={12} />
            <span>Partially Implemented</span>
          </span>
        );
      case "Planned":
      default:
        return (
          <span className="badge badge-planned">
            <Clock size={12} />
            <span>Planned</span>
          </span>
        );
    }
  };

  return (
    <div className={`module-card ${module.status === "Partially Implemented" ? "module-card-active" : ""}`}>
      {/* Top Header */}
      <div className="module-card-header">
        <div className="module-id-badge">
          {getModuleIcon(module.id)}
          <span className="module-number">Module {String(module.id).padStart(2, "0")}</span>
        </div>
        {getStatusBadge(module.status)}
      </div>

      {/* Title & Category */}
      <div className="module-card-body">
        <span className="module-category">{module.category}</span>
        <h3 className="module-title">{module.name}</h3>
        <p className="module-description">{module.description}</p>
      </div>

      {/* Footer Notes */}
      <div className="module-card-footer">
        <div className="module-notes">
          <p>{module.notes}</p>
        </div>
      </div>
    </div>
  );
};
