"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthProvider";
import { apiFetch, getToken } from "@/lib/authStorage";
import { useI18n } from "@/lib/i18n/LanguageProvider";

type AuditItem = {
  id: number;
  url: string;
  overall_score: number | null;
  created_at: string;
  lang: string | null;
};

export default function HistoryPage() {
  const { t } = useI18n();
  const { loading: authLoading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!getToken()) {
      router.replace(`/login?next=${encodeURIComponent("/history")}`);
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch("/api/audits");
        if (res.status === 401) {
          router.replace(`/login?next=${encodeURIComponent("/history")}`);
          return;
        }
        if (!res.ok) throw new Error(t("history.error"));
        const data = (await res.json()) as AuditItem[];
        if (!cancelled) setItems(data);
      } catch (err: any) {
        if (!cancelled) setError(err?.message || t("history.error"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [authLoading, router, t]);

  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">{t("history.title")}</h1>
        <p className="text-muted mb-8">{t("history.subtitle")}</p>

        {loading && <p className="text-muted">{t("history.loading")}</p>}
        {error && (
          <p className="text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
            {error}
          </p>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="panel rounded-md p-8 text-center">
            <p className="text-muted mb-4">{t("history.empty")}</p>
            <Link href="/#audit" className="btn-primary inline-flex">
              {t("nav.cta")}
            </Link>
          </div>
        )}

        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id}>
              <Link
                href={`/history/${item.id}`}
                className="panel rounded-md p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-primary/40 transition-colors block"
              >
                <div className="min-w-0">
                  <p className="font-medium text-ink truncate">{item.url}</p>
                  <p className="text-xs text-muted mt-1">
                    {item.created_at ? new Date(item.created_at).toLocaleString() : "—"}
                    {item.lang ? ` · ${item.lang.toUpperCase()}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <span className="text-sm text-muted">
                    {t("history.score")}:{" "}
                    <strong className="text-ink">{item.overall_score ?? "—"}</strong>
                  </span>
                  <span className="text-sm font-semibold text-primary">{t("history.open")} →</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
