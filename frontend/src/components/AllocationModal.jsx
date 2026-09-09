import React, { useState } from "react";
import { X, CheckCircle2, Shield, Sparkles, Building, Mail, FileText, ArrowRight, UploadCloud } from "lucide-react";
import { RESEARCH_PAPERS } from "../data/products";

export default function AllocationModal({ initialProduct, onClose }) {
  const [selectedPaper, setSelectedPaper] = useState(initialProduct ? initialProduct.id : RESEARCH_PAPERS[0].id);
  const [pipelineMode, setPipelineMode] = useState("langgraph");
  const [institution, setInstitution] = useState("");
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const currentPaper = RESEARCH_PAPERS.find((p) => p.id === selectedPaper) || RESEARCH_PAPERS[0];

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-2xl bg-[#081f16] border border-[#d4af37]/40 rounded-3xl shadow-2xl overflow-hidden my-8 text-white">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#05140e] border-b border-white/10">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#d4af37]" />
            <span className="font-mono text-xs text-[#d4af37] font-semibold uppercase tracking-wider">
              LAUNCH LITERATURE WORKSPACE
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        {!submitted ? (
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-5">
            <div className="space-y-1">
              <h3 className="text-xl font-bold text-white">Configure Document Ingestion Session</h3>
              <p className="text-xs text-[#a2b8ad]">
                Upload your research PDFs or select a pre-indexed clinical trial corpus to begin multi-agent verification.
              </p>
            </div>

            {/* Document Selection */}
            <div className="space-y-2">
              <label className="text-xs font-mono text-[#8fa89b] uppercase">Select Research Paper / Corpus</label>
              <select
                value={selectedPaper}
                onChange={(e) => setSelectedPaper(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-[#05140e] border border-white/20 text-white font-mono text-sm focus:border-[#d4af37] focus:outline-none"
              >
                {RESEARCH_PAPERS.map((p) => (
                  <option key={p.id} value={p.id} className="bg-[#05140e] text-white">
                    {p.name} ({p.sampleSize} • {p.pValue} • {p.doi})
                  </option>
                ))}
              </select>
            </div>

            {/* Pipeline Configuration */}
            <div className="space-y-2">
              <label className="text-xs font-mono text-[#8fa89b] uppercase">Verification Depth</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setPipelineMode("hybrid")}
                  className={`p-3 rounded-xl text-left border transition-all ${
                    pipelineMode === "hybrid"
                      ? "bg-[#0d271c] border-[#d4af37] text-white"
                      : "bg-[#05140e] border-white/10 text-[#8fa89b] hover:border-white/20"
                  }`}
                >
                  <div className="font-mono text-xs font-bold text-[#d4af37]">BM25 + pgvector Hybrid</div>
                  <div className="text-[11px] text-[#adc2b6] mt-0.5">High-speed closed-corpus retrieval & bounding-box sync.</div>
                </button>

                <button
                  type="button"
                  onClick={() => setPipelineMode("langgraph")}
                  className={`p-3 rounded-xl text-left border transition-all ${
                    pipelineMode === "langgraph"
                      ? "bg-[#0d271c] border-[#d4af37] text-white"
                      : "bg-[#05140e] border-white/10 text-[#8fa89b] hover:border-white/20"
                  }`}
                >
                  <div className="font-mono text-xs font-bold text-[#d4af37]">Full LangGraph Multi-Agent</div>
                  <div className="text-[11px] text-[#adc2b6] mt-0.5">Statistical p-value recalculation & conflict matrix.</div>
                </button>
              </div>
            </div>

            {/* Institution & Contact Info */}
            <div className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-[#8fa89b] uppercase">Research Institution / University</label>
                <div className="relative">
                  <Building className="w-4 h-4 text-[#8fa89b] absolute left-3.5 top-3" />
                  <input
                    type="text"
                    required
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    placeholder="e.g. Harvard Medical School, Max Planck Institute"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#05140e] border border-white/20 text-white text-xs placeholder:text-[#5d7568] focus:border-[#d4af37] focus:outline-none"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-[#8fa89b] uppercase">Investigator / Principal Author Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#8fa89b] absolute left-3.5 top-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="investigator@institution.edu"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#05140e] border border-white/20 text-white text-xs placeholder:text-[#5d7568] focus:border-[#d4af37] focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Summary Pill */}
            <div className="p-3.5 rounded-xl bg-[#05140e] border border-white/10 flex items-center justify-between text-xs font-mono">
              <span className="text-[#8fa89b]">Corpus: {currentPaper.name}</span>
              <span className="text-[#d4af37] font-semibold">Dual-Pane Sync Ready</span>
            </div>

            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-mono text-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#d4af37] to-[#b89228] text-[#07150f] font-bold text-xs flex items-center gap-2 cursor-pointer shadow-lg shadow-[#d4af37]/20"
              >
                <span>Launch Dual-Pane Workspace</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        ) : (
          <div className="p-8 text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center mx-auto text-emerald-400">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-bold text-white">Dual-Pane Workspace Initialized</h3>
            <p className="text-xs text-[#a2b8ad] max-w-md mx-auto leading-relaxed">
              Your closed-corpus index has been generated for <strong>{currentPaper.name}</strong> under affiliation with <strong>{institution}</strong>. The secure link has been transmitted to <strong>{email}</strong>.
            </p>
            <div className="p-4 rounded-xl bg-[#05140e] border border-white/10 font-mono text-xs text-[#d4af37] max-w-xs mx-auto">
              SESSION ID: #VER-SESSION-{Math.floor(100000 + Math.random() * 900000)}
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl bg-[#d4af37] text-[#07150f] font-bold text-xs cursor-pointer font-mono"
            >
              Return to Explorer
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
