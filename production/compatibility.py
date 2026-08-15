"""API / release compatibility gates — absence of evidence ≠ PASSED."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

CompatStatus = Literal["PASSED", "FAILED", "UNKNOWN", "NEEDS_HUMAN"]


@dataclass
class CompatibilityResult:
    status: CompatStatus
    checks: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_api_compatibility(evidence: dict[str, Any] | None) -> CompatibilityResult:
    if not evidence:
        return CompatibilityResult(
            "UNKNOWN",
            notes=["no API compatibility evidence — UNKNOWN ≠ PASSED"],
        )
    breaking = evidence.get("breaking_changes")
    if breaking is True:
        return CompatibilityResult("FAILED", checks=[evidence], notes=["API breaking changes detected"])
    if breaking is False and evidence.get("analyzed") is True:
        return CompatibilityResult("PASSED", checks=[evidence])
    return CompatibilityResult("UNKNOWN", checks=[evidence], notes=["incomplete analysis ≠ PASSED"])


def evaluate_release_compatibility(
    *,
    frontend_backend: dict[str, Any] | None = None,
    mobile_backend: dict[str, Any] | None = None,
    database_backend: dict[str, Any] | None = None,
    configuration_artifact: dict[str, Any] | None = None,
) -> CompatibilityResult:
    checks: list[dict[str, Any]] = []
    statuses: list[str] = []
    for name, ev in (
        ("frontend_backend", frontend_backend),
        ("mobile_backend", mobile_backend),
        ("database_backend", database_backend),
        ("configuration_artifact", configuration_artifact),
    ):
        if ev is None:
            checks.append({"pair": name, "status": "UNKNOWN"})
            statuses.append("UNKNOWN")
            continue
        st = str(ev.get("status") or "UNKNOWN").upper()
        if st not in {"PASSED", "FAILED", "UNKNOWN", "NEEDS_HUMAN"}:
            st = "UNKNOWN"
        checks.append({"pair": name, "status": st, **ev})
        statuses.append(st)
    if any(s == "FAILED" for s in statuses):
        return CompatibilityResult("FAILED", checks=checks)
    if any(s in {"UNKNOWN", "NEEDS_HUMAN"} for s in statuses):
        return CompatibilityResult(
            "NEEDS_HUMAN" if "NEEDS_HUMAN" in statuses else "UNKNOWN",
            checks=checks,
            notes=["compatibility not fully verified"],
        )
    return CompatibilityResult("PASSED", checks=checks)
