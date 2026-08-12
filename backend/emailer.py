"""Envío de emails (SMTP). Si no hay config, registra en logs."""
from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("webhealthiq.email")

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
# Env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, APP_URL
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "hello@webhealthiq.com")
APP_URL = os.getenv("APP_URL", "https://webhealthiq.com").rstrip("/")


def send_email(to: str, subject: str, text: str) -> bool:
    if not SMTP_HOST or not SMTP_USER:
        logger.warning("SMTP not configured. Email to %s | %s\n%s", to, subject, text)
        return False

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.starttls()
        if SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    return True


def send_password_reset(to: str, token: str) -> bool:
    link = f"{APP_URL}/reset-password?token={token}"
    subject = "WebHealthIQ — Restablecer contraseña"
    text = (
        "Has solicitado restablecer tu contraseña en WebHealthIQ.\n\n"
        f"Abre este enlace (válido 1 hora):\n{link}\n\n"
        "Si no fuiste tú, ignora este mensaje.\n\n"
        "Soporte: hello@webhealthiq.com\n"
        "https://webhealthiq.com"
    )
    return send_email(to, subject, text)
