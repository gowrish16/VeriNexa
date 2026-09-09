import { useState, useEffect } from "react";
import { useAuth } from "./AuthContext";

function HistorySidebar({ activeSessionId, onSelectSession, onNewSession }) {
  const { authFetch, isAuthenticated } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const fetchHistory = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await authFetch("http://127.0.0.1:8000/api/history");
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error("Failed to load audit history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [isAuthenticated, activeSessionId]);

  if (!isAuthenticated) return null;

  if (isCollapsed) {
    return (
      <div className="flex flex-col items-center py-4 border-r shrink-0" style={{ width: "48px", background: "var(--surface)", borderColor: "var(--border)" }}>
        <button
          onClick={() => setIsCollapsed(false)}
          title="Expand Audit History"
          className="hud-label hover:opacity-80 p-2 text-center"
          style={{ color: "var(--teal)" }}
        >
          ▶
        </button>
      </div>
    );
  }

  return (
    <aside
      className="flex flex-col border-r shrink-0 transition-all duration-300"
      style={{
        width: "280px",
        background: "rgba(11, 19, 27, 0.85)",
        borderColor: "var(--border)",
        backdropFilter: "blur(6px)",
      }}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between p-3 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2">
          <span className="hud-pulse" style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--teal)", display: "inline-block" }} />
          <span className="hud-label">// AUDIT LOGS</span>
        </div>
        <button
          onClick={() => setIsCollapsed(true)}
          title="Collapse sidebar"
          className="text-xs px-1.5 py-0.5 rounded hover:opacity-80"
          style={{ color: "var(--text-secondary)" }}
        >
          ◀
        </button>
      </div>

      {/* New Session Button */}
      <div className="p-3 border-b" style={{ borderColor: "var(--border)" }}>
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded text-xs font-mono tracking-wider transition-all hud-glow-border"
          style={{
            background: "rgba(45, 212, 206, 0.08)",
            border: "1px solid var(--teal)",
            color: "var(--teal)",
          }}
        >
          <span>+</span> NEW AUDIT SESSION
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1.5">
        {loading && sessions.length === 0 && (
          <p className="hud-label text-center py-6" style={{ color: "var(--text-secondary)" }}>
            LOADING SESSIONS...
          </p>
        )}

        {!loading && sessions.length === 0 && (
          <div className="text-center py-8 px-4">
            <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
              No audit sessions recorded yet. Ask a question to begin!
            </p>
          </div>
        )}

        {sessions.map((sess) => {
          const isActive = sess.id === activeSessionId;
          const formattedDate = sess.created_at
            ? new Date(sess.created_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
              })
            : "";

          return (
            <div
              key={sess.id}
              onClick={() => onSelectSession(sess.id)}
              className={`rounded px-3 py-2.5 text-left cursor-pointer transition border ${
                isActive
                  ? "border-l-4"
                  : "border-transparent hover:border-gray-800 hover:bg-white/[0.02]"
              }`}
              style={{
                background: isActive ? "var(--surface)" : "transparent",
                borderColor: isActive ? "var(--teal)" : "rgba(22, 50, 59, 0.3)",
              }}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-[10px]" style={{ color: "var(--text-secondary)" }}>
                  SESSION #{sess.id}
                </span>
                <span className="font-mono text-[10px]" style={{ color: "var(--text-secondary)" }}>
                  {formattedDate}
                </span>
              </div>
              <p
                className="text-xs font-medium line-clamp-2 leading-snug"
                style={{ color: isActive ? "var(--teal)" : "var(--text-primary)" }}
              >
                {sess.title || "Biomedical Audit Session"}
              </p>
              <div className="mt-1.5 flex items-center gap-2">
                <span
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded"
                  style={{ background: "rgba(255,255,255,0.04)", color: "var(--text-secondary)" }}
                >
                  {sess.message_count} {sess.message_count === 1 ? "query" : "queries"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

export default HistorySidebar;
