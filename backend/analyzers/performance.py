from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright
from i18n import t, normalize_lang
from browser import launch_chromium


class PerformanceAnalyzer:
    """Análisis de rendimiento 100% local con Playwright (sin APIs de pago)."""

    def __init__(self, url: str, lang: str = "es"):
        self.url = url
        self.lang = normalize_lang(lang)

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        try:
            async with async_playwright() as p:
                browser = await launch_chromium(p)
                context = await browser.new_context(
                    viewport={"width": 1366, "height": 768},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()

                transferred_bytes = {"total": 0, "count": 0, "heavy": []}

                def on_response(response) -> None:
                    try:
                        headers = {k.lower(): v for k, v in response.headers.items()}
                        length = headers.get("content-length")
                        size = int(length) if length and length.isdigit() else 0
                        # fallback rough size from body if small enough / available
                        if size == 0:
                            return
                        transferred_bytes["total"] += size
                        transferred_bytes["count"] += 1
                        if size > 500 * 1024:
                            url_short = response.url.split("?")[0][-80:]
                            transferred_bytes["heavy"].append(
                                {"name": url_short, "kb": round(size / 1024)}
                            )
                    except Exception:
                        pass

                page.on("response", on_response)

                # Recolectores CWV antes de navegar
                await page.add_init_script(
                    """
                    (() => {
                      window.__whiqPerf = { lcp: null, cls: 0, inp: null };
                      try {
                        new PerformanceObserver((list) => {
                          for (const e of list.getEntries()) {
                            window.__whiqPerf.lcp = e.startTime;
                          }
                        }).observe({ type: 'largest-contentful-paint', buffered: true });
                      } catch (_) {}
                      try {
                        new PerformanceObserver((list) => {
                          for (const e of list.getEntries()) {
                            if (!e.hadRecentInput) {
                              window.__whiqPerf.cls += e.value;
                            }
                          }
                        }).observe({ type: 'layout-shift', buffered: true });
                      } catch (_) {}
                      try {
                        new PerformanceObserver((list) => {
                          for (const e of list.getEntries()) {
                            const delay = e.processingStart - e.startTime;
                            if (window.__whiqPerf.inp == null || delay > window.__whiqPerf.inp) {
                              window.__whiqPerf.inp = delay;
                            }
                          }
                        }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
                      } catch (_) {}
                    })();
                    """
                )

                response = await page.goto(
                    self.url, wait_until="networkidle", timeout=60000
                )
                # Dar tiempo a que se asienten LCP/CLS
                await page.wait_for_timeout(2500)

                metrics = await page.evaluate(
                    """
                    () => {
                      const paints = performance.getEntriesByType('paint');
                      const nav = performance.getEntriesByType('navigation')[0];
                      const resources = performance.getEntriesByType('resource') || [];
                      const fcpEntry = paints.find(p => p.name === 'first-contentful-paint');
                      let transferBytes = 0;
                      let counted = 0;
                      const heavy = [];
                      for (const r of resources) {
                        const size = r.transferSize || r.encodedBodySize || 0;
                        if (size > 0) {
                          transferBytes += size;
                          counted += 1;
                        }
                        if (size > 500 * 1024) {
                          heavy.push({ name: r.name.split('?')[0].slice(-80), kb: Math.round(size / 1024) });
                        }
                      }
                      heavy.sort((a, b) => b.kb - a.kb);
                      return {
                        fcp: fcpEntry ? fcpEntry.startTime : null,
                        lcp: window.__whiqPerf?.lcp ?? null,
                        cls: window.__whiqPerf?.cls ?? 0,
                        inp: window.__whiqPerf?.inp ?? null,
                        ttfb: nav ? nav.responseStart : null,
                        domContentLoaded: nav ? nav.domContentLoadedEventEnd : null,
                        loadEvent: nav ? nav.loadEventEnd : null,
                        requestCount: Math.max(resources.length, counted),
                        transferKb: Math.round(transferBytes / 1024),
                        largeResources: heavy.length,
                        heavyResources: heavy.slice(0, 5),
                      };
                    }
                    """
                )

                # Preferir tamaños capturados por red si son más completos
                net_kb = round(transferred_bytes["total"] / 1024)
                if net_kb > (metrics.get("transferKb") or 0):
                    metrics["transferKb"] = net_kb
                    metrics["requestCount"] = max(
                        metrics.get("requestCount") or 0, transferred_bytes["count"]
                    )
                    heavy = sorted(
                        transferred_bytes["heavy"], key=lambda h: h["kb"], reverse=True
                    )[:5]
                    metrics["heavyResources"] = heavy
                    metrics["largeResources"] = len(transferred_bytes["heavy"])

                cache_ok = False
                if response is not None:
                    cache_control = (response.headers.get("cache-control") or "").lower()
                    cache_ok = any(
                        token in cache_control
                        for token in ("max-age", "s-maxage", "public", "immutable")
                    )

                await browser.close()

            return self._build_result(metrics, cache_ok)

        except Exception as e:
            return {
                "score": 0,
                "error": self._tt("perf.error", error=str(e)),
                "checks": [],
                "lcp": "N/A",
                "cls": "N/A",
                "fcp": "N/A",
            }

    def _build_result(self, metrics: Dict[str, Any], cache_ok: bool) -> Dict[str, Any]:
        fcp_ms = metrics.get("fcp")
        lcp_ms = metrics.get("lcp") or fcp_ms
        cls_val = float(metrics.get("cls") or 0)
        inp_ms = metrics.get("inp")
        ttfb_ms = metrics.get("ttfb")
        transfer_kb = int(metrics.get("transferKb") or 0)
        request_count = int(metrics.get("requestCount") or 0)
        large_resources = int(metrics.get("largeResources") or 0)

        checks: List[Dict[str, Any]] = []
        weighted = 0.0
        weight_total = 0.0

        def add_check(
            name: str,
            status: str,
            message: str,
            recommendation: str,
            impact: int,
            ratio: float,
        ) -> None:
            nonlocal weighted, weight_total
            checks.append(
                {
                    "name": name,
                    "status": status,
                    "message": message,
                    "recommendation": recommendation,
                    "impact": impact,
                }
            )
            weight_total += impact
            if status == "pass":
                weighted += impact
            elif status == "warning":
                weighted += impact * 0.5

        # LCP thresholds (ms): good <=2500, NI <=4000
        lcp_status, lcp_ratio = self._threshold_status(lcp_ms, 2500, 4000)
        add_check(
            self._tt("perf.lcp.name"),
            lcp_status,
            self._tt("perf.lcp.msg", value=self._fmt_ms(lcp_ms)),
            self._tt("perf.lcp.rec"),
            30,
            lcp_ratio,
        )

        # CLS: good <=0.1, NI <=0.25
        if cls_val <= 0.1:
            cls_status, cls_ratio = "pass", 1.0
        elif cls_val <= 0.25:
            cls_status, cls_ratio = "warning", 0.5
        else:
            cls_status, cls_ratio = "fail", 0.0
        add_check(
            self._tt("perf.cls.name"),
            cls_status,
            self._tt("perf.cls.msg", value=f"{cls_val:.3f}"),
            self._tt("perf.cls.rec"),
            25,
            cls_ratio,
        )

        # FCP: good <=1800, NI <=3000
        fcp_status, fcp_ratio = self._threshold_status(fcp_ms, 1800, 3000)
        add_check(
            self._tt("perf.fcp.name"),
            fcp_status,
            self._tt("perf.fcp.msg", value=self._fmt_ms(fcp_ms)),
            self._tt("perf.fcp.rec"),
            15,
            fcp_ratio,
        )

        # TTFB: good <=800, NI <=1800
        ttfb_status, ttfb_ratio = self._threshold_status(ttfb_ms, 800, 1800)
        add_check(
            self._tt("perf.ttfb.name"),
            ttfb_status,
            self._tt("perf.ttfb.msg", value=self._fmt_ms(ttfb_ms)),
            self._tt("perf.ttfb.rec"),
            10,
            ttfb_ratio,
        )

        # INP solo si hubo interacción; en carga fría (auditoría automática) no penalizar.
        if inp_ms is not None:
            inp_status, inp_ratio = self._threshold_status(inp_ms, 200, 500)
            add_check(
                self._tt("perf.inp.name"),
                inp_status,
                self._tt("perf.inp.msg", value=self._fmt_ms(inp_ms)),
                self._tt("perf.inp.rec"),
                10,
                inp_ratio,
            )
        else:
            add_check(
                self._tt("perf.inp.name"),
                "pass",
                self._tt("perf.inp.none"),
                self._tt("perf.inp.none_rec"),
                5,
                1.0,
            )

        # Peso de recursos
        if transfer_kb <= 1500 and large_resources == 0:
            size_status, size_ratio = "pass", 1.0
            size_msg = self._tt("perf.size.ok", kb=transfer_kb, n=request_count)
        elif transfer_kb <= 3500 and large_resources <= 2:
            size_status, size_ratio = "warning", 0.5
            size_msg = self._tt("perf.size.warn", kb=transfer_kb, heavy=large_resources)
        else:
            size_status, size_ratio = "fail", 0.0
            size_msg = self._tt("perf.size.fail", kb=transfer_kb, heavy=large_resources)
        heavy = metrics.get("heavyResources") or []
        if heavy:
            top = ", ".join(f"{h['name']} ({h['kb']} KB)" for h in heavy[:3])
            size_msg += self._tt("perf.size.examples", list=top)
        add_check(
            self._tt("perf.size.name"),
            size_status,
            size_msg,
            self._tt("perf.size.rec"),
            10,
            size_ratio,
        )

        # Cache documento
        if cache_ok:
            add_check(
                self._tt("perf.cache.name"),
                "pass",
                self._tt("perf.cache.ok"),
                self._tt("perf.cache.ok_rec"),
                5,
                1.0,
            )
        else:
            add_check(
                self._tt("perf.cache.name"),
                "warning",
                self._tt("perf.cache.missing"),
                self._tt("perf.cache.missing_rec"),
                5,
                0.5,
            )

        score = int((weighted / weight_total) * 100) if weight_total else 0

        return {
            "score": score,
            "lcp": self._fmt_ms(lcp_ms),
            "cls": f"{cls_val:.3f}",
            "fcp": self._fmt_ms(fcp_ms),
            "inp": self._fmt_ms(inp_ms) if inp_ms is not None else "N/A",
            "ttfb": self._fmt_ms(ttfb_ms),
            "transfer_kb": transfer_kb,
            "request_count": request_count,
            "engine": "playwright-local",
            "checks": checks,
        }

    @staticmethod
    def _threshold_status(
        value: Optional[float], good: float, poor: float
    ) -> tuple[str, float]:
        if value is None:
            return "warning", 0.5
        if value <= good:
            return "pass", 1.0
        if value <= poor:
            return "warning", 0.5
        return "fail", 0.0

    @staticmethod
    def _fmt_ms(value: Optional[float]) -> str:
        if value is None:
            return "N/A"
        if value >= 1000:
            return f"{value / 1000:.2f} s"
        return f"{int(round(value))} ms"
