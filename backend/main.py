from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from analyzers.seo import SEOAnalyzer
from i18n import t, normalize_lang

app = FastAPI(title="WebHealthIQ API")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,eu;q=0.7",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuditRequest(BaseModel):
    url: str
    lang: str = Field(default="es", description="es | en | eu")


class AuditResponse(BaseModel):
    url: str
    overall_score: int
    modules: dict
    timestamp: str
    lang: str


async def fetch_html_with_browser(url: str) -> tuple[str, str]:
    from playwright.async_api import async_playwright
    from browser import launch_chromium

    async with async_playwright() as p:
        browser = await launch_chromium(p)
        page = await browser.new_page()
        response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        if response is None:
            await browser.close()
            raise RuntimeError("No browser response")
        if response.status >= 400:
            await browser.close()
            raise RuntimeError(f"HTTP {response.status}")
        html = await page.content()
        final_url = page.url
        await browser.close()
        return final_url, html


async def fetch_page_html(url: str) -> tuple[str, str]:
    import httpx

    async with httpx.AsyncClient(
        timeout=30.0,
        headers=BROWSER_HEADERS,
        follow_redirects=True,
    ) as client:
        try:
            response = await client.get(url)
            if response.status_code < 400 and response.text.strip():
                return str(response.url), response.text
        except Exception:
            pass

    return await fetch_html_with_browser(url)


@app.post("/api/audit", response_model=AuditResponse)
async def audit_url(request: AuditRequest):
    url = request.url
    lang = normalize_lang(request.lang)

    try:
        try:
            final_url, html_content = await fetch_page_html(url)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=t("err.url_access", lang, error=str(e)),
            )

        url = final_url or url

        from analyzers.performance import PerformanceAnalyzer
        from analyzers.accessibility import AccessibilityAnalyzer
        from analyzers.security import SecurityAnalyzer
        from analyzers.gdpr import GDPRAnalyzer

        seo_results = await SEOAnalyzer(url, html_content, lang).analyze()
        perf_results = await PerformanceAnalyzer(url, lang).analyze()
        a11y_results = await AccessibilityAnalyzer(url, lang).analyze()
        security_results = await SecurityAnalyzer(url, lang).analyze()
        gdpr_results = await GDPRAnalyzer(url, html_content, lang).analyze()

        scores = [seo_results.get("score", 0)]
        if perf_results.get("score"):
            scores.append(perf_results["score"])
        if a11y_results.get("score") and "error" not in a11y_results:
            scores.append(a11y_results["score"])
        if security_results.get("score"):
            scores.append(security_results["score"])
        if gdpr_results.get("score"):
            scores.append(gdpr_results["score"])

        overall_score = int(sum(scores) / len(scores)) if scores else 0

        return AuditResponse(
            url=url,
            overall_score=overall_score,
            modules={
                "seo": seo_results,
                "performance": perf_results,
                "accessibility": a11y_results,
                "security": security_results,
                "gdpr": gdpr_results,
            },
            timestamp=datetime.utcnow().isoformat() + "Z",
            lang=lang,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=t("err.internal", lang, error=str(e)))


@app.get("/")
def read_root():
    return {"message": "WebHealthIQ Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
