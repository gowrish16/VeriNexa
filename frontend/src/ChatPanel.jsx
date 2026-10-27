import { useState, useRef, useEffect } from "react";
import { useAuth } from "./AuthContext";

function ChatPanel({
  activeSessionId,
  sessionMessages = [],
  onSessionCreated,
  onSelectSource,
  onOpenPdf,
  onSelectCitation,
  onOpenAuth,
}) {
  const { isAuthenticated, authFetch } = useAuth();
  const [messages, setMessages] = useState(sessionMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentNode, setCurrentNode] = useState(null);
  const scrollRef = useRef(null);

  const handleViewAnchor = (c) => {
    const pageNum = Number(c.page_num ?? c.page_number ?? c.page ?? 1);
    const bbox =
      Array.isArray(c.bbox) && c.bbox.length === 4
        ? c.bbox.map(Number)
        : [
            Number(c.bbox_x0 ?? 0),
            Number(c.bbox_y0 ?? c.bbox_top ?? 0),
            Number(c.bbox_x1 ?? 0),
            Number(c.bbox_y1 ?? 0),
          ];
    const docId = c.doc_id || c.filename || "medi.pdf";
    const filename = c.filename || c.doc_id || "medi.pdf";

    const citationPayload = {
      ...c,
      page: pageNum,
      page_num: pageNum,
      page_number: pageNum,
      bbox: bbox,
      bbox_x0: bbox[0],
      bbox_y0: bbox[1],
      bbox_top: bbox[1],
      bbox_x1: bbox[2],
      bbox_y1: bbox[3],
      doc_id: docId,
      filename: filename,
      title: c.title || docId,
    };

    if (onSelectSource) {
      onSelectSource(citationPayload);
    }
    if (onOpenPdf) {
      onOpenPdf(filename, citationPayload);
    }
    if (onSelectCitation) {
      onSelectCitation(citationPayload);
    }
  };

  // Helper function to display node names in user-friendly format
  const getNodeDisplayName = (nodeName) => {
    const nodeNames = {
      "retrieve_chunks": "Searching literature corpus...",
      "generate_prompt": "Building context prompt...",
      "generate_answer": "Synthesizing response...",
      "save": "Persisting audit record..."
    };
    return nodeNames[nodeName] || nodeName;
  };

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

    // Create temporary assistant message for streaming
    const tempAssistantMsg = {
      role: "assistant",
      content: "",
      citations: [],
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempAssistantMsg]);

    try {
      const response = await authFetch("http://127.0.0.1:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          session_id: activeSessionId || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Error querying papers");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let fullAnswer = "";
      let citations = [];
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            try {
              const data = JSON.parse(trimmed.slice(6));

              // Handle node lifecycle events
              if (data.type === "node_lifecycle") {
                setCurrentNode(data.node);
              }

              // Handle token streaming
              if (data.type === "token" || (data.token !== undefined && !data.done)) {
                fullAnswer += data.token;
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    content: fullAnswer,
                  };
                  return updated;
                });
              }

              // Handle completion
              if (data.type === "done" || data.done) {
                citations = data.citations || [];
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    ...updated[updated.length - 1],
                    content: fullAnswer,
                    citations: citations,
                  };
                  return updated;
                });

                if (!activeSessionId && data.session_id && onSessionCreated) {
                  onSessionCreated(data.session_id);
                }
              }

              // Handle errors
              if (data.type === "error") {
                throw new Error(data.error);
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: "Audit error: " + err.message,
        };
        return updated;
      });
    } finally {
      setLoading(false);
      setCurrentNode(null);
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
                      onClick={() => handleViewAnchor(c)}
                      className="rounded p-2 text-xs border cursor-pointer hover:opacity-90 transition flex flex-col gap-1"
                      style={{
                        background: "rgba(11, 19, 27, 0.8)",
                        borderColor: "var(--border)",
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[10px] font-semibold" style={{ color: "var(--teal)" }}>
                          📄 {c.title || c.filename || c.doc_id} (Chunk #{c.chunk_index ?? c.chunk_id ?? cIdx + 1})
                        </span>
                        <span
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewAnchor(c);
                          }}
                          className="font-mono text-[9px] underline cursor-pointer"
                          style={{ color: "var(--amber)" }}
                        >
                          View Anchor →
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
            {currentNode ? (
              <span className="flex items-center gap-2">
                <span className="text-[#8fa89b]">🤖</span>
                <span>{getNodeDisplayName(currentNode)}</span>
              </span>
            ) : (
              <span>Analyzing literature and synthesizing biomedical claims...</span>
            )}
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