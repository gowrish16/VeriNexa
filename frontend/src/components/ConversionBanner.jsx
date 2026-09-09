import React, { useState } from "react";
import { Sparkles, CheckCircle2, ArrowRight, Shield, Mail, Lock } from "lucide-react";

export default function ConversionBanner() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email.trim()) {
      setSubmitted(true);
    }
  };

  return (
    <section id="allocation" className="py-20 relative bg-[#07150f] overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Main Glassmorphic Promotional Banner Container */}
        <div className="relative rounded-[32px] bg-gradient-to-br from-[#0c241a] via-[#091b13] to-[#040d09] border border-[#d4af37]/30 shadow-2xl overflow-hidden">
          
          {/* Ambient Lighting Caustics */}
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#d4af37]/10 blur-[100px] pointer-events-none"></div>
          <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-emerald-500/10 blur-[100px] pointer-events-none"></div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center p-8 sm:p-12 lg:p-14 relative z-10">
            
            {/* Left Column: Macro Render of Chemical Compounds / Crystals inside Lab Glass Apparatus */}
            <div className="lg:col-span-6 relative group">
              <div className="relative rounded-2xl overflow-hidden border border-white/15 shadow-2xl aspect-[16/10] bg-[#05110c]">
                <img
                  src="/assets/macro_crystals.jpg"
                  alt="Macro render of crystalline data structures in laboratory apparatus"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                />
                
                {/* Subtle dark vignette gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#07150f]/80 via-transparent to-transparent pointer-events-none"></div>

                {/* Floating Micro-Badge on Image */}
                <div className="absolute bottom-3 left-3 right-3 p-3 rounded-xl bg-[#07150f]/85 backdrop-blur-md border border-white/10 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#d4af37] animate-ping"></span>
                    <span className="text-white font-semibold">LANGGRAPH CONSENSUS CORE</span>
                  </div>
                  <span className="text-[#d4af37] text-[11px]">ACTIVE SYNTHESIS</span>
                </div>
              </div>

              {/* Decorative Corner Framing */}
              <div className="absolute -top-2 -left-2 w-5 h-5 border-t-2 border-l-2 border-[#d4af37]/60 pointer-events-none"></div>
              <div className="absolute -bottom-2 -right-2 w-5 h-5 border-b-2 border-r-2 border-[#d4af37]/60 pointer-events-none"></div>
            </div>

            {/* Right Column: Promotional Copy & Email Opt-in Form */}
            <div className="lg:col-span-6 flex flex-col justify-center space-y-6">
              
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#112d22] border border-[#d4af37]/40 w-fit">
                <Sparkles className="w-3.5 h-3.5 text-[#d4af37]" />
                <span className="text-[11px] font-mono tracking-widest text-[#d4af37] uppercase font-bold">
                  INSTITUTIONAL WORKSPACE INITIATION
                </span>
              </div>

              <div className="space-y-3">
                <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                  Analyze and cross-reference your literature with{" "}
                  <span className="font-serif italic font-normal text-[#d4af37]">
                    empirical
                  </span>{" "}
                  rigor.
                </h3>
                
                <p className="text-sm sm:text-base text-[#b0c4b9] leading-relaxed">
                  Join researchers from leading universities and biotech labs. Upload your literature corpus, activate multi-agent statistical audits, and experience zero-hallucination analysis.
                </p>
              </div>

              {/* Email Form */}
              {!submitted ? (
                <form onSubmit={handleSubmit} className="space-y-3">
                  <div className="flex flex-col sm:flex-row gap-2">
                    <div className="relative flex-1">
                      <Mail className="w-4 h-4 text-[#8fa89b] absolute left-4 top-3.5" />
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter institutional or laboratory email..."
                        className="w-full pl-11 pr-4 py-3.5 rounded-full bg-[#06140e] border border-white/20 text-white placeholder:text-[#5d7568] text-sm focus:border-[#d4af37] focus:outline-none transition-colors"
                      />
                    </div>

                    <button
                      type="submit"
                      className="px-8 py-3.5 rounded-full bg-gradient-to-r from-[#d4af37] via-[#e5c562] to-[#b89228] text-[#07150f] font-bold text-sm tracking-wide shadow-xl shadow-[#d4af37]/25 hover:shadow-[#d4af37]/40 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer shrink-0"
                    >
                      Launch Workspace
                    </button>
                  </div>

                  <div className="flex items-center gap-4 text-[11px] font-mono text-[#8fa89b] pt-1">
                    <span className="flex items-center gap-1.5">
                      <Lock className="w-3 h-3 text-[#d4af37]" />
                      Closed-Corpus Privacy
                    </span>
                    <span>•</span>
                    <span>No External Training</span>
                    <span>•</span>
                    <span>Immediate Access</span>
                  </div>
                </form>
              ) : (
                <div className="p-6 rounded-2xl bg-[#092b1d] border border-[#d4af37]/50 space-y-3">
                  <div className="flex items-center gap-2.5 text-emerald-400 font-bold text-base">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Workspace Credential Generated</span>
                  </div>
                  <p className="text-xs text-[#c4d7cc]">
                    Your workspace invitation and pgvector instance access token have been routed to <strong className="text-white">{email}</strong>.
                  </p>
                  <div className="p-3 rounded-xl bg-[#05140e] border border-[#2dd4ce]/40 font-mono text-sm text-[#2dd4ce] font-bold flex items-center justify-between">
                    <span>TOKEN: VERINEXA-ENTERPRISE-2026</span>
                    <span className="text-[10px] text-[#8fa89b] uppercase">Ready for Upload</span>
                  </div>
                </div>
              )}

            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
