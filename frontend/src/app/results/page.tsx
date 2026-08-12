"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ScoreRing from "@/components/ScoreRing";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/LanguageProvider";
import type { Lang } from "@/lib/i18n/translations";

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const urlParam = searchParams.get("url");
  const langParam = searchParams.get("lang");
  const { t, lang: uiLang, setLang } = useI18n();
  const auditLang = (langParam === 'en' || langParam === 'eu' || langParam === 'es')
    ? (langParam as Lang)
    : uiLang;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (langParam && ['es','en','eu'].includes(langParam) && langParam !== uiLang) {
      setLang(langParam as Lang);
    }
  }, [langParam, uiLang, setLang]);

  useEffect(() => {
    if (!urlParam) {
      router.push("/");
      return;
    }

    const fetchAudit = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiBase}/api/audit`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: urlParam, lang: auditLang }),
        });

        if (!response.ok) {
          let detail = t("results.error_backend");
          try {
            const errBody = await response.json();
            if (errBody?.detail) {
              detail = typeof errBody.detail === "string"
                ? errBody.detail
                : JSON.stringify(errBody.detail);
            }
          } catch {
            // ignore JSON parse errors
          }
          throw new Error(detail);
        }

        const data = await response.json();
        setResult(data);
      } catch (err: any) {
        setError(err.message || t("results.error_generic"));
      } finally {
        setLoading(false);
      }
    };

    fetchAudit();
  }, [urlParam, router, auditLang, t]);

  if (loading) {
    return (
      <div className="min-h-screen pt-32 pb-20 flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-radial-gradient z-0"></div>
        <div className="relative z-10 flex flex-col items-center text-center">
          <div className="w-24 h-24 relative mb-8">
            <div className="absolute inset-0 rounded-md border-4 border-surface-hover"></div>
            <div className="absolute inset-0 rounded-md border-4 border-primary border-t-transparent animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 rounded-md bg-primary/20 "></div>
            </div>
          </div>
          <h2 className="text-2xl font-bold mb-2">{t("results.auditing", { url: urlParam || "" })}</h2>
          <p className="text-muted">{t("results.auditing_hint")}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-32 pb-20 flex flex-col items-center justify-center px-4">
        <div className="panel p-8 rounded-md max-w-lg text-center border-danger/30 relative overflow-hidden">
           <div className="absolute top-0 inset-x-0 h-1 bg-danger"></div>
           <div className="w-16 h-16 rounded-md bg-danger/10 text-danger flex items-center justify-center mx-auto mb-6">
             <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
             </svg>
           </div>
           <h2 className="text-2xl font-bold mb-4">{t("results.error_title")}</h2>
           <p className="text-muted mb-8">{error}</p>
           <Link href="/" className="btn-secondary w-full inline-block">
             {t("results.back")}
           </Link>
        </div>
      </div>
    );
  }

  if (!result) return null;

  // Calculate a fake overall score for MVP
  const seoScore = result.modules?.seo?.score || 0;
  const perfScore = result.modules?.performance?.score || 0;
  const hasPerf = result.modules?.performance && result.modules.performance.score > 0;
  
  const overallScore = result.overall_score || seoScore;

  return (
    <div className="min-h-screen pt-32 pb-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-radial-gradient z-0"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 mb-12 bg-surface border border-border p-8 rounded-md animate-fade-up">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{t("results.report")}</h1>
              <span className="px-3 py-1 bg-primary/10 text-primary text-xs font-bold rounded-md border border-primary/20">
                {t("results.mvp")}
              </span>
            </div>
            <a href={result.url} target="_blank" rel="noreferrer" className="text-muted hover:text-primary transition-colors flex items-center gap-2 text-lg break-all">
              {result.url}
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
          <div className="flex items-center justify-center shrink-0">
             <ScoreRing score={overallScore} size={160} label={t("results.global")} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - Left Column (2/3) */}
          <div className="lg:col-span-2 space-y-8 animate-fade-up stagger-1">
            
            {/* SEO Section */}
            <section className="card overflow-hidden">
              <div className="p-6 border-b border-border bg-surface-hover/50 flex items-center justify-between">
                <div className="flex items-center gap-4">
                   <div className="w-12 h-12 rounded-md bg-primary/20 text-primary flex items-center justify-center">
                     <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                     </svg>
                   </div>
                   <div>
                     <h2 className="text-xl font-bold">{t("results.seo")}</h2>
                     <p className="text-sm text-muted">{t("results.seo_sub")}</p>
                   </div>
                </div>
                <div className={`text-3xl font-black ${seoScore >= 90 ? 'text-success' : seoScore >= 50 ? 'text-warning' : 'text-danger'}`}>
                  {seoScore}<span className="text-lg text-muted">/100</span>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Check list mapped from API */}
                {result.modules?.seo?.checks?.map((check: any, idx: number) => (
                  <div key={idx} className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between p-4 rounded-md border border-border bg-surface-hover">
                    <div className="flex-1 w-full">
                      <div className="flex items-center gap-2 mb-1">
                        {check.status === 'pass' ? (
                          <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        ) : check.status === 'warning' ? (
                          <svg className="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                        ) : (
                          <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                        )}
                        <span className="font-semibold text-ink">{check.name}</span>
                      </div>
                      
                      <p className={`text-sm mb-2 ${check.status === 'fail' ? 'text-danger' : check.status === 'warning' ? 'text-warning' : 'text-muted'}`}>
                        {check.message}
                      </p>
                      
                      {check.status !== 'pass' && (
                        <p className="text-xs text-muted-dark italic border-l-2 border-primary/30 pl-2 mt-2">{t("results.recommendation")}: {check.recommendation}</p>
                      )}
                      
                      {/* Show additional data if present (like H1 tags or missing alts) */}
                      {check.data && Object.keys(check.data).length > 0 && typeof check.data === 'object' && (
                        <div className="mt-3 w-full bg-surface p-3 rounded border border-border/50 text-xs text-muted-dark overflow-x-auto">
                           <pre>{JSON.stringify(check.data, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Performance Section */}
            {hasPerf ? (
              <section className="card overflow-hidden">
                <div className="p-6 border-b border-border bg-surface-hover/50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">{t("results.perf")}</h2>
                      <p className="text-sm text-muted">{t("results.perf_sub")}</p>
                    </div>
                  </div>
                  <div className={`text-3xl font-black ${perfScore >= 90 ? 'text-success' : perfScore >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {perfScore}<span className="text-lg text-muted">/100</span>
                  </div>
                </div>
                
                <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-md border border-border bg-surface flex flex-col justify-between">
                    <span className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">First Contentful Paint (FCP)</span>
                    <span className="text-2xl font-bold text-ink">{result.modules.performance.fcp}</span>
                  </div>
                  <div className="p-4 rounded-md border border-border bg-surface flex flex-col justify-between">
                    <span className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Largest Contentful Paint (LCP)</span>
                    <span className="text-2xl font-bold text-ink">{result.modules.performance.lcp}</span>
                  </div>
                  <div className="p-4 rounded-md border border-border bg-surface flex flex-col justify-between sm:col-span-2">
                    <span className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Cumulative Layout Shift (CLS)</span>
                    <span className="text-2xl font-bold text-ink">{result.modules.performance.cls}</span>
                  </div>
                </div>
                
                {result.modules.performance.checks && result.modules.performance.checks.length > 0 && (
                  <div className="px-6 pb-6 space-y-4 border-t border-border/50 pt-6">
                     <h3 className="text-sm font-semibold text-ink tracking-wider uppercase mb-2">{t("results.breakdown")}</h3>
                     {result.modules.performance.checks.map((check: any, idx: number) => (
                       <div key={idx} className="flex flex-col gap-2 p-4 rounded-md border border-border bg-surface-hover">
                         <div className="flex items-center gap-2">
                           {check.status === 'pass' ? (
                             <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                           ) : check.status === 'warning' ? (
                             <svg className="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                           ) : (
                             <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                           )}
                           <span className="font-semibold text-ink">{check.name}</span>
                         </div>
                         <p className="text-sm text-muted">{check.message}</p>
                         {check.status !== 'pass' && (
                           <p className="text-xs text-muted-dark italic border-l-2 border-primary/30 pl-2">{t("results.recommendation")}: {check.recommendation}</p>
                         )}
                       </div>
                     ))}
                  </div>
                )}
              </section>
            ) : (
               <section className="card overflow-hidden border-dashed border-border/50 bg-transparent">
                 <div className="p-8 text-center flex flex-col items-center">
                   <div className="w-16 h-16 rounded-md bg-surface-hover flex items-center justify-center text-muted-dark mb-4">
                     <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                   </div>
                   <h3 className="text-lg font-bold mb-2">{t("results.perf_unavailable")}</h3>
<p className="text-sm text-muted max-w-md mx-auto">{t("results.perf_unavailable_desc")}</p>
                 </div>
               </section>
            )}

            {/* Accessibility Section */}
            {result.modules?.accessibility && !result.modules.accessibility.error ? (
              <section className="card overflow-hidden">
                <div className="p-6 border-b border-border bg-surface-hover/50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">{t("results.a11y")}</h2>
                      <p className="text-sm text-muted">{t("results.a11y_sub")}</p>
                    </div>
                  </div>
                  <div className={`text-3xl font-black ${result.modules.accessibility.score >= 90 ? 'text-success' : result.modules.accessibility.score >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {result.modules.accessibility.score}<span className="text-lg text-muted">/100</span>
                  </div>
                </div>
                
                <div className="p-6 space-y-4">
                   {result.modules.accessibility.checks.map((check: any, idx: number) => (
                     <div key={idx} className="flex flex-col gap-2 p-4 rounded-md border border-border bg-surface-hover">
                       <div className="flex items-center gap-2">
                         {check.status === 'pass' ? (
                           <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                         ) : check.status === 'warning' ? (
                           <svg className="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                         ) : (
                           <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                         )}
                         <span className="font-semibold text-ink">{check.name}</span>
                       </div>
                       <p className="text-sm text-muted">{check.message}</p>
                       {check.status !== 'pass' && (
                         <>
                           <p className="text-xs text-muted-dark italic border-l-2 border-primary/30 pl-2">{t("results.recommendation")}: {check.recommendation}</p>
                           {check.data && check.data.help_url && (
                             <a href={check.data.help_url} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline mt-1 block">{t("results.more_info")}</a>
                           )}
                         </>
                       )}
                     </div>
                   ))}
                </div>
              </section>
            ) : result.modules?.accessibility?.error ? (
               <section className="card p-6 border-dashed border-danger/30 bg-danger/5 flex flex-col items-center text-center">
                   <h3 className="text-lg font-bold text-danger mb-2">{t("results.a11y_error")}</h3>
                   <p className="text-sm text-danger">{result.modules.accessibility.error}</p>
               </section>
            ) : null}

            {/* Security Section */}
            {result.modules?.security && (
              <section className="card overflow-hidden">
                <div className="p-6 border-b border-border bg-surface-hover/50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-md bg-rose-500/20 text-rose-400 flex items-center justify-center">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">{t("results.security")}</h2>
                      <p className="text-sm text-muted">{t("results.security_sub")}</p>
                    </div>
                  </div>
                  <div className={`text-3xl font-black ${result.modules.security.score >= 90 ? 'text-success' : result.modules.security.score >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {result.modules.security.score}<span className="text-lg text-muted">/100</span>
                  </div>
                </div>
                
                <div className="p-6 space-y-4">
                   {result.modules.security.checks.map((check: any, idx: number) => (
                     <div key={idx} className="flex flex-col gap-2 p-4 rounded-md border border-border bg-surface-hover">
                       <div className="flex items-center gap-2">
                         {check.status === 'pass' ? (
                           <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                         ) : check.status === 'warning' ? (
                           <svg className="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                         ) : (
                           <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                         )}
                         <span className="font-semibold text-ink">{check.name}</span>
                       </div>
                       <p className="text-sm text-muted">{check.message}</p>
                       {check.status !== 'pass' && (
                         <p className="text-xs text-muted-dark italic border-l-2 border-primary/30 pl-2">{t("results.recommendation")}: {check.recommendation}</p>
                       )}
                     </div>
                   ))}
                </div>
              </section>
            )}

            {/* GDPR Section */}
            {result.modules?.gdpr && (
              <section className="card overflow-hidden">
                <div className="p-6 border-b border-border bg-surface-hover/50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">{t("results.gdpr")}</h2>
                      <p className="text-sm text-muted">{t("results.gdpr_sub")}</p>
                    </div>
                  </div>
                  <div className={`text-3xl font-black ${result.modules.gdpr.score >= 90 ? 'text-success' : result.modules.gdpr.score >= 50 ? 'text-warning' : 'text-danger'}`}>
                    {result.modules.gdpr.score}<span className="text-lg text-muted">/100</span>
                  </div>
                </div>
                
                <div className="p-6 space-y-4">
                   {result.modules.gdpr.checks.map((check: any, idx: number) => (
                     <div key={idx} className="flex flex-col gap-2 p-4 rounded-md border border-border bg-surface-hover">
                       <div className="flex items-center gap-2">
                         {check.status === 'pass' ? (
                           <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                         ) : check.status === 'warning' ? (
                           <svg className="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                         ) : (
                           <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                         )}
                         <span className="font-semibold text-ink">{check.name}</span>
                       </div>
                       <p className="text-sm text-muted">{check.message}</p>
                       {check.status !== 'pass' && (
                         <p className="text-xs text-muted-dark italic border-l-2 border-primary/30 pl-2">{t("results.recommendation")}: {check.recommendation}</p>
                       )}
                     </div>
                   ))}
                </div>
              </section>
            )}

          </div>

          {/* Sidebar - Right Column (1/3) */}
          <div className="lg:col-span-1 space-y-6 animate-fade-up stagger-2">
             <div className="card p-6 bg-gradient-to-br from-surface to-surface-hover border-primary/20">
               <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  {t("results.ai_title")}
               </h3>
<p className="text-sm text-muted mb-4">{t("results.ai_desc")}</p>
               <button className="btn-primary w-full text-sm py-2">
                 {t("results.ai_cta")}
               </button>
             </div>

             <div className="card p-6">
               <h3 className="text-lg font-bold mb-4">{t("results.share")}</h3>
<p className="text-sm text-muted mb-4">{t("results.share_desc")}</p>
               <div className="flex gap-2">
                 <input 
                   type="text" 
                   readOnly 
                   value={typeof window !== 'undefined' ? window.location.href : ''} 
                   className="flex-1 bg-surface-hover rounded-lg px-3 py-2 text-sm text-muted border border-border focus:outline-none"
                 />
                 <button 
                    onClick={() => {
                       navigator.clipboard.writeText(window.location.href);
                       alert("Enlace copiado al portapapeles");
                    }}
                    className="bg-surface-hover border border-border rounded-lg px-3 py-2 hover:bg-surface text-ink transition-colors"
                    title={t("results.copy")}
                 >
                   <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                   </svg>
                 </button>
               </div>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default function Results() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 rounded-md border-4 border-primary border-t-transparent animate-spin"></div>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}

