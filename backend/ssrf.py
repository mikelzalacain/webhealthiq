"""Anti-SSRF: validate URLs before server-side fetch / Playwright."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

# Reasonable redirect budget for audit fetches
MAX_REDIRECTS = 5

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.",
        "metadata.google.internal",
        "metadata",
        "kubernetes.default",
        "kubernetes.default.svc",
    }
)

_BLOCKED_SCHEMES = frozenset({"file", "data", "ftp", "gopher", "jar", "dict", "sftp"})


class SSRFError(ValueError):
    """Raised when a URL is unsafe for outbound fetch."""


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped

    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
        or ip in ipaddress.ip_network("169.254.0.0/16")  # AWS/GCP metadata / link-local
        or (isinstance(ip, ipaddress.IPv6Address) and ip in ipaddress.ip_network("fc00::/7"))
    )


def _hostname_blocked(hostname: str) -> bool:
    host = hostname.strip(".").lower()
    if not host:
        return True
    if host in _BLOCKED_HOSTNAMES:
        return True
    if host.endswith(".localhost") or host.endswith(".local"):
        return True
    if host.endswith(".internal") or host.endswith(".intranet"):
        return True
    return False


def _resolve_and_check(hostname: str) -> None:
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise SSRFError(f"DNS resolution failed for host: {hostname}") from e

    if not infos:
        raise SSRFError(f"No DNS records for host: {hostname}")

    for info in infos:
        sockaddr = info[4]
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if _is_blocked_ip(ip):
            raise SSRFError("URL resolves to a blocked/private address")


def validate_url_for_fetch(url: str) -> str:
    """
    Validate that ``url`` is safe for outbound HTTP(S) fetch.
    Returns the stripped URL or raises SSRFError.
    """
    if url is None:
        raise SSRFError("URL is required")

    raw = url.strip()
    if not raw:
        raise SSRFError("URL is required")

    lower = raw.lower()
    if lower.startswith("file:") or lower.startswith("data:"):
        raise SSRFError("Blocked URL scheme")

    parsed = urlparse(raw)
    scheme = (parsed.scheme or "").lower()
    if scheme in _BLOCKED_SCHEMES:
        raise SSRFError("Blocked URL scheme")
    if scheme not in ("http", "https"):
        raise SSRFError("Only http and https URLs are allowed")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL must include a hostname")

    if _hostname_blocked(hostname):
        raise SSRFError("Blocked hostname")

    # Literal IP in hostname
    try:
        ip = ipaddress.ip_address(hostname)
        if _is_blocked_ip(ip):
            raise SSRFError("Blocked IP address")
        return raw
    except ValueError:
        pass

    _resolve_and_check(hostname)
    return raw
