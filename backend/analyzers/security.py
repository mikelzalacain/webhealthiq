import httpx
import ssl
import socket
import datetime
from urllib.parse import urlparse
from typing import Dict, Any
from i18n import t, normalize_lang


class SecurityAnalyzer:
    def __init__(self, url: str, lang: str = "es"):
        self.url = url
        self.lang = normalize_lang(lang)
        self.parsed_url = urlparse(url)
        self.hostname = self.parsed_url.netloc

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        checks = []
        score = 100
        headers = {}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self.url)
                headers = {k.lower(): v for k, v in response.headers.items()}
                final_url = str(response.url)
                if final_url.startswith("https://"):
                    checks.append(
                        self._create_check(
                            self._tt("sec.https.name"),
                            "pass",
                            self._tt("sec.https.ok"),
                            self._tt("common.perfect"),
                            20,
                        )
                    )
                else:
                    checks.append(
                        self._create_check(
                            self._tt("sec.https.name"),
                            "fail",
                            self._tt("sec.https.fail"),
                            self._tt("sec.https.fail_rec"),
                            20,
                        )
                    )
                    score -= 20
        except Exception as e:
            checks.append(
                self._create_check(
                    self._tt("sec.https.name"),
                    "fail",
                    self._tt("sec.https.error", error=str(e)),
                    self._tt("sec.https.error_rec"),
                    20,
                )
            )
            score -= 20

        if "strict-transport-security" in headers:
            checks.append(
                self._create_check(
                    self._tt("sec.hsts.name"), "pass", self._tt("sec.hsts.ok"), self._tt("common.perfect"), 15
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.hsts.name"),
                    "warning",
                    self._tt("sec.hsts.missing"),
                    self._tt("sec.hsts.missing_rec"),
                    15,
                )
            )
            score -= 7

        if "content-security-policy" in headers:
            checks.append(
                self._create_check(
                    self._tt("sec.csp.name"), "pass", self._tt("sec.csp.ok"), self._tt("common.perfect"), 15
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.csp.name"),
                    "warning",
                    self._tt("sec.csp.missing"),
                    self._tt("sec.csp.missing_rec"),
                    15,
                )
            )
            score -= 7

        if "x-frame-options" in headers or "frame-ancestors" in headers.get("content-security-policy", ""):
            checks.append(
                self._create_check(
                    self._tt("sec.click.name"), "pass", self._tt("sec.click.ok"), self._tt("common.perfect"), 10
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.click.name"),
                    "warning",
                    self._tt("sec.click.missing"),
                    self._tt("sec.click.missing_rec"),
                    10,
                )
            )
            score -= 5

        if headers.get("x-content-type-options") == "nosniff":
            checks.append(
                self._create_check(
                    self._tt("sec.mime.name"), "pass", self._tt("sec.mime.ok"), self._tt("common.perfect"), 10
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.mime.name"),
                    "warning",
                    self._tt("sec.mime.missing"),
                    self._tt("sec.mime.missing_rec"),
                    10,
                )
            )
            score -= 5

        ssl_status = self._check_ssl_cert()
        if ssl_status["valid"]:
            checks.append(
                self._create_check(
                    self._tt("sec.ssl.name"),
                    "pass",
                    self._tt("sec.ssl.ok", days=ssl_status["days_left"]),
                    self._tt("common.ok"),
                    30,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.ssl.name"),
                    "fail",
                    self._tt("sec.ssl.fail", error=ssl_status["error"]),
                    self._tt("sec.ssl.fail_rec"),
                    30,
                )
            )
            score -= 30

        return {"score": max(0, score), "checks": checks}

    def _create_check(self, name: str, status: str, message: str, recommendation: str, impact: int) -> Dict[str, Any]:
        return {
            "name": name,
            "status": status,
            "message": message,
            "recommendation": recommendation,
            "impact": impact,
        }

    def _check_ssl_cert(self) -> Dict[str, Any]:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    not_after_str = cert.get("notAfter")
                    if not_after_str:
                        not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                        days_left = (not_after - datetime.datetime.utcnow()).days
                        if days_left > 0:
                            return {"valid": True, "days_left": days_left}
                        return {"valid": False, "error": self._tt("sec.ssl.expired")}
            return {"valid": False, "error": self._tt("sec.ssl.unknown")}
        except Exception as e:
            return {"valid": False, "error": str(e)}
