"""Controlled build/test executors — reuse agents sandbox + allowlist."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from agents.sandbox import Workspace
from agents.tools.commands import CommandPolicyError, parse_command_key, run_allowlisted


def run_build_step(
    workspace: Workspace,
    *,
    command: str = "python3 -m unittest",
    timeout: int = 120,
) -> dict[str, Any]:
    """Minimal 'build' = compile/import check via allowlisted test/unittest runner smoke."""
    t0 = time.perf_counter()
    try:
        key, extra = parse_command_key(command)
        # Build phase prefers discovery that fails closed on zero tests when used as validate;
        # for pure build we allow a no-op compile marker file write outside — keep command only.
        result = run_allowlisted(workspace.root, key, extra, timeout=timeout)
        return {
            "success": result.exit_code == 0,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "argv": result.argv,
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "evidence": [{"kind": "build_command", "argv": result.argv, "exit_code": result.exit_code}],
        }
    except (CommandPolicyError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": str(exc),
            "argv": [],
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "evidence": [{"kind": "build_error", "error": str(exc)}],
            "error": str(exc),
        }


def run_test_step(
    workspace: Workspace,
    *,
    command: str = "python3 -m unittest discover -s . -v",
    timeout: int = 120,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        key, extra = parse_command_key(command)
        if key not in {"pytest", "python_unittest", "npm_test"}:
            raise CommandPolicyError("test executor only allows test commands")
        result = run_allowlisted(workspace.root, key, extra, timeout=timeout)
        blob = f"{result.stdout}\n{result.stderr}"
        zero = "Ran 0 tests" in blob
        passed = result.exit_code == 0 and not zero and ("OK" in blob or "passed" in blob.lower())
        status = "PASSED" if passed else ("FAILED" if not zero or result.exit_code != 0 else "FAILED")
        if zero:
            status = "FAILED"
        return {
            "success": passed,
            "status": status,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "argv": result.argv,
            "zero_tests": zero,
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "evidence": [
                {
                    "kind": "tests",
                    "argv": result.argv,
                    "exit_code": result.exit_code,
                    "zero_tests": zero,
                    "status": status,
                }
            ],
        }
    except (CommandPolicyError, TimeoutError, OSError) as exc:
        return {
            "success": False,
            "status": "FAILED",
            "exit_code": 1,
            "stdout": "",
            "stderr": str(exc),
            "argv": [],
            "zero_tests": False,
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "evidence": [{"kind": "test_error", "error": str(exc)}],
            "error": str(exc),
        }


def write_artifact_bundle(
    workspace: Workspace,
    *,
    relative_dir: str = "build/artifacts",
    name: str = "bundle.txt",
    content: str,
) -> dict[str, Any]:
    rel = f"{relative_dir.rstrip('/')}/{name}"
    path = workspace.resolve(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8")
    path.write_bytes(data)
    digest = __import__("hashlib").sha256(data).hexdigest()
    return {
        "path": rel,
        "digest": digest,
        "bytes": len(data),
        "evidence": [{"kind": "artifact_written", "path": rel, "digest": digest}],
    }
