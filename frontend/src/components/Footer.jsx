import React from "react";
import { BookOpen, ArrowUpRight, Lock, Award, Compass, Globe2 } from "lucide-react";

export default function Footer({ onOpenCoa }) {
  return (
    <footer className="bg-[#040c08] border-t border-white/10 text-[#8fa89b] font-sans text-xs pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Main 4-Column Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-white/10">
          
          {/* Col 1: Brand & Facilities (Takes 2 cols on lg) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#0d221a] border border-[#2dd4ce]/40 flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-[#2dd4ce]" />
              </div>
              <span className="font-bold tracking-[0.2em] text-white uppercase text-sm">
                VERINEXA CLINICAL INTELLIGENCE
              </span>
            </div>
            
            <p className="text-[#98ada2] text-xs leading-relaxed max-w-sm">
              Autonomous multi-agent scientific paper verification, literature analysis, and closed-corpus cross-referencing with synchronized dual-pane attribution.
            </p>

            <div className="pt-2 space-y-1.5 font-mono text-[11px] text-[#768f82]">
              <div className="flex items-center gap-2 text-white/90">
                <Globe2 className="w-3.5 h-3.5 text-[#d4af37]" />
                <span>RESEARCH COMPUTING CENTERS:</span>
              </div>
              <div className="pl-5">ETH Zurich AI Center, Switzerland</div>
              <div className="pl-5">Kendall Square Life Sciences, Cambridge, MA</div>
              <div className="pl-5">Francis Crick Institute Partner Lab, London, UK</div>
            </div>
          </div>

          {/* Col 2: Pipeline Architecture */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
              Architecture
            </h4>
            <ul className="space-y-2 text-[#9bb0a5]">
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  AST PDF Structure Parser
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  BM25 Lexical Keyword Engine
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  pgvector Dense Embeddings
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  LangGraph Multi-Agent Mesh
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  Dual-Pane Real-Time Sync
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Analytical QC & Audit */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
              Verification QC
            </h4>
            <ul className="space-y-2 text-[#9bb0a5]">
              <li>
                <a href="#audit-tool" className="hover:text-[#d4af37] transition-colors">
                  Live Paper Audit Inspector
                </a>
              </li>
              <li>
                <button
                  onClick={() => onOpenCoa("paper-01")}
                  className="hover:text-[#d4af37] transition-colors text-left cursor-pointer"
                >
                  Inspect Sample Audit
                </button>
              </li>
              <li>
                <a href="#features" className="hover:text-[#d4af37] transition-colors">
                  Contradiction Matrix
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-[#d4af37] transition-colors">
                  Abstract Integrity Engine
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-[#d4af37] transition-colors">
                  P-Value Re-Computation
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-[#d4af37] transition-colors">
                  Citation Bounding Boxes
                </a>
              </li>
            </ul>
          </div>

          {/* Col 4: Institutional & Privacy */}
          <div className="space-y-3">
            <h4 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
              Institutional
            </h4>
            <ul className="space-y-2 text-[#9bb0a5]">
              <li>
                <a href="#allocation" className="hover:text-[#d4af37] transition-colors">
                  Academic Lab Deployment
                </a>
              </li>
              <li>
                <a href="#allocation" className="hover:text-[#d4af37] transition-colors">
                  On-Premises VPC Hosting
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[#d4af37] transition-colors">
                  Closed-Corpus Guarantee
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-[#d4af37] transition-colors">
                  Researcher FAQ
                </a>
              </li>
              <li>
                <a href="#allocation" className="hover:text-[#d4af37] transition-colors">
                  Institutional SSO Login
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Closed-Corpus Data Privacy Notice */}
        <div className="py-6 border-b border-white/5 space-y-2">
          <div className="font-mono text-[10.5px] uppercase tracking-wider text-[#2dd4ce]">
            CLOSED-CORPUS DATA INTEGRITY & PRIVACY NOTICE
          </div>
          <p className="text-[11px] text-[#71887b] leading-relaxed">
            VeriNexa enforces a strict closed-corpus security architecture. Uploaded scientific documents, unpublished manuscripts, and clinical datasets are analyzed exclusively within isolated ephemeral pgvector memory partitions. No customer literature is ever used to train foundation models, cached externally, or indexed across tenant boundaries.
          </p>
        </div>

        {/* Bottom Bar: Copyright & Security Seals */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-[#637a6d]">
          <div>
            &copy; {new Date().getFullYear()} VeriNexa Clinical Intelligence Inc. All rights reserved. Air-Gapped Inference.
          </div>

          <div className="flex items-center gap-6">
            <span className="hover:text-white transition-colors cursor-pointer">Security Protocol</span>
            <span className="hover:text-white transition-colors cursor-pointer">Privacy Framework</span>
            <span className="hover:text-white transition-colors cursor-pointer">SOC2 / HIPAA Compliant</span>
            <span className="text-[#d4af37] font-mono">256-BIT ENCRYPTED</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
