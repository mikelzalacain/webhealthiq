"""Simple in-memory rate limiter (single-instance / Render free OK)."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            i = 0
            while i < len(bucket) and bucket[i] <= cutoff:
                i += 1
            if i:
                del bucket[:i]
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_rate_limit(key: str, limit: int, window_seconds: int) -> None:
    if not limiter.allow(key, limit, window_seconds):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(min(window_seconds, 3600))},
        )


def rate_limit_ip(
    request: Request,
    *,
    scope: str,
    limit: int,
    window_seconds: int = 60,
) -> None:
    enforce_rate_limit(f"{scope}:ip:{client_ip(request)}", limit, window_seconds)
