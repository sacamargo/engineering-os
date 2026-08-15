"""Local tool runtime — executes tools inside a Workspace sandbox."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from agents.invocation import ToolInvocation, ToolResult, timed_ms
from agents.model import AgentDefinition, AgentInstance, RiskLevel
from agents.sandbox import Workspace, WorkspaceEscapeError
from agents.tools.commands import CommandPolicyError, parse_command_key, run_allowlisted
from agents.tools.permissions import assert_tool_authorized
from agents.tools.risk import evaluate_tool_risk


class ToolRuntimeError(RuntimeError):
    pass


class LocalToolRuntime:
    def __init__(
        self,
        workspace: Workspace,
        definition: AgentDefinition,
        instance: AgentInstance,
        *,
        approval_granted: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace
        self.definition = definition
        self.instance = instance
        self.approval_granted = approval_granted
        self.dry_run = dry_run
        self.write_log: list[dict[str, Any]] = []

    def invoke(self, invocation: ToolInvocation) -> ToolResult:
        start = time.perf_counter()
        try:
            if invocation.tool_id not in self.definition.authorized_tools:
                raise PermissionError(f"tool not authorized for agent: {invocation.tool_id}")
            assert_tool_authorized(invocation.tool_id, self.instance.permissions)
            risk = evaluate_tool_risk(invocation.tool_id, self.definition.risk_ceiling)
            if not risk.allowed:
                raise PermissionError(risk.reason)
            if risk.requires_gate and not self.approval_granted and invocation.tool_id == "run_command":
                raise PermissionError("approval gate required for run_command")

            if self.instance.tool_call_count >= self.definition.limits.max_tool_calls:
                raise ToolRuntimeError("max tool calls exceeded")

            if self.dry_run and invocation.tool_id in {"write_file", "run_tests", "run_command"}:
                out = {"dry_run": True, "would_invoke": invocation.tool_id, "arguments": invocation.arguments}
                self.instance.tool_call_count += 1
                return ToolResult(
                    True,
                    out,
                    evidence=[{"kind": "dry_run", "tool": invocation.tool_id}],
                    duration_ms=timed_ms(start),
                    invocation_id=invocation.id,
                    tool_id=invocation.tool_id,
                )

            handler = {
                "read_file": self._read_file,
                "list_files": self._list_files,
                "search_code": self._search_code,
                "git_diff": self._git_diff,
                "git_status": self._git_status,
                "write_file": self._write_file,
                "run_tests": self._run_tests,
                "run_command": self._run_command,
            }.get(invocation.tool_id)
            if handler is None:
                raise ToolRuntimeError(f"no handler: {invocation.tool_id}")
            output, evidence = handler(invocation.arguments)
            self.instance.tool_call_count += 1
            return ToolResult(
                True,
                output,
                evidence=evidence,
                duration_ms=timed_ms(start),
                invocation_id=invocation.id,
                tool_id=invocation.tool_id,
            )
        except Exception as exc:  # noqa: BLE001 — surfaced as tool result
            return ToolResult(
                False,
                {},
                evidence=[{"kind": "tool_error", "error": type(exc).__name__, "message": str(exc)}],
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=timed_ms(start),
                invocation_id=invocation.id,
                tool_id=invocation.tool_id,
            )

    def _read_file(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        rel = args["path"]
        path = self.workspace.resolve(rel)
        if not self.workspace.may_read(rel):
            raise PermissionError(f"sensitive/blocked read: {rel}")
        content = path.read_text(encoding="utf-8", errors="replace")
        return {"path": rel, "content": content}, [{"kind": "file_read", "path": rel, "bytes": len(content)}]

    def _list_files(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        rel = args.get("path") or "."
        base = self.workspace.resolve(rel)
        files = []
        for p in sorted(base.rglob("*")):
            if p.is_file():
                files.append(self.workspace.relpath(p))
            if len(files) >= 500:
                break
        return {"files": files}, [{"kind": "list_files", "path": rel, "count": len(files)}]

    def _search_code(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        pattern = args["pattern"]
        regex = re.compile(pattern)
        matches = []
        for p in self.workspace.root.rglob("*"):
            if not p.is_file():
                continue
            rel = self.workspace.relpath(p)
            if not self.workspace.may_read(rel):
                continue
            if p.suffix not in {".py", ".js", ".ts", ".tsx", ".md", ".json", ".yml", ".yaml", ".txt"}:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if regex.search(line):
                    matches.append({"path": rel, "line": i, "text": line[:200]})
                    if len(matches) >= 100:
                        return {"matches": matches}, [{"kind": "search", "pattern": pattern, "count": len(matches)}]
        return {"matches": matches}, [{"kind": "search", "pattern": pattern, "count": len(matches)}]

    def _git_diff(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        result = run_allowlisted(self.workspace.root, "git_diff", timeout=30)
        return {"diff": result.stdout, "exit_code": result.exit_code}, [
            {"kind": "command", "argv": result.argv, "exit_code": result.exit_code}
        ]

    def _git_status(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        result = run_allowlisted(self.workspace.root, "git_status", timeout=30)
        return {"status": result.stdout, "exit_code": result.exit_code}, [
            {"kind": "command", "argv": result.argv, "exit_code": result.exit_code}
        ]

    def _write_file(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        rel = args["path"]
        content = args["content"]
        if not self.workspace.may_write(rel):
            raise PermissionError(f"write forbidden: {rel}")
        if self.instance.files_modified >= self.definition.limits.max_files_modified:
            raise ToolRuntimeError("max files modified exceeded")
        path = self.workspace.resolve(rel)
        before = path.read_text(encoding="utf-8", errors="replace") if path.exists() else None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.instance.files_modified += 1
        entry = {
            "path": rel,
            "before": before,
            "after": content,
            "agent_id": self.instance.id,
            "task_id": self.instance.task_id,
        }
        self.write_log.append(entry)
        evidence = [
            {
                "kind": "file_write",
                "path": rel,
                "bytes": len(content.encode("utf-8")),
                "created": before is None,
            }
        ]
        return {"path": rel, "bytes": len(content.encode("utf-8"))}, evidence

    def _run_tests(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        raw = args.get("command") or "python3 -m unittest"
        key, extra = parse_command_key(raw)
        if key not in {"pytest", "python_unittest", "npm_test"}:
            raise CommandPolicyError("run_tests only allows test commands")
        result = run_allowlisted(
            self.workspace.root, key, extra, timeout=self.definition.limits.timeout_seconds
        )
        return {
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "argv": result.argv,
        }, [{"kind": "tests", "argv": result.argv, "exit_code": result.exit_code}]

    def _run_command(self, args: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        raw = args["command"]
        key, extra = parse_command_key(raw)
        result = run_allowlisted(self.workspace.root, key, extra, timeout=60)
        return {
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "argv": result.argv,
        }, [{"kind": "command", "argv": result.argv, "exit_code": result.exit_code}]
