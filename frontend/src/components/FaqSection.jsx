import React, { useState } from "react";
import { Plus, Minus, HelpCircle, FileText, ChevronRight } from "lucide-react";
import { FAQ_ITEMS } from "../data/products";

export default function FaqSection({ onOpenCoa }) {
  const [openIndex, setOpenIndex] = useState(0);

  const toggleFaq = (index) => {
    setOpenIndex(openIndex === index ? -1 : index);
  };

  return (
    <section id="faq" className="py-24 bg-[#f6f4ee] text-[#0d221a] relative overflow-hidden transition-colors">
      
      {/* Subtle background ambient texture */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header with High-Contrast Editorial Styling */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#e8e4d8] border border-[#d6cfbe] mb-3">
            <HelpCircle className="w-3.5 h-3.5 text-[#8c6d1a]" />
            <span className="text-[11px] font-mono tracking-widest text-[#6e5411] uppercase font-semibold">
              RESEARCHER QUESTIONS & PROTOCOLS
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#091a13] tracking-tight">
            Frequently Asked{" "}
            <span className="font-serif italic font-normal text-[#8c6d1a]">
              Questions
            </span>
          </h2>
          <p className="mt-4 text-[#3d5349] text-base leading-relaxed">
            Everything you need to know about our closed-corpus RAG architecture, PDF parsing precision, and multi-agent statistical verification.
          </p>
        </div>

        {/* Accordion List with Soft Drop-Shadows & Clean Toggles */}
        <div className="space-y-4">
          {FAQ_ITEMS.map((item, idx) => {
            const isOpen = openIndex === idx;
            return (
              <div
                key={idx}
                className={`rounded-2xl transition-all duration-300 border ${
                  isOpen
                    ? "bg-white border-[#d4af37]/60 shadow-xl shadow-[#0d221a]/5"
                    : "bg-white/80 hover:bg-white border-[#e2ddd0] shadow-sm"
                }`}
              >
                <button
                  onClick={() => toggleFaq(idx)}
                  className="w-full text-left px-6 py-5 flex items-center justify-between gap-4 cursor-pointer focus:outline-none"
                  aria-expanded={isOpen}
                >
                  <span className="text-base sm:text-lg font-bold text-[#091a13] tracking-tight">
                    {item.question}
                  </span>
                  
                  {/* Plus / Minus Toggle Button */}
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                      isOpen
                        ? "bg-[#091a13] text-[#d4af37] rotate-180 shadow-md"
                        : "bg-[#e8e4d8] text-[#091a13] hover:bg-[#ded8c9]"
                    }`}
                  >
                    {isOpen ? <Minus className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                  </div>
                </button>

                {/* Animated Collapsible Answer */}
                {isOpen && (
                  <div className="px-6 pb-6 pt-1 text-sm sm:text-base text-[#3d5349] leading-relaxed border-t border-[#f0ece1] mt-1">
                    <p>{item.answer}</p>
                    
                    {idx === 0 && (
                      <div className="mt-4 p-3 rounded-xl bg-[#f7f5ed] border border-[#e2ddd0] flex items-center justify-between text-xs font-mono">
                        <span className="text-[#647c70]">Want to inspect an audited sample paper?</span>
                        <button
                          onClick={() => onOpenCoa("paper-01")}
                          className="text-[#8c6d1a] font-bold hover:underline flex items-center gap-1 cursor-pointer"
                        >
                          <span>Open Verification Audit</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Institutional Contact Footnote */}
        <div className="mt-12 text-center text-xs font-mono text-[#5c7367]">
          Need an on-premises deployment, private VPC instance, or custom PubMed pipeline?{" "}
          <a
            href="#allocation"
            className="text-[#8c6d1a] font-bold hover:underline"
          >
            Schedule an Engineering Briefing &rarr;
          </a>
        </div>

      </div>
    </section>
  );
}
