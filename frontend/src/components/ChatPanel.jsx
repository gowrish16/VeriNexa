import React, { useState, useEffect, useRef } from "react";
import { Send, Sparkles, Bot, User, FileText, Loader2, MapPin } from "lucide-react";
import { chatAudit, API_BASE_URL } from "../services/api";

export default function ChatPanel({
  activeSessionId,
  sessionMessages = [],
  onSessionCreated,
  onOpenPdf,
  onSelectSource,
  onSelectCitation,
  papers = [],
  selectedPaper = null,
  onSelectPaper = null,
  onOpenAuth = null,
}) {
  const [selectedPaperId, setSelectedPaperId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "VeriNexa Closed-Corpus Intelligence Agent ready. Query your active literature corpus to extract p-values, sample cohorts, and cross-reference empirical assertions.",
      citations: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (selectedPaper && (selectedPaper.id || selectedPaper.paper_id)) {
      setSelectedPaperId(selectedPaper.id || selectedPaper.paper_id);
    } else if (!selectedPaperId && papers && papers.length > 0) {
      setSelectedPaperId(papers[0].id || papers[0].paper_id);
    }
  }, [selectedPaper, papers]);

  useEffect(() => {
    if (sessionMessages && sessionMessages.length > 0) {
      setMessages(
        sessionMessages.map((m) => ({
          role: m.role,
          text: m.content || m.text,
          citations: m.citations || [],
          timestamp: m.timestamp,
        }))
      );
    } else if (!activeSessionId) {
      setMessages([
        {
          role: "assistant",
          text: "VeriNexa Closed-Corpus Intelligence Agent ready. Query your active literature corpus to extract p-values, sample cohorts, and cross-reference empirical assertions.",
          citations: [],
        },
      ]);
    }
  }, [sessionMessages, activeSessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const samplePrompts = [
    "What sample sizes and p-values were evaluated in the longevity trial?",
    "Compare reported efficacy versus adverse event thresholds in Table 3.",
    "Does the abstract conclusion reflect the subgroup ANOVA results?",
  ];

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
    const docId = c.doc_id || c.filename || selectedPaper?.filename || "medi.pdf";
    const filename = c.filename || c.doc_id || selectedPaper?.filename || "medi.pdf";
    const paperId = c.paper_id;
    const match = paperId ? papers.find((p) => (p.id || p.paper_id) === paperId) : null;
    const finalFilename = match?.filename || filename;
    const finalTitle = match?.title || c.title || docId;

    const citationPayload = {
      ...c,
      paper_id: paperId,
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
      filename: finalFilename,
      title: finalTitle,
    };

    if (match && onSelectPaper) {
      onSelectPaper(match);
    }

    if (onSelectCitation) {
      onSelectCitation(citationPayload);
    } else if (onSelectSource) {
      onSelectSource(citationPayload);
    } else if (onOpenPdf) {
      onOpenPdf(finalFilename, citationPayload);
    }
  };

  const handleSend = async (questionText) => {
    const q = questionText || input;
    if (!q.trim() || loading) return;

    const effectivePaperId =
      selectedPaperId ||
      selectedPaper?.id ||
      selectedPaper?.paper_id ||
      (papers && papers.length > 0 ? (papers[0].id || papers[0].paper_id) : null);

    const userMsg = { role: "user", text: q, timestamp: new Date().toISOString() };
    const tempAssistantMsg = {
      role: "assistant",
      text: "",
      citations: [],
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg, tempAssistantMsg]);
    setInput("");
    setLoading(true);

    try {
      const token = localStorage.getItem("verilit_token");
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          question: q,
          session_id: activeSessionId || null,
          paper_id: effectivePaperId,
        }),
      });

      if (!res.ok) {
        // Fallback to chatAudit standard endpoint
        const data = await chatAudit(q, activeSessionId || null, effectivePaperId);
        const botMsg = {
          role: "assistant",
          text: data.answer || "No verified evidence found in current closed corpus.",
          citations: data.citations || [],
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = botMsg;
          return next;
        });

        if (!activeSessionId && data.session_id && onSessionCreated) {
          onSessionCreated(data.session_id);
        }
        return;
      }

      // Read SSE stream using response.body.getReader()
      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let fullAnswer = "";
      let citations = [];
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            try {
              const data = JSON.parse(trimmed.slice(6));
              if (data.token && !data.done) {
                fullAnswer += data.token;
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: "assistant",
                    text: fullAnswer,
                    citations: citations,
                    timestamp: new Date().toISOString(),
                  };
                  return updated;
                });
              }
              if (data.done) {
                if (data.citations) citations = data.citations;
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: "assistant",
                    text: fullAnswer || data.answer || "Audit completed.",
                    citations: citations,
                    timestamp: new Date().toISOString(),
                  };
                  return updated;
                });
                if (!activeSessionId && data.session_id && onSessionCreated) {
                  onSessionCreated(data.session_id);
                }
              }
            } catch (parseErr) {
              console.error("SSE parse error:", parseErr);
            }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          text: `Audit query error: ${err.message}. Ensure backend is active at http://127.0.0.1:8000.`,
          citations: [],
          timestamp: new Date().toISOString(),
        };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[560px] rounded-2xl bg-[#08131b]/95 border border-[#16323b] shadow-2xl overflow-hidden">
      {/* Panel Header */}
      <div className="px-4 py-3 bg-[#060b10] border-b border-[#16323b] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#2dd4ce] animate-pulse"></div>
          <span className="font-mono text-xs font-bold text-white tracking-wider uppercase">
            CLOSED-CORPUS AGENTIC RAG CHAT
          </span>
        </div>

        <div className="flex items-center gap-2">
          {papers && papers.length > 0 && (
            <select
              value={selectedPaperId || (selectedPaper ? (selectedPaper.id || selectedPaper.paper_id) : (papers[0]?.id || papers[0]?.paper_id)) || ""}
              onChange={(e) => {
                const val = e.target.value ? Number(e.target.value) : null;
                setSelectedPaperId(val);
                if (onSelectPaper) {
                  if (val) {
                    const match = papers.find((p) => (p.id || p.paper_id) === val);
                    if (match) onSelectPaper(match);
                  } else {
                    onSelectPaper(null);
                  }
                }
              }}
              className="px-2.5 py-1 rounded-lg bg-[#0b1720] border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono text-[11px] focus:outline-none cursor-pointer max-w-[280px] truncate"
            >
              {papers.map((p) => {
                const title = p.detected_title || p.title || p.filename;
                const truncatedTitle = title.length > 40 ? `${title.slice(0, 37)}...` : title;
                return (
                  <option
                    key={p.id || p.paper_id}
                    value={p.id || p.paper_id}
                    title={`${title} (${p.filename})`}
                  >
                    #{p.id || p.paper_id}: {truncatedTitle} [{p.filename}]
                  </option>
                );
              })}
              <option value="">All Indexed Literature (Corpus Mode)</option>
            </select>
          )}

          <span className="text-[10px] font-mono text-[#2dd4ce] bg-[#2dd4ce]/10 px-2.5 py-0.5 rounded-full border border-[#2dd4ce]/30">
            ZERO HALLUCINATION
          </span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 text-xs leading-relaxed ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="w-7 h-7 rounded-lg bg-[#0e272b] border border-[#2dd4ce]/40 flex items-center justify-center shrink-0 text-[#2dd4ce]">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-3.5 space-y-2 ${
                msg.role === "user"
                  ? "bg-[#2dd4ce]/15 border border-[#2dd4ce]/40 text-white ml-auto"
                  : "bg-[#0b1b24] border border-[#16323b] text-[#d8f3f0]"
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>

              {/* Verified Citations Pill List */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="pt-2.5 border-t border-white/10 space-y-2">
                  <span className="text-[10px] font-mono text-[#2dd4ce] uppercase font-bold flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-[#2dd4ce]" />
                    Attributed Excerpts ({msg.citations.length}):
                  </span>
                  <div className="flex flex-col gap-1.5">
                    {msg.citations.map((c, cIdx) => {
                      const paperTitle = c.title || c.filename || c.doc_id || "Paper";
                      const chunkNum = c.chunk_index ?? c.chunk_id ?? cIdx + 1;
                      return (
                        <div
                          key={cIdx}
                          onClick={() => handleViewAnchor(c)}
                          className="p-2.5 rounded-xl bg-[#060b10]/90 border border-[#16323b] hover:border-[#2dd4ce]/60 transition-all cursor-pointer group"
                        >
                          <div className="flex items-center justify-between mb-1 gap-2">
                            <span
                              className="font-mono text-[11px] text-[#2dd4ce] font-semibold truncate max-w-[280px]"
                              title={`[${paperTitle}] Chunk #${chunkNum}`}
                            >
                              📄 [{paperTitle}] Chunk #{chunkNum}
                            </span>
                            <span
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewAnchor(c);
                              }}
                              className="font-mono text-[10px] text-[#d4af37] group-hover:underline cursor-pointer shrink-0 font-medium"
                            >
                              View Anchor →
                            </span>
                          </div>
                          {c.snippet && (
                            <p className="text-[11px] text-[#8fa89b] line-clamp-2 italic leading-snug">
                              "{c.snippet}"
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {msg.role === "user" && (
              <div className="w-7 h-7 rounded-lg bg-[#2dd4ce]/20 border border-[#2dd4ce]/50 flex items-center justify-center shrink-0 text-[#2dd4ce]">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-[#2dd4ce] font-mono p-2 bg-[#060b10] rounded-xl border border-[#16323b] w-fit">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Consulting pgvector embeddings & Llama 3.1:8B...</span>
          </div>
        )}
      </div>

      {/* Suggested Query Chips */}
      {messages.length < 3 && (
        <div className="px-4 py-2 bg-[#060b10]/60 border-t border-[#16323b] flex gap-1.5 overflow-x-auto no-scrollbar">
          {samplePrompts.map((sp, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(sp)}
              className="text-[10.5px] text-[#8fa89b] hover:text-[#2dd4ce] bg-white/5 hover:bg-[#2dd4ce]/10 px-2.5 py-1 rounded-full border border-white/10 whitespace-nowrap transition-colors cursor-pointer"
            >
              {sp}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <div className="p-3 bg-[#060b10] border-t border-[#16323b]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your indexed biomedical papers..."
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-[#0b1720] border border-[#16323b] text-white text-xs placeholder:text-[#5d736a] focus:border-[#2dd4ce] focus:outline-none transition-colors font-sans"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2.5 rounded-xl bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-lg shadow-[#2dd4ce]/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
