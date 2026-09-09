import React, { useEffect, useState, useRef } from "react";
import {
  BookOpen,
  ArrowLeft,
  UploadCloud,
  FileText,
  Search,
  Scale,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Layers,
  ChevronRight,
  Loader2,
  Plus,
  Sparkles,
  User,
  LogOut,
  MapPin,
  ExternalLink
} from "lucide-react";
import { AuthProvider, useAuth } from "./AuthContext";
import LandingPage from "./LandingPage";
import UploadPage from "./UploadPage";
import LoginModal from "./LoginModal";
import HistorySidebar from "./components/HistorySidebar";
import PdfViewer from "./components/PdfViewer";
import ChatPanel from "./components/ChatPanel";
import {
  fetchPapers,
  uploadPaper,
  comparePapers,
  checkIntegrity,
  fetchSessionMessages,
  getPdfFileUrl
} from "./services/api";

function Workspace() {
  const { user, logout, isAuthenticated } = useAuth();
  const [screen, setScreen] = useState("landing"); // "landing" | "upload" | "dashboard"

  // Auth Modal State
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState("login");
  const [pendingAction, setPendingAction] = useState(null);

  // Papers State
  const [papers, setPapers] = useState([]);
  const [loadingPapers, setLoadingPapers] = useState(false);
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [selectedPdfUrl, setSelectedPdfUrl] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);

  // Fast Ingest in Dashboard State
  const [dashFile, setDashFile] = useState(null);
  const [dashTitle, setDashTitle] = useState("");
  const [uploadingDash, setUploadingDash] = useState(false);
  const [uploadFeedback, setUploadFeedback] = useState(null);
  const fileInputRef = useRef(null);

  // Compare Across Papers State
  const [compareQuery, setCompareQuery] = useState("");
  const [comparing, setComparing] = useState(false);
  const [compareResult, setCompareResult] = useState(null);

  // Check Paper Integrity State
  const [integrityPaperId, setIntegrityPaperId] = useState("");
  const [integrityTopic, setIntegrityTopic] = useState("");
  const [checkingIntegrity, setCheckingIntegrity] = useState(false);
  const [integrityResult, setIntegrityResult] = useState(null);

  // Active Audit History Session State
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessionMessages, setSessionMessages] = useState([]);

  const openAuth = (tab = "login", onComplete = null) => {
    setAuthModalTab(tab);
    setPendingAction(() => onComplete);
    setAuthModalOpen(true);
  };

  const loadPapers = async () => {
    setLoadingPapers(true);
    try {
      const data = await fetchPapers();
      setPapers(data);
      if (data.length > 0 && !selectedPaper) {
        setSelectedPaper(data[0]);
        if (data[0].filename) {
          openPdf(data[0].filename, data[0]);
        }
      }
      if (data.length > 0 && !integrityPaperId) {
        setIntegrityPaperId(data[0].id || data[0].paper_id);
      }
    } catch (err) {
      console.warn("Failed to load papers:", err);
    } finally {
      setLoadingPapers(false);
    }
  };

  useEffect(() => {
    loadPapers();
  }, []);

  // Open PDF in Left Viewer
  const openPdf = (filename, paperObj = null, citationObj = null) => {
    if (paperObj) setSelectedPaper(paperObj);
    const url = getPdfFileUrl(filename);
    setSelectedPdfUrl(url);
    setActiveCitation(citationObj || null);
  };

  // Load Past Audit Session
  const handleSelectSession = async (sessionId) => {
    setActiveSessionId(sessionId);
    try {
      const data = await fetchSessionMessages(sessionId);
      setSessionMessages(data.messages || []);
    } catch (err) {
      console.error("Could not load session messages:", err);
    }
  };

  const handleNewSession = () => {
    setActiveSessionId(null);
    setSessionMessages([]);
  };

  // Dashboard Quick Upload
  const handleDashUpload = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      openAuth("login");
      return;
    }

    if (!dashFile) return;
    setUploadingDash(true);
    setUploadFeedback(null);

    try {
      const res = await uploadPaper(dashFile, dashTitle.trim());
      setUploadFeedback({
        type: "success",
        text: `Paper #${res.paper_id} verified & indexed: ${dashFile.name}`,
      });
      setDashFile(null);
      setDashTitle("");
      await loadPapers();
      if (res.filename) {
        openPdf(res.filename, { id: res.paper_id, filename: res.filename, title: res.title });
      }
    } catch (err) {
      setUploadFeedback({
        type: "error",
        text: `Upload failed: ${err.message}${err.details ? ` (${err.details})` : ""}`,
      });
    } finally {
      setUploadingDash(false);
    }
  };

  // Compare Across Papers
  const handleCompare = async (e) => {
    e.preventDefault();
    if (!compareQuery.trim() || comparing) return;

    if (!isAuthenticated) {
      openAuth("login");
      return;
    }

    setComparing(true);
    setCompareResult(null);

    try {
      const res = await comparePapers(compareQuery.trim());
      setCompareResult(res);
    } catch (err) {
      setCompareResult({
        verdict: "VERDICT: CONTRADICT",
        analysis: `Error during cross-paper query: ${err.message}`,
      });
    } finally {
      setComparing(false);
    }
  };

  // Integrity Check
  const handleIntegrityCheck = async (e) => {
    e.preventDefault();
    if (!integrityTopic.trim() || checkingIntegrity) return;

    if (!isAuthenticated) {
      openAuth("login");
      return;
    }

    setCheckingIntegrity(true);
    setIntegrityResult(null);

    try {
      const targetId = integrityPaperId || (papers[0] && papers[0].id) || 1;
      const res = await checkIntegrity(targetId, integrityTopic.trim());
      setIntegrityResult(res);
    } catch (err) {
      setIntegrityResult({
        verdict: "VERDICT: INCONSISTENT",
        explanation: `Error auditing integrity: ${err.message}`,
      });
    } finally {
      setCheckingIntegrity(false);
    }
  };

  // Format Verdict Badge
  const renderVerdictBadge = (verdict) => {
    if (!verdict) return null;
    const clean = verdict.toUpperCase();

    if (clean.includes("CONTRADICT") || clean.includes("INCONSISTENT")) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ff4757]/15 border border-[#ff4757]/40 text-[#ff4757] font-mono font-bold text-xs">
          <XCircle className="w-3.5 h-3.5" />
          {verdict}
        </span>
      );
    } else if (clean.includes("PARTIAL")) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#e8a33d]/15 border border-[#e8a33d]/40 text-[#e8a33d] font-mono font-bold text-xs">
          <AlertTriangle className="w-3.5 h-3.5" />
          {verdict}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#2dd4ce]/15 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono font-bold text-xs">
          <CheckCircle2 className="w-3.5 h-3.5" />
          {verdict}
        </span>
      );
    }
  };

  // Navigation handlers with Auth Gate
  const handleStartWorkflow = () => {
    if (isAuthenticated) {
      setScreen("upload");
    } else {
      openAuth("login", () => setScreen("upload"));
    }
  };

  const handleGoWorkspace = () => {
    if (isAuthenticated) {
      setScreen("dashboard");
    } else {
      openAuth("login", () => setScreen("dashboard"));
    }
  };

  return (
    <>
      <LoginModal
        isOpen={authModalOpen}
        defaultTab={authModalTab}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={() => {
          setAuthModalOpen(false);
          if (pendingAction) {
            pendingAction();
          } else {
            setScreen("dashboard");
          }
        }}
      />

      {screen === "landing" && (
        <LandingPage
          onStart={handleStartWorkflow}
          onOpenAuth={(tab) => openAuth(tab)}
          onGoWorkspace={handleGoWorkspace}
        />
      )}

      {screen === "upload" && (
        <UploadPage
          onContinue={() => setScreen("dashboard")}
          onBack={() => setScreen("landing")}
          onOpenAuth={(tab) => openAuth(tab)}
        />
      )}

      {screen === "dashboard" && (
        <div className="min-h-screen bg-[#060b10] text-[#f4f7f5] flex flex-col font-sans selection:bg-[#2dd4ce]/25 selection:text-[#2dd4ce]">
          {/* Top Header */}
          <header className="sticky top-0 z-40 bg-[#060b10]/95 backdrop-blur-xl border-b border-[#16323b] px-4 sm:px-6 py-3 shadow-xl">
            <div className="max-w-[1780px] mx-auto flex items-center justify-between">
              {/* Left: Brand & Return */}
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setScreen("landing")}
                  className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white border border-white/10 transition-colors cursor-pointer flex items-center gap-1.5 text-xs font-mono"
                  title="Return to Landing Page"
                >
                  <ArrowLeft className="w-3.5 h-3.5 text-[#2dd4ce]" />
                  <span>OVERVIEW</span>
                </button>

                <div className="h-4 w-px bg-white/10"></div>

                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#16323b] to-[#060b10] border border-[#2dd4ce]/40 flex items-center justify-center text-[#2dd4ce]">
                    <BookOpen className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-sans font-bold tracking-[0.2em] text-sm text-white uppercase">
                      VeriNexa
                    </span>
                    <span className="hidden md:inline-block text-[10px] font-mono text-[#2dd4ce] ml-2 px-1.5 py-0.5 rounded bg-[#2dd4ce]/10 border border-[#2dd4ce]/30">
                      DUAL-PANE CLINICAL WORKSPACE
                    </span>
                  </div>
                </div>
              </div>

              {/* Center / Right: Telemetry & User Controls */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setScreen("upload")}
                  className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded-xl border border-[#2dd4ce]/40 text-[#2dd4ce] bg-[#2dd4ce]/5 hover:bg-[#2dd4ce]/15 transition cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>UPLOAD LITERATURE</span>
                </button>

                <div className="px-3 py-1 rounded-full bg-[#0b1e25] border border-[#2dd4ce]/30 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#2dd4ce] animate-pulse"></span>
                  <span className="text-xs font-mono font-bold text-[#2dd4ce] tracking-wider uppercase">
                    {papers.length} {papers.length === 1 ? "PAPER" : "PAPERS"} INDEXED
                  </span>
                </div>

                <button
                  onClick={loadPapers}
                  className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white border border-white/10 transition-colors cursor-pointer"
                  title="Refresh Literature Index"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingPapers ? "animate-spin text-[#2dd4ce]" : ""}`} />
                </button>

                {isAuthenticated ? (
                  <div className="flex items-center gap-2 pl-2 border-l border-[#16323b]">
                    <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-white/5 text-[#adc2b6] flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-[#2dd4ce]" />
                      <span className="truncate max-w-[130px]">{user?.full_name || user?.email}</span>
                    </span>
                    <button
                      onClick={logout}
                      title="Sign Out"
                      className="p-1.5 rounded-lg bg-white/5 hover:bg-[#ff4757]/10 text-[#8fa89b] hover:text-[#ff4757] transition cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => openAuth("login")}
                    className="text-xs font-mono px-3 py-1.5 rounded-lg bg-[#2dd4ce] text-[#060b10] font-bold cursor-pointer"
                  >
                    Sign In
                  </button>
                )}
              </div>
            </div>
          </header>

          {/* Main Workspace Body */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left Sidebar: Audit History & Sessions */}
            <HistorySidebar
              activeSessionId={activeSessionId}
              onSelectSession={handleSelectSession}
              onNewSession={handleNewSession}
            />

            {/* Split-Screen Investigation View */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start max-w-[1780px] mx-auto w-full">
              
              {/* Left Column: Interactive PDF Viewer (when selected) */}
              {selectedPdfUrl && (
                <div className="lg:col-span-6 h-[880px] sticky top-20">
                  <PdfViewer
                    fileUrl={selectedPdfUrl}
                    filename={selectedPaper?.filename || "source.pdf"}
                    activeCitation={activeCitation}
                    onClose={() => {
                      setSelectedPdfUrl(null);
                      setActiveCitation(null);
                    }}
                  />
                </div>
              )}

              {/* Right Column: LangGraph Audit Intelligence Panel */}
              <div
                className={`${
                  selectedPdfUrl ? "lg:col-span-6" : "lg:col-span-12 max-w-5xl mx-auto"
                } space-y-6 transition-all duration-300 w-full`}
              >
                {/* SECTION 1: ADD LITERATURE (Fast Form) */}
                <div className="rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-5 shadow-xl">
                  <div className="flex items-center justify-between mb-4 border-b border-[#16323b] pb-3">
                    <div className="flex items-center gap-2">
                      <UploadCloud className="w-4 h-4 text-[#2dd4ce]" />
                      <h2 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                        SECTION 1: ADD LITERATURE
                      </h2>
                    </div>
                    <span className="text-[10.5px] font-mono text-[#8fa89b]">AIR-GAPPED GATE</span>
                  </div>

                  <form onSubmit={handleDashUpload} className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
                      {/* File Select */}
                      <div className="sm:col-span-6">
                        <div
                          onClick={() => fileInputRef.current && fileInputRef.current.click()}
                          className="p-3 rounded-xl border border-dashed border-[#16323b] hover:border-[#2dd4ce]/50 bg-[#060b10] flex items-center justify-between cursor-pointer transition-colors"
                        >
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept="application/pdf"
                            onChange={(e) => {
                              if (e.target.files && e.target.files[0]) {
                                setDashFile(e.target.files[0]);
                                if (!dashTitle) {
                                  setDashTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
                                }
                              }
                            }}
                            className="hidden"
                          />
                          <div className="flex items-center gap-2 truncate">
                            <FileText className="w-4 h-4 text-[#2dd4ce] shrink-0" />
                            <span className="text-xs font-mono text-[#adc2b6] truncate">
                              {dashFile ? dashFile.name : "Select PDF Document..."}
                            </span>
                          </div>
                          <span className="text-[10px] font-mono text-[#2dd4ce] bg-[#2dd4ce]/10 px-2 py-0.5 rounded shrink-0">
                            Browse
                          </span>
                        </div>
                      </div>

                      {/* Title Input */}
                      <div className="sm:col-span-6">
                        <input
                          type="text"
                          value={dashTitle}
                          onChange={(e) => setDashTitle(e.target.value)}
                          placeholder="Validated Document Title..."
                          className="w-full h-full px-3.5 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none"
                        />
                      </div>
                    </div>

                    {uploadFeedback && (
                      <div
                        className={`text-xs font-mono p-2.5 rounded-lg border ${
                          uploadFeedback.type === "success"
                            ? "bg-[#2dd4ce]/10 text-[#2dd4ce] border-[#2dd4ce]/30"
                            : "bg-[#ff4757]/10 text-[#ff4757] border-[#ff4757]/30"
                        }`}
                      >
                        {uploadFeedback.text}
                      </div>
                    )}

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={uploadingDash || !dashFile}
                        className="px-4 py-2 rounded-xl bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-[#2dd4ce]/20 transition-all cursor-pointer"
                      >
                        {uploadingDash ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Validating & Ingesting...</span>
                          </>
                        ) : (
                          <>
                            <Plus className="w-3.5 h-3.5" />
                            <span>Upload & Verify</span>
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>

                {/* SECTION 2: ACTIVE LITERATURE */}
                <div className="rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-5 shadow-xl">
                  <div className="flex items-center justify-between mb-4 border-b border-[#16323b] pb-3">
                    <div className="flex items-center gap-2">
                      <Layers className="w-4 h-4 text-[#2dd4ce]" />
                      <h2 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                        SECTION 2: ACTIVE LITERATURE ({papers.length})
                      </h2>
                    </div>
                    <span className="text-[10.5px] font-mono text-[#8fa89b]">DUAL-PANE ANCHOR</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-56 overflow-y-auto pr-1 no-scrollbar">
                    {papers.map((paper, idx) => {
                      const isSelected = selectedPaper && (selectedPaper.id === paper.id || selectedPaper.filename === paper.filename);
                      return (
                        <div
                          key={paper.id || idx}
                          onClick={() => paper.filename && openPdf(paper.filename, paper)}
                          className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                            isSelected
                              ? "bg-[#0c232c] border-[#2dd4ce] shadow-lg shadow-[#2dd4ce]/15"
                              : "bg-[#060b10] hover:bg-[#081720] border-[#16323b] hover:border-[#2dd4ce]/40"
                          }`}
                        >
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-[10px] font-mono text-[#2dd4ce] font-bold">
                                #{paper.id || paper.paper_id}
                              </span>
                              <span className="text-[10px] font-mono text-[#8fa89b]">PDF</span>
                            </div>
                            <h3 className="text-xs font-bold text-white line-clamp-2 leading-snug">
                              {paper.title || paper.filename}
                            </h3>
                          </div>

                          <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10.5px] font-mono text-[#8fa89b]">
                            <span className="truncate max-w-[130px]">{paper.filename}</span>
                            <span className="text-[#2dd4ce] hover:underline flex items-center gap-0.5">
                              <span>Inspect in Reader</span>
                              <ChevronRight className="w-3 h-3" />
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* SECTION 3: CLOSED-CORPUS RAG CHAT & CITATIONS */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <span className="font-mono text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-[#2dd4ce]" />
                      SECTION 3: EVIDENCE CHAT & CITATION ANCHORS
                    </span>
                    <span className="text-[10.5px] font-mono text-[#8fa89b]">Llama 3.1:8B Grounded</span>
                  </div>

                  <ChatPanel
                    activeSessionId={activeSessionId}
                    sessionMessages={sessionMessages}
                    onSessionCreated={(newId) => setActiveSessionId(newId)}
                    onOpenPdf={(fn, c) => openPdf(fn, null, c)}
                  />
                </div>

                {/* SECTION 4: COMPARE ACROSS PAPERS (Conflict Matrix) */}
                <div className="rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-5 shadow-xl space-y-4">
                  <div className="flex items-center justify-between border-b border-[#16323b] pb-3">
                    <div className="flex items-center gap-2">
                      <Scale className="w-4 h-4 text-[#e8a33d]" />
                      <h2 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                        SECTION 4: COMPARE ACROSS PAPERS
                      </h2>
                    </div>
                    <span className="text-[10.5px] font-mono text-[#8fa89b]">LangGraph Conflict Engine</span>
                  </div>

                  <p className="text-xs text-[#adc2b6]">
                    Detect empirical conflicts, dosage variance, and divergent cohort outcomes across all indexed literature.
                  </p>

                  <form onSubmit={handleCompare} className="flex gap-2">
                    <input
                      type="text"
                      value={compareQuery}
                      onChange={(e) => setCompareQuery(e.target.value)}
                      placeholder="e.g. effect of SGLT2 inhibitor on body weight or HbA1c..."
                      className="flex-1 px-4 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#e8a33d] focus:outline-none"
                    />
                    <button
                      type="submit"
                      disabled={comparing || !compareQuery.trim()}
                      className="px-5 py-2.5 rounded-xl bg-[#e8a33d] hover:bg-[#d8932d] text-[#060b10] font-bold text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-md shadow-[#e8a33d]/20"
                    >
                      {comparing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                      <span>Cross-Examine</span>
                    </button>
                  </form>

                  {compareResult && (
                    <div className="p-4 rounded-xl bg-[#060b10] border border-[#16323b] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs text-[#8fa89b] uppercase">Arbitration Verdict:</span>
                        {renderVerdictBadge(compareResult.verdict)}
                      </div>
                      <p className="text-xs text-[#d8f3f0] leading-relaxed">
                        {compareResult.verdict?.split("REASON:")[1] || compareResult.analysis || compareResult.verdict}
                      </p>
                    </div>
                  )}
                </div>

                {/* SECTION 5: CHECK PAPER INTEGRITY (Abstract Spin Detector) */}
                <div className="rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-5 shadow-xl space-y-4">
                  <div className="flex items-center justify-between border-b border-[#16323b] pb-3">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-[#2dd4ce]" />
                      <h2 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                        SECTION 5: CHECK PAPER INTEGRITY
                      </h2>
                    </div>
                    <span className="text-[10.5px] font-mono text-[#8fa89b]">Abstract Spin Auditor</span>
                  </div>

                  <p className="text-xs text-[#adc2b6]">
                    Audit whether a paper's abstract exaggerates statistical outcomes against its own raw results and tables.
                  </p>

                  <form onSubmit={handleIntegrityCheck} className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-3">
                      <div className="sm:col-span-5">
                        <select
                          value={integrityPaperId}
                          onChange={(e) => setIntegrityPaperId(e.target.value)}
                          className="w-full px-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs focus:border-[#2dd4ce] focus:outline-none"
                        >
                          {papers.map((p) => (
                            <option key={p.id} value={p.id}>
                              #{p.id} — {p.title || p.filename}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="sm:col-span-7 flex gap-2">
                        <input
                          type="text"
                          value={integrityTopic}
                          onChange={(e) => setIntegrityTopic(e.target.value)}
                          placeholder="e.g. SGLT2 inhibitor effect on cardiovascular death..."
                          className="flex-1 px-3.5 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none"
                        />
                        <button
                          type="submit"
                          disabled={checkingIntegrity || !integrityTopic.trim()}
                          className="px-4 py-2.5 rounded-xl bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-md shadow-[#2dd4ce]/20"
                        >
                          {checkingIntegrity ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                          <span>Audit</span>
                        </button>
                      </div>
                    </div>
                  </form>

                  {integrityResult && (
                    <div className="p-4 rounded-xl bg-[#060b10] border border-[#16323b] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs text-[#8fa89b] uppercase">Integrity Verdict:</span>
                        {renderVerdictBadge(integrityResult.verdict)}
                      </div>
                      <p className="text-xs text-[#d8f3f0] leading-relaxed">
                        {integrityResult.verdict?.split("REASON:")[1] || integrityResult.explanation || integrityResult.verdict}
                      </p>
                    </div>
                  )}
                </div>

              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Workspace />
    </AuthProvider>
  );
}