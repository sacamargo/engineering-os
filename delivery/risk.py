"""Delivery risk from environment + change impact signals."""

from __future__ import annotations

from typing import Any

from delivery.model import RiskLevel

RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def max_risk(a: RiskLevel, b: RiskLevel) -> RiskLevel:
    return a if RANK[a] >= RANK[b] else b


def classify_change_risk(
    changed_paths: list[str],
    *,
    findings: list[dict[str, Any]] | None = None,
    environment: str = "local",
) -> RiskLevel:
    risk: RiskLevel = "low"
    for p in changed_paths:
        pl = p.lower()
        if any(x in pl for x in ("auth", "payment", "billing", "migrat", "infra", "docker", "compose")):
            risk = max_risk(risk, "high")
        elif any(x in pl for x in ("booking", "core", "security", "gateway")):
            risk = max_risk(risk, "medium")
        elif pl.endswith((".css", ".md", "ui/", "frontend/")):
            risk = max_risk(risk, "low")
    for f in findings or []:
        if f.get("severity") in {"high", "critical"} or f.get("kind") == "insecure_pattern":
            risk = max_risk(risk, "high")
    if environment == "production":
        risk = max_risk(risk, "critical")
    elif environment == "staging":
        risk = max_risk(risk, "medium")
    return risk
