import React, { useState } from "react";
import {
  UploadCloud,
  Layers,
  GitBranch,
  SplitSquareVertical,
  CheckCircle,
  Search,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Award,
  FileCheck2,
  Database
} from "lucide-react";
import { RESEARCH_PAPERS, WORKFLOW_STEPS } from "../data/products";

export default function TrustSection({ onSelectBatch, onOpenCoa }) {
  const [searchCode, setSearchCode] = useState("paper-01");
  const [selectedPaperData, setSelectedPaperData] = useState(RESEARCH_PAPERS[0]);
  const [lookupFeedback, setLookupFeedback] = useState(null);

  const handleSearch = (code) => {
    const clean = code.trim().toLowerCase();
    setSearchCode(clean);
    const found = RESEARCH_PAPERS.find(
      (p) =>
        p.id.toLowerCase() === clean ||
        p.doi.toLowerCase().includes(clean) ||
        p.name.toLowerCase().includes(clean)
    );
    if (found) {
      setSelectedPaperData(found);
      setLookupFeedback({ status: "success", text: "Paper Indexed & Multi-Agent Verified • All Claims Traceable" });
    } else {
      setLookupFeedback({ status: "error", text: "Paper identifier not in current local index. Showing sample audit." });
    }
  };

  const workflowIcons = [UploadCloud, Layers, GitBranch, SplitSquareVertical];

  return (
    <section id="workflow" className="py-24 relative overflow-hidden bg-[#05110c] border-t border-b border-white/5">
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-0 w-[500px] h-[500px] bg-emerald-900/10 blur-[130px] pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-[450px] h-[450px] bg-[#d4af37]/5 blur-[120px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0e271e] border border-[#d4af37]/30 mb-3">
            <Award className="w-3.5 h-3.5 text-[#d4af37]" />
            <span className="text-[11px] font-mono tracking-widest text-[#d4af37] uppercase">
              AUTONOMOUS 4-STEP VERIFICATION PIPELINE
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            How it{" "}
            <span className="font-serif italic font-normal text-[#d4af37]">
              works
            </span>
            .
          </h2>
          <p className="mt-4 text-[#a6bcb1] text-base sm:text-lg leading-relaxed">
            From raw, unstructured scientific PDFs to verified p-values and real-time bounding-box claim synchronization. Here is our exact multi-agent architecture.
          </p>
        </div>

        {/* Two-Column Architecture */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch mb-16">
          
          {/* Left Side: Explanatory Card Paired with Laboratory Imagery */}
          <div className="lg:col-span-5 flex flex-col justify-between rounded-3xl bg-[#091f16]/90 border border-white/10 p-6 sm:p-8 relative overflow-hidden shadow-2xl">
            <div className="space-y-6 z-10">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div>
                  <span className="text-xs font-mono text-[#d4af37] tracking-wider uppercase block">
                    CLOSED-CORPUS ARCHITECTURE
                  </span>
                  <h3 className="text-xl font-bold text-white mt-1">
                    Rigorous Verification Standards
                  </h3>
                </div>
                <div className="w-8 h-8 rounded-full bg-[#d4af37]/10 border border-[#d4af37]/30 flex items-center justify-center">
                  <FileCheck2 className="w-4 h-4 text-[#d4af37]" />
                </div>
              </div>

              <p className="text-sm text-[#b2c8be] leading-relaxed">
                By enforcing hard closed-corpus retrieval boundaries, our system operates strictly on your uploaded files. It cross-checks methodology claims against results tables to eliminate hallucinations and flag statistical incongruities.
              </p>

              {/* Architecture Tech Badges */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <span className="text-xs font-bold text-white font-mono block">PostgreSQL pgvector</span>
                  <span className="text-[11px] text-[#8fa89b]">1536-dim Embeddings</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <span className="text-xs font-bold text-white font-mono block">LangGraph Multi-Agent</span>
                  <span className="text-[11px] text-[#8fa89b]">Stateful Graph Nodes</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <span className="text-xs font-bold text-white font-mono block">BM25 Lexical Match</span>
                  <span className="text-[11px] text-[#8fa89b]">Exact Keyword Recall</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <span className="text-xs font-bold text-white font-mono block">Dual-Pane Coordinates</span>
                  <span className="text-[11px] text-[#8fa89b]">Real-Time Highlight Sync</span>
                </div>
              </div>
            </div>

            {/* Laboratory / Multi-Agent Instrumentation Imagery */}
            <div className="relative mt-8 rounded-2xl overflow-hidden border border-white/10 group aspect-[4/3]">
              <img
                src="/assets/lab_tubes.jpg"
                alt="Illuminated scientific apparatus and multi-agent document analysis"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#07150f] via-transparent to-transparent opacity-80 pointer-events-none"></div>
              
              <div className="absolute bottom-3 left-3 right-3 p-3 rounded-xl bg-[#07150f]/80 backdrop-blur-md border border-white/10 text-xs">
                <div className="flex items-center justify-between text-[#d4af37] font-mono text-[10.5px]">
                  <span>STATION: LANGGRAPH AGENT 03</span>
                  <span className="flex items-center gap-1 text-emerald-400">
                    <CheckCircle className="w-3 h-3" /> P-VALUE CONFIRMED
                  </span>
                </div>
                <p className="text-[#c4d4cb] text-[11px] mt-1 font-sans">
                  Active consensus node recalculating ANOVA degrees of freedom across 14 tables.
                </p>
              </div>
            </div>
          </div>

          {/* Right Side: The Exact 4-Step Process Workflow Cards */}
          <div className="lg:col-span-7 flex flex-col justify-between space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 h-full">
              {WORKFLOW_STEPS.map((step, idx) => {
                const Icon = workflowIcons[idx];
                return (
                  <div
                    key={idx}
                    className="p-6 rounded-3xl bg-[#0a2117]/70 hover:bg-[#0e2c1f] border border-white/10 hover:border-[#d4af37]/40 transition-all duration-300 shadow-xl flex flex-col justify-between group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-[#06140e] border border-white/10 group-hover:border-[#d4af37]/50 flex items-center justify-center transition-all duration-300 group-hover:shadow-lg group-hover:shadow-[#d4af37]/10">
                          <Icon className="w-5 h-5 text-[#d4af37] stroke-[1.5]" />
                        </div>
                        <span className="text-xl font-mono font-bold text-white/20 group-hover:text-[#d4af37]/60 transition-colors">
                          {step.step}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-base font-bold text-white group-hover:text-[#fceda8] transition-colors">
                          {step.title}
                        </h4>
                      </div>

                      <p className="text-xs text-[#a2b7ac] leading-relaxed">
                        {step.subtitle}
                      </p>
                    </div>

                    <div className="mt-5 pt-3 border-t border-white/10 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-[#8fa89b] uppercase">{step.badge}</span>
                      <span className="text-xs font-mono font-semibold text-[#d4af37] px-2 py-0.5 rounded bg-[#d4af37]/10 border border-[#d4af37]/20">
                        {step.spec}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick Micro-Banner inside Right Column */}
            <div className="p-5 rounded-2xl bg-gradient-to-r from-[#0d271c] to-[#081811] border border-[#d4af37]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-[#d4af37]/15 border border-[#d4af37]/30 flex items-center justify-center shrink-0">
                  <TrendingUp className="w-4 h-4 text-[#d4af37]" />
                </div>
                <div>
                  <div className="text-xs font-bold text-white">Full Source Bounding-Box Transparency</div>
                  <div className="text-[11px] text-[#9eb2a6]">Every AI claim highlights exact coordinate spans on original PDF pages.</div>
                </div>
              </div>
              <button
                onClick={() => onOpenCoa("paper-01")}
                className="text-xs font-mono text-[#d4af37] hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer shrink-0"
              >
                <span>View Sample Audit</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>

        </div>

        {/* Live Interactive Paper Verification & Audit Tool */}
        <div id="audit-tool" className="rounded-3xl bg-[#091f16] border border-[#d4af37]/30 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Info & Search Input */}
            <div className="lg:col-span-6 space-y-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#d4af37] animate-pulse"></span>
                <span className="text-xs font-mono text-[#d4af37] font-semibold tracking-wider uppercase">
                  LIVE PAPER AUDIT INSPECTOR
                </span>
              </div>

              <h3 className="text-2xl font-bold text-white tracking-tight">
                Inspect Real-Time Paper Verification
              </h3>
              
              <p className="text-sm text-[#adc0b5]">
                Input any research DOI or paper ID to inspect LangGraph statistical verification, abstract-to-body concordance, and hybrid embedding distances.
              </p>

              {/* Input Form */}
              <div className="flex flex-col sm:flex-row gap-2 pt-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={searchCode}
                    onChange={(e) => setSearchCode(e.target.value)}
                    placeholder="e.g. paper-01 or 10.1016/j.cell.2026..."
                    className="w-full px-4 py-2.5 rounded-xl bg-[#06140e] border border-white/20 text-white font-mono text-sm placeholder:text-[#5d7568] focus:border-[#d4af37] focus:outline-none transition-colors"
                  />
                  <Search className="w-4 h-4 text-[#8fa89b] absolute right-3.5 top-3" />
                </div>
                <button
                  onClick={() => handleSearch(searchCode)}
                  className="px-5 py-2.5 rounded-xl bg-[#d4af37] hover:bg-[#e8c865] text-[#07150f] font-semibold text-xs font-mono tracking-wider uppercase transition-colors cursor-pointer shrink-0 shadow-lg shadow-[#d4af37]/20"
                >
                  Verify Paper
                </button>
              </div>

              {/* Sample Shortcuts */}
              <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] font-mono text-[#8fa89b]">
                <span>Sample Papers:</span>
                {RESEARCH_PAPERS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => handleSearch(p.id)}
                    className="px-2 py-0.5 rounded bg-white/5 hover:bg-[#d4af37]/20 hover:text-[#d4af37] border border-white/10 transition-colors cursor-pointer"
                  >
                    {p.id} ({p.name.split(" ")[0]})
                  </button>
                ))}
              </div>

              {lookupFeedback && (
                <div
                  className={`text-xs font-mono p-2.5 rounded-xl border ${
                    lookupFeedback.status === "success"
                      ? "bg-emerald-950/40 text-emerald-300 border-emerald-500/30"
                      : "bg-amber-950/40 text-amber-300 border-amber-500/30"
                  }`}
                >
                  {lookupFeedback.text}
                </div>
              )}
            </div>

            {/* Right Side: Visual Statistical Curve & Spec Box */}
            <div className="lg:col-span-6 rounded-2xl bg-[#06140e] border border-white/10 p-5 relative">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
                  <span className="font-mono text-xs text-white font-bold">
                    P-VALUE RE-COMPUTATION & RETRIEVAL DENSITY — {selectedPaperData.name}
                  </span>
                </div>
                <span className="text-[11px] font-mono text-[#d4af37] bg-[#d4af37]/15 px-2 py-0.5 rounded border border-[#d4af37]/30">
                  INTEGRITY: {selectedPaperData.integrityScore}
                </span>
              </div>

              {/* SVG Statistical Verification Curve */}
              <div className="relative h-32 w-full bg-[#030906] rounded-xl border border-white/5 overflow-hidden flex items-end p-2">
                <svg className="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
                  {/* Grid Lines */}
                  <line x1="0" y1="30" x2="400" y2="30" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
                  <line x1="0" y1="60" x2="400" y2="60" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
                  <line x1="0" y1="90" x2="400" y2="90" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
                  
                  {/* Statistical Peak Curve */}
                  <path
                    d="M 0 115 L 70 115 Q 110 115 130 114 Q 160 114 175 110 Q 185 102 195 40 Q 200 10 205 40 Q 215 102 225 110 Q 240 114 270 115 L 400 115"
                    fill="none"
                    stroke="#d4af37"
                    strokeWidth="2.5"
                  />
                  {/* Under Peak Gradient Fill */}
                  <path
                    d="M 180 115 Q 185 102 195 40 Q 200 10 205 40 Q 215 102 220 115 Z"
                    fill="url(#goldGradientFill2)"
                    opacity="0.35"
                  />
                  <defs>
                    <linearGradient id="goldGradientFill2" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#d4af37" />
                      <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                  </defs>
                </svg>

                {/* Annotation marker */}
                <div className="absolute top-3 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded bg-[#0d261c] border border-[#d4af37]/40 text-[10px] font-mono text-[#d4af37]">
                  Stat Peak: {selectedPaperData.pValue} ({selectedPaperData.sampleSize})
                </div>
              </div>

              {/* Data Table Row */}
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-white/10 text-[11px] font-mono">
                <div>
                  <span className="text-[#7d978a] block text-[10px]">ABSTRACT MATCH</span>
                  <span className="text-white font-semibold">{selectedPaperData.abstractMatch}</span>
                </div>
                <div>
                  <span className="text-[#7d978a] block text-[10px]">CONTRADICTIONS</span>
                  <span className="text-emerald-400 font-semibold">{selectedPaperData.contradictionsFound}</span>
                </div>
                <div className="text-right">
                  <button
                    onClick={() => onOpenCoa(selectedPaperData.id)}
                    className="inline-flex items-center gap-1 text-[#d4af37] hover:underline cursor-pointer"
                  >
                    <span>Full Audit</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>

            </div>

          </div>
        </div>

      </div>
    </section>
  );
}
