"""Tool risk levels and gate requirements."""

from __future__ import annotations

from dataclasses import dataclass

from agents.model import RiskLevel
from agents.tools import ToolDefinition, get_tool

RISK_RANK: dict[RiskLevel, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


@dataclass
class RiskDecision:
    allowed: bool
    requires_gate: bool
    reason: str


def risk_allows(tool: ToolDefinition, ceiling: RiskLevel) -> RiskDecision:
    if RISK_RANK[tool.risk_level] > RISK_RANK[ceiling]:
        return RiskDecision(
            False,
            True,
            f"tool risk {tool.risk_level} exceeds agent ceiling {ceiling}",
        )
    if tool.requires_approval or tool.risk_level in {"HIGH", "CRITICAL"}:
        return RiskDecision(True, True, "approval/gate required for elevated risk")
    return RiskDecision(True, False, "within ceiling")


def evaluate_tool_risk(tool_id: str, ceiling: RiskLevel) -> RiskDecision:
    return risk_allows(get_tool(tool_id), ceiling)
