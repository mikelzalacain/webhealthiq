"""Genera un plan de acción priorizado a partir de los módulos de auditoría."""
from __future__ import annotations

from typing import Any


PRIORITY = {"fail": 0, "warning": 1, "pass": 2}


def build_insights(modules: dict[str, Any], lang: str = "es") -> dict[str, Any]:
    labels = {
        "es": {
            "title": "Plan de acción",
            "summary_good": "La web está en buen estado. Prioriza mejoras menores y monitoriza.",
            "summary_mid": "Hay puntos importantes que conviene corregir pronto.",
            "summary_bad": "Hay fallos críticos. Empieza por seguridad, accesibilidad y SEO básico.",
            "empty": "No se detectaron acciones pendientes.",
        },
        "en": {
            "title": "Action plan",
            "summary_good": "The site looks solid. Focus on minor polish and keep monitoring.",
            "summary_mid": "There are important issues worth fixing soon.",
            "summary_bad": "Critical issues found. Start with security, accessibility and basic SEO.",
            "empty": "No pending actions detected.",
        },
        "eu": {
            "title": "Ekintza-plana",
            "summary_good": "Webgunea egoera onean dago. Hobekuntza txikiak lehenetsi.",
            "summary_mid": "Laster zuzendu beharreko puntu garrantzitsuak daude.",
            "summary_bad": "Akats kritikoak daude. Hasi segurtasun, irisgarritasun eta SEO oinarrizkotik.",
            "empty": "Ez da ekintza zainik detektatu.",
        },
    }
    L = labels.get(lang, labels["es"])

    items: list[dict[str, Any]] = []
    for module_key, module in (modules or {}).items():
        if not isinstance(module, dict):
            continue
        checks = module.get("checks") or []
        for check in checks:
            status = (check.get("status") or "").lower()
            if status not in ("fail", "warning"):
                continue
            items.append(
                {
                    "module": module_key,
                    "status": status,
                    "name": check.get("name") or module_key,
                    "message": check.get("message") or "",
                    "recommendation": check.get("recommendation") or "",
                    "impact": int(check.get("impact") or 0),
                }
            )

    items.sort(key=lambda x: (PRIORITY.get(x["status"], 9), -x["impact"]))
    top = items[:8]

    fails = sum(1 for i in items if i["status"] == "fail")
    if fails >= 4:
        summary = L["summary_bad"]
    elif items:
        summary = L["summary_mid"]
    else:
        summary = L["summary_good"]

    return {
        "title": L["title"],
        "summary": summary,
        "actions": top,
        "total_issues": len(items),
        "engine": "rules-v1",
    }
