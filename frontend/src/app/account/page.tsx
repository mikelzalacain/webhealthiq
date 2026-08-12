"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthProvider";
import { apiFetch, getToken } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function AccountPage() {
  const { t } = useI18n();
  const { user, loading: authLoading, refreshMe } = useAuth();
  const router = useRouter();
  const [brandName, setBrandName] = useState("");
  const [brandPrimary, setBrandPrimary] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!getToken()) {
      router.replace(`/login?next=${encodeURIComponent("/account")}`);
      return;
    }
  }, [authLoading, router]);

  useEffect(() => {
    if (user) {
      setBrandName(user.brand_name || "");
      setBrandPrimary(user.brand_primary || "");
    }
  }, [user]);

  const isAgency = (user?.plan || "").toLowerCase() === "agency";

  const onSave = async (e: FormEvent) => {
    e.preventDefault();
    setMsg(null);
    setError(null);
    setBusy(true);
    try {
      const res = await apiFetch("/api/account/branding", {
        method: "PATCH",
        body: JSON.stringify({
          brand_name: brandName,
          brand_primary: brandPrimary,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string" ? data.detail : t("account.error")
        );
      }
      await refreshMe();
      setMsg(t("account.saved"));
    } catch (err: any) {
      setError(err?.message || t("account.error"));
    } finally {
      setBusy(false);
    }
  };

  if (authLoading || !user) {
    return <div className="min-h-screen pt-32 text-center text-muted">{t("auth.busy")}</div>;
  }

  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <div className="max-w-lg mx-auto">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">{t("account.title")}</h1>
        <p className="text-muted mb-8">{t("account.subtitle")}</p>

        <div className="panel rounded-md p-6 mb-6 space-y-3">
          <p className="text-sm text-muted">
            {t("auth.email")}: <strong className="text-ink">{user.email}</strong>
          </p>
          <p className="text-sm text-muted">
            {t("account.plan")}:{" "}
            <strong className="text-ink capitalize">{user.plan}</strong>
          </p>
          <p className="text-sm text-muted">
            {t("account.usage")}:{" "}
            <strong className="text-ink">
              {user.audits_used}/{user.audits_limit}
            </strong>{" "}
            ({user.year_month})
          </p>
          <Link href="/history" className="text-sm text-primary font-semibold inline-block mt-2">
            {t("nav.history")} →
          </Link>
        </div>

        <div className="panel rounded-md p-6">
          <h2 className="text-lg font-bold mb-1">{t("account.branding")}</h2>
          <p className="text-sm text-muted mb-4">{t("account.branding_desc")}</p>

          {!isAgency ? (
            <p className="text-sm text-muted">{t("account.agency_only")}</p>
          ) : (
            <form onSubmit={onSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">
                  {t("account.brand_name")}
                </label>
                <input
                  type="text"
                  maxLength={120}
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">
                  {t("account.brand_primary")}
                </label>
                <input
                  type="text"
                  maxLength={16}
                  placeholder="#0F766E"
                  value={brandPrimary}
                  onChange={(e) => setBrandPrimary(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface px-3 py-2.5 text-ink focus:outline-none focus:border-primary"
                />
              </div>
              {msg && <p className="text-sm text-success">{msg}</p>}
              {error && (
                <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
                  {error}
                </p>
              )}
              <button type="submit" disabled={busy} className="btn-primary disabled:opacity-60">
                {busy ? t("auth.busy") : t("account.save")}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
