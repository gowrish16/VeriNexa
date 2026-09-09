import React, { useState } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  FileCheck,
  ArrowRight,
  Activity,
  Layers,
  Sparkles,
  Lock,
  Zap,
  Shield,
  FileText,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  Database
} from "lucide-react";

export default function Hero({ onOpenCoa, onExplore, onExploreBenchmark }) {
  const [activeTab, setActiveTab] = useState("empagliflozin");

  const benchmarks = {
    empagliflozin: {
      trialName: "EMPA-REG OUTCOME (Cardiorenal Subgroup)",
      abstractClaim:
        "Empagliflozin showed a 38% relative risk reduction in cardiovascular death and consistently demonstrated significant glycemic control across all baseline HbA1c tiers.",
      resultsData:
        "Table 3: Baseline HbA1c > 8.5% subgroup yielded hazard ratio 0.94 (95% CI 0.77-1.15; p = 0.54). Primary composite endpoint significance driven predominantly by reduced heart failure hospitalization.",
      pValClaim: "Claimed: p < 0.01",
      pValExtracted: "Extracted Table 3: p = 0.54",
      spinVerdict: "Abstract Spin Detected • Statistical Divergence p > 0.05",
      anchorCoordinates: "Anchored to Page 4, Paragraph 2 coordinates",
      sampleSize: "N = 7,020 Patients",
      confidence: "99.2% Agentic Match"
    },
    dapagliflozin: {
      trialName: "DAPA-CKD (Renal Protective Mechanisms)",
      abstractClaim:
        "Dapagliflozin uniformly halted eGFR decline regardless of preexisting cardiovascular co-morbidities with zero observed variance in adverse renal events.",
      resultsData:
        "Table 2 & Figure 4: Acute initial eGFR dip (-3.9 mL/min/1.73m²) observed at week 2 before long-term trajectory stabilization. Partial disagreement on acute volume depletion rate.",
      pValClaim: "Claimed: Absolute Uniformity",
      pValExtracted: "Extracted: Initial Dip p = 0.003",
      spinVerdict: "Partial Consistency • Hemodynamic Dip Omitted in Abstract",
      anchorCoordinates: "Anchored to Page 8, Section 3.2 coordinates",
      sampleSize: "N = 4,304 Patients",
      confidence: "98.8% Agentic Match"
    }
  };

  const active = benchmarks[activeTab] || benchmarks.empagliflozin;

  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
      {/* Background ambient lighting refractions */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[780px] h-[580px] cyan-radial-glow pointer-events-none -z-10 blur-3xl opacity-70"></div>
      <div className="absolute top-1/3 right-10 w-[500px] h-[500px] gold-radial-glow pointer-events-none -z-10 blur-3xl opacity-35"></div>
      <div className="absolute bottom-10 left-10 w-[500px] h-[500px] emerald-radial-glow pointer-events-none -z-10 blur-3xl opacity-40"></div>

      {/* Fine grid lines overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_40%,#000_70%,transparent_100%)] pointer-events-none -z-10"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">

          {/* Left Column: Rebranded Hero Copy */}
          <div className="lg:col-span-6 flex flex-col items-start text-left space-y-6">

            {/* Top Live Pill */}
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#0b1b22]/90 border border-[#2dd4ce]/35 shadow-lg shadow-black/40 backdrop-blur-xl">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2dd4ce] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#2dd4ce]"></span>
              </span>
              <span className="text-[11px] font-mono tracking-wider text-[#2dd4ce] uppercase font-semibold">
                ✦ VeriNexa Clinical Intelligence Suite v1.0
              </span>
              <span className="hidden sm:inline-block w-px h-3 bg-white/20"></span>
              <span className="hidden sm:inline-block text-[11px] font-mono text-[#8fa89b]">
                Air-Gapped Local Inference
              </span>
            </div>

            {/* Main Headline */}
            <div className="space-y-2">
              <p className="text-xs sm:text-sm font-mono tracking-[0.25em] text-[#2dd4ce] uppercase font-semibold">
                // ON-DEVICE BIOMEDICAL EVIDENCE AUDIT
              </p>
              <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.08]">
                <span className="silver-gradient-text inline-block">VeriNexa</span>
              </h1>
              <p className="text-2xl sm:text-3xl text-[#d4af37] font-serif italic font-normal tracking-wide">
                Rigorous scientific truth in every clinical claim.
              </p>
            </div>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-[#adc2b6] font-normal leading-relaxed max-w-xl">
              Cross-document contradiction detection, abstract spin verification, and multi-agent clinical claim synthesis for biomedical research.
            </p>

            {/* Luxury CTA Section */}
            <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
              <button
                onClick={onExplore}
                className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] text-[#060b10] font-bold text-sm tracking-wide shadow-xl shadow-[#2dd4ce]/25 hover:shadow-[#2dd4ce]/40 hover:brightness-110 active:scale-[0.99] transition-all duration-300 cursor-pointer"
              >
                <span>Start Verification →</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={onExploreBenchmark}
                className="inline-flex items-center justify-center gap-2.5 px-6 py-4 rounded-xl bg-[#0b1920]/80 hover:bg-[#10242e] text-[#f4f7f5] border border-white/10 hover:border-[#d4af37]/50 font-medium text-sm transition-all duration-300 backdrop-blur-md cursor-pointer"
              >
                <FileCheck className="w-4 h-4 text-[#d4af37]" />
                <span>Explore SGLT2 Benchmark Data</span>
              </button>
            </div>

            {/* Live Telemetry Badges */}
            <div className="pt-4 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/10 text-xs font-mono text-[#adc2b6]">
                <Lock className="w-3.5 h-3.5 text-[#2dd4ce]" />
                <span>🔒 100% On-Device</span>
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/10 text-xs font-mono text-[#adc2b6]">
                <Zap className="w-3.5 h-3.5 text-[#e8a33d]" />
                <span>⚡ Hybrid BM25 + pgvector</span>
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/10 text-xs font-mono text-[#adc2b6]">
                <Shield className="w-3.5 h-3.5 text-[#10b981]" />
                <span>🛡️ Zero Data Leakage</span>
              </span>
            </div>

          </div>

          {/* Right Column: Interactive 3D Perspective Glass Card (Hero Feature Preview) */}
          <div className="lg:col-span-6 relative flex justify-center items-center">
            
            {/* Ambient Backlight Behind Card */}
            <div className="absolute -inset-2 rounded-[32px] bg-gradient-to-tr from-[#2dd4ce]/20 via-[#d4af37]/15 to-transparent blur-2xl opacity-80 pointer-events-none"></div>

            {/* Main Floating Glass Container */}
            <div className="relative w-full max-w-[560px] rounded-[28px] bg-[#09151e]/90 backdrop-blur-2xl border border-white/10 p-5 sm:p-6 shadow-2xl shadow-black/90">
              
              {/* Card Header: Switcher between trials */}
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#2dd4ce] animate-pulse"></div>
                  <span className="font-mono text-xs font-bold text-white tracking-wider uppercase">
                    ACTIVE AGENTIC AUDIT PREVIEW
                  </span>
                </div>
                <div className="flex items-center gap-1 bg-[#050c12] p-1 rounded-lg border border-white/10">
                  <button
                    onClick={() => setActiveTab("empagliflozin")}
                    className={`px-2.5 py-1 text-[10.5px] font-mono rounded transition-all cursor-pointer ${
                      activeTab === "empagliflozin"
                        ? "bg-[#2dd4ce] text-[#060b10] font-bold shadow"
                        : "text-[#8fa89b] hover:text-white"
                    }`}
                  >
                    EMPA-REG
                  </button>
                  <button
                    onClick={() => setActiveTab("dapagliflozin")}
                    className={`px-2.5 py-1 text-[10.5px] font-mono rounded transition-all cursor-pointer ${
                      activeTab === "dapagliflozin"
                        ? "bg-[#2dd4ce] text-[#060b10] font-bold shadow"
                        : "text-[#8fa89b] hover:text-white"
                    }`}
                  >
                    DAPA-CKD
                  </button>
                </div>
              </div>

              {/* Trial Title Banner */}
              <div className="mb-4 px-3.5 py-2 rounded-xl bg-white/[0.03] border border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2 truncate">
                  <FileText className="w-4 h-4 text-[#d4af37] shrink-0" />
                  <span className="text-xs font-mono font-medium text-white truncate">
                    {active.trialName}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#2dd4ce] shrink-0 px-2 py-0.5 rounded bg-[#2dd4ce]/10 border border-[#2dd4ce]/30">
                  {active.sampleSize}
                </span>
              </div>

              {/* Dual Perspective Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mb-4">
                
                {/* Left Card: Abstract Conclusion */}
                <div className="p-3.5 rounded-2xl bg-[#060e14] border border-[#16323b] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#8fa89b]">
                        // 1. ABSTRACT CLAIM
                      </span>
                      <span className="text-[9px] font-mono text-[#d4af37] bg-[#d4af37]/10 px-1.5 py-0.5 rounded">
                        Published
                      </span>
                    </div>
                    <p className="text-xs text-[#adc2b6] leading-relaxed italic">
                      "{active.abstractClaim}"
                    </p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-[#8fa89b]">Stated P-Value:</span>
                    <span className="text-white font-bold">{active.pValClaim}</span>
                  </div>
                </div>

                {/* Right Card: Extracted Results Table */}
                <div className="p-3.5 rounded-2xl bg-[#060e14] border border-[#16323b] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#2dd4ce]">
                        // 2. PARSED RAW RESULTS
                      </span>
                      <span className="text-[9px] font-mono text-[#2dd4ce] bg-[#2dd4ce]/10 px-1.5 py-0.5 rounded">
                        Verified
                      </span>
                    </div>
                    <p className="text-xs text-[#adc2b6] leading-relaxed">
                      {active.resultsData}
                    </p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-[#8fa89b]">Extracted Math:</span>
                    <span className="text-[#e8a33d] font-bold">{active.pValExtracted}</span>
                  </div>
                </div>

              </div>

              {/* Amber Spin Detected Banner */}
              <div className="p-3 rounded-xl bg-[#e8a33d]/10 border border-[#e8a33d]/30 flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[#e8a33d] shrink-0" />
                  <span className="text-xs font-mono font-bold text-[#e8a33d]">
                    {active.spinVerdict}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#f4f7f5] bg-[#e8a33d]/20 px-2 py-0.5 rounded">
                  FLAGGED
                </span>
              </div>

              {/* Tag Coordinate Anchor & Inspector Button */}
              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs font-mono text-[#8fa89b]">
                <div className="flex items-center gap-1.5 truncate">
                  <Activity className="w-3.5 h-3.5 text-[#2dd4ce] shrink-0" />
                  <span className="truncate">{active.anchorCoordinates}</span>
                </div>
                <button
                  onClick={() => onOpenCoa("paper-01")}
                  className="text-[#2dd4ce] hover:text-[#5eead4] flex items-center gap-1 transition-colors cursor-pointer shrink-0 ml-2"
                >
                  <span>Inspect Audit Proof</span>
                  <ChevronRight className="w-3 h-3" />
                </button>
              </div>

            </div>

          </div>

        </div>
      </div>
    </section>
  );
}
