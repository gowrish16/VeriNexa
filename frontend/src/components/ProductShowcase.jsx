import React, { useState } from "react";
import {
  Sparkles,
  FileCheck,
  CheckCircle2,
  ChevronRight,
  Filter,
  Plus,
  ArrowUpRight,
  ShieldCheck,
  ExternalLink,
  Scale,
  FileSearch,
  Lock,
  SplitSquareVertical,
  AlertTriangle
} from "lucide-react";
import { RESEARCH_PAPERS, CORE_FEATURES } from "../data/products";

export default function ProductShowcase({ onOpenCoa, onAddToOrder }) {
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = [
    "All",
    "Cellular Biology",
    "Metabolic Research",
    "Genomics",
    "Gene Editing"
  ];

  const filteredPapers =
    activeCategory === "All"
      ? RESEARCH_PAPERS
      : RESEARCH_PAPERS.filter((item) => item.category === activeCategory);

  const featureIcons = [Scale, FileSearch, Lock, SplitSquareVertical];

  return (
    <section id="features" className="py-24 relative overflow-hidden bg-[#07150f]">
      {/* Background glow refractions */}
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] emerald-radial-glow pointer-events-none -z-10 blur-3xl opacity-40"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section 1: Key Features Showcase */}
        <div className="mb-20">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0e271e] border border-[#d4af37]/30 mb-3">
              <Sparkles className="w-3.5 h-3.5 text-[#d4af37]" />
              <span className="text-[11px] font-mono tracking-widest text-[#d4af37] uppercase">
                CORE VERIFICATION MODULES
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight">
              Key{" "}
              <span className="font-serif italic font-normal text-[#d4af37]">
                Features
              </span>
            </h2>
            <p className="mt-3 text-[#a1b7ac] text-base max-w-xl">
              Architected to eliminate hallucinated citations, surface hidden data conflicts across study cohorts, and hold scientific literature to absolute empirical standards.
            </p>
          </div>

          {/* 4 Feature Grid Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {CORE_FEATURES.map((feat, idx) => {
              const Icon = featureIcons[idx];
              return (
                <div
                  key={idx}
                  className="rounded-[22px] bg-[#091e15]/80 hover:bg-[#0c261b] border border-white/10 hover:border-[#d4af37]/40 transition-all duration-300 p-6 flex flex-col justify-between shadow-xl group relative overflow-hidden"
                >
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="w-12 h-12 rounded-2xl bg-[#06140e] border border-white/10 group-hover:border-[#d4af37]/50 flex items-center justify-center transition-all duration-300 group-hover:shadow-lg group-hover:shadow-[#d4af37]/10">
                        <Icon className="w-5 h-5 text-[#d4af37] stroke-[1.5]" />
                      </div>
                      <span className="text-[10.5px] font-mono font-semibold px-2 py-0.5 rounded-full bg-[#d4af37]/10 text-[#d4af37] border border-[#d4af37]/20">
                        {feat.tag}
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-white group-hover:text-[#f8ecbb] transition-colors leading-snug">
                      {feat.title}
                    </h3>

                    <p className="text-xs text-[#adc1b6] leading-relaxed">
                      {feat.description}
                    </p>
                  </div>

                  <div className="mt-6 pt-3 border-t border-white/10 flex items-center justify-between">
                    <span className="text-[10px] font-mono text-[#8fa89b] uppercase">Capability</span>
                    <span className="text-xs font-mono font-bold text-[#d4af37]">
                      {feat.metric}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section 2: Validated Literature Benchmarks */}
        <div id="literature" className="pt-10 border-t border-white/10">
          
          {/* Header & Subtitle */}
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0e271e] border border-[#d4af37]/30 mb-3">
                <ShieldCheck className="w-3.5 h-3.5 text-[#d4af37]" />
                <span className="text-[11px] font-mono tracking-widest text-[#d4af37] uppercase">
                  BENCHMARK AUDITS
                </span>
              </div>
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight">
                Audited Research{" "}
                <span className="font-serif italic font-normal text-[#d4af37]">
                  Papers
                </span>
              </h2>
              <p className="mt-3 text-[#a1b7ac] text-base max-w-xl">
                Inspect live multi-agent verification reports across peer-reviewed publications. See verified p-values, sample cohort recalculations, and dual-pane bounding boxes.
              </p>
            </div>

            {/* Lineup Visual Banner Micro-Badge */}
            <div className="hidden lg:flex items-center gap-3 p-3 rounded-2xl bg-[#0a1e15] border border-white/10 max-w-md">
              <div className="w-16 h-12 rounded-xl overflow-hidden shrink-0 border border-white/10">
                <img
                  src="/assets/vials_lineup.jpg"
                  alt="Verified literature documents"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="text-xs">
                <div className="font-mono text-[#d4af37] font-semibold">CROSS-STUDY REPLICATION</div>
                <div className="text-[#8fa89b] text-[11px]">Real-time detection of conflicting trial metrics and endpoints.</div>
              </div>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-10 no-scrollbar">
            <div className="flex items-center gap-1.5 p-1 rounded-full bg-[#0a1e15] border border-white/10">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-4 py-2 rounded-full text-xs font-medium transition-all duration-200 whitespace-nowrap cursor-pointer ${
                    activeCategory === cat
                      ? "bg-[#d4af37] text-[#07150f] font-semibold shadow-md shadow-[#d4af37]/20"
                      : "text-[#a2b7ac] hover:text-white hover:bg-white/5"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Uniform Dark-Green Product Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredPapers.map((paper) => (
              <div
                key={paper.id}
                className="group rounded-[22px] bg-[#091e15]/80 hover:bg-[#0c261b] border border-white/10 hover:border-[#d4af37]/40 transition-all duration-300 p-6 flex flex-col justify-between shadow-xl relative overflow-hidden"
              >
                {/* Top Accent Gradient Ribbon */}
                <div
                  className="absolute top-0 left-0 right-0 h-1 opacity-75 group-hover:opacity-100 transition-opacity"
                  style={{
                    background: `linear-gradient(90deg, ${paper.accentHex}, #d4af37)`
                  }}
                ></div>

                {/* Card Header & Badges */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className="text-[11px] font-mono font-semibold px-2.5 py-0.5 rounded-full uppercase tracking-wider"
                      style={{
                        backgroundColor: `${paper.accentHex}18`,
                        color: paper.accentHex,
                        border: `1px solid ${paper.accentHex}40`
                      }}
                    >
                      {paper.tagLabel}
                    </span>

                    <div className="flex items-center gap-1 text-[11px] font-mono text-[#8fa89b]">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      <span>Verified</span>
                    </div>
                  </div>

                  {/* Document Name & Subtitle */}
                  <div className="mb-4">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-xl font-bold text-white group-hover:text-[#f8ecbb] transition-colors line-clamp-1">
                        {paper.name}
                      </h3>
                    </div>
                    <p className="text-xs text-[#9eb2a7] mt-1 font-mono line-clamp-1">
                      {paper.title}
                    </p>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-[#adc1b6] leading-relaxed mb-5 line-clamp-3">
                    {paper.description}
                  </p>

                  {/* Micro-Badges Detailing */}
                  <div className="flex flex-wrap gap-1.5 mb-6">
                    <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/5 text-[10.5px] font-mono text-[#d4af37] font-medium">
                      Integrity {paper.integrityScore}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/5 text-[10.5px] font-mono text-[#adc1b6]">
                      {paper.sampleSize}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/5 text-[10.5px] font-mono text-[#adc1b6]">
                      {paper.pValue}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/5 text-[10.5px] font-mono text-[#8fa89b]">
                      {paper.abstractMatch}
                    </span>
                  </div>

                  {/* Technical Molecular Specs */}
                  <div className="p-3 rounded-xl bg-[#06140e] border border-white/5 mb-6 text-[11px] font-mono space-y-1">
                    <div className="flex justify-between text-[#8fa89b]">
                      <span>DOI:</span>
                      <span className="text-white font-medium truncate max-w-[140px]">{paper.doi}</span>
                    </div>
                    <div className="flex justify-between text-[#8fa89b]">
                      <span>RAG Engine:</span>
                      <span className="text-white font-medium truncate max-w-[140px]">BM25+pgvector</span>
                    </div>
                    <div className="flex justify-between text-[#8fa89b]">
                      <span>Hallucination:</span>
                      <span className="text-emerald-400 font-medium">{paper.hallucinationRisk}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons: View Audit and Analyze Document */}
                <div className="grid grid-cols-2 gap-2.5 pt-2 border-t border-white/10">
                  <button
                    onClick={() => onOpenCoa(paper.id)}
                    className="w-full py-2.5 px-3 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/10 text-xs font-mono flex items-center justify-center gap-1.5 transition-all cursor-pointer hover:border-[#d4af37]/30"
                  >
                    <FileCheck className="w-3.5 h-3.5 text-[#d4af37]" />
                    <span>View Audit</span>
                  </button>

                  <button
                    onClick={() => onAddToOrder(paper)}
                    className="w-full py-2.5 px-3 rounded-xl bg-[#d4af37] hover:bg-[#e6ca65] text-[#07150f] font-semibold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-[#d4af37]/20 cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Cross-Ref</span>
                  </button>
                </div>

              </div>
            ))}
          </div>

          {/* Bottom Institutional Quality Guarantee */}
          <div className="mt-14 p-6 rounded-3xl bg-gradient-to-r from-[#091f16] via-[#0d271c] to-[#091f16] border border-white/10 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-[#06140e] border border-[#d4af37]/30 flex items-center justify-center shrink-0">
                <ShieldCheck className="w-6 h-6 text-[#d4af37]" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">
                  Guaranteed Closed-Corpus Grounding & Citation Precision
                </div>
                <div className="text-xs text-[#9eb2a7] mt-0.5">
                  Every AI assertion without an exact coordinate bounding box on the original PDF is mathematically blocked.
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={() => onOpenCoa("paper-01")}
                className="text-xs font-mono font-medium text-[#d4af37] hover:underline flex items-center gap-1 cursor-pointer"
              >
                <span>Download Protocol Whitepaper</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
