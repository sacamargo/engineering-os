"""Skill failure taxonomy and escalation — integrate with Failure/Retry/Replan patterns."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

SkillFailureCode = Literal[
    "SKILL_UNAVAILABLE",
    "SKILL_SOURCE_MISSING",
    "SKILL_VERSION_UNRESOLVED",
    "SKILL_NOT_APPLICABLE",
    "SKILL_INPUT_INCOMPLETE",
    "SKILL_TOOL_MISSING",
    "SKILL_KNOWLEDGE_MISSING",
    "SKILL_OUTPUT_INVALID",
    "SKILL_GATE_FAILED",
    "SKILL_CONFLICT",
    "SKILL_UNCERTAIN",
]

Disposition = Literal["retry", "replan", "escalate", "blocked", "needs_input", "needs_human"]


@dataclass
class SkillFailure:
    code: SkillFailureCode
    message: str
    skill_id: str | None = None
    retryable: bool = False
    disposition: Disposition = "blocked"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_RETRYABLE = frozenset({"SKILL_TOOL_MISSING", "SKILL_VERSION_UNRESOLVED"})
_NEEDS_INPUT = frozenset({"SKILL_INPUT_INCOMPLETE", "SKILL_SOURCE_MISSING", "SKILL_UNAVAILABLE"})
_NEEDS_HUMAN = frozenset({"SKILL_CONFLICT", "SKILL_UNCERTAIN"})


def classify_skill_failure(code: SkillFailureCode, skill_id: str | None = None, message: str = "") -> SkillFailure:
    if code in _NEEDS_INPUT:
        disp: Disposition = "needs_input"
        retry = False
    elif code in _NEEDS_HUMAN:
        disp = "needs_human"
        retry = False
    elif code in _RETRYABLE:
        disp = "retry"
        retry = True
    elif code == "SKILL_NOT_APPLICABLE":
        disp = "replan"
        retry = False
    else:
        disp = "blocked"
        retry = False
    return SkillFailure(code=code, message=message or code, skill_id=skill_id, retryable=retry, disposition=disp)


def escalation_for_pack(pack_status: str, missing_source: bool, domain_beyond_authority: bool) -> dict[str, str]:
    if missing_source or pack_status == "unavailable":
        return {"action": "NEEDS_SOURCE", "reason": "Skill source required"}
    if domain_beyond_authority:
        return {"action": "NEEDS_HUMAN", "reason": "Domain beyond Skill authority"}
    return {"action": "NONE", "reason": ""}
