import React, { useState, useRef, useEffect } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  ShieldCheck,
  Cpu,
  Layers,
  Check,
  Loader2,
  XCircle,
  User,
  Shield
} from "lucide-react";
import { uploadPaper, fetchPapers } from "./services/api";
import { useAuth } from "./AuthContext";

export default function UploadPage({ onContinue, onBack, onOpenAuth }) {
  const { isAuthenticated, user } = useAuth();
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [parseStages, setParseStages] = useState([]);
  const [uploadedResult, setUploadedResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [rejectDetails, setRejectDetails] = useState(null);
  const [existingPapers, setExistingPapers] = useState([]);

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchPapers()
      .then((papers) => setExistingPapers(papers))
      .catch(() => {});
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (selectedFile) => {
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Please select a valid biomedical PDF document (.pdf).");
      return;
    }
    setErrorMessage(null);
    setRejectDetails(null);
    setFile(selectedFile);
    if (!title) {
      const cleanName = selectedFile.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ");
      setTitle(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      if (onOpenAuth) onOpenAuth("login");
      return;
    }

    if (!file) {
      setErrorMessage("Please select a PDF file before uploading.");
      return;
    }
    if (!title.trim()) {
      setErrorMessage("Please specify a document title for semantic indexing.");
      return;
    }

    setErrorMessage(null);
    setRejectDetails(null);
    setUploading(true);
    setParseStages([
      "Uploading binary payload to VeriNexa air-gapped pipeline...",
      "Consulting on-device Llama 3.2:1B biomedical validation gate...",
      "Decomposing layout into Abstract Syntax Tree (AST)...",
      "Generating dense vector embeddings via all-MiniLM-L6-v2 (pgvector)...",
      "Indexing BM25 lexical token inverted index...",
    ]);

    try {
      const result = await uploadPaper(file, title.trim());
      setUploadedResult(result);
      fetchPapers().then((p) => setExistingPapers(p));
    } catch (err) {
      if (err.statusCode === 422 || err.isRejected) {
        setErrorMessage(err.message || "Document rejected: Not a biomedical research paper.");
        setRejectDetails(err.details || "Non-biomedical content detected.");
      } else {
        setErrorMessage(err.message || "Document ingestion failed.");
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060b10] text-[#f4f7f5] flex flex-col font-sans selection:bg-[#2dd4ce]/25 selection:text-[#2dd4ce]">
      {/* Header Bar */}
      <header className="border-b border-[#16323b] bg-[#060b10]/95 backdrop-blur-xl px-6 py-4 sticky top-0 z-30 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-xs font-mono text-[#8fa89b] hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4 text-[#2dd4ce]" />
            <span>RETURN TO OVERVIEW</span>
          </button>

          <div className="flex items-center gap-3">
            <span className="font-bold tracking-[0.2em] text-sm text-white uppercase">
              VeriNexa
            </span>
            <span className="hidden sm:inline text-[10.5px] font-mono text-[#2dd4ce] px-2 py-0.5 rounded bg-[#2dd4ce]/10 border border-[#2dd4ce]/30">
              DOCUMENT INGESTION GATE
            </span>
          </div>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-[#0b1e25] border border-[#2dd4ce]/40 text-[#2dd4ce] flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" />
                <span className="truncate max-w-[120px]">{user?.email}</span>
              </span>
            ) : (
              <button
                onClick={() => onOpenAuth("login")}
                className="text-xs font-mono px-3 py-1 rounded bg-[#2dd4ce] text-[#060b10] font-bold cursor-pointer"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Upload Body */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-12 flex flex-col items-center">
        {/* Step Indicator */}
        <div className="w-full max-w-lg mb-8">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="h-1 rounded-full mb-2 bg-[#2dd4ce]" />
              <p className="text-xs font-mono font-bold text-[#2dd4ce]">Step 1 of 2</p>
              <p className="text-xs text-[#8fa89b]">Biomedical Gate & Ingestion</p>
            </div>
            <div>
              <div className="h-1 rounded-full mb-2 bg-[#16323b]" />
              <p className="text-xs font-mono font-bold text-[#8fa89b]">Step 2 of 2</p>
              <p className="text-xs text-[#8fa89b]">Interactive Audit Workspace</p>
            </div>
          </div>
        </div>

        {/* Title Header */}
        <div className="text-center max-w-xl mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0b1e25] border border-[#2dd4ce]/30 mb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-[#2dd4ce]" />
            <span className="text-[10px] font-mono tracking-widest text-[#2dd4ce] uppercase font-bold">
              ZERO-HALLUCINATION BIOMEDICAL GATE
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Upload Literature Dossier
          </h1>
          <p className="text-xs sm:text-sm text-[#adc2b6] mt-2 leading-relaxed">
            VeriNexa screens incoming research PDFs with on-device Llama 3.2:1B. Non-biomedical documents are rejected via HTTP 422 to preserve vector index integrity.
          </p>
        </div>

        {/* Upload Form Card */}
        <div className="w-full max-w-2xl rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-6 sm:p-8 shadow-2xl shadow-black/80 relative">
          <form onSubmit={handleUploadSubmit} className="space-y-6">
            {/* Drag & Drop Area */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className={`relative rounded-2xl border-2 border-dashed p-8 sm:p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 ${
                dragActive
                  ? "border-[#2dd4ce] bg-[#2dd4ce]/10 scale-[1.01]"
                  : file
                  ? "border-[#2dd4ce]/70 bg-[#2dd4ce]/5"
                  : "border-[#16323b] hover:border-[#2dd4ce]/40 bg-[#060b10]"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                onChange={(e) => e.target.files && e.target.files[0] && handleFileSelected(e.target.files[0])}
                className="hidden"
              />

              <div className="w-12 h-12 rounded-2xl bg-[#0e272b] border border-[#2dd4ce]/30 flex items-center justify-center mb-3 text-[#2dd4ce] shadow-lg shadow-[#2dd4ce]/10">
                <UploadCloud className="w-6 h-6" />
              </div>

              {file ? (
                <div className="space-y-1">
                  <div className="flex items-center justify-center gap-2 text-white font-bold text-sm">
                    <FileText className="w-4 h-4 text-[#2dd4ce]" />
                    <span className="truncate max-w-[320px]">{file.name}</span>
                  </div>
                  <p className="text-xs font-mono text-[#2dd4ce]">
                    {(file.size / 1024 / 1024).toFixed(2)} MB • Ready for Ingestion
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-sm font-bold text-white">
                    Drop biomedical PDF here or <span className="text-[#2dd4ce] underline">browse</span>
                  </p>
                  <p className="text-xs text-[#8fa89b]">
                    Clinical trials, systematic reviews, or meta-analyses (.pdf only)
                  </p>
                </div>
              )}
            </div>

            {/* Document Title Input */}
            <div className="space-y-1.5 text-left">
              <label className="block text-xs font-mono text-[#8fa89b] uppercase">
                Document Semantic Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. SGLT2 Inhibitor Glycemic and Renal Outcomes Meta-Analysis"
                className="w-full px-4 py-3 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition-colors"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] text-[#060b10] font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-[#2dd4ce]/20 hover:brightness-110 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying & Indexing Document...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Ingest & Verify Literature →</span>
                </>
              )}
            </button>
          </form>

          {/* Progress / Parsing Feedback */}
          {uploading && (
            <div className="mt-6 p-4 rounded-xl bg-[#060b10] border border-[#2dd4ce]/30 space-y-2 text-left">
              <div className="flex items-center gap-2 text-xs font-mono text-[#2dd4ce] font-bold">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>ACTIVE DECOMPOSITION PIPELINE</span>
              </div>
              <div className="space-y-1 pl-4">
                {parseStages.map((stage, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-[11px] font-mono text-[#8fa89b]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#2dd4ce]"></span>
                    <span>{stage}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error / HTTP 422 Rejection Feedback */}
          {errorMessage && (
            <div className="mt-6 p-4 rounded-xl bg-[#ff4757]/10 border border-[#ff4757]/40 text-left space-y-2">
              <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#ff4757]">
                <XCircle className="w-4 h-4 shrink-0" />
                <span>DOCUMENT REJECTED BY BIOMEDICAL GATE [HTTP 422]</span>
              </div>
              <p className="text-xs text-white leading-relaxed">{errorMessage}</p>
              {rejectDetails && (
                <div className="p-2.5 rounded-lg bg-[#060b10] border border-[#ff4757]/20 text-[11px] font-mono text-[#ff4757]">
                  {rejectDetails}
                </div>
              )}
            </div>
          )}

          {/* Success Card */}
          {uploadedResult && (
            <div className="mt-6 p-5 rounded-xl bg-[#2dd4ce]/10 border border-[#2dd4ce]/40 text-left space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-mono font-bold text-[#2dd4ce]">
                  <CheckCircle2 className="w-4 h-4 text-[#2dd4ce]" />
                  <span>DOCUMENT VERIFIED & INDEXED (PAPER #{uploadedResult.paper_id})</span>
                </div>
                <span className="text-[10px] font-mono text-[#060b10] bg-[#2dd4ce] px-2 py-0.5 rounded font-bold">
                  READY FOR AUDIT
                </span>
              </div>
              <p className="text-xs text-white">
                Title: <strong className="text-[#2dd4ce]">{uploadedResult.title}</strong>
              </p>
              <button
                onClick={onContinue}
                className="w-full py-2.5 rounded-lg bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md shadow-[#2dd4ce]/20"
              >
                <span>Proceed to Dual-Pane Workspace</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Existing Loaded Papers Chips */}
        {existingPapers.length > 0 && (
          <div className="w-full max-w-2xl mt-8 text-left">
            <p className="text-xs font-mono uppercase tracking-wider text-[#8fa89b] mb-2">
              // ACTIVE LITERATURE CORPUS ({existingPapers.length} PAPERS)
            </p>
            <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto no-scrollbar">
              {existingPapers.map((p) => (
                <span
                  key={p.id}
                  className="px-3 py-1.5 rounded-lg bg-[#08131b] border border-[#16323b] text-xs font-mono text-[#adc2b6] flex items-center gap-1.5"
                >
                  <span className="text-[#2dd4ce]">✓</span>
                  <span className="truncate max-w-[220px]">{p.filename}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}