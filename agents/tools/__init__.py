"""Tool model — operational actions Agents may invoke."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from agents.model import Permission, RiskLevel

SideEffect = Literal["none", "read", "write", "process", "network", "git"]


@dataclass
class ToolDefinition:
    id: str
    purpose: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    required_permissions: list[Permission]
    side_effects: list[SideEffect]
    risk_level: RiskLevel
    timeout_seconds: int = 30
    requires_approval: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Catalog — least privilege; no arbitrary shell tool by default
TOOL_CATALOG: dict[str, ToolDefinition] = {
    "read_file": ToolDefinition(
        id="read_file",
        purpose="Read a text file inside the workspace",
        input_schema={"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
        required_permissions=["READ"],
        side_effects=["read"],
        risk_level="LOW",
    ),
    "list_files": ToolDefinition(
        id="list_files",
        purpose="List files under a workspace-relative directory",
        input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"files": {"type": "array"}}},
        required_permissions=["READ"],
        side_effects=["read"],
        risk_level="LOW",
    ),
    "search_code": ToolDefinition(
        id="search_code",
        purpose="Search file contents for a pattern",
        input_schema={"type": "object", "required": ["pattern"], "properties": {"pattern": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"matches": {"type": "array"}}},
        required_permissions=["READ"],
        side_effects=["read"],
        risk_level="LOW",
    ),
    "git_diff": ToolDefinition(
        id="git_diff",
        purpose="Show git diff in workspace",
        input_schema={"type": "object", "properties": {}},
        output_schema={"type": "object", "properties": {"diff": {"type": "string"}}},
        required_permissions=["READ"],
        side_effects=["read"],
        risk_level="LOW",
    ),
    "git_status": ToolDefinition(
        id="git_status",
        purpose="Show git status",
        input_schema={"type": "object", "properties": {}},
        output_schema={"type": "object", "properties": {"status": {"type": "string"}}},
        required_permissions=["READ"],
        side_effects=["read"],
        risk_level="LOW",
    ),
    "write_file": ToolDefinition(
        id="write_file",
        purpose="Write or create a file inside the workspace",
        input_schema={
            "type": "object",
            "required": ["path", "content"],
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        },
        output_schema={"type": "object", "properties": {"path": {"type": "string"}, "bytes": {"type": "integer"}}},
        required_permissions=["WRITE"],
        side_effects=["write"],
        risk_level="MEDIUM",
    ),
    "run_tests": ToolDefinition(
        id="run_tests",
        purpose="Run an allowlisted test command",
        input_schema={
            "type": "object",
            "properties": {"command": {"type": "string"}, "args": {"type": "array"}},
        },
        output_schema={
            "type": "object",
            "properties": {"exit_code": {"type": "integer"}, "stdout": {"type": "string"}},
        },
        required_permissions=["EXECUTE"],
        side_effects=["process"],
        risk_level="MEDIUM",
        timeout_seconds=120,
    ),
    "run_command": ToolDefinition(
        id="run_command",
        purpose="Run an allowlisted command only",
        input_schema={"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"exit_code": {"type": "integer"}}},
        required_permissions=["EXECUTE"],
        side_effects=["process"],
        risk_level="HIGH",
        requires_approval=True,
        timeout_seconds=60,
        notes=["Never arbitrary shell; allowlist enforced at runtime."],
    ),
}


def get_tool(tool_id: str) -> ToolDefinition:
    if tool_id not in TOOL_CATALOG:
        raise KeyError(f"unknown tool: {tool_id}")
    return TOOL_CATALOG[tool_id]
