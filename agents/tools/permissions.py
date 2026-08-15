"""Permission checks — deny by default."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from agents.model import Permission
from agents.tools import ToolDefinition, get_tool

PERMISSION_ORDER: tuple[Permission, ...] = (
    "READ",
    "WRITE",
    "EXECUTE",
    "NETWORK",
    "GIT",
    "DEPLOY",
)


@dataclass
class PermissionDecision:
    allowed: bool
    missing: list[str]
    reason: str


def has_permissions(granted: Iterable[str], required: Iterable[str]) -> PermissionDecision:
    g = set(granted)
    missing = [p for p in required if p not in g]
    if missing:
        return PermissionDecision(False, missing, f"missing permissions: {missing}")
    return PermissionDecision(True, [], "ok")


def authorize_tool(tool_id: str, granted: Iterable[str]) -> PermissionDecision:
    tool = get_tool(tool_id)
    return has_permissions(granted, tool.required_permissions)


def assert_tool_authorized(tool_id: str, granted: Iterable[str]) -> ToolDefinition:
    decision = authorize_tool(tool_id, granted)
    if not decision.allowed:
        raise PermissionError(decision.reason)
    return get_tool(tool_id)
