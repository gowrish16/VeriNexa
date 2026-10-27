import React, { useState, useEffect } from "react";
import { Shield, Key, CheckCircle2, AlertCircle, Loader2, ArrowRight, ArrowLeft } from "lucide-react";

export default function ResetPasswordPage({ onGoLogin }) {
  const [token, setToken] = useState("");
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [targetEmail, setTargetEmail] = useState("");
  const [tokenError, setTokenError] = useState("");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const t = urlParams.get("token") || "";
    setToken(t);

    if (!t) {
      setVerifying(false);
      setTokenValid(false);
      setTokenError("No recovery token was found in the URL. Please verify your reset link.");
      return;
    }

    // Verify token with backend
    fetch(`http://127.0.0.1:8000/api/auth/verify-reset-token?token=${encodeURIComponent(t)}`)
      .then((res) => res.json())
      .then((data) => {
        setVerifying(false);
        if (data.valid) {
          setTokenValid(true);
          setTargetEmail(data.email || "");
        } else {
          setTokenValid(false);
          setTokenError(data.error || "This recovery link is invalid or has expired.");
        }
      })
      .catch((err) => {
        setVerifying(false);
        setTokenValid(false);
        setTokenError("Could not reach verification service. Please try again.");
      });
  }, []);

  const handleReset = async (e) => {
    e.preventDefault();
    setSaveError("");

    if (!password || !confirmPassword) {
      setSaveError("Please fill in both password fields.");
      return;
    }

    if (password.length < 6) {
      setSaveError("Password must be at least 6 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setSaveError("Passwords do not match. Please re-enter.");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: token,
          new_password: password,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to reset password.");
      }

      setSaveSuccess(true);
    } catch (err) {
      setSaveError(err.message || "An unexpected error occurred while resetting password.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060b10] flex flex-col items-center justify-center p-4 relative text-[#f4f7f5] selection:bg-[#2dd4ce]/25 selection:text-[#2dd4ce]">
      {/* Background ambient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#2dd4ce]/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Main Card */}
      <div className="relative z-10 w-full max-w-md rounded-2xl p-6 sm:p-8 bg-[#09151e]/95 border border-[#16323b] shadow-2xl shadow-black/80">
        {/* Brand Header */}
        <div className="mb-6 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0e272b] border border-[#2dd4ce]/30 mb-2">
            <Shield className="w-3.5 h-3.5 text-[#2dd4ce]" />
            <span className="text-[10.5px] font-mono tracking-widest text-[#2dd4ce] uppercase font-bold">
              VERINEXA CREDENTIAL RECOVERY
            </span>
          </div>
          <h1 className="font-display text-2xl font-bold text-white tracking-tight">
            Set New Password
          </h1>
          <p className="text-xs text-[#8fa89b] mt-1 leading-relaxed">
            {targetEmail
              ? `Enter your updated credentials for ${targetEmail}`
              : "Create a secure new password for your VeriNexa account."}
          </p>
        </div>

        {/* Verifying Token State */}
        {verifying && (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 text-[#2dd4ce] animate-spin" />
            <span className="text-xs font-mono text-[#8fa89b]">Validating security token...</span>
          </div>
        )}

        {/* Invalid or Expired Token */}
        {!verifying && !tokenValid && (
          <div className="space-y-5 text-left">
            <div className="rounded-xl p-4 text-xs border border-[#ff4757]/30 bg-[#ff4757]/10 text-[#ff4757] flex items-start gap-3 font-mono">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Recovery Link Invalid</p>
                <p className="mt-1 text-[11px] text-[#ff808b] leading-relaxed">{tokenError}</p>
              </div>
            </div>
            <button
              onClick={onGoLogin}
              className="w-full py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white font-mono text-xs border border-white/10 flex items-center justify-center gap-2 transition cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Login Screen</span>
            </button>
          </div>
        )}

        {/* Success State */}
        {!verifying && tokenValid && saveSuccess && (
          <div className="space-y-5 text-left">
            <div className="rounded-xl p-4 text-xs border border-[#2dd4ce]/30 bg-[#2dd4ce]/10 text-[#2dd4ce] flex items-start gap-3 font-mono">
              <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Password Reset Successfully</p>
                <p className="mt-1 text-[11px] text-[#adc2b6] leading-relaxed">
                  Your new password is now active across all clinical audit services.
                </p>
              </div>
            </div>
            <button
              onClick={onGoLogin}
              className="w-full py-3 rounded-xl bg-[#2dd4ce] hover:bg-[#26b8b3] text-[#060b10] font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-[#2dd4ce]/20 transition cursor-pointer"
            >
              <span>SIGN IN WITH NEW PASSWORD</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* New Password Form */}
        {!verifying && tokenValid && !saveSuccess && (
          <form onSubmit={handleReset} className="flex flex-col gap-4 text-left">
            {saveError && (
              <div className="rounded-xl p-3 text-xs border border-[#ff4757]/30 bg-[#ff4757]/10 text-[#ff4757] flex items-center gap-2 font-mono">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{saveError}</span>
              </div>
            )}

            <div>
              <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
                New Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
                />
                <Key className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
              </div>
            </div>

            <div>
              <label className="block mb-1 text-[11px] font-mono uppercase text-[#8fa89b]">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#4d6359] focus:border-[#2dd4ce] focus:outline-none transition"
                />
                <Key className="w-4 h-4 text-[#8fa89b] absolute left-3 top-3" />
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="mt-2 w-full py-3 rounded-xl bg-gradient-to-r from-[#2dd4ce] via-[#14b8a6] to-[#0d9488] text-[#060b10] font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-[#2dd4ce]/20 hover:brightness-110 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving New Password...</span>
                </>
              ) : (
                <span>SAVE NEW PASSWORD →</span>
              )}
            </button>

            <div className="pt-3 border-t border-[#16323b] text-center">
              <button
                type="button"
                onClick={onGoLogin}
                className="text-xs text-[#8fa89b] hover:text-[#2dd4ce] transition-colors cursor-pointer"
              >
                ← Return to Sign In
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
