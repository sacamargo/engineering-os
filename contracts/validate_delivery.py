#!/usr/bin/env python3
"""Validate Delivery Layer payloads."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from typing import Any

DELIVERY_RE = re.compile(r"^eos\.delivery\.[a-f0-9]+$")
BUILD_RE = re.compile(r"^eos\.build\.[a-f0-9]+$")
ART_RE = re.compile(r"^eos\.dartifact\.[a-z0-9_]+\.[a-f0-9]+$")
VAL_RE = re.compile(r"^eos\.validation\.[a-z0-9_]+\.[a-f0-9]+$")
RC_RE = re.compile(r"^eos\.rc\.[a-f0-9]+$")
VAL_STATUS = frozenset({"NOT_RUN", "PASSED", "FAILED", "BLOCKED", "UNKNOWN"})
DELIVERY_STATUS = frozenset(
    {"draft", "building", "validating", "ready", "blocked", "needs_human", "released", "failed", "cancelled"}
)


@dataclass
class Finding:
    path: str
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


def validate_delivery_result(payload: dict[str, Any], path: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    delivery = payload.get("delivery") or {}
    if not DELIVERY_RE.match(str(delivery.get("id") or "")):
        findings.append(Finding(f"{path}.delivery", "invalid_id", "bad delivery id"))
    if delivery.get("status") not in DELIVERY_STATUS:
        findings.append(Finding(f"{path}.delivery", "invalid_status", f"bad status {delivery.get('status')}"))
    build = payload.get("build")
    if build:
        if not BUILD_RE.match(str(build.get("id") or "")):
            findings.append(Finding(f"{path}.build", "invalid_id", "bad build id"))
        if build.get("status") == "succeeded" and not build.get("evidence"):
            findings.append(Finding(f"{path}.build", "missing_evidence", "succeeded build needs evidence"))
    for i, a in enumerate(payload.get("artifacts") or []):
        if not ART_RE.match(str(a.get("id") or "")):
            findings.append(Finding(f"{path}.artifacts[{i}]", "invalid_id", "bad artifact id"))
        if a.get("type") in {"package", "build_output", "source_bundle"} and not a.get("digest"):
            findings.append(Finding(f"{path}.artifacts[{i}]", "invalid_artifact", "digest required"))
    for i, v in enumerate(payload.get("validations") or []):
        if not VAL_RE.match(str(v.get("id") or "")):
            findings.append(Finding(f"{path}.validations[{i}]", "invalid_id", "bad validation id"))
        if v.get("status") not in VAL_STATUS:
            findings.append(Finding(f"{path}.validations[{i}]", "invalid_status", "bad validation status"))
        if v.get("status") == "NOT_RUN" and payload.get("readiness") in {
            "READY_FOR_RELEASE",
            "READY_FOR_DEPLOYMENT",
        }:
            findings.append(Finding(f"{path}", "gate_bypass", "NOT_RUN cannot yield ready release"))
    rc = payload.get("release_candidate")
    if rc and not RC_RE.match(str(rc.get("id") or "")):
        findings.append(Finding(f"{path}.release_candidate", "invalid_id", "bad rc id"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        bad = {
            "delivery": {"id": "bad", "status": "released"},
            "build": {"id": "eos.build.abc123def456", "status": "succeeded", "evidence": []},
            "readiness": "READY_FOR_DEPLOYMENT",
            "validations": [{"id": "eos.validation.unit.abc123def4", "status": "NOT_RUN"}],
        }
        findings = validate_delivery_result(bad)
        if not findings:
            print("expected failures", file=sys.stderr)
            return 1
        print("delivery contracts self-check OK")
        return 0
    print("pass --self-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
