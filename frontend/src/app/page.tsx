"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ScoreRing from "@/components/ScoreRing";
import SubscribeButton from "@/components/SubscribeButton";
import { useI18n } from "@/lib/i18n/LanguageProvider";
import { useAuth } from "@/lib/AuthProvider";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { t, lang } = useI18n();
  const { user, loading: authLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    let targetUrl = url;
    if (!/^https?:\/\//i.test(targetUrl)) {
      targetUrl = "https://" + targetUrl;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ url: targetUrl, lang });
      const resultsPath = `/results?${params.toString()}`;
      if (!authLoading && !user) {
        router.push(`/login?next=${encodeURIComponent(resultsPath)}`);
        return;
      }
      router.push(resultsPath);
    } catch (err: any) {
      setError(err.message || t("results.error_generic"));
      setLoading(false);
    }
  };

  const modules = [
    { title: t("mod.seo"), desc: t("mod.seo_desc"), tone: "bg-primary/10 text-primary-dark" },
    { title: t("mod.perf"), desc: t("mod.perf_desc"), tone: "bg-accent/10 text-[#9a3412]" },
    { title: t("mod.a11y"), desc: t("mod.a11y_desc"), tone: "bg-success/10 text-[#166534]" },
    { title: t("mod.sec"), desc: t("mod.sec_desc"), tone: "bg-warning/15 text-[#854d0e]" },
    { title: t("mod.gdpr"), desc: t("mod.gdpr_desc"), tone: "bg-ink/5 text-ink" },
  ];

  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-grid z-0 pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <section className="pt-36 pb-24 md:pt-44 md:pb-28">
          <p className="font-display text-4xl sm:text-5xl md:text-6xl font-bold text-ink mb-6 animate-fade-up stagger-1">
            {t("hero.brand")}
          </p>
          <h1 className="font-display text-3xl sm:text-4xl md:text-5xl font-semibold text-ink max-w-3xl leading-[1.1] mb-5 animate-fade-up stagger-2">
            {t("hero.title_before")}{" "}
            <span className="accent-underline">{t("hero.title_accent")}</span>
            {t("hero.title_after")}
          </h1>
          <p className="text-lg text-muted max-w-xl mb-10 animate-fade-up stagger-3">
            {t("hero.subtitle")}
          </p>

          <div id="audit" className="max-w-2xl animate-fade-up stagger-4">
            <form
              onSubmit={handleSubmit}
              className="panel rounded-md p-2 flex flex-col sm:flex-row gap-2 shadow-[0_12px_40px_rgba(20,36,31,0.06)]"
            >
              <label className="sr-only" htmlFor="audit-url">
                {t("hero.url_label")}
              </label>
              <input
                id="audit-url"
                type="text"
                required
                placeholder={t("hero.placeholder")}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 bg-transparent text-ink placeholder-muted-dark rounded-md px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-primary/30 text-lg"
              />
              <button
                type="submit"
                disabled={loading}
                aria-busy={loading}
                aria-label={loading ? t("hero.analyze") : undefined}
                className="btn-primary flex items-center justify-center min-w-[148px]"
              >
                {loading ? (
                  <span
                    className="w-5 h-5 border-2 border-white/40 border-t-white rounded-sm animate-spin"
                    aria-hidden="true"
                  />
                ) : (
                  t("hero.analyze")
                )}
              </button>
            </form>
            {error && (
              <p className="mt-3 text-sm text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
                {error}
              </p>
            )}
            <p className="mt-3 text-sm text-muted">{t("hero.free")}</p>
          </div>
        </section>

        <section id="features" className="py-20 border-t border-border">
          <div className="max-w-2xl mb-12">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-ink mb-3">
              {t("features.title")}
            </h2>
            <p className="text-muted text-lg">{t("features.subtitle")}</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {modules.map((m) => (
              <article key={m.title} className="panel rounded-md p-6">
                <span className={`inline-block text-xs font-semibold tracking-wide uppercase px-2 py-1 rounded-md mb-4 ${m.tone}`}>
                  {m.title}
                </span>
                <p className="text-muted leading-relaxed">{m.desc}</p>
              </article>
            ))}
            <article className="panel rounded-md p-6 border-dashed border-2 bg-transparent">
              <span className="inline-block text-xs font-semibold tracking-wide uppercase px-2 py-1 rounded-md mb-4 bg-surface-hover text-muted">
                {t("mod.ai")}
              </span>
              <p className="text-muted leading-relaxed mb-3">{t("mod.ai_desc")}</p>
              <span className="text-xs font-mono uppercase tracking-wider text-primary">
                {t("mod.ai_soon")}
              </span>
            </article>
          </div>
        </section>

        <section id="how-it-works" className="py-20 border-t border-border">
          <div className="grid lg:grid-cols-2 gap-14 items-center">
            <div>
              <h2 className="font-display text-3xl md:text-4xl font-bold text-ink mb-4">
                {t("method.title")}
              </h2>
              <p className="text-muted text-lg mb-8">{t("method.subtitle")}</p>
              <ol className="space-y-5">
                {[
                  [t("method.s1"), t("method.s1_desc")],
                  [t("method.s2"), t("method.s2_desc")],
                  [t("method.s3"), t("method.s3_desc")],
                ].map(([title, desc], i) => (
                  <li key={title} className="flex gap-4">
                    <span className="font-mono text-sm text-primary mt-0.5 w-6">0{i + 1}</span>
                    <div>
                      <h3 className="font-semibold text-ink mb-1">{title}</h3>
                      <p className="text-sm text-muted">{desc}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>

            <div className="panel rounded-md p-8">
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-border">
                <span className="text-xs font-mono uppercase tracking-[0.14em] text-muted">
                  {t("method.demo")}
                </span>
              </div>
              <div className="flex justify-center mb-8">
                <ScoreRing score={78} size={180} strokeWidth={10} label="Health Score" />
              </div>
              <div className="space-y-3">
                {[
                  { label: "SEO", score: 92 },
                  { label: t("mod.perf"), score: 65 },
                  { label: t("mod.a11y"), score: 85 },
                  { label: t("mod.sec"), score: 95 },
                  { label: t("mod.gdpr"), score: 50 },
                ].map((metric) => (
                  <div key={metric.label} className="flex items-center gap-3 text-sm">
                    <span className="w-28 text-muted truncate">{metric.label}</span>
                    <div className="flex-1 h-2 bg-surface-hover overflow-hidden rounded-sm">
                      <div className="h-full bg-primary" style={{ width: `${metric.score}%` }} />
                    </div>
                    <span className="w-8 text-right font-mono text-ink">{metric.score}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="pricing" className="py-20 border-t border-border mb-8">
          <div className="max-w-2xl mb-12">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-ink mb-3">
              {t("pricing.title")}
            </h2>
            <p className="text-muted text-lg">{t("pricing.subtitle")}</p>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            <div className="panel rounded-md p-7 flex flex-col">
              <h3 className="font-display text-xl font-bold text-ink mb-1">{t("pricing.basic")}</h3>
              <p className="text-sm text-muted mb-6">{t("pricing.basic_desc")}</p>
              <p className="mb-6">
                <span className="font-display text-4xl font-bold text-ink">0€</span>
                <span className="text-muted">{t("pricing.month")}</span>
              </p>
              <ul className="space-y-3 text-sm text-muted mb-8 flex-1">
                <li>{t("pricing.b1")}</li>
                <li>{t("pricing.b2")}</li>
                <li>{t("pricing.b3")}</li>
              </ul>
              <a href="/#audit" className="btn-secondary w-full text-center">
                {t("pricing.start")}
              </a>
            </div>

            <div className="panel rounded-md p-7 flex flex-col border-primary border-2 relative">
              <span className="absolute -top-3 left-6 bg-primary text-white text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 rounded-sm">
                {t("pricing.recommended")}
              </span>
              <h3 className="font-display text-xl font-bold text-ink mb-1">{t("pricing.pro")}</h3>
              <p className="text-sm text-muted mb-6">{t("pricing.pro_desc")}</p>
              <p className="mb-6">
                <span className="font-display text-4xl font-bold text-ink">{t("pricing.pro_price")}</span>
                <span className="text-muted">{t("pricing.month")}</span>
              </p>
              <ul className="space-y-3 text-sm text-ink mb-8 flex-1">
                <li>{t("pricing.p1")}</li>
                <li>{t("pricing.p2")}</li>
                <li>{t("pricing.p3")}</li>
                <li>{t("pricing.p4")}</li>
              </ul>
              <SubscribeButton plan="pro" />
            </div>

            <div className="panel rounded-md p-7 flex flex-col">
              <h3 className="font-display text-xl font-bold text-ink mb-1">{t("pricing.agency")}</h3>
              <p className="text-sm text-muted mb-6">{t("pricing.agency_desc")}</p>
              <p className="mb-6">
                <span className="font-display text-4xl font-bold text-ink">{t("pricing.agency_price")}</span>
                <span className="text-muted">{t("pricing.month")}</span>
              </p>
              <ul className="space-y-3 text-sm text-muted mb-8 flex-1">
                <li>{t("pricing.a1")}</li>
                <li>{t("pricing.a2")}</li>
                <li>{t("pricing.a3")}</li>
                <li>{t("pricing.a4")}</li>
              </ul>
              <SubscribeButton
                plan="agency"
                className="btn-secondary w-full text-center disabled:opacity-60"
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
