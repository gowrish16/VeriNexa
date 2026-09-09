import React, { useState, useEffect } from "react";
import { Plus, History, ChevronLeft, ChevronRight, MessageSquare, Clock, Sparkles } from "lucide-react";
import { fetchAuditHistory } from "../services/api";

export default function HistorySidebar({ activeSessionId, onSelectSession, onNewSession }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditHistory();
      setSessions(data || []);
    } catch (err) {
      console.warn("Could not load audit history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [activeSessionId]);

  if (isCollapsed) {
    return (
      <div className="flex flex-col items-center py-4 border-r border-[#16323b] bg-[#060b10] shrink-0 w-12 transition-all">
        <button
          onClick={() => setIsCollapsed(false)}
          title="Expand Audit History"
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-[#2dd4ce] transition cursor-pointer"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <aside className="w-72 flex flex-col border-r border-[#16323b] bg-[#060b10]/95 backdrop-blur-xl shrink-0 transition-all shadow-xl">
      {/* Top Header */}
      <div className="p-3.5 border-b border-[#16323b] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-[#2dd4ce]" />
          <span className="font-mono text-xs font-bold text-white uppercase tracking-wider">
            AUDIT SESSIONS ({sessions.length})
          </span>
        </div>
        <button
          onClick={() => setIsCollapsed(true)}
          title="Collapse Sidebar"
          className="p-1 rounded bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition cursor-pointer"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* New Session Button */}
      <div className="p-3 border-b border-[#16323b]">
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-[#2dd4ce]/10 hover:bg-[#2dd4ce]/20 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono text-xs font-bold transition-all shadow-md shadow-[#2dd4ce]/10 cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>NEW AUDIT SESSION</span>
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5 no-scrollbar">
        {loading && sessions.length === 0 && (
          <div className="text-center py-8 text-xs font-mono text-[#8fa89b] animate-pulse">
            Loading sessions...
          </div>
        )}

        {!loading && sessions.length === 0 && (
          <div className="text-center py-10 px-4 text-xs text-[#8fa89b]">
            No previous audit threads recorded. Inquire in the chat to start an air-gapped session.
          </div>
        )}

        {sessions.map((sess) => {
          const isActive = sess.id === activeSessionId;
          const dateStr = sess.created_at
            ? new Date(sess.created_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })
            : "";

          return (
            <div
              key={sess.id}
              onClick={() => onSelectSession(sess.id)}
              className={`p-3 rounded-xl border text-left cursor-pointer transition-all ${
                isActive
                  ? "bg-[#0c222a] border-[#2dd4ce] shadow-lg shadow-[#2dd4ce]/10"
                  : "bg-[#08131b] hover:bg-[#0b1b24] border-[#16323b] hover:border-[#2dd4ce]/40"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-[10px] text-[#2dd4ce] font-semibold">
                  AUDIT #{sess.id}
                </span>
                <span className="font-mono text-[10px] text-[#8fa89b] flex items-center gap-1">
                  <Clock className="w-2.5 h-2.5" />
                  {dateStr}
                </span>
              </div>
              <p
                className={`text-xs font-medium line-clamp-2 leading-snug ${
                  isActive ? "text-white" : "text-[#adc2b6]"
                }`}
              >
                {sess.title || "Biomedical Audit Session"}
              </p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-[#8fa89b] border border-white/5 flex items-center gap-1">
                  <MessageSquare className="w-2.5 h-2.5 text-[#2dd4ce]" />
                  {sess.message_count || 1} queries
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
