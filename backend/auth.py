import hashlib
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import User, get_db

logger = logging.getLogger("webhealthiq.auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

_DEV_JWT_SECRET = "webhealthiq-dev-secret-change-me"
_WEAK_SECRETS = frozenset(
    {
        "",
        _DEV_JWT_SECRET,
        "secret",
        "changeme",
        "change-me",
        "jwt-secret",
        "your-secret",
    }
)


def is_production() -> bool:
    if os.getenv("DEBUG", "").strip().lower() in ("1", "true", "yes"):
        return False
    env = (os.getenv("ENV") or os.getenv("ENVIRONMENT") or "").strip().lower()
    if env in ("production", "prod"):
        return True
    # Render sets RENDER=true
    if os.getenv("RENDER", "").strip().lower() in ("1", "true", "yes"):
        return True
    return False


def _load_jwt_secret() -> str:
    raw = os.getenv("JWT_SECRET")
    if raw is None or not str(raw).strip():
        if is_production():
            raise RuntimeError(
                "JWT_SECRET is required in production. "
                "Set a strong random secret in the environment."
            )
        return _DEV_JWT_SECRET
    secret = str(raw).strip()
    if is_production() and (secret in _WEAK_SECRETS or len(secret) < 16):
        raise RuntimeError(
            "JWT_SECRET is weak or default. "
            "Set a strong random secret (at least 16 characters) in production."
        )
    return secret


JWT_SECRET = _load_jwt_secret()
JWT_ALG = "HS256"
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "14"))

_PASSWORD_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_DIGIT = re.compile(r"\d")


def validate_password_policy(password: str) -> None:
    """Raise HTTPException if password does not meet policy (min 8 + letter + digit)."""
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Password is too long")
    if not _PASSWORD_LETTER.search(password) or not _PASSWORD_DIGIT.search(password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one letter and one number",
        )


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = int(payload.get("sub", "0"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
