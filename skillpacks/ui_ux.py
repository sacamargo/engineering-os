"""UI UX PRO MAX helpers — fail closed without source; no code mutation grants."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from skillpacks.registry import load_registry

UI_UX_ID = "eos.skillpack.design.ui-ux-pro-max"
Mode = Literal["DESIGN", "REVIEW", "IMPROVEMENT"]


@dataclass
class UiUxInvocation:
    skill_id: str
    skill_version: str
    mode: Mode
    status: str
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    grants_code_execution: bool = False
    bypasses_security: bool = False
    evidence: list[dict[str, Any]] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def invoke_ui_ux(mode: Mode, *, intent: str = "") -> UiUxInvocation:
    pack = load_registry().get(UI_UX_ID)
    version = pack.version if pack else "unknown"
    if pack is None or not pack.is_selectable():
        return UiUxInvocation(
            skill_id=UI_UX_ID,
            skill_version=version,
            mode=mode,
            status="unavailable",
            grants_code_execution=False,
            bypasses_security=False,
            uncertainty=["UI UX PRO MAX source missing; methodology not fabricated"],
            evidence=[{"kind": "skill_unavailable", "action": "NEEDS_SOURCE", "intent": intent}],
        )
    return UiUxInvocation(
        skill_id=UI_UX_ID,
        skill_version=version,
        mode=mode,
        status="ready",
        grants_code_execution=False,
        bypasses_security=False,
        artifacts=[{"kind": "placeholder", "note": "source-backed artifacts only"}],
        evidence=[{"kind": "mode_selected", "mode": mode}],
        uncertainty=[],
    )
