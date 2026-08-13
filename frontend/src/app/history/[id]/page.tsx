"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import ScoreRing from "@/components/ScoreRing";
import { useAuth } from "@/lib/AuthProvider";
import { apiFetch, getToken } from "@/lib/authStorage";
import { downloadAuditPdf } from "@/lib/exportReportPdf";
import { useI18n } from "@/lib/i18n/LanguageProvider";

type AuditDetail = {
  id: number;
  url: string;
  overall_score: number | null;
  created_at: string;
  lang: string | null;
  result: {
    url?: string;
    overall_score?: number;
    modules?: Record<string, any>;
    timestamp?: string;
  } | null;
  insights: {
    title?: string;
    summary?: string;
    actions?: Array<{
      name?: string;
      status?: string;
      message?: string;
      recommendation?: string;
      module?: string;
    }>;
    total_issues?: number;
  } | null;
};

export default function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useI18n();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<AuditDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfBusy, setPdfBusy] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!getToken()) {
      router.replace(`/login?next=${encodeURIComponent(`/history/${id}`)}`);
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch(`/api/audits/${id}`);
        if (res.status === 401) {
          router.replace(`/login?next=${encodeURIComponent(`/history/${id}`)}`);
          return;
        }
        if (res.status === 404) {
          throw new Error(t("history.not_found"));
        }
        if (!res.ok) throw new Error(t("history.error"));
        const json = (await res.json()) as AuditDetail;
        if (!cancelled) setData(json);
      } catch (err: any) {
        if (!cancelled) setError(err?.message || t("history.error"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [authLoading, id, router, t]);

  const modules = data?.result?.modules || {};
  const score = data?.overall_score ?? data?.result?.overall_score ?? 0;
  const insights = data?.insights;
  const actions = insights?.actions || [];

  const handlePdf = async () => {
    if (!data?.result) return;
    try {
      setPdfBusy(true);
      await downloadAuditPdf(
        {
          url: data.result.url || data.url,
          overall_score: score,
          timestamp: data.result.timestamp || data.created_at,
          modules,
          insights: insights || data.result.insights || null,
        },
        {
          title: t("history.detail_title"),
          brand: user?.brand_name || "WebHealthIQ",
        }
      );
    } catch {
      alert(t("results.error_generic"));
    } finally {
      setPdfBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-32 flex items-center justify-center text-muted">
        {t("history.loading")}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen pt-32 px-4 flex flex-col items-center">
        <p className="text-danger mb-4">{error || t("history.not_found")}</p>
        <Link href="/history" className="btn-secondary">
          {t("history.back")}
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <div className="max-w-4xl mx-auto">
        <Link href="/history" className="text-sm text-primary font-medium mb-6 inline-block">
          ← {t("history.back")}
        </Link>

        <div className="panel rounded-md p-6 sm:p-8 mb-8 flex flex-col sm:flex-row gap-6 items-start sm:items-center justify-between">
          <div className="min-w-0">
            <h1 className="font-display text-2xl font-bold text-ink mb-2">
              {t("history.detail_title")}
            </h1>
            <a
              href={data.url}
              target="_blank"
              rel="noreferrer"
              className="text-muted hover:text-primary break-all"
            >
              {data.url}
            </a>
            <p className="text-xs text-muted mt-2">
              {data.created_at ? new Date(data.created_at).toLocaleString() : ""}
            </p>
            <button
              type="button"
              onClick={handlePdf}
              disabled={pdfBusy || !data.result}
              className="btn-primary mt-4 text-sm py-2 px-4 disabled:opacity-60"
            >
              {pdfBusy ? t("results.pdf_generating") : t("results.pdf")}
            </button>
          </div>
          <ScoreRing score={score} size={120} label={t("results.global")} />
        </div>

        {insights && (
          <section className="panel rounded-md p-6 mb-8">
            <h2 className="text-lg font-bold mb-2">{insights.title || t("results.ai_title")}</h2>
            <p className="text-sm text-muted mb-4">{insights.summary || t("results.ai_desc")}</p>
            {actions.length === 0 ? (
              <p className="text-sm text-muted">{t("results.ai_empty")}</p>
            ) : (
              <ul className="space-y-3">
                {actions.map((a, i) => (
                  <li key={i} className="border border-border rounded-md p-3 bg-surface-hover">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-xs font-bold uppercase ${
                          a.status === "fail" ? "text-danger" : "text-warning"
                        }`}
                      >
                        {a.status}
                      </span>
                      <span className="font-semibold text-ink text-sm">{a.name}</span>
                    </div>
                    {a.message && <p className="text-sm text-muted">{a.message}</p>}
                    {a.recommendation && (
                      <p className="text-xs text-muted-dark italic mt-1 border-l-2 border-primary/30 pl-2">
                        {a.recommendation}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        <div className="space-y-4">
          {Object.entries(modules).map(([key, mod]) => {
            if (!mod || typeof mod !== "object") return null;
            const m = mod as { score?: number; checks?: any[]; error?: string };
            return (
              <section key={key} className="panel rounded-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold capitalize text-ink">{key}</h3>
                  <span className="text-xl font-black text-ink">
                    {typeof m.score === "number" ? m.score : "—"}
                    <span className="text-sm text-muted font-normal">/100</span>
                  </span>
                </div>
                {m.error && <p className="text-sm text-danger">{m.error}</p>}
                <ul className="space-y-2">
                  {(m.checks || []).slice(0, 8).map((c: any, idx: number) => (
                    <li key={idx} className="text-sm border border-border/60 rounded-md p-3">
                      <span className="font-medium text-ink">{c.name}</span>
                      <span className="text-xs uppercase ml-2 text-muted">{c.status}</span>
                      {c.message && <p className="text-muted mt-1">{c.message}</p>}
                    </li>
                  ))}
                </ul>
              </section>
            );
          })}
        </div>
      </div>
    </div>
  );
}
