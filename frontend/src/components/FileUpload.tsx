import React, { useState, useRef, useEffect } from "react";
import {
  UploadCloud,
  FileCheck2,
  AlertTriangle,
  FileText,
  FileCode,
  Table,
  CheckCircle,
  XCircle,
  RefreshCw,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Layers,
  Trash2,
  Plus,
  FileUp,
  FolderGit2,
  RotateCcw,
  Building2,
} from "lucide-react";
import {
  uploadDocument,
  getDocuments,
  deleteDocument,
  getProjectWorkspace,
  resetProjectWorkspace,
  startNewProjectWorkspace,
  UploadApiError,
  UploadResponse,
  DocumentMetadata,
  FileUploadResultItem,
  ProjectWorkspace,
} from "../services/api";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".csv", ".txt"];
const MAX_SIZE_MB = 15;

interface StagedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  extension: string;
  isValid: boolean;
  validationError?: string;
}

interface FileUploadProps {
  onDocumentUploaded?: (doc: UploadResponse) => void;
  onWorkspaceChanged?: () => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onDocumentUploaded, onWorkspaceChanged }) => {
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [processedDocs, setProcessedDocs] = useState<DocumentMetadata[]>([]);
  const [workspace, setWorkspace] = useState<ProjectWorkspace | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [conflictError, setConflictError] = useState<{ message: string; stagedFiles: StagedFile[] } | null>(null);
  const [batchResults, setBatchResults] = useState<FileUploadResultItem[] | null>(null);
  const [expandedChunkIds, setExpandedChunkIds] = useState<Set<string>>(new Set());
  const [copiedChunkId, setCopiedChunkId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadProjectWorkspace = async () => {
    try {
      const ws = await getProjectWorkspace();
      setWorkspace(ws);
    } catch {
      // Backend may be starting up
    }
  };

  // Load existing uploaded documents on initial render
  const loadExistingDocuments = async () => {
    try {
      const docs = await getDocuments();
      setProcessedDocs(docs);
      await loadProjectWorkspace();
    } catch {
      // Backend may be starting up; fail gracefully
    }
  };

  useEffect(() => {
    loadExistingDocuments();
  }, []);

  const validateFile = (file: File): { isValid: boolean; error?: string; ext: string } => {
    const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return {
        isValid: false,
        error: `Unsupported format '${ext}'. Allowed: .pdf, .docx, .csv, .txt`,
        ext,
      };
    }
    if (file.size === 0) {
      return {
        isValid: false,
        error: "File is empty (0 bytes)",
        ext,
      };
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return {
        isValid: false,
        error: `Exceeds ${MAX_SIZE_MB} MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB)`,
        ext,
      };
    }
    return { isValid: true, ext };
  };

  const addFilesToStaging = (incomingFiles: FileList | File[]) => {
    setErrorMessage(null);
    setBatchResults(null);

    const fileArray = Array.from(incomingFiles);
    if (fileArray.length === 0) return;

    setStagedFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.name.toLowerCase()));
      const processedNames = new Set(processedDocs.map((d) => d.filename.toLowerCase()));
      const newItems: StagedFile[] = [];

      for (const file of fileArray) {
        // Skip exact duplicate filenames already staged
        if (existingNames.has(file.name.toLowerCase())) {
          continue;
        }
        existingNames.add(file.name.toLowerCase());

        const validation = validateFile(file);
        const isDuplicateUploaded = processedNames.has(file.name.toLowerCase());
        newItems.push({
          id: `${file.name}-${file.size}-${Date.now()}-${Math.random()}`,
          file,
          name: file.name,
          size: file.size,
          extension: validation.ext,
          isValid: validation.isValid && !isDuplicateUploaded,
          validationError: isDuplicateUploaded
            ? `Duplicate: '${file.name}' is already indexed in this workspace.`
            : validation.error,
        });
      }

      return [...prev, ...newItems];
    });

    // Reset input value so re-selecting identical file names fires onChange
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveStagedFile = (id: string) => {
    setStagedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClearStaged = () => {
    setStagedFiles([]);
    setErrorMessage(null);
    setConflictError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFilesToStaging(e.dataTransfer.files);
    }
  };

  const handleUpload = async () => {
    const validItems = stagedFiles.filter((f) => f.isValid);
    if (validItems.length === 0) {
      setErrorMessage("Please select at least one valid document to upload.");
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);
    setConflictError(null);
    setBatchResults(null);

    try {
      const filesToSend = validItems.map((item) => item.file);
      const response = await uploadDocument(filesToSend);

      // Collect new DocumentMetadata from successful items
      const newDocs: DocumentMetadata[] = [];
      if (response.results && response.results.length > 0) {
        setBatchResults(response.results);
        for (const res of response.results) {
          if (res.success && res.document) {
            newDocs.push(res.document);
          }
        }
      } else if (response.document) {
        newDocs.push(response.document);
      }

      // Prepend to processed documents without losing existing ones
      if (newDocs.length > 0) {
        setProcessedDocs((prev) => {
          const newIds = new Set(newDocs.map((d) => d.document_id));
          return [...newDocs, ...prev.filter((d) => !newIds.has(d.document_id))];
        });
      }

      // Clear staged files on completion
      setStagedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadProjectWorkspace();

      if (onDocumentUploaded) {
        onDocumentUploaded(response);
      }
      if (onWorkspaceChanged) {
        onWorkspaceChanged();
      }
    } catch (err: any) {
      if (err instanceof UploadApiError && err.isConflict) {
        setConflictError({
          message: err.message,
          stagedFiles: [...validItems],
        });
      } else if (err.message && (err.message.includes("Project identity conflict") || err.message.includes("409"))) {
        setConflictError({
          message: err.message,
          stagedFiles: [...validItems],
        });
      } else {
        setErrorMessage(err.message || "Upload failed due to an unexpected backend communication error.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleStartNewWorkspace = async () => {
    const projName = window.prompt(
      "Enter a name for the new project workspace (or leave blank to auto-detect from first document):"
    );
    if (projName === null) return;

    setIsUploading(true);
    setErrorMessage(null);
    setConflictError(null);
    try {
      await startNewProjectWorkspace(projName.trim() || undefined);
      setProcessedDocs([]);
      setBatchResults(null);
      await loadProjectWorkspace();
      if (onWorkspaceChanged) onWorkspaceChanged();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to start new project workspace.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleResolveConflictNewWorkspace = async () => {
    setIsUploading(true);
    setErrorMessage(null);
    const filesToUpload = conflictError?.stagedFiles || stagedFiles.filter((f) => f.isValid);
    setConflictError(null);
    try {
      await startNewProjectWorkspace();
      setProcessedDocs([]);
      setBatchResults(null);
      await loadProjectWorkspace();
      if (onWorkspaceChanged) onWorkspaceChanged();

      if (filesToUpload.length > 0) {
        const response = await uploadDocument(filesToUpload.map((f) => f.file));
        const newDocs: DocumentMetadata[] = [];
        if (response.results && response.results.length > 0) {
          setBatchResults(response.results);
          for (const res of response.results) {
            if (res.success && res.document) {
              newDocs.push(res.document);
            }
          }
        } else if (response.document) {
          newDocs.push(response.document);
        }
        setProcessedDocs(newDocs);
        setStagedFiles([]);
        await loadProjectWorkspace();
        if (onDocumentUploaded) onDocumentUploaded(response);
        if (onWorkspaceChanged) onWorkspaceChanged();
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to initialize new project workspace.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveDoc = async (docId: string) => {
    try {
      await deleteDocument(docId);
      setProcessedDocs((prev) => prev.filter((d) => d.document_id !== docId));
      await loadProjectWorkspace();
      if (onWorkspaceChanged) onWorkspaceChanged();
    } catch {
      // Fallback local removal if backend delete fails
      setProcessedDocs((prev) => prev.filter((d) => d.document_id !== docId));
      await loadProjectWorkspace();
      if (onWorkspaceChanged) onWorkspaceChanged();
    }
  };

  const handleResetWorkspace = async () => {
    if (!window.confirm("Reset the project workspace? All documents and vector indexing will be cleared.")) {
      return;
    }
    setIsUploading(true);
    setErrorMessage(null);
    setConflictError(null);
    try {
      await resetProjectWorkspace();
      setProcessedDocs([]);
      setBatchResults(null);
      await loadProjectWorkspace();
      if (onWorkspaceChanged) onWorkspaceChanged();
    } catch (err) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to reset project workspace.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const toggleChunkExpand = (chunkId: string) => {
    setExpandedChunkIds((prev) => {
      const next = new Set(prev);
      if (next.has(chunkId)) {
        next.delete(chunkId);
      } else {
        next.add(chunkId);
      }
      return next;
    });
  };

  const handleCopyText = (chunkId: string, text: string) => {
    const handleSuccess = () => {
      setCopiedChunkId(chunkId);
      setTimeout(() => {
        setCopiedChunkId((prev) => (prev === chunkId ? null : prev));
      }, 2000);
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(handleSuccess).catch(() => {
        fallbackCopy(text, handleSuccess);
      });
    } else {
      fallbackCopy(text, handleSuccess);
    }
  };

  const fallbackCopy = (text: string, onSuccess: () => void) => {
    try {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      onSuccess();
    } catch {
      // Fallback silently
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase();
    if (ext === "pdf") return <FileText className="file-format-icon pdf" size={24} />;
    if (ext === "docx") return <FileCheck2 className="file-format-icon docx" size={24} />;
    if (ext === "csv") return <Table className="file-format-icon csv" size={24} />;
    return <FileCode className="file-format-icon txt" size={24} />;
  };

  const validStagedCount = stagedFiles.filter((f) => f.isValid).length;

  return (
    <div className="upload-container" id="ingestion">
      <div className="section-header">
        <span className="section-eyebrow">Documents</span>
        <h2 className="section-title">Upload Documents</h2>
        <p className="section-desc">
          Upload project documents (PDF, DOCX, CSV, TXT) to extract text and generate boundary-aware chunks
          for multi-agent project analysis. Select and upload multiple files together.
        </p>
      </div>

      <div className="upload-card">
        {/* Project Workspace Identity Card */}
        <div className="workspace-identity-card" style={{
          backgroundColor: "rgba(15, 23, 42, 0.6)",
          border: "1px solid var(--border-color)",
          borderRadius: "var(--radius-md)",
          padding: "1.1rem 1.25rem",
          marginBottom: "1.5rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <div style={{
              background: "linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.3))",
              color: "var(--accent-primary)",
              padding: "0.65rem",
              borderRadius: "var(--radius-md)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <FolderGit2 size={24} />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                <span style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>
                  {workspace?.project_name || "Project Workspace"}
                </span>
                <span className="badge badge-milestone font-mono">
                  ID: {workspace?.project_id || "proj_workspace_default"}
                </span>
                <span className="badge badge-success">
                  Single Knowledge Base
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap", marginTop: "0.35rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                {workspace?.client && (
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                    <Building2 size={13} style={{ color: "var(--accent-primary)" }} />
                    <span>Client / Sponsor: <strong>{workspace.client}</strong></span>
                  </span>
                )}
                <span style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                  <Layers size={13} style={{ color: "var(--accent-emerald)" }} />
                  <span>Total Documents: <strong>{processedDocs.length}</strong></span>
                </span>
                <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                  (All uploaded files belong to this project)
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={handleStartNewWorkspace}
              disabled={isUploading}
              className="btn-outline"
              title="Start a fresh, isolated project workspace"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                fontSize: "0.82rem",
                padding: "0.45rem 0.85rem",
                color: "var(--accent-primary)",
                borderColor: "rgba(59, 130, 246, 0.4)",
                background: "rgba(59, 130, 246, 0.08)"
              }}
            >
              <Plus size={14} />
              <span>Start New Project</span>
            </button>
            <button
              type="button"
              onClick={handleResetWorkspace}
              disabled={isUploading}
              className="btn-outline"
              title="Reset project workspace and delete all indexed documents"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                fontSize: "0.82rem",
                padding: "0.45rem 0.85rem",
                color: "var(--text-secondary)",
                borderColor: "var(--border-color)"
              }}
            >
              <RotateCcw size={14} className={isUploading ? "spin-icon" : ""} />
              <span>Reset Workspace</span>
            </button>
          </div>
        </div>

        {/* Dropzone */}
        <div
          className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            accept=".pdf,.docx,.csv,.txt"
            multiple={true}
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                addFilesToStaging(e.target.files);
              }
            }}
          />

          <div className="dropzone-idle">
            <div className="upload-icon-circle">
              <UploadCloud size={36} />
            </div>
            <h4>Drag & drop multiple project documents here</h4>
            <p>or click to browse from your device (use Ctrl / Shift to select multiple)</p>
            <div className="format-chips">
              <span className="chip">.PDF</span>
              <span className="chip">.DOCX</span>
              <span className="chip">.CSV</span>
              <span className="chip">.TXT</span>
            </div>
            <span className="size-hint">Maximum file size: {MAX_SIZE_MB} MB per file • Multi-file upload supported</span>
          </div>
        </div>

        {/* Staged Files Queue (Before Upload) */}
        {stagedFiles.length > 0 && (
          <div className="staged-files-panel" style={{ marginTop: "1.25rem" }}>
            <div className="batch-summary-bar">
              <span>
                <strong>{stagedFiles.length}</strong> {stagedFiles.length === 1 ? "file" : "files"} selected
                {validStagedCount !== stagedFiles.length && (
                  <span style={{ color: "var(--accent-rose)", marginLeft: "0.5rem" }}>
                    ({stagedFiles.length - validStagedCount} invalid)
                  </span>
                )}
              </span>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  className="btn-outline"
                  style={{ fontSize: "0.78rem", padding: "0.3rem 0.6rem" }}
                  disabled={isUploading}
                >
                  <Plus size={14} style={{ marginRight: "0.25rem" }} />
                  Add More
                </button>
                <button
                  type="button"
                  onClick={handleClearStaged}
                  className="btn-outline"
                  style={{ fontSize: "0.78rem", padding: "0.3rem 0.6rem" }}
                  disabled={isUploading}
                >
                  Clear Selection
                </button>
              </div>
            </div>

            <div className="selected-files-list" style={{ marginTop: "0.75rem" }}>
              {stagedFiles.map((item) => (
                <div
                  key={item.id}
                  className={`selected-file-row ${!item.isValid ? "is-invalid" : ""}`}
                >
                  {getFileIcon(item.name)}
                  <div className="selected-file-info">
                    <span className="selected-filename">{item.name}</span>
                    <span className="selected-filesize">
                      {(item.size / 1024).toFixed(1)} KB
                      {item.isValid ? (
                        <span className="file-status-tag valid" style={{ marginLeft: "0.6rem" }}>
                          <CheckCircle size={12} /> Ready
                        </span>
                      ) : (
                        <span className="file-status-tag invalid" style={{ marginLeft: "0.6rem" }}>
                          <XCircle size={12} /> {item.validationError}
                        </span>
                      )}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveStagedFile(item.id)}
                    className="btn-text-danger"
                    title="Remove this file from selection"
                    disabled={isUploading}
                  >
                    <XCircle size={18} />
                  </button>
                </div>
              ))}
            </div>

            <div className="upload-action-bar" style={{ marginTop: "1rem" }}>
              <button
                type="button"
                onClick={handleUpload}
                disabled={isUploading || validStagedCount === 0}
                className="btn-primary"
              >
                {isUploading ? (
                  <>
                    <RefreshCw size={16} className="spin-icon" />
                    <span>Uploading & Processing {validStagedCount} Document{validStagedCount > 1 ? "s" : ""}...</span>
                  </>
                ) : (
                  <>
                    <FileUp size={16} />
                    <span>
                      Upload {validStagedCount > 0 ? `${validStagedCount} ` : ""}File{validStagedCount > 1 ? "s" : ""}
                    </span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Project Identity Conflict Resolution Banner */}
        {conflictError && (
          <div
            className="conflict-resolution-banner"
            style={{
              backgroundColor: "rgba(239, 68, 68, 0.12)",
              border: "1px solid var(--accent-rose)",
              borderRadius: "var(--radius-md)",
              padding: "1.1rem 1.25rem",
              margin: "1rem 0",
              display: "flex",
              flexDirection: "column",
              gap: "0.85rem",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
              <AlertTriangle size={22} style={{ color: "var(--accent-rose)", flexShrink: 0, marginTop: "2px" }} />
              <div>
                <strong style={{ color: "var(--accent-rose)", fontSize: "0.95rem" }}>
                  Project Identity Conflict Detected
                </strong>
                <p style={{ fontSize: "0.85rem", marginTop: "0.3rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  {conflictError.message}
                </p>
                <p style={{ fontSize: "0.82rem", marginTop: "0.25rem", color: "var(--text-muted)" }}>
                  Each workspace isolates a single project. To analyze this document without mixing unrelated project data,
                  you can start a new workspace for it.
                </p>
              </div>
            </div>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginLeft: "2rem" }}>
              <button
                type="button"
                className="btn-primary"
                style={{
                  fontSize: "0.82rem",
                  padding: "0.45rem 0.95rem",
                  backgroundColor: "var(--accent-primary)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.4rem",
                }}
                onClick={handleResolveConflictNewWorkspace}
                disabled={isUploading}
              >
                <FolderGit2 size={15} />
                <span>Start New Project Workspace with this Document</span>
              </button>
              <button
                type="button"
                className="btn-outline"
                style={{ fontSize: "0.82rem", padding: "0.45rem 0.85rem" }}
                onClick={() => setConflictError(null)}
                disabled={isUploading}
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="error-banner">
            <AlertTriangle className="error-icon" size={20} />
            <div className="error-text">
              <strong>Upload Error:</strong> {errorMessage}
            </div>
            <button onClick={() => setErrorMessage(null)} className="btn-dismiss">
              Dismiss
            </button>
          </div>
        )}

        {/* Per-file Batch Result Status Banner */}
        {batchResults && batchResults.length > 0 && (
          <div className="batch-results-panel">
            <div className="batch-results-header">
              <span>Batch Upload Results ({batchResults.length} files)</span>
              <button
                onClick={() => setBatchResults(null)}
                className="btn-dismiss"
                style={{ cursor: "pointer" }}
              >
                Dismiss
              </button>
            </div>
            <div className="batch-results-list">
              {batchResults.map((res, idx) => (
                <div
                  key={`${res.filename}-${idx}`}
                  className={`batch-result-row ${res.success ? "success" : "failed"}`}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {res.success ? (
                      <CheckCircle size={15} className="text-emerald" />
                    ) : (
                      <XCircle size={15} style={{ color: "var(--accent-rose)" }} />
                    )}
                    <strong>{res.filename}</strong>
                  </div>
                  <div>
                    {res.success ? (
                      <span style={{ color: "var(--text-secondary)" }}>
                        {res.chunk_count} chunks • {res.extracted_characters.toLocaleString()} characters
                      </span>
                    ) : (
                      <span style={{ color: "var(--accent-rose)" }}>
                        {res.error || "Failed validation"}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Processed Documents List */}
        {processedDocs.length > 0 && (
          <div className="processing-results-container" style={{ marginTop: "2rem" }}>
            <div className="results-header-bar">
              <div className="results-section-title">
                <Layers className="text-blue" size={24} />
                <span>Documents ({processedDocs.length})</span>
              </div>
            </div>

            {processedDocs.map((docItem) => (
              <div key={docItem.document_id} className="doc-group-card">
                {/* Document Group Header */}
                <div className="doc-group-header">
                  <div className="doc-group-info">
                    {getFileIcon(docItem.filename)}
                    <div>
                      <div className="doc-filename">{docItem.filename}</div>
                      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                        <span>Doc ID: <code className="font-mono">{docItem.document_id}</code></span>
                        <span>•</span>
                        <span>Project: <code className="font-mono">{docItem.project_id || workspace?.project_id || "proj_workspace_default"}</code></span>
                        {docItem.is_project_inherited && (
                          <span className="badge badge-partial" style={{ fontSize: "0.68rem", padding: "0.1rem 0.4rem" }}>
                            Inherited
                          </span>
                        )}
                        {docItem.upload_batch_id && (
                          <span>• Batch: <code className="font-mono">{docItem.upload_batch_id}</code></span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="doc-stats-pills">
                    <span className="stat-chip highlight">
                      Status: <strong>{docItem.status}</strong>
                    </span>
                    <span className="stat-chip">
                      Characters: <strong>{docItem.char_count?.toLocaleString() || 0}</strong>
                    </span>
                    <span className="stat-chip highlight">
                      Chunks: <strong>{docItem.chunk_count || 0}</strong>
                    </span>
                    {docItem.file_size_kb !== undefined && (
                      <span className="stat-chip">
                        Size: <strong>{docItem.file_size_kb} KB</strong>
                      </span>
                    )}
                    {docItem.page_count !== null && docItem.page_count !== undefined && (
                      <span className="stat-chip">
                        Pages: <strong>{docItem.page_count}</strong>
                      </span>
                    )}
                    {docItem.row_count !== null && docItem.row_count !== undefined && (
                      <span className="stat-chip">
                        Rows: <strong>{docItem.row_count}</strong>
                      </span>
                    )}
                    <button
                      onClick={() => handleRemoveDoc(docItem.document_id)}
                      className="btn-text-danger"
                      title="Delete this document"
                      style={{ marginLeft: "0.5rem" }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                {/* Chunks List */}
                <div className="chunks-list">
                  <div className="chunks-list-header">
                    <span>Extracted Text Chunks ({docItem.chunks?.length || 0})</span>
                  </div>

                  {(!docItem.chunks || docItem.chunks.length === 0) ? (
                    <div className="warning-banner">
                      <AlertTriangle size={18} />
                      <span>No text chunks are available for this document.</span>
                    </div>
                  ) : (
                    docItem.chunks.map((chunk) => {
                      const isExpanded = expandedChunkIds.has(chunk.chunk_id);
                      const isLong = chunk.text.length > 250;
                      const displayText =
                        isLong && !isExpanded
                          ? chunk.text.slice(0, 250) + "..."
                          : chunk.text;
                      const isCopied = copiedChunkId === chunk.chunk_id;

                      return (
                        <div key={chunk.chunk_id} className="chunk-card">
                          <div className="chunk-card-header">
                            <div className="chunk-meta-left">
                              <span className="chunk-id-tag">#{chunk.chunk_id}</span>
                              {chunk.page_number !== null && chunk.page_number !== undefined && (
                                <span className="source-ref-badge">
                                  Page {chunk.page_number}
                                </span>
                              )}
                              {chunk.row_number !== null && chunk.row_number !== undefined && (
                                <span className="source-ref-badge">
                                  {chunk.source_ref || `Row ${chunk.row_number}`}
                                </span>
                              )}
                              {chunk.source_ref &&
                                chunk.page_number === null &&
                                chunk.row_number === null && (
                                  <span className="source-ref-badge">
                                    {chunk.source_ref}
                                  </span>
                                )}
                              <span className="chunk-chars-badge">
                                {chunk.char_count} chars • {chunk.word_count} words
                              </span>
                            </div>

                            <div className="chunk-card-actions">
                              <button
                                onClick={() => handleCopyText(chunk.chunk_id, chunk.text)}
                                className={`btn-chunk-action ${isCopied ? "copied" : ""}`}
                                title="Copy chunk text to clipboard"
                              >
                                {isCopied ? (
                                  <>
                                    <Check size={13} /> Copied!
                                  </>
                                ) : (
                                  <>
                                    <Copy size={13} /> Copy Text
                                  </>
                                )}
                              </button>
                            </div>
                          </div>

                          <div className="chunk-card-content">
                            <pre className="chunk-text-box">{displayText}</pre>
                            {isLong && (
                              <button
                                onClick={() => toggleChunkExpand(chunk.chunk_id)}
                                className="chunk-expand-toggle"
                              >
                                {isExpanded ? (
                                  <>
                                    <ChevronUp size={14} /> Collapse text
                                  </>
                                ) : (
                                  <>
                                    <ChevronDown size={14} /> Expand full chunk ({chunk.char_count} chars)
                                  </>
                                )}
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
