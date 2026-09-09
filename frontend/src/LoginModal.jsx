import { useState } from "react";
import { Lock, Mail, Key, User, X, Shield, Sparkles, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "./AuthContext";

function LoginModal({ isOpen, onClose, defaultTab = "login", onSuccess }) {
  const { login, register } = useAuth();
  const [tab, setTab] = useState(defaultTab);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (tab === "login") {
        const res = await login(email, password);
        if (!res.success) {
          setError(res.error || "Failed to sign in. Please verify your credentials.");
          setLoading(false);
          return;
        }
      } else {
        if (!email.trim() || !password.trim()) {
          setError("Email and password are required.");
          setLoading(false);
          return;
        }
        const res = await register(email, password, fullName);
        if (!res.success) {
          setError(res.error || "Failed to create account.");
          setLoading(false);
          return;
        }
      }

      setLoading(false);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || "An unexpected error occurred.");
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Dark backdrop with blur */}
      <div
        onClick={onClose}
        className="fixed inset-0 transition-opacity bg-[#03070b]/80 backdrop-blur-xl"
      />

      {/* Modal Container */}
      <div
        className="relative z-10 w-full max-w-md rounded-2xl p-6 sm:p-8 shadow-2xl bg-[#09151e]/95 border border-[#16323b] shadow-black/80"
        style={{
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 40px rgba(45, 212, 206, 0.12)",
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header Branding */}
        <div className="mb-6 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0e272b] border border-[#2dd4ce]/30 mb-2">
            <Shield className="w-3 h-3 text-[#2dd4ce]" />
            <span className="text-[10px] font-mono tracking-widest text-[#2dd4ce] uppercase font-bold">
              VERINEXA SECURE RESEARCH ACCESS
            </span>
          </div>
          <h2 className="font-display text-2xl font-bold text-white tracking-tight">
            {tab === "login" ? "Authenticate to VeriNexa" : "Create Clinical Account"}
          </h2>
          <p className="text-xs text-[#8fa89b] mt-1 leading-relaxed">
            Air-gapped biomedical literature verification & cross-paper integrity audit suite.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[#16323b] mb-6">
          <button
            type="button"
            onClick={() => { setTab("login"); setError(""); }}
            className={`pb-2.5 text-xs font-mono uppercase tracking-wider transition-all flex-1 text-center cursor-pointer ${
              tab === "login"
                ? "border-b-2 border-[#2dd4ce] font-bold text-[#2dd4ce]"
                : "text-[#8fa89b] hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setTab("register"); setError(""); }}
            className={`pb-2.5 text-xs font-mono uppercase tracking-wider transition-all flex-1 text-center cursor-pointer ${
              tab === "register"
                ? "border-b-2 border-[#2dd4ce] font-bold text-[#2dd4ce]"
                : "text-[#8fa89b] hover:text-white"
            }`}
          >
            Register
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-4 rounded-xl p-3 text-xs border border-[#ff4757]/30 bg-[#ff4757]/10 text-[#ff4757] flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-left">
          {tab === "register" && (
            <div>
              <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
                Full Name / Researcher Title
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Dr. Jane Doe"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
                />
                <User className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
              </div>
            </div>
          )}

          <div>
            <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
              Institutional / Research Email
            </label>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="researcher@lab.org"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
              />
              <Mail className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
            </div>
          </div>

          <div>
            <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
              Access Password
            </label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
              />
              <Key className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 w-full py-3 rounded-xl bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] text-[#060b10] font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-[#2dd4ce]/20 hover:brightness-110 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating with VeriNexa Engine...</span>
              </>
            ) : tab === "login" ? (
              <span>ENTER WORKSPACE →</span>
            ) : (
              <span>CREATE ACCOUNT & LAUNCH →</span>
            )}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-[#16323b] text-center">
          <p className="text-xs text-[#8fa89b]">
            {tab === "login" ? "New clinical researcher? " : "Already registered? "}
            <button
              type="button"
              onClick={() => {
                setTab(tab === "login" ? "register" : "login");
                setError("");
              }}
              className="text-[#2dd4ce] font-semibold hover:underline cursor-pointer ml-1"
            >
              {tab === "login" ? "Create an account" : "Sign in instead"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
