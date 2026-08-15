"""Role discovery for agency scenarios — REQUIRED / OPTIONAL / NOT_REQUIRED / UNKNOWN.

Does not hardcode that all roles are required.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Need = Literal["REQUIRED", "OPTIONAL", "NOT_REQUIRED", "UNKNOWN"]


@dataclass
class RoleNeed:
    role_id: str
    need: Need
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_roles_for_intent(intent: dict[str, Any]) -> list[RoleNeed]:
    utterance = str(intent.get("utterance") or "").lower()
    possible = set(intent.get("possible_intents") or [])
    decisions: dict[str, RoleNeed] = {}

    def set_need(role: str, need: Need, reason: str) -> None:
        # First decision wins unless upgrading UNKNOWN → something stronger
        prev = decisions.get(role)
        if prev and prev.need != "UNKNOWN" and need == "UNKNOWN":
            return
        if prev and prev.need == "REQUIRED":
            return
        decisions[role] = RoleNeed(role_id=role, need=need, reason=reason)

    buildish = "build" in possible or any(
        x in utterance for x in ("crear", "aplicación", "application", "constru")
    )
    if buildish:
        set_need("eos.role.product-manager", "REQUIRED", "Greenfield product needs outcome ownership")
        set_need("eos.role.system-architect", "REQUIRED", "Architecture for new application")
        set_need("eos.role.software-architect", "OPTIONAL", "May share architecture load")
        set_need("eos.role.backend-engineer", "REQUIRED", "Application services expected")
        set_need("eos.role.qa-test-engineer", "REQUIRED", "Acceptance criteria imply validation")
        set_need("eos.role.security-engineer", "REQUIRED", "New networked app — security review needed")
        set_need("eos.role.observability-engineer", "OPTIONAL", "Ops visibility usually needed later")
        set_need("eos.role.devops-engineer", "OPTIONAL", "Delivery path not fully specified")
        set_need("eos.role.technical-writer", "OPTIONAL", "Docs may be needed later")
    else:
        set_need("eos.role.product-manager", "UNKNOWN", "Intent class unclear")

    has_ios = "ios" in utterance
    has_android = "android" in utterance
    has_web = "web" in utterance
    if has_ios or has_android:
        set_need(
            "eos.role.mobile-engineer",
            "REQUIRED",
            "iOS/Android called out explicitly — not equivalent to responsive web",
        )
        set_need("eos.role.ui-ux-designer", "REQUIRED", "Multi-platform UX needs design ownership")
    elif has_web:
        set_need("eos.role.mobile-engineer", "NOT_REQUIRED", "Web only — no native mobile stated")
        set_need("eos.role.ui-ux-designer", "OPTIONAL", "Web UX may be needed")
    else:
        set_need("eos.role.mobile-engineer", "UNKNOWN", "Platform targets not stated")
        set_need("eos.role.ui-ux-designer", "UNKNOWN", "UX need not explicit")

    if has_web:
        set_need("eos.role.frontend-engineer", "REQUIRED", "Web visualization target")
    elif buildish:
        set_need("eos.role.frontend-engineer", "UNKNOWN", "Web not explicitly required")

    if "electrolinera" in utterance or "eléctric" in utterance or "electric" in utterance:
        set_need(
            "eos.role.integration-engineer",
            "UNKNOWN",
            "IoT/charging hardware integration not specified — do not invent",
        )
        set_need(
            "eos.role.electrical-engineer-professional",
            "UNKNOWN",
            "Physical electrical work not requested; escalate only if appears",
        )

    # Payments: never invent a dedicated payments engineer as REQUIRED
    set_need(
        "eos.role.product-manager",
        "REQUIRED" if buildish else "UNKNOWN",
        "Payment provider UNKNOWN — product must decide; not assumed",
    )

    return list(decisions.values())
