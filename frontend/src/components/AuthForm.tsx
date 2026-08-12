"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/AuthProvider";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function LoginForm({ mode }: { mode: "login" | "register" }) {
  const { t } = useI18n();
  const { login, register } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const next = search.get("next") || "/";

  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const title = useMemo(
    () => (mode === "login" ? t("auth.login_title") : t("auth.register_title")),
    [mode, t]
  );

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (mode === "register") {
      if (password !== passwordConfirm) {
        setError(t("auth.password_mismatch"));
        return;
      }
      if (!acceptTerms) {
        setError(t("auth.terms_required"));
        return;
      }
    }

    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register({
          email,
          password,
          password_confirm: passwordConfirm,
          full_name: fullName,
          company: company.trim() || undefined,
          accept_terms: acceptTerms,
        });
      }
      router.push(next.startsWith("/") ? next : "/");
    } catch (err: any) {
      setError(err?.message || t("auth.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-[70vh] pt-28 pb-16 px-4 flex items-start justify-center">
      <div className="w-full max-w-md panel rounded-md p-8">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">{title}</h1>
        <p className="text-muted text-sm mb-8">
          {mode === "login" ? t("auth.login_sub") : t("auth.register_sub")}
        </p>

        <form onSubmit={onSubmit} className="space-y-4">
          {mode === "register" && (
            <>
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">
                  {t("auth.full_name")}
                </label>
                <input
                  type="text"
                  required
                  minLength={2}
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">
                  {t("auth.company")}{" "}
                  <span className="text-muted font-normal">({t("auth.optional")})</span>
                </label>
                <input
                  type="text"
                  autoComplete="organization"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
                />
              </div>
            </>
          )}

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

          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">
              {t("auth.password")}
            </label>
            <input
              type="password"
              required
              minLength={8}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
            />
            {mode === "register" && (
              <p className="text-xs text-muted mt-1.5">{t("auth.password_hint")}</p>
            )}
          </div>

          {mode === "register" && (
            <>
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

              <label className="flex items-start gap-2.5 text-sm text-muted cursor-pointer">
                <input
                  type="checkbox"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                  className="mt-1"
                  required
                />
                <span>
                  {t("auth.terms_prefix")}{" "}
                  <Link href="/#pricing" className="text-primary font-medium">
                    {t("auth.terms_link")}
                  </Link>{" "}
                  {t("auth.and")}{" "}
                  <Link href="/#pricing" className="text-primary font-medium">
                    {t("auth.privacy_link")}
                  </Link>
                  .
                </span>
              </label>
            </>
          )}

          {error && (
            <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <button type="submit" disabled={busy} className="btn-primary w-full disabled:opacity-60">
            {busy
              ? t("auth.busy")
              : mode === "login"
                ? t("auth.login_cta")
                : t("auth.register_cta")}
          </button>
        </form>

        <p className="text-sm text-muted mt-6 text-center">
          {mode === "login" ? (
            <>
              {t("auth.no_account")}{" "}
              <Link href={`/register?next=${encodeURIComponent(next)}`} className="text-primary font-semibold">
                {t("auth.register_link")}
              </Link>
            </>
          ) : (
            <>
              {t("auth.has_account")}{" "}
              <Link href={`/login?next=${encodeURIComponent(next)}`} className="text-primary font-semibold">
                {t("auth.login_link")}
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
