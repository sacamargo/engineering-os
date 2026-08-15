"""Agent Definition vs Runtime Instance models."""

from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

AgentType = Literal["coding", "analysis", "human", "mock", "deterministic"]
Permission = Literal["READ", "WRITE", "EXECUTE", "NETWORK", "GIT", "DEPLOY"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class AgentLimits:
    timeout_seconds: int = 120
    max_tool_calls: int = 50
    max_retries: int = 2
    max_files_modified: int = 20
    max_context_bytes: int = 200_000

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentDefinition:
    id: str
    type: AgentType
    operational_capabilities: list[str] = field(default_factory=list)
    authorized_tools: list[str] = field(default_factory=list)
    permissions: list[Permission] = field(default_factory=lambda: ["READ"])
    limits: AgentLimits = field(default_factory=AgentLimits)
    risk_ceiling: RiskLevel = "MEDIUM"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "operational_capabilities": self.operational_capabilities,
            "authorized_tools": self.authorized_tools,
            "permissions": list(self.permissions),
            "limits": self.limits.to_dict(),
            "risk_ceiling": self.risk_ceiling,
            "notes": self.notes,
        }

    def validate_not_god(self) -> None:
        """Reject omnipotent definitions."""
        all_perms = {"READ", "WRITE", "EXECUTE", "NETWORK", "GIT", "DEPLOY"}
        if set(self.permissions) >= all_perms:
            raise ValueError("god agent forbidden: all permissions")
        if self.risk_ceiling == "CRITICAL" and "DEPLOY" in self.permissions:
            raise ValueError("god agent forbidden: CRITICAL+DEPLOY")
        if len(self.authorized_tools) > 40:
            raise ValueError("god agent forbidden: excessive tools")


@dataclass
class AgentInstance:
    id: str
    definition_id: str
    status: str = "created"
    task_id: str | None = None
    context_ref: str | None = None
    permissions: list[Permission] = field(default_factory=list)
    timeout_seconds: int = 120
    evidence_ids: list[str] = field(default_factory=list)
    tool_call_count: int = 0
    files_modified: int = 0
    started_at: float | None = None
    ended_at: float | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_run_id(definition_id: str, task_id: str | None = None) -> str:
    raw = f"{definition_id}|{task_id or ''}|{time.time_ns()}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"eos.agent.run.{digest}"


def instantiate(definition: AgentDefinition, task_id: str | None = None) -> AgentInstance:
    definition.validate_not_god()
    return AgentInstance(
        id=new_run_id(definition.id, task_id),
        definition_id=definition.id,
        status="created",
        task_id=task_id,
        permissions=list(definition.permissions),
        timeout_seconds=definition.limits.timeout_seconds,
        notes=["Instance permissions are capped by definition."],
    )


# Built-in definitions (catalog stubs — not a zoo)
ANALYSIS_AGENT = AgentDefinition(
    id="eos.agent.analysis",
    type="analysis",
    operational_capabilities=["inspect", "search"],
    authorized_tools=["read_file", "list_files", "search_code", "git_diff", "git_status"],
    permissions=["READ"],
    risk_ceiling="LOW",
    notes=["Read-only analysis agent."],
)

CODING_AGENT = AgentDefinition(
    id="eos.agent.coding",
    type="coding",
    operational_capabilities=["inspect", "modify", "test"],
    authorized_tools=[
        "read_file",
        "list_files",
        "search_code",
        "git_diff",
        "git_status",
        "write_file",
        "run_tests",
    ],
    permissions=["READ", "WRITE", "EXECUTE"],
    risk_ceiling="MEDIUM",
    limits=AgentLimits(timeout_seconds=180, max_tool_calls=80, max_files_modified=15),
    notes=["May write and run tests; no DEPLOY/NETWORK/GIT push."],
)

HUMAN_EXECUTOR = AgentDefinition(
    id="eos.agent.human",
    type="human",
    operational_capabilities=["approve", "perform_professional_work"],
    authorized_tools=[],
    permissions=["READ"],
    risk_ceiling="CRITICAL",
    notes=["Human executor — not an AI agent; professional authority stays human."],
)
