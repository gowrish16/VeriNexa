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
  HelpCircle,
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
import AdminDashboard from "./AdminDashboard";
import ResetPasswordPage from "./ResetPasswordPage";
import HistorySidebar from "./components/HistorySidebar";
import PdfViewer from "./components/PdfViewer";
import ChatPanel from "./components/ChatPanel";
import CrossTrialMatrix from "./components/CrossTrialMatrix";
import {
  fetchPapers,
  uploadPaper,
  comparePapers,
  checkIntegrity,
  fetchSessionMessages,
  getPdfFileUrl
} from "./services/api";

function Workspace() {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const [screen, setScreen] = useState(() => {
    if (typeof window !== "undefined") {
      const p = window.location.pathname.toLowerCase();
      if (p.startsWith("/reset-password")) return "reset-password";
      if (p.startsWith("/admin")) return "admin";
      if (p.startsWith("/dashboard")) return "dashboard";
      if (p.startsWith("/upload")) return "upload";
    }
    return "landing";
  });

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
  const [comparePaper1Id, setComparePaper1Id] = useState("");
  const [comparePaper2Id, setComparePaper2Id] = useState("");
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
      setPapers(data || []);
      if (data && data.length > 0) {
        if (!integrityPaperId) {
          setIntegrityPaperId(data[0].id || data[0].paper_id);
        }
        if (!selectedPaper) {
          setSelectedPaper(data[0]);
          if (data[0].filename && !selectedPdfUrl) {
            openPdf(data[0].filename, data[0]);
          }
        }
        setComparePaper1Id((prev) => prev || String(data[0].id || data[0].paper_id));
        setComparePaper2Id((prev) => {
          if (prev) return prev;
          const second = data.length > 1 ? data[1] : data[0];
          return String(second.id || second.paper_id);
        });
      }
      return data || [];
    } catch (err) {
      console.warn("Failed to load papers:", err);
      setPapers([]);
      return [];
    } finally {
      setLoadingPapers(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadPapers();
    } else {
      setPapers([]);
      setSelectedPaper(null);
      setSelectedPdfUrl(null);
      setActiveCitation(null);
      setComparePaper1Id("");
      setComparePaper2Id("");
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    if (selectedPaper?.id) {
      setIntegrityPaperId(selectedPaper.id);
    }
  }, [selectedPaper]);

  // Open PDF in Left Viewer
  const openPdf = (filename, paperObj = null, citationObj = null) => {
    // Discern citation vs paperObj if 2nd arg was citationObj
    const isSecondArgCitation =
      paperObj &&
      (paperObj.bbox ||
        paperObj.page ||
        paperObj.page_num ||
        paperObj.page_number ||
        paperObj.snippet ||
        paperObj.chunk_id ||
        paperObj.chunk_index);

    const citation = citationObj || (isSecondArgCitation ? paperObj : null);
    const passedPaper = isSecondArgCitation ? null : paperObj;

    const targetPaperId = citation?.paper_id || passedPaper?.id || passedPaper?.paper_id;
    const targetFilename =
      filename ||
      passedPaper?.filename ||
      citation?.filename ||
      citation?.doc_id ||
      selectedPaper?.filename;

    const matchedPaper =
      passedPaper ||
      (targetPaperId
        ? papers.find(
            (p) =>
              p.id === targetPaperId ||
              p.paper_id === targetPaperId ||
              String(p.id) === String(targetPaperId)
          )
        : null) ||
      (targetFilename
        ? papers.find(
            (p) =>
              p.filename === targetFilename ||
              p.title === targetFilename ||
              (p.filename &&
                targetFilename &&
                p.filename.toLowerCase() === targetFilename.toLowerCase()) ||
              (p.filename &&
                targetFilename &&
                targetFilename.toLowerCase().includes(p.filename.toLowerCase()))
          )
        : null) ||
      selectedPaper;

    if (matchedPaper) {
      setSelectedPaper(matchedPaper);
      if (matchedPaper.id || matchedPaper.paper_id) {
        setIntegrityPaperId(matchedPaper.id || matchedPaper.paper_id);
      }
    }

    const actualFilename = matchedPaper?.filename || targetFilename;
    if (actualFilename) {
      const url = getPdfFileUrl(actualFilename);
      setSelectedPdfUrl(url);
    }

    if (citation) {
      const pageNum = Number(
        citation.page_num ?? citation.page_number ?? citation.page ?? 1
      );
      const bbox =
        Array.isArray(citation.bbox) && citation.bbox.length === 4
          ? citation.bbox.map(Number)
          : [
              Number(citation.bbox_x0 ?? 0),
              Number(citation.bbox_y0 ?? citation.bbox_top ?? 0),
              Number(citation.bbox_x1 ?? 0),
              Number(citation.bbox_y1 ?? 0),
            ];
      const docId = citation.doc_id || citation.filename || actualFilename;

      const normalizedCitation = {
        ...citation,
        paper_id: matchedPaper?.id || matchedPaper?.paper_id || targetPaperId,
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
        filename: actualFilename || docId,
      };
      setActiveCitation(normalizedCitation);
    } else {
      setActiveCitation(null);
    }
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
      const isRejection = err.statusCode === 422 || err.isRejected;
      setUploadFeedback({
        type: "error",
        isRejection,
        text: isRejection
          ? (err.message || "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature.")
          : `Upload failed: ${err.message}${err.details ? ` (${err.details})` : ""}`,
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
      const p1 = comparePaper1Id || (papers.length > 0 ? (papers[0].id || papers[0].paper_id) : null);
      const p2 = comparePaper2Id || (papers.length > 1 ? (papers[1].id || papers[1].paper_id) : p1);
      const targetIds = p1 && p2 ? [Number(p1), Number(p2)] : (Array.isArray(papers) ? papers.map((p) => p.id) : null);
      const res = await comparePapers(compareQuery.trim(), targetIds);
      setCompareResult(res);
    } catch (err) {
      console.error("Compare failed:", err);
      setCompareResult({
        verdict: "VERDICT: INSUFFICIENT DATA",
        analysis: `Comparison failed: ${err.message}. Ensure backend is running.`,
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
      const targetId = integrityPaperId || selectedPaper?.id || (papers[0] && papers[0].id) || 1;
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

  // Helper to render markdown bold syntax **bold** cleanly
  const renderInlineMarkdown = (text) => {
    if (!text) return null;
    const parts = text.split(/(\*\*[^*]+?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        return (
          <strong key={index} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  // Helper to sanitize leading asterisk combinations and render structured bullets
  const renderFormattedReason = (rawReason) => {
    if (!rawReason) return null;

    const rawLines = String(rawReason).split(/\r?\n/);
    const elements = [];
    let currentBulletList = [];

    const flushBulletList = () => {
      if (currentBulletList.length > 0) {
        const listItems = [...currentBulletList];
        elements.push(
          <ul key={`ul-${elements.length}`} className="space-y-2 my-2 pl-1">
            {listItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-[#d8f3f0] leading-relaxed">
                <span className="text-[#e8a33d] font-bold text-sm leading-none mt-0.5">•</span>
                <span className="flex-1">{renderInlineMarkdown(item)}</span>
              </li>
            ))}
          </ul>
        );
        currentBulletList = [];
      }
    };

    for (let i = 0; i < rawLines.length; i++) {
      let line = rawLines[i].trim();
      if (!line) {
        flushBulletList();
        continue;
      }

      // Check if line is a bullet point or has leading asterisk combinations
      // Examples: '* **Title**:', '***Title***:', '**Title**:', '- **Title**:', '* Title'
      const bulletMatch = line.match(/^([*•\-–]|\d+\.)\s*(.*)$/);
      const isAsteriskCombo = /^(\*{2,3})\s*(.*)$/.test(line);

      if (bulletMatch || isAsteriskCombo) {
        let content = bulletMatch ? bulletMatch[2] : line;

        // Clean leading double/triple asterisk combinations e.g., '***', '**'
        content = content.replace(/^\*{3}([^*]+?)\*{3}/, "**$1**");
        content = content.replace(/^\*{2,3}\s*/, "**");
        content = content.trim();

        currentBulletList.push(content);
      } else {
        flushBulletList();
        // Regular paragraph (introductory or concluding sentence)
        const cleanedPara = line.replace(/^\*{2,3}\s*/, "").trim();
        elements.push(
          <p key={`p-${elements.length}`} className="text-xs text-[#d8f3f0] leading-relaxed">
            {renderInlineMarkdown(cleanedPara)}
          </p>
        );
      }
    }

    flushBulletList();

    return <div className="space-y-2">{elements}</div>;
  };

  // Parse Verdict string into clean badge label & explanation text
  const parseVerdictInfo = (rawVerdict, fallbackText = "") => {
    if (!rawVerdict) {
      return { label: "VERDICT: INSUFFICIENT DATA", type: "unclear", reason: fallbackText };
    }

    const str = String(rawVerdict).trim();

    // 1. Locate all VERDICT occurrences to extract candidate verdict line
    const verdictMatches = [...str.matchAll(/VERDICT:\s*([^\n\r]+)/gi)];
    let lastVerdictLine = "";
    if (verdictMatches.length > 0) {
      lastVerdictLine = verdictMatches[verdictMatches.length - 1][1].trim();
    } else {
      lastVerdictLine = str.split("\n")[0].trim();
    }

    const upperText = (lastVerdictLine + " " + str).toUpperCase();

    // 2. Classify strictly into the 4 canonical categories:
    // VERDICT: PARTIAL, VERDICT: CONFLICT DETECTED, VERDICT: CONCORDANT, VERDICT: INSUFFICIENT DATA
    let label = "VERDICT: PARTIAL";
    let type = "amber";

    if (
      upperText.includes("CONFLICT") ||
      upperText.includes("CONTRADICT") ||
      upperText.includes("INCONSISTENT") ||
      upperText.includes("DISCORDANT")
    ) {
      label = "VERDICT: CONFLICT DETECTED";
      type = "red";
    } else if (
      upperText.includes("PARTIAL") ||
      upperText.includes("PARTIALLY")
    ) {
      label = "VERDICT: PARTIAL";
      type = "amber";
    } else if (
      upperText.includes("CONCORDANT") ||
      upperText.includes("CONSISTENT") ||
      upperText.includes("AGREE") ||
      upperText.includes("MATCH")
    ) {
      label = "VERDICT: CONCORDANT";
      type = "green";
    } else if (
      upperText.includes("INSUFFICIENT") ||
      upperText.includes("UNCLEAR") ||
      upperText.includes("NO DATA") ||
      upperText.includes("NOT ENOUGH")
    ) {
      label = "VERDICT: INSUFFICIENT DATA";
      type = "unclear";
    } else {
      // Fallback cleanly to VERDICT: PARTIAL
      label = "VERDICT: PARTIAL";
      type = "amber";
    }

    // 3. Strip all verdict tags (e.g., 'VERDICT: PARTIAL -', 'VERDICT: CONFLICT', 'REASON:')
    let cleanText = str;
    cleanText = cleanText
      .replace(/VERDICT:\s*[A-Za-z_\s]+(?:\s*-\s*|\s*:\s*|\n|$)/gi, "")
      .replace(/(?:REASON|EXPLANATION):\s*/gi, "")
      .trim();

    if (!cleanText) {
      cleanText = fallbackText || str;
    }

    return { label, type, reason: cleanText };
  };

  // Format Verdict Badge
  const renderVerdictBadge = (verdict, fallbackText = "") => {
    const { label, type } = parseVerdictInfo(verdict, fallbackText);

    if (type === "red") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ff4757]/15 border border-[#ff4757]/40 text-[#ff4757] font-mono font-bold text-xs">
          <XCircle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "green") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#2dd4ce]/15 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono font-bold text-xs">
          <CheckCircle2 className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else if (type === "unclear") {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#8fa89b]/15 border border-[#8fa89b]/40 text-[#8fa89b] font-mono font-bold text-xs">
          <HelpCircle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#e8a33d]/15 border border-[#e8a33d]/40 text-[#e8a33d] font-mono font-bold text-xs">
          <AlertTriangle className="w-3.5 h-3.5" />
          {label}
        </span>
      );
    }
  };

  // Centralized URL synchronization and navigation
  const navigate = (path, replace = false) => {
    if (typeof window !== "undefined") {
      if (replace) {
        window.history.replaceState({}, "", path);
      } else {
        window.history.pushState({}, "", path);
      }
    }
    syncRouteFromPath(path);
  };

  const syncRouteFromPath = (path) => {
    const rawPath = path || (typeof window !== "undefined" ? window.location.pathname : "/");
    const cleanPath = (rawPath || "/").toLowerCase();

    if (cleanPath.startsWith("/reset-password")) {
      setScreen("reset-password");
      return;
    }

    if (cleanPath.startsWith("/admin")) {
      if (loading) return; // Wait for auth token validation
      if (!isAuthenticated || !user?.is_admin) {
        // Access Denied: Send back to login screen
        if (typeof window !== "undefined") {
          window.history.replaceState({}, "", "/");
        }
        setScreen("landing");
        openAuth("login");
        return;
      }
      setScreen("admin");
      return;
    }

    if (cleanPath.startsWith("/dashboard")) {
      if (loading) return;
      if (!isAuthenticated) {
        if (typeof window !== "undefined") {
          window.history.replaceState({}, "", "/");
        }
        setScreen("landing");
        openAuth("login");
        return;
      }
      setScreen("dashboard");
      return;
    }

    if (cleanPath.startsWith("/upload")) {
      if (loading) return;
      if (!isAuthenticated) {
        if (typeof window !== "undefined") {
          window.history.replaceState({}, "", "/");
        }
        setScreen("landing");
        openAuth("login");
        return;
      }
      setScreen("upload");
      return;
    }

    setScreen("landing");
  };

  // Browser navigation popstate listener
  useEffect(() => {
    const handlePopState = () => {
      syncRouteFromPath(window.location.pathname);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [isAuthenticated, user?.is_admin, loading]);

  // Initial and reactive route synchronization
  useEffect(() => {
    if (!loading) {
      syncRouteFromPath(window.location.pathname);
    }
  }, [loading, isAuthenticated, user?.is_admin]);

  // Centralized Navigation Gate: If 0 papers, route to upload; otherwise dashboard
  const navigateByPapers = async (overridePapers = null) => {
    const list = overridePapers !== null ? overridePapers : await loadPapers();
    if (!list || list.length === 0) {
      navigate("/upload");
    } else {
      navigate("/dashboard");
    }
  };

  // Navigation handlers with Auth Gate
  const handleStartWorkflow = () => {
    if (isAuthenticated) {
      if (user?.is_admin) {
        navigate("/admin");
      } else {
        navigateByPapers();
      }
    } else {
      openAuth("login", () => navigateByPapers());
    }
  };

  const handleGoWorkspace = () => {
    if (isAuthenticated) {
      if (user?.is_admin) {
        navigate("/admin");
      } else {
        navigateByPapers();
      }
    } else {
      openAuth("login", () => navigateByPapers());
    }
  };

  return (
    <>
      <LoginModal
        isOpen={authModalOpen}
        defaultTab={authModalTab}
        onClose={() => {
          setAuthModalOpen(false);
          setPendingAction(null);
        }}
        onSuccess={async (isAdminLogin, loggedInUser) => {
          setAuthModalOpen(false);
          const isAdm = Boolean(isAdminLogin ?? loggedInUser?.is_admin ?? user?.is_admin);
          if (isAdm) {
            navigate("/admin");
            return;
          }
          const action = pendingAction;
          setPendingAction(null);
          if (action) {
            await action();
          } else {
            navigate("/dashboard");
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

      {screen === "reset-password" && (
        <ResetPasswordPage
          onGoLogin={() => {
            navigate("/");
            openAuth("login");
          }}
        />
      )}

      {screen === "admin" && (
        <AdminDashboard
          onGoWorkspace={() => navigate("/dashboard")}
          onLogout={() => {
            logout();
            navigate("/");
          }}
        />
      )}

      {screen === "upload" && (
        <UploadPage
          onContinue={async (newDoc) => {
            const updated = await loadPapers();
            if (newDoc && newDoc.filename) {
              openPdf(newDoc.filename, {
                id: newDoc.paper_id || newDoc.id,
                filename: newDoc.filename,
                title: newDoc.title,
              });
            } else if (updated && updated.length > 0) {
              const latest = updated[updated.length - 1];
              openPdf(latest.filename, latest);
            }
            navigate("/dashboard");
          }}
          onBack={() => navigate("/")}
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
                  onClick={() => navigate("/")}
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
                {user?.is_admin && (
                  <button
                    onClick={() => navigate("/admin")}
                    className="hidden sm:inline-flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded-xl border border-[#2dd4ce]/40 text-[#2dd4ce] bg-[#2dd4ce]/10 hover:bg-[#2dd4ce]/20 transition cursor-pointer font-bold"
                  >
                    <Shield className="w-3.5 h-3.5" />
                    <span>ADMIN CONSOLE</span>
                  </button>
                )}

                <button
                  onClick={() => navigate("/upload")}
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
                      onClick={() => {
                        logout();
                        navigate("/");
                      }}
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
              
              {/* Left Column: Interactive PDF Viewer or Clinical Standby Placeholder */}
              <div className="lg:col-span-6 h-[880px] sticky top-20">
                {selectedPdfUrl ? (
                  <PdfViewer
                    fileUrl={selectedPdfUrl}
                    filename={selectedPaper?.filename || "source.pdf"}
                    paperId={selectedPaper?.id || selectedPaper?.paper_id}
                    activeCitation={activeCitation}
                    onClose={() => {
                      setSelectedPdfUrl(null);
                      setActiveCitation(null);
                    }}
                  />
                ) : (
                  <div className="h-full rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-8 flex flex-col justify-between shadow-2xl relative overflow-hidden backdrop-blur-xl">
                    <div className="absolute -top-24 -left-24 w-72 h-72 bg-[#2dd4ce]/5 rounded-full blur-3xl pointer-events-none" />
                    <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-[#16323b]/30 rounded-full blur-3xl pointer-events-none" />

                    {/* Top status header */}
                    <div className="flex items-center justify-between border-b border-[#16323b] pb-4 relative z-10">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#8fa89b]"></span>
                        <span className="font-mono text-xs font-bold text-[#8fa89b] uppercase tracking-wider">
                          CLINICAL EVIDENCE VIEWER • STANDBY
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-[#8fa89b] px-2 py-0.5 rounded bg-white/5 border border-white/10">
                        AIR-GAPPED READER
                      </span>
                    </div>

                    {/* Center Callout */}
                    <div className="my-auto text-center max-w-md mx-auto py-8 relative z-10">
                      <div className="w-16 h-16 rounded-2xl bg-[#0b1e25] border border-[#2dd4ce]/30 mx-auto flex items-center justify-center text-[#2dd4ce] mb-5 shadow-lg shadow-[#2dd4ce]/10">
                        <BookOpen className="w-8 h-8 stroke-[1.5]" />
                      </div>
                      <h3 className="text-lg font-bold text-white mb-2 tracking-tight">
                        No Document Selected
                      </h3>
                      <p className="text-xs text-[#8fa89b] leading-relaxed mb-6">
                        Select a verified trial paper below, or click{" "}
                        <span className="text-[#2dd4ce] font-mono font-bold">"View Anchor →"</span>{" "}
                        on any citation in the evidence chat to inspect original PDF pages with bounding box highlight overlays.
                      </p>

                      {papers.length > 0 ? (
                        <div className="text-left bg-[#060b10] p-4 rounded-xl border border-[#16323b] space-y-2">
                          <div className="flex items-center justify-between text-[11px] font-mono text-[#8fa89b] border-b border-white/5 pb-1.5">
                            <span>AVAILABLE LITERATURE ({papers.length})</span>
                            <span className="text-[#2dd4ce]">Click to load</span>
                          </div>
                          <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1 no-scrollbar">
                            {papers.map((p) => (
                              <button
                                key={p.id}
                                onClick={() => openPdf(p.filename, p)}
                                className="w-full text-left p-2.5 rounded-lg bg-[#0b1820] hover:bg-[#0e222d] border border-white/5 hover:border-[#2dd4ce]/40 transition flex items-center justify-between group cursor-pointer"
                              >
                                <div className="truncate pr-2">
                                  <div className="text-xs font-medium text-white group-hover:text-[#2dd4ce] truncate" title={p.detected_title || p.title}>
                                    {p.detected_title || p.title || p.filename}
                                  </div>
                                  <div className="text-[10px] font-mono text-[#8fa89b] truncate">
                                    File: {p.filename}
                                  </div>
                                </div>
                                <ChevronRight className="w-4 h-4 text-[#8fa89b] group-hover:text-[#2dd4ce] shrink-0" />
                              </button>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setScreen("upload")}
                          className="px-5 py-2.5 rounded-xl bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs inline-flex items-center gap-2 shadow-lg shadow-[#2dd4ce]/20 transition cursor-pointer"
                        >
                          <Plus className="w-4 h-4" />
                          <span>Upload Biomedical Paper</span>
                        </button>
                      )}
                    </div>

                    {/* Bottom Telemetry */}
                    <div className="border-t border-[#16323b] pt-3 flex items-center justify-between text-[10px] font-mono text-[#8fa89b] relative z-10">
                      <span>PDF.JS HIGH-DPI CANVAS ENGINE</span>
                      <span>NORMALIZED BBOX ANCHORING ACTIVE</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: LangGraph Audit Intelligence Panel */}
              <div className="lg:col-span-6 space-y-6 transition-all duration-300 w-full">
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
                        className={`text-xs font-mono p-3 rounded-xl border flex items-start gap-2.5 ${
                          uploadFeedback.type === "success"
                            ? "bg-[#2dd4ce]/10 text-[#2dd4ce] border-[#2dd4ce]/30"
                            : "bg-[#ff4757]/10 text-[#ff4757] border-[#ff4757]/40 shadow-lg shadow-[#ff4757]/10"
                        }`}
                      >
                        {uploadFeedback.type === "error" ? (
                          <XCircle className="w-4 h-4 shrink-0 mt-0.5 text-[#ff4757]" />
                        ) : (
                          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-[#2dd4ce]" />
                        )}
                        <div>
                          {uploadFeedback.isRejection && (
                            <div className="font-bold uppercase tracking-wider mb-0.5 text-[10.5px] text-[#ff4757]">
                              BIOMEDICAL DOMAIN GATE REJECTION [HTTP 422]
                            </div>
                          )}
                          <div className="text-white text-xs leading-relaxed">{uploadFeedback.text}</div>
                        </div>
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
                    {papers.length === 0 ? (
                      <div className="col-span-2 p-6 rounded-xl border border-dashed border-[#16323b] bg-[#060b10] text-center">
                        <FileText className="w-8 h-8 text-[#8fa89b] mx-auto mb-2 opacity-50" />
                        <p className="text-xs text-[#8fa89b] mb-3">
                          No active verified papers in your workspace.
                        </p>
                        <button
                          onClick={() => setScreen("upload")}
                          className="px-3.5 py-1.5 rounded-lg bg-[#2dd4ce]/10 hover:bg-[#2dd4ce]/20 border border-[#2dd4ce]/30 text-[#2dd4ce] text-xs font-mono font-bold inline-flex items-center gap-1.5 cursor-pointer"
                        >
                          <Plus className="w-3.5 h-3.5" />
                          <span>Upload Literature</span>
                        </button>
                      </div>
                    ) : (
                      papers.map((paper, idx) => {
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
                                <span className="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-[#2dd4ce]/10 text-[#2dd4ce] border border-[#2dd4ce]/30">
                                  VERIFIED
                                </span>
                              </div>
                              <h3
                                className="text-xs font-bold text-white line-clamp-2 leading-snug mb-1"
                                title={paper.detected_title || paper.title || paper.filename}
                              >
                                {paper.detected_title || paper.title || paper.filename}
                              </h3>
                            </div>

                            <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10.5px] font-mono text-[#8fa89b]">
                              <span className="truncate max-w-[130px]" title={paper.filename}>
                                📄 {paper.filename}
                              </span>
                              <span className="text-[#2dd4ce] hover:underline flex items-center gap-0.5">
                                <span>Inspect in Reader</span>
                                <ChevronRight className="w-3 h-3" />
                              </span>
                            </div>
                          </div>
                        );
                      })
                    )}
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
                    onSelectSource={(c) => {
                      const fn = c?.filename || c?.doc_id || selectedPaper?.filename;
                      openPdf(fn, null, c);
                    }}
                    onOpenPdf={(filename, c) => {
                      const fn = filename || c?.filename || c?.doc_id || selectedPaper?.filename;
                      openPdf(fn, null, c);
                    }}
                    onSelectCitation={(c) => {
                      const fn = c?.filename || c?.doc_id || selectedPaper?.filename;
                      openPdf(fn, null, c);
                    }}
                    onOpenAuth={(tab) => openAuth(tab)}
                    papers={papers}
                    selectedPaper={selectedPaper}
                    onSelectPaper={(p) => {
                      if (p && p.filename) {
                        openPdf(p.filename, p);
                      }
                    }}
                  />
                </div>

                {/* SECTION 4: CROSS-TRIAL METRIC MATRIX */}
                <CrossTrialMatrix
                  papers={papers}
                  onOpenPdf={(fn, c) => openPdf(fn, null, c)}
                />

                {/* SECTION 5: COMPARE ACROSS PAPERS (Conflict Matrix) */}
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

                  <form onSubmit={handleCompare} className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <label className="text-[10.5px] font-mono text-[#8fa89b] uppercase tracking-wider flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#e8a33d]"></span>
                          Paper 1 (Reference Trial)
                        </label>
                        <select
                          value={comparePaper1Id || (papers.length > 0 ? (papers[0].id || papers[0].paper_id) : "")}
                          onChange={(e) => setComparePaper1Id(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl bg-[#060b10] border border-[#16323b] text-[#d8f3f0] text-xs focus:border-[#e8a33d] focus:outline-none"
                        >
                          {papers.map((p) => {
                            const title = p.detected_title || p.title || p.filename;
                            const truncatedTitle = title.length > 38 ? `${title.slice(0, 35)}...` : title;
                            return (
                              <option key={p.id || p.paper_id} value={p.id || p.paper_id} title={`${title} (${p.filename})`}>
                                #{p.id || p.paper_id}: {truncatedTitle}
                              </option>
                            );
                          })}
                        </select>
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10.5px] font-mono text-[#8fa89b] uppercase tracking-wider flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4ce]"></span>
                          Paper 2 (Comparator Trial)
                        </label>
                        <select
                          value={comparePaper2Id || (papers.length > 1 ? (papers[1].id || papers[1].paper_id) : (papers[0]?.id || papers[0]?.paper_id || ""))}
                          onChange={(e) => setComparePaper2Id(e.target.value)}
                          className="w-full px-3 py-2 rounded-xl bg-[#060b10] border border-[#16323b] text-[#d8f3f0] text-xs focus:border-[#e8a33d] focus:outline-none"
                        >
                          {papers.map((p) => {
                            const title = p.detected_title || p.title || p.filename;
                            const truncatedTitle = title.length > 38 ? `${title.slice(0, 35)}...` : title;
                            return (
                              <option key={p.id || p.paper_id} value={p.id || p.paper_id} title={`${title} (${p.filename})`}>
                                #{p.id || p.paper_id}: {truncatedTitle}
                              </option>
                            );
                          })}
                        </select>
                      </div>
                    </div>

                    <div className="flex gap-2">
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
                        className="px-5 py-2.5 rounded-xl bg-[#e8a33d] hover:bg-[#d8932d] text-[#060b10] font-bold text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-md shadow-[#e8a33d]/20 shrink-0"
                      >
                        {comparing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                        <span>Cross-Examine</span>
                      </button>
                    </div>
                  </form>

                  {compareResult && (() => {
                    const parsed = parseVerdictInfo(compareResult.verdict, compareResult.analysis);
                    return (
                      <div className="p-4 rounded-xl bg-[#060b10] border border-[#16323b] space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs text-[#8fa89b] uppercase">Arbitration Verdict:</span>
                          {renderVerdictBadge(compareResult.verdict, compareResult.analysis)}
                        </div>
                        <div className="text-xs text-[#d8f3f0] leading-relaxed">
                          {renderFormattedReason(parsed.reason)}
                        </div>
                      </div>
                    );
                  })()}
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
                          value={integrityPaperId || selectedPaper?.id || ""}
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

                  {integrityResult && (() => {
                    const parsed = parseVerdictInfo(integrityResult.verdict, integrityResult.explanation);
                    return (
                      <div className="p-4 rounded-xl bg-[#060b10] border border-[#16323b] space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs text-[#8fa89b] uppercase">Integrity Verdict:</span>
                          {renderVerdictBadge(integrityResult.verdict, integrityResult.explanation)}
                        </div>
                        <div className="text-xs text-[#d8f3f0] leading-relaxed">
                          {renderFormattedReason(parsed.reason)}
                        </div>
                      </div>
                    );
                  })()}
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