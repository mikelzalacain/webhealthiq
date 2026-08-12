import httpx
import ssl
import socket
import datetime
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple
from i18n import t, normalize_lang


class SecurityAnalyzer:
    """Auditoría defensiva de HTTPS, certificado, cabeceras, cookies y CORS."""

    def __init__(self, url: str, lang: str = "es"):
        self.url = url
        self.lang = normalize_lang(lang)
        self.parsed_url = urlparse(url)
        self.hostname = self.parsed_url.hostname or self.parsed_url.netloc.split(":")[0]

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        score = 100
        headers: Dict[str, str] = {}
        set_cookies: List[str] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(self.url)
                headers = {k.lower(): v for k, v in response.headers.items()}
                # httpx may expose multiple Set-Cookie via .headers.get_list if available
                get_list = getattr(response.headers, "get_list", None)
                if callable(get_list):
                    set_cookies = get_list("set-cookie") or []
                elif "set-cookie" in headers:
                    set_cookies = [headers["set-cookie"]]

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

        # --- SSL certificate ---
        ssl_status = self._check_ssl_cert()
        if ssl_status["valid"]:
            days = ssl_status["days_left"]
            if days < 30:
                checks.append(
                    self._create_check(
                        self._tt("sec.ssl.name"),
                        "warning",
                        self._tt("sec.ssl.soon", days=days),
                        self._tt("sec.ssl.soon_rec"),
                        30,
                    )
                )
                score -= 10
            else:
                checks.append(
                    self._create_check(
                        self._tt("sec.ssl.name"),
                        "pass",
                        self._tt("sec.ssl.ok", days=days),
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

        # --- HSTS ---
        hsts = headers.get("strict-transport-security", "")
        if hsts:
            max_age = self._parse_hsts_max_age(hsts)
            if max_age is not None and max_age < 15552000:  # < ~6 months
                checks.append(
                    self._create_check(
                        self._tt("sec.hsts.name"),
                        "warning",
                        self._tt("sec.hsts.weak", max_age=max_age),
                        self._tt("sec.hsts.weak_rec"),
                        12,
                    )
                )
                score -= 5
            else:
                checks.append(
                    self._create_check(
                        self._tt("sec.hsts.name"),
                        "pass",
                        self._tt("sec.hsts.ok"),
                        self._tt("common.perfect"),
                        12,
                    )
                )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.hsts.name"),
                    "warning",
                    self._tt("sec.hsts.missing"),
                    self._tt("sec.hsts.missing_rec"),
                    12,
                )
            )
            score -= 7

        # --- CSP presence + quality ---
        csp = headers.get("content-security-policy", "")
        if not csp:
            checks.append(
                self._create_check(
                    self._tt("sec.csp.name"),
                    "warning",
                    self._tt("sec.csp.missing"),
                    self._tt("sec.csp.missing_rec"),
                    12,
                )
            )
            score -= 7
        else:
            unsafe = []
            csp_l = csp.lower()
            if "'unsafe-inline'" in csp_l:
                unsafe.append("unsafe-inline")
            if "'unsafe-eval'" in csp_l:
                unsafe.append("unsafe-eval")
            if unsafe:
                checks.append(
                    self._create_check(
                        self._tt("sec.csp.name"),
                        "warning",
                        self._tt("sec.csp.weak", flags=", ".join(unsafe)),
                        self._tt("sec.csp.weak_rec"),
                        12,
                    )
                )
                score -= 5
            else:
                checks.append(
                    self._create_check(
                        self._tt("sec.csp.name"),
                        "pass",
                        self._tt("sec.csp.ok"),
                        self._tt("common.perfect"),
                        12,
                    )
                )

        # --- Clickjacking ---
        if "x-frame-options" in headers or "frame-ancestors" in csp.lower():
            checks.append(
                self._create_check(
                    self._tt("sec.click.name"),
                    "pass",
                    self._tt("sec.click.ok"),
                    self._tt("common.perfect"),
                    8,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.click.name"),
                    "warning",
                    self._tt("sec.click.missing"),
                    self._tt("sec.click.missing_rec"),
                    8,
                )
            )
            score -= 5

        # --- MIME sniffing ---
        if headers.get("x-content-type-options", "").lower() == "nosniff":
            checks.append(
                self._create_check(
                    self._tt("sec.mime.name"),
                    "pass",
                    self._tt("sec.mime.ok"),
                    self._tt("common.perfect"),
                    8,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.mime.name"),
                    "warning",
                    self._tt("sec.mime.missing"),
                    self._tt("sec.mime.missing_rec"),
                    8,
                )
            )
            score -= 4

        # --- Referrer-Policy ---
        if headers.get("referrer-policy"):
            checks.append(
                self._create_check(
                    self._tt("sec.referrer.name"),
                    "pass",
                    self._tt("sec.referrer.ok", value=headers["referrer-policy"]),
                    self._tt("common.perfect"),
                    6,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.referrer.name"),
                    "warning",
                    self._tt("sec.referrer.missing"),
                    self._tt("sec.referrer.missing_rec"),
                    6,
                )
            )
            score -= 3

        # --- Permissions-Policy ---
        if headers.get("permissions-policy") or headers.get("feature-policy"):
            checks.append(
                self._create_check(
                    self._tt("sec.permissions.name"),
                    "pass",
                    self._tt("sec.permissions.ok"),
                    self._tt("common.perfect"),
                    6,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.permissions.name"),
                    "warning",
                    self._tt("sec.permissions.missing"),
                    self._tt("sec.permissions.missing_rec"),
                    6,
                )
            )
            score -= 3

        # --- Cookies ---
        cookie_delta, cookie_check = self._analyze_cookies(set_cookies)
        checks.append(cookie_check)
        score -= cookie_delta

        # --- CORS ---
        cors_delta, cors_check = self._analyze_cors(headers)
        checks.append(cors_check)
        score -= cors_delta

        # --- Server disclosure ---
        server = headers.get("server", "")
        if server and any(ch.isdigit() for ch in server):
            checks.append(
                self._create_check(
                    self._tt("sec.server.name"),
                    "warning",
                    self._tt("sec.server.version", value=server),
                    self._tt("sec.server.version_rec"),
                    5,
                )
            )
            score -= 2
        elif server:
            checks.append(
                self._create_check(
                    self._tt("sec.server.name"),
                    "pass",
                    self._tt("sec.server.ok", value=server),
                    self._tt("common.ok"),
                    5,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("sec.server.name"),
                    "pass",
                    self._tt("sec.server.hidden"),
                    self._tt("common.perfect"),
                    5,
                )
            )

        return {"score": max(0, min(100, score)), "checks": checks}

    def _analyze_cookies(self, set_cookies: List[str]) -> Tuple[int, Dict[str, Any]]:
        if not set_cookies:
            return 0, self._create_check(
                self._tt("sec.cookies.name"),
                "pass",
                self._tt("sec.cookies.none"),
                self._tt("common.ok"),
                10,
            )

        issues = {"secure": 0, "httponly": 0, "samesite": 0}
        total = 0
        for raw in set_cookies:
            # A single header can contain one cookie; ignore empty
            parts = [p.strip() for p in raw.split(";") if p.strip()]
            if not parts:
                continue
            total += 1
            flags = {p.lower().split("=", 1)[0] for p in parts[1:]}
            if "secure" not in flags:
                issues["secure"] += 1
            if "httponly" not in flags:
                issues["httponly"] += 1
            if not any(f.startswith("samesite") for f in flags):
                issues["samesite"] += 1

        if total == 0:
            return 0, self._create_check(
                self._tt("sec.cookies.name"),
                "pass",
                self._tt("sec.cookies.none"),
                self._tt("common.ok"),
                10,
            )

        bad = issues["secure"] + issues["httponly"] + issues["samesite"]
        if bad == 0:
            return 0, self._create_check(
                self._tt("sec.cookies.name"),
                "pass",
                self._tt("sec.cookies.ok", count=total),
                self._tt("common.perfect"),
                10,
            )

        return 8, self._create_check(
            self._tt("sec.cookies.name"),
            "warning",
            self._tt(
                "sec.cookies.weak",
                count=total,
                secure=issues["secure"],
                httponly=issues["httponly"],
                samesite=issues["samesite"],
            ),
            self._tt("sec.cookies.weak_rec"),
            10,
        )

    def _analyze_cors(self, headers: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
        acao = headers.get("access-control-allow-origin", "")
        acac = headers.get("access-control-allow-credentials", "").lower()
        if not acao:
            return 0, self._create_check(
                self._tt("sec.cors.name"),
                "pass",
                self._tt("sec.cors.none"),
                self._tt("common.ok"),
                8,
            )
        if acao.strip() == "*" and acac == "true":
            return 10, self._create_check(
                self._tt("sec.cors.name"),
                "fail",
                self._tt("sec.cors.star_creds"),
                self._tt("sec.cors.star_creds_rec"),
                8,
            )
        if acao.strip() == "*":
            return 5, self._create_check(
                self._tt("sec.cors.name"),
                "warning",
                self._tt("sec.cors.star"),
                self._tt("sec.cors.star_rec"),
                8,
            )
        return 0, self._create_check(
            self._tt("sec.cors.name"),
            "pass",
            self._tt("sec.cors.ok", value=acao),
            self._tt("common.ok"),
            8,
        )

    @staticmethod
    def _parse_hsts_max_age(value: str) -> int | None:
        for part in value.split(";"):
            part = part.strip().lower()
            if part.startswith("max-age="):
                try:
                    return int(part.split("=", 1)[1].strip())
                except ValueError:
                    return None
        return None

    def _create_check(
        self, name: str, status: str, message: str, recommendation: str, impact: int
    ) -> Dict[str, Any]:
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
                        not_after = datetime.datetime.strptime(
                            not_after_str, "%b %d %H:%M:%S %Y %Z"
                        )
                        days_left = (not_after - datetime.datetime.utcnow()).days
                        if days_left > 0:
                            return {"valid": True, "days_left": days_left}
                        return {"valid": False, "error": self._tt("sec.ssl.expired")}
            return {"valid": False, "error": self._tt("sec.ssl.unknown")}
        except Exception as e:
            return {"valid": False, "error": str(e)}
