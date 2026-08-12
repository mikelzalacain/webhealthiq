"""Stripe Billing helpers for WebHealthIQ (Checkout + Customer Portal + webhooks)."""

from __future__ import annotations

import logging
import os
from typing import Literal

import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session

from db import User

logger = logging.getLogger("webhealthiq.billing")

PaidPlan = Literal["pro", "agency"]


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def app_url() -> str:
    return _env("APP_URL").rstrip("/") or "http://localhost:3000"


def stripe_secret_key() -> str:
    return _env("STRIPE_SECRET_KEY")


def stripe_webhook_secret() -> str:
    return _env("STRIPE_WEBHOOK_SECRET")


def stripe_price_pro() -> str:
    return _env("STRIPE_PRICE_PRO")


def stripe_price_agency() -> str:
    return _env("STRIPE_PRICE_AGENCY")


def stripe_configured() -> bool:
    return bool(
        stripe_secret_key()
        and stripe_webhook_secret()
        and stripe_price_pro()
        and stripe_price_agency()
    )


def require_stripe_billing() -> None:
    if not stripe_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Billing is not configured. Set STRIPE_SECRET_KEY, "
                "STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_PRO and STRIPE_PRICE_AGENCY."
            ),
        )


def configure_stripe() -> None:
    require_stripe_billing()
    stripe.api_key = stripe_secret_key()


def price_id_for_plan(plan: PaidPlan) -> str:
    if plan == "pro":
        return stripe_price_pro()
    if plan == "agency":
        return stripe_price_agency()
    raise HTTPException(status_code=400, detail="Invalid plan")


def plan_from_price_id(price_id: str | None) -> str | None:
    if not price_id:
        return None
    if price_id == stripe_price_pro():
        return "pro"
    if price_id == stripe_price_agency():
        return "agency"
    return None


def success_url() -> str:
    custom = _env("STRIPE_SUCCESS_URL")
    if custom:
        return custom
    return f"{app_url()}/account?billing=success"


def cancel_url() -> str:
    custom = _env("STRIPE_CANCEL_URL")
    if custom:
        return custom
    return f"{app_url()}/#pricing"


def portal_return_url() -> str:
    return f"{app_url()}/account"


def _subscription_price_id(subscription: dict | stripe.Subscription) -> str | None:
    items = None
    if isinstance(subscription, dict):
        items = (subscription.get("items") or {}).get("data") or []
    else:
        items = getattr(getattr(subscription, "items", None), "data", None) or []
    if not items:
        return None
    first = items[0]
    price = first.get("price") if isinstance(first, dict) else getattr(first, "price", None)
    if price is None:
        return None
    if isinstance(price, str):
        return price
    if isinstance(price, dict):
        return price.get("id")
    return getattr(price, "id", None)


def _find_user_for_subscription(db: Session, subscription: dict | stripe.Subscription) -> User | None:
    meta = (
        subscription.get("metadata")
        if isinstance(subscription, dict)
        else getattr(subscription, "metadata", None)
    ) or {}
    user_id_raw = meta.get("user_id") if isinstance(meta, dict) else None
    if user_id_raw:
        try:
            user = db.query(User).filter(User.id == int(user_id_raw)).first()
            if user:
                return user
        except (TypeError, ValueError):
            pass

    sub_id = subscription.get("id") if isinstance(subscription, dict) else getattr(subscription, "id", None)
    if sub_id:
        user = db.query(User).filter(User.stripe_subscription_id == sub_id).first()
        if user:
            return user

    customer_id = (
        subscription.get("customer")
        if isinstance(subscription, dict)
        else getattr(subscription, "customer", None)
    )
    if isinstance(customer_id, dict):
        customer_id = customer_id.get("id")
    if customer_id:
        return db.query(User).filter(User.stripe_customer_id == str(customer_id)).first()
    return None


def apply_checkout_completed(db: Session, session_obj: dict) -> None:
    meta = session_obj.get("metadata") or {}
    user_id_raw = meta.get("user_id")
    plan = (meta.get("plan") or "").lower().strip()
    if plan not in ("pro", "agency"):
        # Fallback from line items / subscription metadata if needed
        plan = None

    user: User | None = None
    if user_id_raw:
        try:
            user = db.query(User).filter(User.id == int(user_id_raw)).first()
        except (TypeError, ValueError):
            user = None
    if user is None:
        customer_id = session_obj.get("customer")
        if customer_id:
            user = db.query(User).filter(User.stripe_customer_id == str(customer_id)).first()
    if user is None:
        logger.warning("checkout.session.completed: user not found (meta=%s)", meta)
        return

    customer_id = session_obj.get("customer")
    subscription_id = session_obj.get("subscription")
    if customer_id:
        user.stripe_customer_id = str(customer_id)
    if subscription_id:
        user.stripe_subscription_id = str(subscription_id)

    if plan in ("pro", "agency"):
        user.plan = plan
    elif subscription_id:
        # Resolve plan from subscription price if metadata missing
        try:
            configure_stripe()
            sub = stripe.Subscription.retrieve(str(subscription_id))
            resolved = plan_from_price_id(_subscription_price_id(sub))
            if resolved:
                user.plan = resolved
        except Exception:
            logger.exception("Failed to resolve plan from subscription %s", subscription_id)

    db.commit()
    logger.info("Checkout completed: user_id=%s plan=%s", user.id, user.plan)


def apply_subscription_updated(db: Session, subscription: dict) -> None:
    user = _find_user_for_subscription(db, subscription)
    if not user:
        logger.warning("subscription.updated: user not found for sub=%s", subscription.get("id"))
        return

    status = (subscription.get("status") or "").lower()
    sub_id = subscription.get("id")
    customer_id = subscription.get("customer")
    if customer_id:
        user.stripe_customer_id = str(customer_id)
    if sub_id:
        user.stripe_subscription_id = str(sub_id)

    if status in ("canceled", "unpaid", "incomplete_expired"):
        user.plan = "free"
        if status == "canceled":
            user.stripe_subscription_id = None
    else:
        meta_plan = ((subscription.get("metadata") or {}).get("plan") or "").lower().strip()
        resolved = plan_from_price_id(_subscription_price_id(subscription))
        if resolved:
            user.plan = resolved
        elif meta_plan in ("pro", "agency"):
            user.plan = meta_plan

    db.commit()
    logger.info(
        "Subscription updated: user_id=%s status=%s plan=%s",
        user.id,
        status,
        user.plan,
    )


def apply_subscription_deleted(db: Session, subscription: dict) -> None:
    user = _find_user_for_subscription(db, subscription)
    if not user:
        logger.warning("subscription.deleted: user not found for sub=%s", subscription.get("id"))
        return

    user.plan = "free"
    user.stripe_subscription_id = None
    customer_id = subscription.get("customer")
    if customer_id and not user.stripe_customer_id:
        user.stripe_customer_id = str(customer_id)
    db.commit()
    logger.info("Subscription deleted: user_id=%s → free", user.id)


def create_checkout_session(*, user: User, plan: PaidPlan) -> str:
    configure_stripe()
    price_id = price_id_for_plan(plan)
    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url(),
        "cancel_url": cancel_url(),
        "client_reference_id": str(user.id),
        "metadata": {"user_id": str(user.id), "plan": plan},
        "subscription_data": {
            "metadata": {"user_id": str(user.id), "plan": plan},
        },
        "allow_promotion_codes": True,
    }
    if user.stripe_customer_id:
        params["customer"] = user.stripe_customer_id
    else:
        params["customer_email"] = user.email

    session = stripe.checkout.Session.create(**params)
    url = getattr(session, "url", None) or (session.get("url") if isinstance(session, dict) else None)
    if not url:
        raise HTTPException(status_code=502, detail="Stripe did not return a checkout URL")
    return str(url)


def create_portal_session(*, user: User) -> str:
    configure_stripe()
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No Stripe customer for this account. Subscribe to a plan first.",
        )
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=portal_return_url(),
    )
    url = getattr(session, "url", None) or (session.get("url") if isinstance(session, dict) else None)
    if not url:
        raise HTTPException(status_code=502, detail="Stripe did not return a portal URL")
    return str(url)


def construct_webhook_event(payload: bytes, sig_header: str | None):
    require_stripe_billing()
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")
    try:
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            stripe_webhook_secret(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload") from e
    except Exception as e:
        # stripe.error.SignatureVerificationError (v8) or stripe.SignatureVerificationError
        if "SignatureVerification" in type(e).__name__:
            raise HTTPException(status_code=400, detail="Invalid signature") from e
        raise
