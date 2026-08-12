"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthProvider";
import { apiFetch, getToken } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";

type PaidPlan = "pro" | "agency";

type Props = {
  plan: PaidPlan;
  className?: string;
  label?: string;
};

export default function SubscribeButton({ plan, className, label }: Props) {
  const { t } = useI18n();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const defaultLabel =
    plan === "pro" ? t("billing.subscribe_pro") : t("billing.subscribe_agency");

  const onClick = async () => {
    setError(null);
    if (authLoading) return;

    if (!getToken() || !user) {
      router.push(
        `/login?next=${encodeURIComponent(`/account?checkout=${plan}`)}`
      );
      return;
    }

    setBusy(true);
    try {
      const res = await apiFetch("/api/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : res.status === 503
              ? t("billing.unavailable")
              : t("billing.error");
        throw new Error(detail);
      }
      if (!data.url || typeof data.url !== "string") {
        throw new Error(t("billing.error"));
      }
      window.location.assign(data.url);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t("billing.error");
      setError(msg);
      setBusy(false);
    }
  };

  return (
    <div className="w-full">
      <button
        type="button"
        onClick={() => void onClick()}
        disabled={busy || authLoading}
        className={className || "btn-primary w-full text-center disabled:opacity-60"}
      >
        {busy ? t("billing.redirecting") : label || defaultLabel}
      </button>
      {error && (
        <p className="text-xs text-danger mt-2 text-center" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
