from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
import json
import logging
import os
import secrets
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from analyzers.seo import SEOAnalyzer
from i18n import t, normalize_lang
from insights import build_insights
from emailer import send_password_reset
from db import (
    AuditLog,
    PasswordResetToken,
    init_db,
    get_db,
    get_or_create_usage,
    plan_limit,
    history_limit,
)
from auth import (
    create_access_token,
    get_current_user,
    get_user_by_email,
    hash_password,
    hash_reset_token,
    is_production,
    validate_password_policy,
    verify_password,
)
from db import User
from billing import (
    apply_checkout_completed,
    apply_subscription_deleted,
    apply_subscription_updated,
    construct_webhook_event,
    create_checkout_session,
    create_portal_session,
    require_stripe_billing,
    stripe_configured,
)
from ratelimit import enforce_rate_limit, rate_limit_ip
from ssrf import MAX_REDIRECTS, SSRFError, validate_url_for_fetch

logger = logging.getLogger("webhealthiq")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="WebHealthIQ API")


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "https://webhealthiq.com,https://www.webhealthiq.com,http://localhost:3000",
    )
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or [
        "https://webhealthiq.com",
        "https://www.webhealthiq.com",
        "http://localhost:3000",
    ]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info(
        "WebHealthIQ API started (production=%s, cors_origins=%s, stripe=%s)",
        is_production(),
        _cors_origins(),
        "configured" if stripe_configured() else "disabled",
    )


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,eu;q=0.7",
}

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuditRequest(BaseModel):
    url: str
    lang: str = Field(default="es", description="es | en | eu")


class AuditResponse(BaseModel):
    id: int | None = None
    url: str
    overall_score: int
    modules: dict
    timestamp: str
    lang: str
    insights: dict | None = None
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=16, max_length=256)
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)


class BrandingRequest(BaseModel):
    brand_name: str | None = Field(default=None, max_length=120)
    brand_primary: str | None = Field(default=None, max_length=16)


class CheckoutRequest(BaseModel):
    plan: str = Field(description="pro | agency")


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MeResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    company: str | None = None
    brand_name: str | None = None
    brand_primary: str | None = None
    plan: str
    audits_used: int
    audits_limit: int
    year_month: str


class AuditListItem(BaseModel):
    id: int
    url: str
    overall_score: int | None
    created_at: str
    lang: str | None


class AuditDetailResponse(BaseModel):
    id: int
    url: str
    overall_score: int | None
    created_at: str
    lang: str | None
    result: dict | None
    insights: dict | None


def _client_error_detail(lang: str, key: str, *, error: Exception | str | None = None) -> str:
    """Public error message: generic in production, detailed in local/dev."""
    if is_production() or error is None:
        return t(key, lang)
    err_text = str(error) if not isinstance(error, str) else error
    return t(f"{key}_detail", lang, error=err_text)


async def fetch_html_with_browser(url: str) -> tuple[str, str]:
    from playwright.async_api import async_playwright
    from browser import launch_chromium

    validate_url_for_fetch(url)

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
        try:
            validate_url_for_fetch(final_url)
        except SSRFError:
            raise SSRFError("Redirect target is not allowed")
        return final_url, html


async def fetch_page_html(url: str) -> tuple[str, str]:
    import httpx

    current = validate_url_for_fetch(url)

    async with httpx.AsyncClient(
        timeout=30.0,
        headers=BROWSER_HEADERS,
        follow_redirects=False,
    ) as client:
        try:
            for _ in range(MAX_REDIRECTS + 1):
                validate_url_for_fetch(current)
                response = await client.get(current)
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        break
                    current = urljoin(str(response.url), location)
                    continue
                if response.status_code < 400 and response.text.strip():
                    final = str(response.url)
                    validate_url_for_fetch(final)
                    return final, response.text
                break
        except SSRFError:
            raise
        except Exception:
            pass

    return await fetch_html_with_browser(url)


def _user_payload(user: User, used: int, limit: int, year_month: str) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "brand_name": user.brand_name,
        "brand_primary": user.brand_primary,
        "plan": user.plan,
        "audits_used": used,
        "audits_limit": limit,
        "year_month": year_month,
    }


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return dt.isoformat().replace("+00:00", "Z")


@app.post("/api/auth/register", response_model=AuthResponse)
def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit_ip(request, scope="auth.register", limit=5, window_seconds=60)

    email = body.email.lower().strip()
    full_name = (body.full_name or "").strip()
    company = (body.company or "").strip() or None

    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    validate_password_policy(body.password)
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
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit_ip(request, scope="auth.login", limit=10, window_seconds=60)

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
        brand_name=user.brand_name,
        brand_primary=user.brand_primary,
        plan=user.plan,
        audits_used=usage.count,
        audits_limit=limit,
        year_month=usage.year_month,
    )


@app.post("/api/auth/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Always returns a generic 200 to avoid email enumeration."""
    rate_limit_ip(request, scope="auth.forgot", limit=5, window_seconds=60)
    email = body.email.lower().strip()
    enforce_rate_limit(f"auth.forgot:email:{email}", limit=3, window_seconds=3600)

    user = get_user_by_email(db, body.email)
    if user:
        plain_token = secrets.token_urlsafe(32)
        row = PasswordResetToken(
            user_id=user.id,
            token=hash_reset_token(plain_token),
            expires_at=_utc_now() + timedelta(hours=1),
        )
        db.add(row)
        db.commit()
        try:
            send_password_reset(user.email, plain_token)
        except Exception:
            logger.exception("Failed to send password reset email")
    return {
        "ok": True,
        "message": "If the email exists, you will receive reset instructions.",
    }


@app.post("/api/auth/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    rate_limit_ip(request, scope="auth.reset", limit=10, window_seconds=60)

    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    validate_password_policy(body.password)

    token_hash = hash_reset_token(body.token.strip())
    row = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == token_hash)
        .first()
    )
    if not row or row.used_at is not None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < _utc_now():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == row.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.password_hash = hash_password(body.password)
    row.used_at = _utc_now()
    db.commit()
    return {"ok": True, "message": "Password updated"}


@app.patch("/api/account/branding", response_model=MeResponse)
def update_branding(
    body: BrandingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (user.plan or "").lower() != "agency":
        raise HTTPException(status_code=403, detail="Agency plan required")

    if body.brand_name is not None:
        name = body.brand_name.strip()
        user.brand_name = name or None
    if body.brand_primary is not None:
        color = body.brand_primary.strip()
        user.brand_primary = color or None

    db.commit()
    db.refresh(user)
    usage = get_or_create_usage(db, user)
    limit = plan_limit(user.plan)
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        brand_name=user.brand_name,
        brand_primary=user.brand_primary,
        plan=user.plan,
        audits_used=usage.count,
        audits_limit=limit,
        year_month=usage.year_month,
    )


@app.post("/api/billing/checkout", response_model=CheckoutResponse)
def billing_checkout(
    body: CheckoutRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_stripe_billing()
    rate_limit_ip(request, scope="billing.checkout", limit=8, window_seconds=60)
    enforce_rate_limit(
        f"billing.checkout:user:{user.id}",
        limit=10,
        window_seconds=3600,
    )

    plan = (body.plan or "").lower().strip()
    if plan not in ("pro", "agency"):
        raise HTTPException(status_code=400, detail='plan must be "pro" or "agency"')

    try:
        url = create_checkout_session(user=user, plan=plan)  # type: ignore[arg-type]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Stripe checkout failed for user_id=%s plan=%s", user.id, plan)
        raise HTTPException(status_code=502, detail="Could not start Stripe Checkout")

    # Persist customer id if Stripe already assigned one on a previous attempt
    db.refresh(user)
    return CheckoutResponse(url=url)


@app.post("/api/billing/portal", response_model=PortalResponse)
def billing_portal(
    request: Request,
    user: User = Depends(get_current_user),
):
    require_stripe_billing()
    rate_limit_ip(request, scope="billing.portal", limit=10, window_seconds=60)

    try:
        url = create_portal_session(user=user)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Stripe portal failed for user_id=%s", user.id)
        raise HTTPException(status_code=502, detail="Could not open Stripe Customer Portal")
    return PortalResponse(url=url)


@app.post("/api/billing/webhook")
async def billing_webhook(request: Request, db: Session = Depends(get_db)):
    """Stripe webhook — raw body + signature verification. No JWT."""
    require_stripe_billing()
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    event = construct_webhook_event(payload, sig)

    etype = event["type"] if isinstance(event, dict) else event.type
    data_object = (
        event["data"]["object"]
        if isinstance(event, dict)
        else event.data.object
    )
    # Normalize to dict for handlers
    if not isinstance(data_object, dict):
        try:
            data_object = data_object.to_dict()  # type: ignore[union-attr]
        except Exception:
            data_object = dict(data_object)  # type: ignore[arg-type]

    try:
        if etype == "checkout.session.completed":
            apply_checkout_completed(db, data_object)
        elif etype == "customer.subscription.updated":
            apply_subscription_updated(db, data_object)
        elif etype == "customer.subscription.deleted":
            apply_subscription_deleted(db, data_object)
        else:
            logger.debug("Stripe webhook ignored type=%s", etype)
    except Exception:
        logger.exception("Stripe webhook handler failed type=%s", etype)
        raise HTTPException(status_code=500, detail="Webhook handler error")

    return {"received": True}


@app.post("/api/audit", response_model=AuditResponse)
async def audit_url(
    body: AuditRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rate_limit_ip(request, scope="audit", limit=20, window_seconds=60)

    url = body.url
    lang = normalize_lang(body.lang)

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
            url = validate_url_for_fetch(url)
        except SSRFError:
            logger.warning("SSRF blocked URL for user_id=%s", user.id)
            raise HTTPException(
                status_code=400,
                detail=t("err.ssrf", lang),
            )

        try:
            final_url, html_content = await fetch_page_html(url)
        except SSRFError:
            logger.warning("SSRF blocked during fetch for user_id=%s", user.id)
            raise HTTPException(
                status_code=400,
                detail=t("err.ssrf", lang),
            )
        except Exception as e:
            logger.exception("URL access failed for user_id=%s", user.id)
            raise HTTPException(
                status_code=400,
                detail=_client_error_detail(lang, "err.url_access", error=e),
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

        modules = {
            "seo": seo_results,
            "performance": perf_results,
            "accessibility": a11y_results,
            "security": security_results,
            "gdpr": gdpr_results,
        }

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
        timestamp = datetime.utcnow().isoformat() + "Z"
        insights = build_insights(modules, lang)

        result_payload = {
            "url": url,
            "overall_score": overall_score,
            "modules": modules,
            "timestamp": timestamp,
            "lang": lang,
        }

        usage.count += 1
        audit_row = AuditLog(
            user_id=user.id,
            url=url,
            overall_score=overall_score,
            lang=lang,
            result_json=json.dumps(result_payload, ensure_ascii=False),
            insights_json=json.dumps(insights, ensure_ascii=False),
        )
        db.add(audit_row)
        db.commit()
        db.refresh(usage)
        db.refresh(audit_row)

        return AuditResponse(
            id=audit_row.id,
            url=url,
            overall_score=overall_score,
            modules=modules,
            timestamp=timestamp,
            lang=lang,
            insights=insights,
            audits_used=usage.count,
            audits_limit=limit,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Internal audit error for user_id=%s", user.id)
        raise HTTPException(
            status_code=500,
            detail=_client_error_detail(lang, "err.internal", error=e),
        )


@app.get("/api/audits", response_model=list[AuditListItem])
def list_audits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    limit = history_limit(user.plan)
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        AuditListItem(
            id=r.id,
            url=r.url,
            overall_score=r.overall_score,
            created_at=_iso(r.created_at),
            lang=r.lang,
        )
        for r in rows
    ]


@app.get("/api/audits/{audit_id}", response_model=AuditDetailResponse)
def get_audit(
    audit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(AuditLog)
        .filter(AuditLog.id == audit_id, AuditLog.user_id == user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Audit not found")

    result = None
    insights = None
    if row.result_json:
        try:
            result = json.loads(row.result_json)
        except json.JSONDecodeError:
            result = None
    if row.insights_json:
        try:
            insights = json.loads(row.insights_json)
        except json.JSONDecodeError:
            insights = None

    return AuditDetailResponse(
        id=row.id,
        url=row.url,
        overall_score=row.overall_score,
        created_at=_iso(row.created_at),
        lang=row.lang,
        result=result,
        insights=insights,
    )


@app.get("/")
def read_root():
    return {"message": "WebHealthIQ Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
