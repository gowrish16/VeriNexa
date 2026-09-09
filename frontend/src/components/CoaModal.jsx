import React from "react";
import { X, CheckCircle2, Download, Printer, ShieldCheck, QrCode, FileText, ExternalLink, SplitSquareVertical } from "lucide-react";
import { RESEARCH_PAPERS } from "../data/products";

export default function CoaModal({ peptideId, onClose }) {
  const paper = RESEARCH_PAPERS.find((p) => p.id === peptideId) || RESEARCH_PAPERS[0];

  if (!paper) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto bg-black/80 backdrop-blur-md">
      {/* Modal Container */}
      <div className="relative w-full max-w-4xl bg-[#091f16] border border-[#d4af37]/40 rounded-3xl shadow-2xl overflow-hidden my-8 text-[#f4f7f5]">
        
        {/* Top Control Bar */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#05140e] border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span className="font-mono text-xs text-[#d4af37] font-semibold uppercase tracking-wider">
              DOCUMENT INTEGRITY & STATISTICAL AUDIT REPORT
            </span>
            <span className="text-white/20">|</span>
            <span className="font-mono text-xs text-[#8fa89b]">REF: {paper.id.toUpperCase()}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-[#adc2b6] hover:text-white border border-white/10 text-xs transition-colors cursor-pointer"
              title="Print Certificate"
            >
              <Printer className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-[#adc2b6] hover:text-white border border-white/10 text-xs transition-colors cursor-pointer"
              title="Close Modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Inner Content */}
        <div className="p-6 sm:p-8 space-y-6 max-h-[80vh] overflow-y-auto">
          
          {/* Lab Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-white/10 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-[#2dd4ce]" />
                <span className="text-lg font-extrabold tracking-widest text-white uppercase font-sans">
                  VERINEXA CLINICAL AUDIT LABS
                </span>
              </div>
              <p className="text-xs text-[#8fa89b] font-mono mt-1">
                Autonomous Multi-Agent Verification & Closed-Corpus Evidence Suite • Cambridge • Zurich
              </p>
            </div>

            <div className="text-left sm:text-right font-mono text-xs">
              <span className="text-[#8fa89b] block">AUDIT COMPLIANCE REF:</span>
              <span className="text-[#d4af37] font-semibold">CLOSED-CORPUS RAG #VER-99214</span>
              <span className="text-emerald-400 block mt-0.5">STATUS: STATISTICALLY REPRODUCIBLE</span>
            </div>
          </div>

          {/* Document Details Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-[#05140e] border border-white/10 font-mono text-xs">
            <div>
              <span className="text-[#7d978a] block text-[10.5px]">DOCUMENT NAME</span>
              <span className="text-white font-bold text-sm truncate block">{paper.name}</span>
            </div>
            <div>
              <span className="text-[#7d978a] block text-[10.5px]">DIGITAL OBJECT ID (DOI)</span>
              <span className="text-[#d4af37] font-bold text-sm truncate block">{paper.doi}</span>
            </div>
            <div>
              <span className="text-[#7d978a] block text-[10.5px]">SAMPLE SIZE (COHORT)</span>
              <span className="text-white">{paper.sampleSize}</span>
            </div>
            <div>
              <span className="text-[#7d978a] block text-[10.5px]">CONFIRMED P-VALUE</span>
              <span className="text-emerald-400 font-bold">{paper.pValue}</span>
            </div>

            <div className="col-span-2 sm:col-span-4 pt-2 border-t border-white/10">
              <span className="text-[#7d978a] block text-[10.5px]">HYBRID VECTOR & LEXICAL PIPELINE</span>
              <span className="text-white text-xs break-all">{paper.ragEngine} • {paper.specs.claimAttribution}</span>
            </div>
          </div>

          {/* Statistical Distribution & Cosine Similarity Section */}
          <div className="p-5 rounded-2xl bg-[#05140e] border border-white/10 space-y-3">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#d4af37]"></span>
                <span className="text-white font-bold">
                  LANGGRAPH STATISTICAL RE-COMPUTATION & RETRIEVAL DENSITY
                </span>
              </div>
              <span className="text-[#d4af37] bg-[#d4af37]/10 px-2 py-0.5 rounded border border-[#d4af37]/20">
                P-VALUE DENSITY • 1536-DIM PGVECTOR
              </span>
            </div>

            {/* Visual SVG Statistical Graph */}
            <div className="relative h-44 w-full bg-[#020705] rounded-xl border border-white/5 p-4 flex items-end">
              <svg className="w-full h-full" viewBox="0 0 500 140" preserveAspectRatio="none">
                {/* Horizontal Baseline Grids */}
                <line x1="0" y1="35" x2="500" y2="35" stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
                <line x1="0" y1="70" x2="500" y2="70" stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
                <line x1="0" y1="105" x2="500" y2="105" stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
                
                {/* Significance Peak Curve */}
                <path
                  d="M 0 135 L 120 135 Q 180 135 210 134 Q 230 130 242 110 Q 248 70 250 15 Q 252 70 258 110 Q 270 130 290 134 Q 320 135 500 135"
                  fill="none"
                  stroke="#d4af37"
                  strokeWidth="2.5"
                />
                {/* Peak Shading Area */}
                <path
                  d="M 235 135 Q 242 110 248 70 Q 250 15 252 70 Q 258 110 265 135 Z"
                  fill="url(#peakGlowFill3)"
                  opacity="0.4"
                />
                <defs>
                  <linearGradient id="peakGlowFill3" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#d4af37" />
                    <stop offset="100%" stopColor="transparent" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Peak Annotation Label */}
              <div className="absolute top-4 left-1/2 -translate-x-1/2 px-3 py-1 rounded-md bg-[#0d271c] border border-[#d4af37]/40 text-xs font-mono text-[#d4af37] shadow-lg">
                Verified Statistical Significance: {paper.pValue} • Abstract Concordance: {paper.abstractMatch}
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] font-mono text-[#7d978a]">
              <span>AST Tables Parsed: 14 Extracted</span>
              <span>pgvector Cosine Metric: 0.942</span>
              <span>Dual-Pane Bounding-Box Sync: Active</span>
            </div>
          </div>

          {/* Test Results Table */}
          <div className="border border-white/10 rounded-2xl overflow-hidden text-xs font-mono">
            <table className="w-full text-left">
              <thead className="bg-[#05140e] text-[#8fa89b] border-b border-white/10 uppercase text-[10.5px]">
                <tr>
                  <th className="p-3.5">Verification Parameter</th>
                  <th className="p-3.5">Methodology</th>
                  <th className="p-3.5">Benchmark Expectation</th>
                  <th className="p-3.5">Observed Audit Result</th>
                  <th className="p-3.5 text-right">Verdict</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-[#dbe6df]">
                <tr>
                  <td className="p-3.5 font-medium text-white">Abstract Integrity Audit</td>
                  <td className="p-3.5 text-[#8fa89b]">LangGraph Consensus Node</td>
                  <td className="p-3.5">No unsubstantiated claims</td>
                  <td className="p-3.5 text-[#d4af37] font-bold">{paper.abstractMatch}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-medium text-white">P-Value Re-computation</td>
                  <td className="p-3.5 text-[#8fa89b]">Independent Welch/ANOVA Recalc</td>
                  <td className="p-3.5">p &lt; 0.05</td>
                  <td className="p-3.5 text-emerald-300 font-semibold">{paper.pValue}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-medium text-white">Sample Size Concordance</td>
                  <td className="p-3.5 text-[#8fa89b]">Cohort Cross-Table Mapping</td>
                  <td className="p-3.5">Exact N-count across tables</td>
                  <td className="p-3.5">{paper.sampleSize}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-medium text-white">Contradiction & Conflict Matrix</td>
                  <td className="p-3.5 text-[#8fa89b]">Multi-Document Conflict Graph</td>
                  <td className="p-3.5">0 Internal Discrepancies</td>
                  <td className="p-3.5">{paper.contradictionsFound}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-medium text-white">Closed-Corpus Attribution</td>
                  <td className="p-3.5 text-[#8fa89b]">Exact Bounding-Box Coordinates</td>
                  <td className="p-3.5">100% Source Highlighting</td>
                  <td className="p-3.5">{paper.specs.claimAttribution}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
                <tr>
                  <td className="p-3.5 font-medium text-white">Hallucination Threshold</td>
                  <td className="p-3.5 text-[#8fa89b]">pgvector Context Boundary</td>
                  <td className="p-3.5">0.00% Tolerated</td>
                  <td className="p-3.5 text-emerald-400 font-bold">{paper.hallucinationRisk}</td>
                  <td className="p-3.5 text-right text-emerald-400 font-bold">PASSED</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Signature & Cryptographic Sign-Off */}
          <div className="flex flex-col sm:flex-row items-center justify-between p-5 rounded-2xl bg-[#05140e] border border-white/10 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                <QrCode className="w-7 h-7 text-[#d4af37]" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-[#8fa89b] uppercase block">IMMUTABLE AUDIT LEDGER HASH</span>
                <span className="text-xs font-mono text-[#d4af37] font-semibold break-all">
                  0x7d81a9f...b420cc (Verified On-Chain)
                </span>
              </div>
            </div>

            <div className="text-right">
              <div className="text-xs font-serif italic text-white text-base">
                Dr. Elena Vance, Ph.D.
              </div>
              <div className="text-[10.5px] font-mono text-[#8fa89b]">
                Head of Multi-Agent Systems & Literature Verification
              </div>
            </div>
          </div>

        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-[#05140e] border-t border-white/10 flex items-center justify-between">
          <span className="text-[11px] font-mono text-[#8fa89b]">
            Verification Protocol: VER-RAG-2026.Q3
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white font-mono text-xs cursor-pointer"
            >
              Close
            </button>
            <button
              onClick={() => alert(`Downloading verified audit PDF for ${paper.name}`)}
              className="px-5 py-2 rounded-xl bg-[#d4af37] hover:bg-[#e6ca65] text-[#07150f] font-mono text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-md shadow-[#d4af37]/20"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Signed Audit PDF</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
