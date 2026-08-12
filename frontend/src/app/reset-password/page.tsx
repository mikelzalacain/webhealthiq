"use client";

import { FormEvent, Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { apiFetch } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";

function ResetPasswordForm() {
  const { t } = useI18n();
  const search = useSearchParams();
  const token = search.get("token") || "";

  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError(t("auth.reset_invalid"));
      return;
    }
    if (password !== passwordConfirm) {
      setError(t("auth.password_mismatch"));
      return;
    }
    setBusy(true);
    try {
      const res = await apiFetch("/api/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({
          token,
          password,
          password_confirm: passwordConfirm,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string" ? data.detail : t("auth.reset_invalid")
        );
      }
      setOk(true);
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
          {t("auth.reset_title")}
        </h1>
        <p className="text-muted text-sm mb-8">{t("auth.reset_sub")}</p>

        {ok ? (
          <div className="space-y-4">
            <p className="text-sm text-ink bg-primary/10 border border-primary/20 rounded-md px-3 py-3">
              {t("auth.reset_ok")}
            </p>
            <Link href="/login" className="btn-primary inline-flex">
              {t("auth.login_cta")}
            </Link>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            {!token && (
              <p className="text-sm text-danger">{t("auth.reset_invalid")}</p>
            )}
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">
                {t("auth.password")}
              </label>
              <input
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
              />
              <p className="text-xs text-muted mt-1.5">{t("auth.password_hint")}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">
                {t("auth.password_confirm")}
              </label>
              <input
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
              />
            </div>
            {error && (
              <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
                {error}
              </p>
            )}
            <button
              type="submit"
              disabled={busy || !token}
              className="btn-primary w-full disabled:opacity-60"
            >
              {busy ? t("auth.busy") : t("auth.reset_cta")}
            </button>
            <p className="text-xs text-muted text-center">
              {t("legal.contact")}:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-[50vh]" />}>
      <ResetPasswordForm />
    </Suspense>
  );
}
