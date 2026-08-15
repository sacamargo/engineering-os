"""Skill security — Skills cannot elevate authority."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

FORBIDDEN_SKILL_ACTIONS = frozenset(
    {
        "bypass_permissions",
        "execute_shell",
        "grant_tools",
        "grant_deploy",
        "bypass_approval",
        "bypass_human_escalation",
        "modify_security_policy",
        "modify_other_skill_permissions",
        "inject_tool_commands",
    }
)


@dataclass
class SecurityVerdict:
    allowed: bool
    violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_skill_security(manifest: dict[str, Any], agent_permissions: list[str] | None = None) -> SecurityVerdict:
    violations: list[str] = []
    meta = manifest.get("metadata") or {}
    for key in FORBIDDEN_SKILL_ACTIONS:
        if manifest.get(key) or meta.get(key):
            violations.append(key)
    for key in ("grants_permissions", "grants_tools", "bypass_gates", "auto_approve", "deploy_execute"):
        if key in manifest or key in meta:
            violations.append(key)
    # Skill instructions must not inject tool command lists as grants
    for wf in manifest.get("workflows") or []:
        for step in wf.get("steps") or []:
            if not isinstance(step, str):
                continue
            if step.strip().startswith("!") or "rm -rf" in step:
                violations.append("inject_tool_commands")
    notes = [
        "Skill instructions may influence strategy only",
        "Skill cannot elevate Agent permissions",
    ]
    if agent_permissions and "DEPLOY_EXECUTE" in agent_permissions:
        # Skill still cannot be the granter — presence on agent is separate
        notes.append("Deploy permission must come from Agent policy, never Skill")
    return SecurityVerdict(allowed=not violations, violations=violations, notes=notes)
