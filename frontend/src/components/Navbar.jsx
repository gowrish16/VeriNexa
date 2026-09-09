import React, { useState, useEffect } from "react";
import { Shield, Search, Menu, X, ArrowUpRight, Sparkles, BookOpen, User, LogOut } from "lucide-react";
import { useAuth } from "../AuthContext";

export default function Navbar({ onOpenBatchSearch, onOpenAllocation, onOpenAuth }) {
  const { isAuthenticated, user, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Workflow", href: "#workflow" },
    { name: "Core Engine", href: "#features" },
    { name: "Live Benchmark", href: "#audit-tool" },
    { name: "Clinical Trials", href: "#literature" },
    { name: "Research FAQ", href: "#faq" }
  ];

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#060b10]/90 backdrop-blur-xl border-b border-[#16323b] shadow-2xl shadow-black/50 py-3.5"
          : "bg-transparent py-5 border-b border-white/5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Brand Identity */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-[#16323b] via-[#0d221a] to-[#060b10] p-0.5 border border-[#2dd4ce]/40 shadow-lg shadow-[#2dd4ce]/10 flex items-center justify-center group-hover:border-[#2dd4ce] transition-all duration-300">
              <div className="w-full h-full rounded-[10px] bg-[#060b10] flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-[#2dd4ce] stroke-[1.5] transition-transform duration-300 group-hover:scale-110" />
              </div>
              <span className="absolute -bottom-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2dd4ce] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#2dd4ce]"></span>
              </span>
            </div>
            <div className="flex flex-col">
              <span className="font-sans font-bold tracking-[0.22em] text-sm text-white uppercase flex items-center gap-1.5">
                VERINEXA
                <span className="text-[10px] font-mono tracking-widest px-1.5 py-0.5 rounded bg-[#2dd4ce]/15 text-[#2dd4ce] border border-[#2dd4ce]/30">
                  CLINICAL RAG
                </span>
              </span>
              <span className="text-[9.5px] font-mono tracking-wider text-[#8fa89b] uppercase">
                ON-DEVICE BIOMEDICAL EVIDENCE AUDIT
              </span>
            </div>
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 bg-[#0b131b]/80 border border-[#16323b] backdrop-blur-md rounded-full px-5 py-1.5 shadow-inner">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-xs font-medium text-[#adc2b6] hover:text-[#2dd4ce] transition-colors duration-200 px-3.5 py-1.5 rounded-full hover:bg-white/5"
              >
                {link.name}
              </a>
            ))}
          </nav>

          {/* Action Buttons & Auth Gate */}
          <div className="hidden sm:flex items-center gap-3">
            <button
              onClick={onOpenBatchSearch}
              title="Search SGLT2 Trial DOI"
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-mono text-[#8fa89b] hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 transition-all duration-200 cursor-pointer"
            >
              <Search className="w-3.5 h-3.5 text-[#d4af37]" />
              <span className="hidden md:inline">Inspect Trial DOI</span>
            </button>

            {isAuthenticated ? (
              <div className="flex items-center gap-2.5 pl-2">
                <span className="text-xs font-mono px-3 py-1.5 rounded-full bg-[#0b1e25] border border-[#2dd4ce]/40 text-[#2dd4ce] flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[120px]">{user?.full_name || user?.email}</span>
                </span>
                <button
                  onClick={onOpenAllocation}
                  className="px-4 py-2 rounded-full bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-[#2dd4ce]/20 cursor-pointer"
                >
                  <span>Workspace</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={logout}
                  title="Sign Out"
                  className="p-2 rounded-full bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-[#ff4757] border border-white/10 transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onOpenAuth("login")}
                  className="px-3.5 py-1.5 rounded-full text-xs font-mono text-white hover:text-[#2dd4ce] bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer"
                >
                  Sign In
                </button>
                <button
                  onClick={onOpenAllocation}
                  className="relative group overflow-hidden rounded-full p-px font-semibold text-xs transition-all duration-300 cursor-pointer shadow-md shadow-[#2dd4ce]/20"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] transition-all duration-300 group-hover:opacity-90"></span>
                  <span className="relative flex items-center gap-2 px-4 py-2 rounded-full bg-[#060b10] text-[#f4f7f5] group-hover:bg-opacity-80 transition-all duration-300">
                    <Sparkles className="w-3.5 h-3.5 text-[#2dd4ce]" />
                    <span className="tracking-wide">Launch Workspace</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-[#2dd4ce] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </span>
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex lg:hidden items-center gap-2">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-lg bg-white/5 border border-white/10 text-[#2dd4ce] hover:bg-white/10"
              aria-label="Toggle Navigation"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileOpen && (
          <div className="lg:hidden mt-4 pb-4 pt-2 px-4 rounded-2xl bg-[#08131b] border border-[#16323b] shadow-2xl">
            <div className="flex flex-col space-y-2">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2 text-sm text-[#adc2b6] hover:text-[#2dd4ce] rounded-lg hover:bg-white/5 transition-colors"
                >
                  {link.name}
                </a>
              ))}
              <div className="pt-3 border-t border-[#16323b] flex flex-col gap-2">
                {isAuthenticated ? (
                  <>
                    <div className="flex items-center justify-between text-xs font-mono py-1 text-[#2dd4ce]">
                      <span>User: {user?.email}</span>
                      <button onClick={logout} className="text-[#ff4757]">Sign Out</button>
                    </div>
                    <button
                      onClick={() => {
                        setMobileOpen(false);
                        onOpenAllocation();
                      }}
                      className="w-full py-2.5 px-4 text-xs font-semibold text-center rounded-xl bg-[#2dd4ce] text-[#060b10]"
                    >
                      Enter Workspace →
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        setMobileOpen(false);
                        onOpenAuth("login");
                      }}
                      className="w-full py-2.5 px-4 text-xs font-mono text-center rounded-xl bg-white/5 border border-white/10 text-white"
                    >
                      Sign In / Register
                    </button>
                    <button
                      onClick={() => {
                        setMobileOpen(false);
                        onOpenAllocation();
                      }}
                      className="w-full py-2.5 px-4 text-xs font-semibold text-center rounded-xl bg-gradient-to-r from-[#2dd4ce] to-[#0d9488] text-[#060b10]"
                    >
                      Start Verification →
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
