"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function ForgotPasswordPage() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await apiFetch("/api/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          typeof data.detail === "string" ? data.detail : t("auth.error")
        );
      }
      setSent(true);
    } catch (err: any) {
      setError(err?.message || t("auth.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-[70vh] pt-28 pb-16 px-4 flex items-start justify-center">
      <div className="w-full max-w-md panel rounded-md p-8">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          {t("auth.forgot_title")}
        </h1>
        <p className="text-muted text-sm mb-8">{t("auth.forgot_sub")}</p>

        {sent ? (
          <div className="space-y-4">
            <p className="text-sm text-ink bg-primary/10 border border-primary/20 rounded-md px-3 py-3">
              {t("auth.forgot_sent")}
            </p>
            <p className="text-xs text-muted">
              {t("legal.contact")}:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
            </p>
            <Link href="/login" className="text-primary font-semibold text-sm">
              {t("auth.login_link")}
            </Link>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">
                {t("auth.email")}
              </label>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
              />
            </div>
            {error && (
              <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
                {error}
              </p>
            )}
            <button type="submit" disabled={busy} className="btn-primary w-full disabled:opacity-60">
              {busy ? t("auth.busy") : t("auth.forgot_cta")}
            </button>
            <p className="text-sm text-center text-muted">
              <Link href="/login" className="text-primary font-semibold">
                {t("auth.login_link")}
              </Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
