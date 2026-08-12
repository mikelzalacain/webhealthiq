from typing import Dict, Any, List
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe
from i18n import t, normalize_lang


KNOWN_RULES = {
    "color-contrast": ("a11y.rule.color-contrast", "a11y.rule.color-contrast.rec"),
    "image-alt": ("a11y.rule.image-alt", "a11y.rule.image-alt.rec"),
    "link-name": ("a11y.rule.link-name", "a11y.rule.link-name.rec"),
    "button-name": ("a11y.rule.button-name", "a11y.rule.button-name.rec"),
}


class AccessibilityAnalyzer:
    def __init__(self, url: str, lang: str = "es"):
        self.url = url
        self.lang = normalize_lang(lang)

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        score = 100
        checks = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.url, wait_until="networkidle", timeout=45000)

                axe = Axe()
                results = await axe.run(page)
                violations: List[dict] = results.response.get("violations", [])

                if not violations:
                    checks.append(
                        {
                            "name": self._tt("a11y.ok.name"),
                            "status": "pass",
                            "message": self._tt("a11y.ok.msg"),
                            "recommendation": self._tt("a11y.ok.rec"),
                            "impact": 0,
                        }
                    )
                else:
                    for violation in violations:
                        impact_str = violation.get("impact") or "moderate"
                        points_deducted = 0
                        status = "warning"
                        if impact_str == "critical":
                            points_deducted = 15
                            status = "fail"
                        elif impact_str == "serious":
                            points_deducted = 10
                            status = "fail"
                        elif impact_str == "moderate":
                            points_deducted = 5
                        elif impact_str == "minor":
                            points_deducted = 2

                        score = max(0, score - points_deducted)
                        rule_id = violation.get("id", "unknown")
                        msg_key, rec_key = KNOWN_RULES.get(
                            rule_id, ("a11y.rule.generic", "a11y.rule.generic.rec")
                        )
                        message = self._tt(msg_key, id=rule_id)
                        recommendation = self._tt(rec_key, id=rule_id)

                        nodes = violation.get("nodes", [])[:3]
                        affected = [node.get("html", "") for node in nodes]
                        checks.append(
                            {
                                "name": self._tt("a11y.issue.name", id=rule_id),
                                "status": status,
                                "message": message,
                                "recommendation": recommendation,
                                "impact": points_deducted,
                                "data": {
                                    "impact_level": impact_str,
                                    "help_url": violation.get("helpUrl"),
                                    "affected_elements": affected,
                                },
                            }
                        )

                await browser.close()

        except Exception as e:
            return {
                "score": 0,
                "error": self._tt("a11y.error", error=str(e)),
                "checks": [],
            }

        return {"score": score, "checks": checks}
