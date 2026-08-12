import re
from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from i18n import t, normalize_lang


class GDPRAnalyzer:
    def __init__(self, url: str, html_content: str, lang: str = "es"):
        self.url = url
        self.html_content = html_content
        self.lang = normalize_lang(lang)
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.hostname = urlparse(url).netloc

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        checks = []
        score = 100

        tracking_found = self._detect_tracking_scripts()
        if tracking_found:
            checks.append(
                self._create_check(
                    self._tt("gdpr.track.name"),
                    "warning",
                    self._tt("gdpr.track.found", list=", ".join(tracking_found)),
                    self._tt("gdpr.track.found_rec"),
                    20,
                )
            )
            score -= 10
        else:
            checks.append(
                self._create_check(
                    self._tt("gdpr.track.name"),
                    "pass",
                    self._tt("gdpr.track.ok"),
                    self._tt("gdpr.track.ok_rec"),
                    20,
                )
            )

        if tracking_found:
            if self._detect_consent_mode():
                checks.append(
                    self._create_check(
                        self._tt("gdpr.consent.name"),
                        "pass",
                        self._tt("gdpr.consent.ok"),
                        self._tt("gdpr.consent.ok_rec"),
                        15,
                    )
                )
            else:
                checks.append(
                    self._create_check(
                        self._tt("gdpr.consent.name"),
                        "warning",
                        self._tt("gdpr.consent.missing"),
                        self._tt("gdpr.consent.missing_rec"),
                        15,
                    )
                )
                score -= 10

        legal_links = self._check_legal_links()
        missing_links = [name for name, found in legal_links.items() if not found]
        if not missing_links:
            checks.append(
                self._create_check(
                    self._tt("gdpr.legal.name"),
                    "pass",
                    self._tt("gdpr.legal.ok"),
                    self._tt("common.ok"),
                    30,
                )
            )
        else:
            checks.append(
                self._create_check(
                    self._tt("gdpr.legal.name"),
                    "fail",
                    self._tt("gdpr.legal.missing", list=", ".join(missing_links)),
                    self._tt("gdpr.legal.missing_rec"),
                    30,
                )
            )
            score -= 10 * len(missing_links)

        return {"score": max(0, score), "checks": checks}

    def _create_check(self, name: str, status: str, message: str, recommendation: str, impact: int) -> Dict[str, Any]:
        return {
            "name": name,
            "status": status,
            "message": message,
            "recommendation": recommendation,
            "impact": impact,
        }

    def _detect_tracking_scripts(self) -> list:
        found = []
        scripts = self.soup.find_all("script")
        patterns = {
            "Google Analytics / GTM": r"(googletagmanager\.com|google-analytics\.com|gtag)",
            "Facebook Pixel": r"fbevents\.js",
            "Hotjar": r"hotjar\.com",
            "TikTok Pixel": r"tiktok\.com/analytics",
            "LinkedIn Insight": r"snap\.licdn\.com",
        }
        for script in scripts:
            src = script.get("src", "")
            content = script.string or ""
            text_to_check = src + content
            for name, pattern in patterns.items():
                if name not in found and re.search(pattern, text_to_check, re.IGNORECASE):
                    found.append(name)
        return found

    def _detect_consent_mode(self) -> bool:
        for script in self.soup.find_all("script"):
            content = script.string or ""
            if "gtag('consent'" in content or 'gtag("consent"' in content:
                return True
        return False

    def _check_legal_links(self) -> dict:
        privacy = self._tt("gdpr.legal.privacy")
        cookies = self._tt("gdpr.legal.cookies")
        notice = self._tt("gdpr.legal.notice")
        found = {privacy: False, cookies: False, notice: False}

        for link in self.soup.find_all("a"):
            text = (link.get_text(" ") or "").lower()
            href = (link.get("href") or "").lower()
            blob = f"{text} {href}"

            if any(k in blob for k in ("privacidad", "privacy", "pribatutasun")):
                found[privacy] = True
            if "cookie" in blob:
                found[cookies] = True
            if any(k in blob for k in ("aviso legal", "legal notice", "lege-ohar", "términos", "terms", "legal")):
                found[notice] = True

        return found
