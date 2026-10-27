import React, { useState, useEffect } from "react";
import {
  Shield,
  Users,
  FileText,
  Database,
  Cpu,
  Layers,
  Search,
  RefreshCw,
  LogOut,
  ArrowUpRight,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Server,
  KeyRound,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { useAuth } from "./AuthContext";

export default function AdminDashboard({ onGoWorkspace, onLogout }) {
  const { user, authFetch } = useAuth();
  const [stats, setStats] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [papersList, setPapersList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [userSearch, setUserSearch] = useState("");
  const [paperSearch, setPaperSearch] = useState("");
  const [activeTab, setActiveTab] = useState("overview"); // "overview" | "users" | "papers"

  const loadAdminData = async () => {
    try {
      const [resStats, resUsers, resPapers] = await Promise.all([
        authFetch("http://127.0.0.1:8000/api/admin/stats"),
        authFetch("http://127.0.0.1:8000/api/admin/users"),
        authFetch("http://127.0.0.1:8000/api/admin/papers"),
      ]);

      if (resStats.ok) {
        const statsData = await resStats.json();
        setStats(statsData);
      }
      if (resUsers.ok) {
        const usersData = await resUsers.json();
        setUsersList(usersData);
      }
      if (resPapers.ok) {
        const papersData = await resPapers.json();
        setPapersList(papersData);
      }
    } catch (err) {
      console.error("Failed to fetch admin stats:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadAdminData();
  };

  const filteredUsers = usersList.filter(
    (u) =>
      u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
      (u.full_name && u.full_name.toLowerCase().includes(userSearch.toLowerCase()))
  );

  const filteredPapers = papersList.filter(
    (p) =>
      p.filename.toLowerCase().includes(paperSearch.toLowerCase()) ||
      (p.detected_title && p.detected_title.toLowerCase().includes(paperSearch.toLowerCase())) ||
      (p.owner_email && p.owner_email.toLowerCase().includes(paperSearch.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-[#04090d] text-[#f4f7f5] font-sans selection:bg-[#2dd4ce]/25 selection:text-[#2dd4ce] flex flex-col">
      {/* Top Admin Header */}
      <header className="sticky top-0 z-40 bg-[#060e14]/95 backdrop-blur-xl border-b border-[#16323b] px-4 sm:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#16323b] to-[#0a1f26] p-0.5 border border-[#2dd4ce]/40 flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#2dd4ce]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-wider text-sm text-white">VERINEXA</span>
                <span className="text-[10px] font-mono tracking-widest px-2 py-0.5 rounded bg-[#2dd4ce]/15 text-[#2dd4ce] border border-[#2dd4ce]/30 font-bold uppercase">
                  ADMIN CONSOLE
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#8fa89b]">
                SYSTEM-WIDE TENANT & LITERATURE ARBITRATION GOVERNANCE
              </span>
            </div>
          </div>

          {/* Quick Actions & Profile */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              title="Refresh System Metrics"
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white border border-white/10 transition cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-[#2dd4ce]" : ""}`} />
            </button>

            <button
              onClick={onGoWorkspace}
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-[#2dd4ce] text-xs font-mono font-medium border border-[#2dd4ce]/30 transition cursor-pointer"
            >
              <span>Clinical Workspace</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>

            <div className="flex items-center gap-2 pl-2 border-l border-[#16323b]">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-xs font-mono text-white font-semibold">{user?.email}</span>
                <span className="text-[10px] font-mono text-[#2dd4ce]">Primary Administrator</span>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                className="p-2 rounded-xl bg-[#ff4757]/10 hover:bg-[#ff4757]/20 text-[#ff4757] border border-[#ff4757]/30 transition cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-8 space-y-6">
        
        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-[#16323b] pb-3">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wider transition cursor-pointer ${
              activeTab === "overview"
                ? "bg-[#2dd4ce] text-[#060b10] shadow-md shadow-[#2dd4ce]/20"
                : "text-[#8fa89b] hover:text-white hover:bg-white/5"
            }`}
          >
            SYSTEM OVERVIEW
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wider transition cursor-pointer ${
              activeTab === "users"
                ? "bg-[#2dd4ce] text-[#060b10] shadow-md shadow-[#2dd4ce]/20"
                : "text-[#8fa89b] hover:text-white hover:bg-white/5"
            }`}
          >
            USER DIRECTORY ({usersList.length})
          </button>
          <button
            onClick={() => setActiveTab("papers")}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wider transition cursor-pointer ${
              activeTab === "papers"
                ? "bg-[#2dd4ce] text-[#060b10] shadow-md shadow-[#2dd4ce]/20"
                : "text-[#8fa89b] hover:text-white hover:bg-white/5"
            }`}
          >
            GLOBAL LITERATURE ({papersList.length})
          </button>
        </div>

        {/* METRICS CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Users */}
          <div className="p-5 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#8fa89b]">Genuine Accounts</span>
              <Users className="w-4 h-4 text-[#2dd4ce]" />
            </div>
            <div className="mt-3 text-3xl font-bold font-mono text-white">
              {stats ? stats.total_users : "—"}
            </div>
            <p className="mt-1 text-[11px] font-mono text-[#2dd4ce]">
              {stats?.active_users ?? stats?.total_users ?? 0} active clinical researchers
            </p>
          </div>

          {/* Card 2: Papers */}
          <div className="p-5 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#8fa89b]">Uploaded Literature</span>
              <FileText className="w-4 h-4 text-[#d4af37]" />
            </div>
            <div className="mt-3 text-3xl font-bold font-mono text-white">
              {stats ? stats.total_papers : "—"}
            </div>
            <p className="mt-1 text-[11px] font-mono text-[#4d6359]">Verified clinical papers in PostgreSQL</p>
          </div>

          {/* Card 3: Chunks */}
          <div className="p-5 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#8fa89b]">Spatial Vector Chunks</span>
              <Layers className="w-4 h-4 text-[#2dd4ce]" />
            </div>
            <div className="mt-3 text-3xl font-bold font-mono text-white">
              {stats ? stats.total_chunks : "—"}
            </div>
            <p className="mt-1 text-[11px] font-mono text-[#4d6359]">pgvector 384-dim active chunks</p>
          </div>

          {/* Card 4: Audit Sessions */}
          <div className="p-5 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#8fa89b]">Audit Sessions</span>
              <Clock className="w-4 h-4 text-[#e8a33d]" />
            </div>
            <div className="mt-3 text-3xl font-bold font-mono text-white">
              {stats ? stats.total_sessions : "—"}
            </div>
            <p className="mt-1 text-[11px] font-mono text-[#4d6359]">
              {stats?.total_messages || 0} synthesized evidence claims
            </p>
          </div>
        </div>

        {/* OVERVIEW TAB CONTENT */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* System Health Status */}
            <div className="lg:col-span-1 p-6 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl space-y-4 text-left">
              <div className="flex items-center justify-between border-b border-[#16323b] pb-3">
                <div className="flex items-center gap-2">
                  <Server className="w-4 h-4 text-[#2dd4ce]" />
                  <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                    Engine Diagnostics
                  </h3>
                </div>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#2dd4ce]/10 text-[#2dd4ce] text-[10px] font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4ce] animate-pulse" />
                  HEALTHY
                </span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-[#060b10] border border-[#16323b] flex items-center justify-between">
                  <span className="text-[#8fa89b]">Vector Engine</span>
                  <span className="text-white font-bold">PostgreSQL 17 + pgvector</span>
                </div>
                <div className="p-3 rounded-xl bg-[#060b10] border border-[#16323b] flex items-center justify-between">
                  <span className="text-[#8fa89b]">LLM Model</span>
                  <span className="text-[#2dd4ce] font-bold">Ollama {stats?.ollama_model || "llama3.1:8b"}</span>
                </div>
                <div className="p-3 rounded-xl bg-[#060b10] border border-[#16323b] flex items-center justify-between">
                  <span className="text-[#8fa89b]">Ollama Status</span>
                  <span className={`font-bold ${stats?.ollama_status === "online" ? "text-[#2dd4ce]" : "text-[#ff4757]"}`}>
                    {stats?.ollama_status?.toUpperCase() || "ONLINE"}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-[#060b10] border border-[#16323b] flex items-center justify-between">
                  <span className="text-[#8fa89b]">Embedding Model</span>
                  <span className="text-white">all-MiniLM-L6-v2 (local)</span>
                </div>
                <div className="p-3 rounded-xl bg-[#060b10] border border-[#16323b] flex items-center justify-between">
                  <span className="text-[#8fa89b]">Biomedical Ingestion Gate</span>
                  <span className="text-[#2dd4ce]">Active (3-Tier Heuristic)</span>
                </div>
              </div>
            </div>

            {/* Recent Registrations & Quick Directory Preview */}
            <div className="lg:col-span-2 p-6 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl space-y-4 text-left">
              <div className="flex items-center justify-between border-b border-[#16323b] pb-3">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#2dd4ce]" />
                  <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                    Recent Tenant Registrations
                  </h3>
                </div>
                <button
                  onClick={() => setActiveTab("users")}
                  className="text-xs font-mono text-[#2dd4ce] hover:underline cursor-pointer"
                >
                  View All ({usersList.length}) →
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-[#16323b] text-[#8fa89b] text-[11px]">
                      <th className="py-2 px-3">UID</th>
                      <th className="py-2 px-3">Account Email</th>
                      <th className="py-2 px-3">Role</th>
                      <th className="py-2 px-3 text-right">Papers</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#16323b]/50">
                    {usersList.slice(0, 5).map((u) => (
                      <tr key={u.id} className="hover:bg-white/[0.02] transition">
                        <td className="py-2.5 px-3 text-[#8fa89b]">#{u.id}</td>
                        <td className="py-2.5 px-3 text-white font-medium">
                          {u.email}
                          {u.full_name && (
                            <span className="block text-[10px] text-[#4d6359]">{u.full_name}</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3">
                          {u.is_admin ? (
                            <span className="px-2 py-0.5 rounded bg-[#2dd4ce]/20 text-[#2dd4ce] font-bold text-[10px]">
                              ADMIN
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded bg-white/5 text-[#8fa89b] text-[10px]">
                              RESEARCHER
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-right text-[#2dd4ce] font-bold">
                          {u.paper_count}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* USERS TAB CONTENT */}
        {activeTab === "users" && (
          <div className="p-6 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl space-y-4 text-left">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#16323b] pb-4">
              <div>
                <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
                  User Accounts Directory
                </h3>
                <p className="text-xs text-[#8fa89b] mt-0.5">
                  Complete registry of all registered tenants, admins, and researchers.
                </p>
              </div>

              {/* Search */}
              <div className="relative w-full sm:w-72">
                <input
                  type="text"
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  placeholder="Filter users by email or name..."
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none font-mono"
                />
                <Search className="w-3.5 h-3.5 text-[#8fa89b] absolute left-3 top-2.5" />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[#16323b] text-[#8fa89b] text-[11px] uppercase">
                    <th className="py-2.5 px-3">UID</th>
                    <th className="py-2.5 px-3">Email Address</th>
                    <th className="py-2.5 px-3">Full Name</th>
                    <th className="py-2.5 px-3">Access Level</th>
                    <th className="py-2.5 px-3 text-right">Papers</th>
                    <th className="py-2.5 px-3 text-right">Sessions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#16323b]/50">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-white/[0.02] transition">
                      <td className="py-3 px-3 text-[#8fa89b]">#{u.id}</td>
                      <td className="py-3 px-3 text-white font-medium">{u.email}</td>
                      <td className="py-3 px-3 text-[#adc2b6]">{u.full_name || "—"}</td>
                      <td className="py-3 px-3">
                        {u.is_admin ? (
                          <span className="px-2 py-0.5 rounded-full bg-[#2dd4ce]/20 text-[#2dd4ce] font-bold text-[10px] border border-[#2dd4ce]/30">
                            ADMINISTRATOR
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full bg-white/5 text-[#8fa89b] text-[10px] border border-white/10">
                            RESEARCHER
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-right text-[#2dd4ce] font-bold">
                        {u.paper_count}
                      </td>
                      <td className="py-3 px-3 text-right text-[#e8a33d] font-bold">
                        {u.session_count}
                      </td>
                    </tr>
                  ))}
                  {filteredUsers.length === 0 && (
                    <tr>
                      <td colSpan="6" className="py-8 text-center text-[#8fa89b]">
                        No user accounts match "{userSearch}".
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* PAPERS TAB CONTENT */}
        {activeTab === "papers" && (
          <div className="p-6 rounded-2xl bg-[#09151e]/80 border border-[#16323b] shadow-xl space-y-4 text-left">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#16323b] pb-4">
              <div>
                <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-white">
                  Global Literature Repository
                </h3>
                <p className="text-xs text-[#8fa89b] mt-0.5">
                  All clinical papers indexed in pgvector across all system users.
                </p>
              </div>

              {/* Search */}
              <div className="relative w-full sm:w-72">
                <input
                  type="text"
                  value={paperSearch}
                  onChange={(e) => setPaperSearch(e.target.value)}
                  placeholder="Filter papers by title or file..."
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none font-mono"
                />
                <Search className="w-3.5 h-3.5 text-[#8fa89b] absolute left-3 top-2.5" />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[#16323b] text-[#8fa89b] text-[11px] uppercase">
                    <th className="py-2.5 px-3">PID</th>
                    <th className="py-2.5 px-3">Detected Paper Title / Filename</th>
                    <th className="py-2.5 px-3">Tenant Owner</th>
                    <th className="py-2.5 px-3 text-right">Chunks</th>
                    <th className="py-2.5 px-3 text-right">Upload Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#16323b]/50">
                  {filteredPapers.map((p) => (
                    <tr key={p.id} className="hover:bg-white/[0.02] transition">
                      <td className="py-3 px-3 text-[#8fa89b]">#{p.id}</td>
                      <td className="py-3 px-3 text-white">
                        <span className="font-semibold block truncate max-w-md">
                          {p.detected_title || p.title || p.filename}
                        </span>
                        <span className="text-[10px] text-[#4d6359] block truncate max-w-md">
                          {p.filename}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-[#adc2b6]">
                        {p.owner_email || `UID: ${p.user_id}`}
                      </td>
                      <td className="py-3 px-3 text-right text-[#2dd4ce] font-bold">
                        {p.chunk_count}
                      </td>
                      <td className="py-3 px-3 text-right text-[#8fa89b] text-[11px]">
                        {p.uploaded_at ? p.uploaded_at.split("T")[0] : "—"}
                      </td>
                    </tr>
                  ))}
                  {filteredPapers.length === 0 && (
                    <tr>
                      <td colSpan="5" className="py-8 text-center text-[#8fa89b]">
                        No literature files match "{paperSearch}".
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
