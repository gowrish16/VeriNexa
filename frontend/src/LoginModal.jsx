import { useState } from "react";
import { Lock, Mail, Key, User, X, Shield, AlertCircle, CheckCircle2, Loader2, ArrowLeft, ExternalLink } from "lucide-react";
import { useAuth } from "./AuthContext";

function LoginModal({ isOpen, onClose, defaultTab = "login", onSuccess }) {
  const { login, register } = useAuth();
  const [tab, setTab] = useState(defaultTab); // "login" | "register" | "forgot"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [devResetUrl, setDevResetUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    setDevResetUrl(null);
    setLoading(true);

    try {
      if (tab === "login") {
        const res = await login(email, password);
        if (!res.success) {
          setError(res.error || "Invalid email or password");
          setLoading(false);
          return;
        }
        setLoading(false);
        if (onSuccess) {
          onSuccess(res.is_admin, res.user);
        }
        onClose();
      } else if (tab === "register") {
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
        setLoading(false);
        if (onSuccess) {
          onSuccess(res.is_admin, res.user);
        }
        onClose();
      } else if (tab === "forgot") {
        const res = await fetch("http://127.0.0.1:8000/api/auth/forgot-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim().toLowerCase() }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Unable to send recovery email");
        }
        setSuccessMsg(data.message || "A secure password recovery link has been dispatched to your email address.");
        if (data.reset_link) {
          setDevResetUrl(data.reset_link);
        }
        setLoading(false);
      }
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
              {tab === "forgot" ? "PASSWORD RECOVERY" : "VERINEXA SECURE ACCESS"}
            </span>
          </div>
          <h2 className="font-display text-2xl font-bold text-white tracking-tight">
            {tab === "login"
              ? "Sign In"
              : tab === "register"
              ? "Create Account"
              : "Reset Password"}
          </h2>
          <p className="text-xs text-[#8fa89b] mt-1 leading-relaxed">
            {tab === "forgot"
              ? "Enter your registered email address and we'll dispatch a secure recovery link."
              : "Air-gapped biomedical literature verification and cross-paper integrity audit suite."}
          </p>
        </div>

        {/* Navigation Tabs (Only when not in forgot password mode) */}
        {tab !== "forgot" && (
          <div className="flex border-b border-[#16323b] mb-6">
            <button
              type="button"
              onClick={() => { setTab("login"); setError(""); setSuccessMsg(""); }}
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
              onClick={() => { setTab("register"); setError(""); setSuccessMsg(""); }}
              className={`pb-2.5 text-xs font-mono uppercase tracking-wider transition-all flex-1 text-center cursor-pointer ${
                tab === "register"
                  ? "border-b-2 border-[#2dd4ce] font-bold text-[#2dd4ce]"
                  : "text-[#8fa89b] hover:text-white"
              }`}
            >
              Register
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mb-4 rounded-xl p-3 text-xs border border-[#ff4757]/30 bg-[#ff4757]/10 text-[#ff4757] flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Alert */}
        {successMsg && (
          <div className="mb-4 rounded-xl p-3.5 text-xs border border-[#2dd4ce]/30 bg-[#2dd4ce]/10 text-[#d8f3f0] space-y-2 font-mono text-left">
            <div className="flex items-center gap-2 text-[#2dd4ce] font-bold">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Recovery Link Dispatched</span>
            </div>
            <p className="text-[11.5px] leading-relaxed text-[#adc2b6]">{successMsg}</p>
            {devResetUrl && (
              <a
                href={devResetUrl}
                className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#2dd4ce]/20 hover:bg-[#2dd4ce]/30 text-[#2dd4ce] text-xs font-mono font-semibold transition"
              >
                <span>Open Password Reset Page</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        )}

        {/* Unified Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-left">
          {tab === "register" && (
            <div>
              <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
                Full Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Doe"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
                />
                <User className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
              </div>
            </div>
          )}

          <div>
            <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
              Email Address
            </label>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
              />
              <Mail className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
            </div>
          </div>

          {tab !== "forgot" && (
            <div>
              <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
                Password
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

              {/* Forgot password link directly under password input */}
              {tab === "login" && (
                <div className="flex justify-end mt-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      setTab("forgot");
                      setError("");
                      setSuccessMsg("");
                      setDevResetUrl(null);
                    }}
                    className="text-[11.5px] font-mono text-[#2dd4ce] hover:underline cursor-pointer transition-colors"
                  >
                    Forgot password?
                  </button>
                </div>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 w-full py-3 rounded-xl bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] text-[#060b10] font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-[#2dd4ce]/20 hover:brightness-110 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>
                  {tab === "forgot" ? "Dispatching Recovery Link..." : "Verifying Credentials..."}
                </span>
              </>
            ) : tab === "login" ? (
              <span>SIGN IN →</span>
            ) : tab === "register" ? (
              <span>CREATE ACCOUNT & LAUNCH →</span>
            ) : (
              <span>SEND RECOVERY LINK →</span>
            )}
          </button>
        </form>

        {/* Bottom Switcher */}
        <div className="mt-6 pt-4 border-t border-[#16323b] text-center">
          {tab === "forgot" ? (
            <button
              type="button"
              onClick={() => {
                setTab("login");
                setError("");
                setSuccessMsg("");
              }}
              className="inline-flex items-center gap-1.5 text-xs text-[#2dd4ce] font-semibold hover:underline cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Sign In</span>
            </button>
          ) : (
            <p className="text-xs text-[#8fa89b]">
              {tab === "login" ? "Don't have an account? " : "Already registered? "}
              <button
                type="button"
                onClick={() => {
                  setTab(tab === "login" ? "register" : "login");
                  setError("");
                  setSuccessMsg("");
                }}
                className="text-[#2dd4ce] font-semibold hover:underline cursor-pointer ml-1"
              >
                {tab === "login" ? "Create an account" : "Sign in instead"}
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
