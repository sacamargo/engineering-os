#!/usr/bin/env python3
"""Validate Production Operations payloads."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from typing import Any

OP_RE = re.compile(r"^eos\.prodop\.[a-f0-9]+$")
ENVS = frozenset({"local", "development", "test", "staging", "production"})
OPS_STATUS = frozenset(
    {
        "planned",
        "validating",
        "awaiting_approval",
        "deploying",
        "verifying",
        "succeeded",
        "failed",
        "degraded",
        "rollback_required",
        "rolling_back",
        "rolled_back",
        "needs_human",
        "cancelled",
    }
)
HEALTH = frozenset({"healthy", "degraded", "unhealthy", "unknown"})
SEV = frozenset({"SEV1", "SEV2", "SEV3", "SEV4"})
INC_STATUS = frozenset({"detected", "triaging", "mitigating", "monitoring", "resolved", "needs_human"})


@dataclass
class Finding:
    path: str
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


def validate_environment(env: dict[str, Any], path: str = "$.environment") -> list[Finding]:
    findings: list[Finding] = []
    if env.get("name") not in ENVS and env.get("classification") not in ENVS:
        findings.append(Finding(path, "invalid_environment", "unknown environment class"))
    if env.get("classification") == "production" and env.get("risk") not in {"high", "critical"}:
        findings.append(Finding(path, "production_risk", "production must be high/critical risk"))
    if env.get("classification") == "production" and env.get("approval_policy") != "human_required":
        findings.append(Finding(path, "approval_policy", "production requires human_required"))
    return findings


def validate_operation(op: dict[str, Any], path: str = "$.operation") -> list[Finding]:
    findings: list[Finding] = []
    if op.get("status") not in OPS_STATUS:
        findings.append(Finding(path, "invalid_status", f"bad status {op.get('status')}"))
    if op.get("health_status") not in HEALTH | {None}:
        findings.append(Finding(path, "invalid_health", f"bad health {op.get('health_status')}"))
    if op.get("status") == "succeeded" and op.get("health_status") not in {"healthy", None}:
        # dry-run may leave unknown; require healthy for real success with health set
        if op.get("health_status") and op.get("health_status") != "healthy":
            findings.append(Finding(path, "invalid_success", "succeeded requires healthy"))
    if op.get("status") == "succeeded" and op.get("health_status") == "unknown":
        findings.append(Finding(path, "unknown_as_passed", "UNKNOWN health ≠ succeeded"))
    return findings


def validate_incident(inc: dict[str, Any], path: str = "$.incident") -> list[Finding]:
    findings: list[Finding] = []
    if inc.get("severity") not in SEV:
        findings.append(Finding(path, "invalid_severity", "bad severity"))
    if inc.get("status") not in INC_STATUS:
        findings.append(Finding(path, "invalid_status", "bad incident status"))
    if inc.get("status") == "resolved" and not (inc.get("resolution") or inc.get("evidence")):
        findings.append(Finding(path, "missing_resolution", "resolved needs evidence"))
    return findings


def validate_alert(alert: dict[str, Any], path: str = "$.alert") -> list[Finding]:
    findings: list[Finding] = []
    if alert.get("severity") not in SEV:
        findings.append(Finding(path, "invalid_severity", "bad severity"))
    if alert.get("status") not in {"open", "resolved", "discarded", "promoted_incident"}:
        findings.append(Finding(path, "invalid_status", "bad alert status"))
    return findings


def validate_production_result(payload: dict[str, Any], path: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    op = payload.get("operation") or {}
    findings.extend(validate_operation(op, f"{path}.operation"))
    env = payload.get("environment")
    if env:
        findings.extend(validate_environment(env, f"{path}.environment"))
    if payload.get("incident"):
        findings.extend(validate_incident(payload["incident"], f"{path}.incident"))
    if payload.get("alert"):
        findings.extend(validate_alert(payload["alert"], f"{path}.alert"))
    # secrets must not appear
    blob = str(payload).lower()
    if "password:" in blob or "api_key=" in blob or "bearer " in blob:
        findings.append(Finding(path, "secret_leakage", "secrets forbidden in payload"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        bad = {
            "operation": {"status": "succeeded", "health_status": "unknown"},
            "environment": {"classification": "production", "risk": "low", "approval_policy": "none"},
            "incident": {"severity": "SEV1", "status": "resolved"},
            "alert": {"severity": "SEV9", "status": "open"},
        }
        findings = validate_production_result(bad)
        if len(findings) < 4:
            print("expected multiple failures", findings, file=sys.stderr)
            return 1
        good = {
            "operation": {"status": "succeeded", "health_status": "healthy"},
            "environment": {
                "classification": "production",
                "risk": "critical",
                "approval_policy": "human_required",
            },
        }
        if validate_production_result(good):
            print("unexpected failures on good payload", file=sys.stderr)
            return 1
        print("production contracts self-check OK")
        return 0
    print("use --self-check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
