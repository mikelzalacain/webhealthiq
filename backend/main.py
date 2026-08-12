from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from analyzers.seo import SEOAnalyzer
from i18n import t, normalize_lang
from db import (
    AuditLog,
    init_db,
    get_db,
    get_or_create_usage,
    plan_limit,
)
from auth import (
    create_access_token,
    get_current_user,
    get_user_by_email,
    hash_password,
    verify_password,
)
from db import User

app = FastAPI(title="WebHealthIQ API")


@app.on_event("startup")
def on_startup():
    init_db()


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
    audits_used: int | None = None
    audits_limit: int | None = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    company: str | None = Field(default=None, max_length=120)
    accept_terms: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MeResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    company: str | None = None
    plan: str
    audits_used: int
    audits_limit: int
    year_month: str


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


def _user_payload(user: User, used: int, limit: int, year_month: str) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "plan": user.plan,
        "audits_used": used,
        "audits_limit": limit,
        "year_month": year_month,
    }


@app.post("/api/auth/register", response_model=AuthResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    full_name = (body.full_name or "").strip()
    company = (body.company or "").strip() or None

    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(full_name) < 2:
        raise HTTPException(status_code=400, detail="Full name is required")
    if not body.accept_terms:
        raise HTTPException(status_code=400, detail="You must accept the terms")

    user = User(
        email=email,
        password_hash=hash_password(body.password),
        full_name=full_name,
        company=company,
        terms_accepted_at=datetime.utcnow(),
        plan="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    usage = get_or_create_usage(db, user)
    limit = plan_limit(user.plan)
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        user=_user_payload(user, usage.count, limit, usage.year_month),
    )


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    usage = get_or_create_usage(db, user)
    limit = plan_limit(user.plan)
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        user=_user_payload(user, usage.count, limit, usage.year_month),
    )


@app.get("/api/auth/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    usage = get_or_create_usage(db, user)
    limit = plan_limit(user.plan)
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        plan=user.plan,
        audits_used=usage.count,
        audits_limit=limit,
        year_month=usage.year_month,
    )


@app.post("/api/audit", response_model=AuditResponse)
async def audit_url(
    request: AuditRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = request.url
    lang = normalize_lang(request.lang)

    usage = get_or_create_usage(db, user)
    limit = plan_limit(user.plan)
    if usage.count >= limit:
        raise HTTPException(
            status_code=402,
            detail=t(
                "err.quota",
                lang,
                used=usage.count,
                limit=limit,
                plan=user.plan,
            ),
        )

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

        usage.count += 1
        db.add(
            AuditLog(
                user_id=user.id,
                url=url,
                overall_score=overall_score,
            )
        )
        db.commit()
        db.refresh(usage)

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
            audits_used=usage.count,
            audits_limit=limit,
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
