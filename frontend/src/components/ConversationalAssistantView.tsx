import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Trash2,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  FolderLock,
} from "lucide-react";
import {
  ChatMessage,
  ChatResponse,
  chatWithAssistant,
  getAssistantHistory,
  clearAssistantConversation,
} from "../services/api";

interface Props {
  workspaceVersion?: number;
}

const SUGGESTED_QUESTIONS = [
  "Are we on track?",
  "What are our biggest risks?",
  "What are the current blockers?",
  "Who is responsible for the payment API?",
  "What deliverables are pending?",
  "What is the current project health?",
];

export function ConversationalAssistantView({ workspaceVersion }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadHistory = async () => {
    try {
      const hist = await getAssistantHistory();
      setMessages(hist.messages);
      setActiveProjectId(hist.project_id);
    } catch {
      // ignore empty
    }
  };

  useEffect(() => {
    loadHistory();
  }, [workspaceVersion]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (questionToSend?: string) => {
    const q = (questionToSend || inputQuestion).trim();
    if (!q || loading) return;

    setInputQuestion("");
    setError(null);

    // Optimistically append user message
    const tempUserMsg: ChatMessage = {
      message_id: `temp_${Date.now()}`,
      role: "user",
      content: q,
      timestamp: new Date().toISOString(),
      citations: [],
      has_evidence: true,
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const res: ChatResponse = await chatWithAssistant({ question: q });
      const assistantMsg: ChatMessage = {
        message_id: `resp_${Date.now()}`,
        role: "assistant",
        content: res.answer,
        timestamp: res.timestamp,
        citations: res.citations,
        has_evidence: res.has_evidence,
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setActiveProjectId(res.project_id);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to obtain answer from project assistant.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!window.confirm("Clear conversation history for this project workspace?")) return;
    try {
      await clearAssistantConversation();
      setMessages([]);
    } catch (err) {
      alert("Failed to clear conversation");
    }
  };

  return (
    <div className="assistant-container card">
      {/* Header */}
      <div className="assistant-header">
        <div>
          <div className="assistant-title-cluster">
            <span className="section-eyebrow">Milestone 3 Conversational AI</span>
            <span className="badge badge-subtle">
              <FolderLock size={12} /> {activeProjectId ? `Project: ${activeProjectId}` : "Project Isolated"}
            </span>
          </div>
          <h2 className="section-title">Conversational Project Intelligence Assistant</h2>
          <p className="section-desc">
            Ask any question about project scope, risks, blockers, assignees, or health. Answers are strictly grounded in retrieved document evidence with explicit coordinates.
          </p>
        </div>

        {messages.length > 0 && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleClear}
            title="Clear active conversation"
          >
            <Trash2 size={14} /> Clear Chat
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Suggested Questions Chips */}
      <div className="suggested-chips-row">
        <span className="text-xs text-muted flex items-center gap-1 font-semibold">
          <Sparkles size={13} className="text-accent" /> Suggested Questions:
        </span>
        <div className="chips-wrap">
          {SUGGESTED_QUESTIONS.map((sq, i) => (
            <button
              key={i}
              className="chip-btn"
              onClick={() => handleSend(sq)}
              disabled={loading}
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Panel */}
      <div className="chat-messages-panel">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Bot size={40} className="text-accent" />
            <p className="font-semibold">How can I assist with your project intelligence?</p>
            <p className="text-xs text-muted">
              I can identify pending deliverables, trace overdue schedule delays, verify unassigned blockers, or summarize meeting action items based on uploaded documents.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.message_id}
              className={`chat-message-row ${msg.role === "user" ? "user-row" : "assistant-row"}`}
            >
              <div className="message-avatar">
                {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div className="message-bubble-wrap">
                <div
                  className={`message-bubble ${
                    msg.role === "user" ? "user-bubble" : "assistant-bubble"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="message-text markdown-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <div className="message-text whitespace-pre-wrap">{msg.content}</div>
                  )}

                  {/* Citations Box for Assistant */}
                  {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                    <div className="citations-accordion">
                      <div className="citations-header">
                        <ShieldCheck size={13} className="text-success" />
                        <span>Grounding Citations ({msg.citations.length})</span>
                      </div>
                      <div className="citations-list">
                        {msg.citations.map((c, idx) => (
                          <div key={idx} className="citation-pill">
                            <span className="citation-source font-semibold">{c.filename}</span>
                            <span className="citation-coord badge badge-subtle text-xs">
                              {c.source_ref || "Passage"}
                            </span>
                            <p className="citation-excerpt text-xs text-muted">
                              "{c.excerpt}"
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {!msg.has_evidence && msg.role === "assistant" && (
                    <div className="no-evidence-alert text-xs text-warning mt-2 flex items-center gap-1">
                      <AlertCircle size={13} />
                      <em>No explicit evidence was found in the uploaded documents for this query.</em>
                    </div>
                  )}
                </div>

                <span className="message-time text-xs text-muted">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="chat-message-row assistant-row">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-bubble assistant-bubble typing-bubble">
              <RefreshCw size={14} className="spin text-accent" />
              <span className="text-xs text-muted">Searching knowledge base and retrieving citations...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form
        className="chat-input-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about project goals, risks, deliverables, or health..."
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          className="btn btn-primary chat-send-btn"
          disabled={!inputQuestion.trim() || loading}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
