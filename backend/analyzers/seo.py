from bs4 import BeautifulSoup
import httpx
import json
from typing import Dict, Any
from urllib.parse import urljoin, urlparse
from i18n import t, normalize_lang


class SEOAnalyzer:
    def __init__(self, url: str, html_content: str, lang: str = "es"):
        self.url = url
        self.html_content = html_content
        self.lang = normalize_lang(lang)
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    def _tt(self, key: str, **kwargs) -> str:
        return t(key, self.lang, **kwargs)

    async def analyze(self) -> Dict[str, Any]:
        checks = [
            self._check_title(),
            self._check_meta_description(),
            self._check_h1(),
            self._check_images_alt(),
            self._check_canonical(),
            self._check_open_graph(),
            self._check_schema_org(),
            await self._check_robots_txt(),
            await self._check_sitemap(),
        ]

        total_impact = 0
        max_impact = 0
        for check in checks:
            max_impact += check["impact"]
            if check["status"] == "pass":
                total_impact += check["impact"]
            elif check["status"] == "warning":
                total_impact += check["impact"] * 0.5

        score = int((total_impact / max_impact) * 100) if max_impact else 0
        return {"score": score, "checks": checks}

    def _create_result(
        self, name: str, status: str, message: str, recommendation: str, impact: int, data: Any = None
    ) -> Dict[str, Any]:
        return {
            "name": name,
            "status": status,
            "message": message,
            "recommendation": recommendation,
            "impact": impact,
            "data": data,
        }

    def _check_title(self) -> Dict[str, Any]:
        title_tag = self.soup.title
        title = title_tag.string.strip() if title_tag and title_tag.string else None
        name = self._tt("seo.title.name")
        if not title:
            return self._create_result(
                name, "fail", self._tt("seo.title.missing"), self._tt("seo.title.missing_rec"), 15
            )
        length = len(title)
        if 50 <= length <= 60:
            return self._create_result(
                name, "pass", self._tt("seo.title.ok", n=length), self._tt("common.good_length"), 15, {"title": title}
            )
        return self._create_result(
            name,
            "warning",
            self._tt("seo.title.warn", n=length),
            self._tt("seo.title.warn_rec"),
            15,
            {"title": title},
        )

    def _check_meta_description(self) -> Dict[str, Any]:
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        desc = meta_desc.get("content", "").strip() if meta_desc else None
        name = self._tt("seo.meta.name")
        if not desc:
            return self._create_result(
                name, "fail", self._tt("seo.meta.missing"), self._tt("seo.meta.missing_rec"), 10
            )
        length = len(desc)
        if 120 <= length <= 160:
            return self._create_result(
                name, "pass", self._tt("seo.meta.ok", n=length), self._tt("common.good_length"), 10, {"description": desc}
            )
        return self._create_result(
            name,
            "warning",
            self._tt("seo.meta.warn", n=length),
            self._tt("seo.meta.warn_rec"),
            10,
            {"description": desc},
        )

    def _check_h1(self) -> Dict[str, Any]:
        h1_tags = [h1.text.strip() for h1 in self.soup.find_all("h1")]
        name = self._tt("seo.h1.name")
        if not h1_tags:
            return self._create_result(
                name, "fail", self._tt("seo.h1.missing"), self._tt("seo.h1.missing_rec"), 15
            )
        if len(h1_tags) == 1:
            return self._create_result(
                name, "pass", self._tt("seo.h1.ok"), self._tt("common.perfect"), 15, {"h1": h1_tags[0]}
            )
        return self._create_result(
            name,
            "warning",
            self._tt("seo.h1.multi", n=len(h1_tags)),
            self._tt("seo.h1.multi_rec"),
            15,
            {"h1_tags": h1_tags},
        )

    def _check_images_alt(self) -> Dict[str, Any]:
        images = self.soup.find_all("img")
        name = self._tt("seo.alt.name")
        if not images:
            return self._create_result(name, "pass", self._tt("seo.alt.none"), self._tt("common.na"), 5)
        missing_alt = [img.get("src", "unknown") for img in images if not img.get("alt") and img.get("alt") != ""]
        if not missing_alt:
            return self._create_result(name, "pass", self._tt("seo.alt.ok"), self._tt("seo.alt.ok_rec"), 10)
        pct = (len(missing_alt) / len(images)) * 100
        return self._create_result(
            name,
            "warning" if pct < 50 else "fail",
            self._tt("seo.alt.missing", missing=len(missing_alt), total=len(images)),
            self._tt("seo.alt.missing_rec"),
            10,
            {"missing_alt_src": missing_alt[:5]},
        )

    def _check_canonical(self) -> Dict[str, Any]:
        canonical = self.soup.find("link", rel="canonical")
        href = canonical.get("href") if canonical else None
        name = self._tt("seo.canonical.name")
        if href:
            return self._create_result(
                name, "pass", self._tt("seo.canonical.ok"), self._tt("common.ok"), 5, {"canonical": href}
            )
        return self._create_result(
            name, "warning", self._tt("seo.canonical.missing"), self._tt("seo.canonical.missing_rec"), 5
        )

    def _check_open_graph(self) -> Dict[str, Any]:
        og_tags = self.soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        found = {tag.get("property"): tag.get("content") for tag in og_tags}
        required = ["og:title", "og:description", "og:image"]
        missing = [r for r in required if r not in found]
        name = self._tt("seo.og.name")
        if not missing:
            return self._create_result(name, "pass", self._tt("seo.og.ok"), self._tt("common.ok"), 5, found)
        if len(missing) < len(required):
            return self._create_result(
                name,
                "warning",
                self._tt("seo.og.partial", tags=", ".join(missing)),
                self._tt("seo.og.partial_rec"),
                5,
                {"missing": missing},
            )
        return self._create_result(
            name, "fail", self._tt("seo.og.missing"), self._tt("seo.og.missing_rec"), 5
        )

    def _check_schema_org(self) -> Dict[str, Any]:
        scripts = self.soup.find_all("script", type="application/ld+json")
        name = self._tt("seo.schema.name")
        if scripts:
            try:
                data = json.loads(scripts[0].string)
                schema_type = data.get("@type", self._tt("common.unknown"))
                return self._create_result(
                    name, "pass", self._tt("seo.schema.ok", type=schema_type), self._tt("common.ok"), 10
                )
            except Exception:
                return self._create_result(
                    name, "warning", self._tt("seo.schema.invalid"), self._tt("seo.schema.invalid_rec"), 10
                )
        return self._create_result(
            name, "warning", self._tt("seo.schema.missing"), self._tt("seo.schema.missing_rec"), 10
        )

    async def _check_robots_txt(self) -> Dict[str, Any]:
        robots_url = urljoin(self.base_url, "/robots.txt")
        name = self._tt("seo.robots.name")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    return self._create_result(
                        name, "pass", self._tt("seo.robots.ok"), self._tt("common.ok"), 10, {"url": robots_url}
                    )
                return self._create_result(
                    name,
                    "warning",
                    self._tt("seo.robots.status", code=response.status_code),
                    self._tt("seo.robots.status_rec"),
                    10,
                )
        except Exception:
            return self._create_result(
                name, "warning", self._tt("seo.robots.error"), self._tt("seo.robots.error_rec"), 10
            )

    async def _check_sitemap(self) -> Dict[str, Any]:
        sitemap_url = urljoin(self.base_url, "/sitemap.xml")
        name = self._tt("seo.sitemap.name")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(sitemap_url)
                if response.status_code == 200 and "xml" in response.headers.get("Content-Type", "").lower():
                    return self._create_result(
                        name, "pass", self._tt("seo.sitemap.ok"), self._tt("common.ok"), 10, {"url": sitemap_url}
                    )
                return self._create_result(
                    name, "warning", self._tt("seo.sitemap.missing"), self._tt("seo.sitemap.missing_rec"), 10
                )
        except Exception:
            return self._create_result(
                name, "warning", self._tt("seo.sitemap.error"), self._tt("seo.sitemap.error_rec"), 10
            )
