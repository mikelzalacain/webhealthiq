"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/AuthProvider";
import { apiFetch, getToken } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";
import SubscribeButton from "@/components/SubscribeButton";

function AccountContent() {
  const { t } = useI18n();
  const { user, loading: authLoading, refreshMe } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [brandName, setBrandName] = useState("");
  const [brandPrimary, setBrandPrimary] = useState("");
  const [busy, setBusy] = useState(false);
  const [portalBusy, setPortalBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [billingMsg, setBillingMsg] = useState<string | null>(null);
  const [billingError, setBillingError] = useState<string | null>(null);

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

  useEffect(() => {
    const billing = searchParams.get("billing");
    if (billing === "success") {
      setBillingMsg(t("billing.success"));
      void refreshMe();
    }
  }, [searchParams, refreshMe, t]);

  const plan = (user?.plan || "free").toLowerCase();
  const isAgency = plan === "agency";
  const isPaid = plan === "pro" || plan === "agency";

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

  const openPortal = async () => {
    setBillingError(null);
    setPortalBusy(true);
    try {
      const res = await apiFetch("/api/billing/portal", { method: "POST" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string" ? data.detail : t("billing.error")
        );
      }
      if (!data.url || typeof data.url !== "string") {
        throw new Error(t("billing.error"));
      }
      window.location.href = data.url;
    } catch (err: unknown) {
      setBillingError(err instanceof Error ? err.message : t("billing.error"));
      setPortalBusy(false);
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

        <div className="panel rounded-md p-6 mb-6 space-y-4">
          <h2 className="text-lg font-bold">{t("billing.title")}</h2>
          <p className="text-sm text-muted">{t("billing.subtitle")}</p>

          {billingMsg && <p className="text-sm text-success">{billingMsg}</p>}
          {billingError && (
            <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
              {billingError}
            </p>
          )}

          {isPaid ? (
            <button
              type="button"
              onClick={() => void openPortal()}
              disabled={portalBusy}
              className="btn-secondary w-full disabled:opacity-60"
            >
              {portalBusy ? t("billing.redirecting") : t("billing.manage")}
            </button>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-muted">{t("billing.upgrade_hint")}</p>
              <SubscribeButton plan="pro" className="btn-primary w-full text-center disabled:opacity-60" />
              <SubscribeButton
                plan="agency"
                className="btn-secondary w-full text-center disabled:opacity-60"
              />
            </div>
          )}

          {plan === "pro" && (
            <div className="pt-2">
              <p className="text-xs text-muted mb-2">{t("billing.upgrade_agency_hint")}</p>
              <SubscribeButton
                plan="agency"
                className="btn-secondary w-full text-center disabled:opacity-60"
              />
            </div>
          )}
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

export default function AccountPage() {
  return (
    <Suspense fallback={<div className="min-h-[50vh]" />}>
      <AccountContent />
    </Suspense>
  );
}
