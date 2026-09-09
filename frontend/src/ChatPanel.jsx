import { useState, useRef, useEffect } from "react";
import { useAuth } from "./AuthContext";

function ChatPanel({
  activeSessionId,
  sessionMessages = [],
  onSessionCreated,
  onSelectSource,
  onOpenAuth,
}) {
  const { isAuthenticated, authFetch } = useAuth();
  const [messages, setMessages] = useState(sessionMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // Sync messages whenever parent's active session changes
  useEffect(() => {
    setMessages(sessionMessages);
  }, [sessionMessages, activeSessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    if (!isAuthenticated) {
      if (onOpenAuth) onOpenAuth();
      return;
    }

    const question = input.trim();
    const tempUserMsg = {
      role: "user",
      content: question,
      citations: [],
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await authFetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          session_id: activeSessionId || null,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Error querying papers");
      }

      const assistantMsg = {
        role: "assistant",
        content: data.answer,
        citations: data.citations || [],
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (!activeSessionId && data.session_id && onSessionCreated) {
        onSessionCreated(data.session_id);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Audit error: " + err.message,
          citations: [],
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full">
      {messages.length === 0 && (
        <div className="rounded p-3 mb-3 border text-xs" style={{ background: "rgba(45,212,206,0.04)", borderColor: "var(--border)" }}>
          <p className="font-mono mb-1" style={{ color: "var(--teal)" }}>// AGENTIC RAG CHAT</p>
          <p style={{ color: "var(--text-secondary)" }}>
            Query your uploaded literature corpus. The model retrieves hybrid BM25 + dense vector embeddings and cites specific source excerpts.
          </p>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="overflow-y-auto flex flex-col gap-3 mb-3 pr-1 w-full"
        style={{ maxHeight: "320px", minHeight: "120px" }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className="rounded-lg p-3 text-sm flex flex-col gap-2 transition"
            style={{
              background: msg.role === "user" ? "var(--surface)" : "rgba(6, 11, 16, 0.9)",
              border: "1px solid " + (msg.role === "user" ? "var(--border)" : "rgba(45, 212, 206, 0.25)"),
              color: "var(--text-primary)",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "92%",
              wordBreak: "break-word",
            }}
          >
            <div className="flex items-center justify-between gap-2 border-b pb-1" style={{ borderColor: "rgba(22,50,59,0.4)" }}>
              <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: msg.role === "user" ? "var(--text-secondary)" : "var(--teal)" }}>
                {msg.role === "user" ? "Researcher Query" : "VeriLit Evidence Engine"}
              </span>
              {msg.timestamp && (
                <span className="font-mono text-[9px]" style={{ color: "var(--text-secondary)" }}>
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              )}
            </div>

            <p className="leading-relaxed text-sm whitespace-pre-wrap">{msg.content || msg.text}</p>

            {/* Citations & Evidence Excerpts */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 pt-2 border-t flex flex-col gap-1.5" style={{ borderColor: "rgba(22,50,59,0.5)" }}>
                <p className="font-mono text-[10px] uppercase tracking-wider" style={{ color: "var(--amber)" }}>
                  Grounded In {msg.citations.length} Verified Excerpts:
                </p>
                <div className="flex flex-col gap-1.5">
                  {msg.citations.map((c, cIdx) => (
                    <div
                      key={cIdx}
                      onClick={() => onSelectSource && onSelectSource(c)}
                      className="rounded p-2 text-xs border cursor-pointer hover:opacity-90 transition flex flex-col gap-1"
                      style={{
                        background: "rgba(11, 19, 27, 0.8)",
                        borderColor: "var(--border)",
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[10px] font-semibold" style={{ color: "var(--teal)" }}>
                          📄 {c.title || c.filename} (Chunk #{c.chunk_index})
                        </span>
                        <span className="font-mono text-[9px] underline" style={{ color: "var(--amber)" }}>
                          View Source →
                        </span>
                      </div>
                      <p className="text-[11px] italic leading-snug line-clamp-2" style={{ color: "var(--text-secondary)" }}>
                        "{c.snippet}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="rounded p-3 text-xs font-mono flex items-center gap-2" style={{ background: "var(--surface)", color: "var(--teal)" }}>
            <span className="hud-pulse" style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--teal)" }} />
            Analyzing literature and synthesizing biomedical claims...
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="flex gap-2 w-full">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={
            isAuthenticated
              ? "e.g. Compare reported reductions in HbA1c across papers..."
              : "Sign in to query research papers..."
          }
          className="flex-1 min-w-0 rounded px-3 py-2 text-sm outline-none border transition"
          style={{
            background: "var(--ink)",
            borderColor: "var(--border)",
            color: "var(--text-primary)",
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="shrink-0 px-4 py-2 rounded text-sm font-medium transition-all hover:opacity-90 hud-glow-border"
          style={{ background: "var(--teal)", color: "var(--ink)" }}
        >
          {loading ? "..." : "QUERY"}
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;