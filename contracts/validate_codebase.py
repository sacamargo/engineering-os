#!/usr/bin/env python3
"""Validate Codebase Intelligence analysis payloads / snapshots."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SNAPSHOT_RE = re.compile(r"^eos\.snapshot\.[a-f0-9]+$")
FINDING_RE = re.compile(r"^eos\.finding\.[a-z0-9_]+\.\d+$")
EVIDENCE_RE = re.compile(r"^eos\.evidence\.")
SYMBOL_RE = re.compile(r"^eos\.symbol\.[a-f0-9]+$")
DEP_RE = re.compile(r"^eos\.dep\.")

CERTAINTY = frozenset({"observed", "inferred", "unknown"})
DEP_KINDS = frozenset({"import", "package", "inferred_runtime"})
ANALYSIS_STATUS = frozenset({"not_run", "deferred", "complete", "failed"})


@dataclass
class Finding:
    path: str
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


def _require(cond: bool, findings: list[Finding], path: str, code: str, message: str) -> None:
    if not cond:
        findings.append(Finding(path, code, message))


def validate_snapshot(snapshot: dict[str, Any], path: str = "snapshot") -> list[Finding]:
    findings: list[Finding] = []
    _require(isinstance(snapshot, dict), findings, path, "invalid_type", "snapshot must be object")
    if findings:
        return findings

    sid = snapshot.get("id")
    _require(isinstance(sid, str) and bool(SNAPSHOT_RE.match(sid)), findings, path, "invalid_id", f"bad snapshot id {sid!r}")

    meta = snapshot.get("meta") or {}
    _require(isinstance(meta, dict), findings, f"{path}.meta", "invalid_type", "meta must be object")
    _require(bool(meta.get("root")), findings, f"{path}.meta", "invalid_snapshot", "meta.root required")
    _require(bool(meta.get("analyzed_at")), findings, f"{path}.meta", "invalid_snapshot", "meta.analyzed_at required")

    for i, sym in enumerate(snapshot.get("symbols") or []):
        p = f"{path}.symbols[{i}]"
        _require(isinstance(sym, dict), findings, p, "invalid_type", "symbol must be object")
        if not isinstance(sym, dict):
            continue
        _require(isinstance(sym.get("id"), str) and bool(SYMBOL_RE.match(sym["id"])), findings, p, "invalid_id", "bad symbol id")
        _require(bool(sym.get("path")), findings, p, "missing_location", "symbol.path required")
        _require(isinstance(sym.get("line_start"), int), findings, p, "missing_location", "symbol.line_start required")
        _require(sym.get("certainty", "observed") in CERTAINTY, findings, p, "invalid_status", "bad certainty")

    for i, dep in enumerate(snapshot.get("dependencies") or []):
        p = f"{path}.dependencies[{i}]"
        _require(isinstance(dep, dict), findings, p, "invalid_type", "dependency must be object")
        if not isinstance(dep, dict):
            continue
        _require(isinstance(dep.get("id"), str) and bool(DEP_RE.match(dep["id"])), findings, p, "invalid_id", "bad dependency id")
        _require(bool(dep.get("source_path")), findings, p, "invalid_dependency", "source_path required")
        _require(bool(dep.get("target")), findings, p, "invalid_dependency", "target required")
        _require(dep.get("kind") in DEP_KINDS, findings, p, "invalid_dependency", f"bad kind {dep.get('kind')}")
        _require(dep.get("certainty") in CERTAINTY, findings, p, "invalid_status", "bad certainty")

    for i, f in enumerate(snapshot.get("findings") or []):
        p = f"{path}.findings[{i}]"
        _require(isinstance(f, dict), findings, p, "invalid_type", "finding must be object")
        if not isinstance(f, dict):
            continue
        _require(isinstance(f.get("id"), str) and bool(FINDING_RE.match(f["id"])), findings, p, "invalid_id", "bad finding id")
        evidence = f.get("evidence")
        _require(isinstance(evidence, list) and len(evidence) > 0, findings, p, "missing_evidence", "finding requires evidence")
        _require(f.get("confidence") in CERTAINTY, findings, p, "invalid_status", "bad confidence")

    for i, e in enumerate(snapshot.get("evidence") or []):
        p = f"{path}.evidence[{i}]"
        _require(isinstance(e, dict), findings, p, "invalid_type", "evidence must be object")
        if not isinstance(e, dict):
            continue
        _require(isinstance(e.get("id"), str) and bool(EVIDENCE_RE.match(e["id"])), findings, p, "invalid_id", "bad evidence id")
        _require(bool(e.get("pointer")), findings, p, "missing_evidence", "evidence.pointer required")

    for i, t in enumerate(snapshot.get("tests") or []):
        p = f"{path}.tests[{i}]"
        if not isinstance(t, dict):
            continue
        cov = t.get("coverage", "unknown")
        if cov in {0, 0.0, "0", "0%"}:
            findings.append(Finding(p, "invalid_status", "coverage 0/0% without measurement is forbidden; use unknown"))

    return findings


def validate_analysis_payload(payload: dict[str, Any], path: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    _require(isinstance(payload, dict), findings, path, "invalid_type", "payload must be object")
    if findings:
        return findings
    schema = payload.get("schema")
    _require(schema == "eos.codebase.analysis.v1", findings, path, "invalid_metadata", f"unexpected schema {schema!r}")
    snap = payload.get("snapshot")
    _require(isinstance(snap, dict), findings, f"{path}.snapshot", "invalid_snapshot", "snapshot required")
    if isinstance(snap, dict):
        findings.extend(validate_snapshot(snap, f"{path}.snapshot"))
    return findings


def self_check() -> list[Finding]:
    """Validate a tiny in-memory valid + invalid pair."""
    findings: list[Finding] = []
    valid = {
        "schema": "eos.codebase.analysis.v1",
        "snapshot": {
            "id": "eos.snapshot.abc123def456",
            "meta": {"root": "/tmp/r", "analyzed_at": "2026-01-01T00:00:00+00:00"},
            "symbols": [
                {
                    "id": "eos.symbol.abcdef1234",
                    "name": "f",
                    "kind": "function",
                    "path": "a.py",
                    "line_start": 1,
                    "certainty": "observed",
                }
            ],
            "dependencies": [
                {
                    "id": "eos.dep.1",
                    "source_path": "a.py",
                    "target": "b",
                    "kind": "import",
                    "certainty": "observed",
                }
            ],
            "findings": [
                {
                    "id": "eos.finding.missing_tests.1",
                    "kind": "missing_tests",
                    "confidence": "observed",
                    "evidence": ["tests:0"],
                }
            ],
            "evidence": [{"id": "eos.evidence.x", "pointer": "a.py:1"}],
            "tests": [{"path": "t.py", "coverage": "unknown"}],
        },
    }
    findings.extend(validate_analysis_payload(valid, "valid"))
    invalid = {
        "schema": "eos.codebase.analysis.v1",
        "snapshot": {
            "id": "bad",
            "meta": {},
            "findings": [{"id": "eos.finding.x.1", "confidence": "observed", "evidence": []}],
            "tests": [{"coverage": "0%"}],
        },
    }
    inv = validate_analysis_payload(invalid, "invalid")
    if not inv:
        findings.append(Finding("invalid", "self_check", "expected invalid payload to fail"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Codebase Intelligence JSON")
    parser.add_argument("path", nargs="?", help="analysis JSON path")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    all_findings: list[Finding] = []
    if args.self_check or not args.path:
        all_findings.extend(self_check())
    if args.path:
        payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
        all_findings.extend(validate_analysis_payload(payload))
    for f in all_findings:
        # self_check valid section should be empty; filter path prefix
        if f.path.startswith("valid"):
            print(f.format(), file=sys.stderr)
    real = [f for f in all_findings if not f.path.startswith("valid")]
    # For self-check, only report unexpected issues on valid; invalid findings are expected
    if args.self_check and not args.path:
        unexpected = [f for f in all_findings if f.path.startswith("valid") or f.code == "self_check"]
        if unexpected:
            for f in unexpected:
                print(f.format(), file=sys.stderr)
            return 1
        print("codebase contracts self-check OK")
        return 0
    if real:
        for f in real:
            print(f.format(), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
