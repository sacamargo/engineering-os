"""Allowlisted command execution."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ALLOWED_COMMANDS: dict[str, tuple[str, ...]] = {
    "pytest": ("pytest",),
    "python_unittest": ("python3", "-m", "unittest"),
    "npm_test": ("npm", "test"),
    "npm_lint": ("npm", "run", "lint"),
    "git_diff": ("git", "diff"),
    "git_status": ("git", "status", "--porcelain"),
}

FORBIDDEN_TOKENS = (
    "sudo",
    "rm",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    ">",
    "|",
    ";",
    "&&",
    "`",
    "$(",
)


@dataclass
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str
    argv: list[str]


class CommandPolicyError(PermissionError):
    pass


def resolve_allowlisted(command_key: str, extra_args: Sequence[str] | None = None) -> list[str]:
    if command_key not in ALLOWED_COMMANDS:
        raise CommandPolicyError(f"command not allowlisted: {command_key}")
    argv = list(ALLOWED_COMMANDS[command_key])
    for a in extra_args or ():
        s = str(a)
        if any(tok in s for tok in FORBIDDEN_TOKENS):
            raise CommandPolicyError(f"forbidden token in args: {s}")
        if s.startswith("-") and command_key.startswith("git"):
            # allow limited git flags only
            if s not in {"--porcelain", "--stat", "-u"}:
                raise CommandPolicyError(f"git flag not allowed: {s}")
        argv.append(s)
    return argv


def run_allowlisted(
    workspace: Path,
    command_key: str,
    extra_args: Sequence[str] | None = None,
    *,
    timeout: int = 60,
) -> CommandResult:
    argv = resolve_allowlisted(command_key, extra_args)
    # Re-check joined string for injection attempts
    joined = " ".join(argv)
    if any(tok in joined for tok in (";", "&&", "|", "`", "$(")):
        raise CommandPolicyError("shell metacharacters forbidden")
    try:
        proc = subprocess.run(
            argv,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"command timed out: {argv}") from exc
    return CommandResult(
        exit_code=proc.returncode,
        stdout=proc.stdout[-50_000:],
        stderr=proc.stderr[-50_000:],
        argv=argv,
    )


def parse_command_key(raw: str) -> tuple[str, list[str]]:
    """Map user-facing command strings to allowlist keys."""
    parts = shlex.split(raw) if raw else []
    if not parts:
        raise CommandPolicyError("empty command")
    if parts[:3] == ["python3", "-m", "unittest"]:
        return "python_unittest", parts[3:]
    if parts[0] == "pytest":
        return "pytest", parts[1:]
    if parts[:2] == ["npm", "test"]:
        return "npm_test", parts[2:]
    if parts[:3] == ["npm", "run", "lint"]:
        return "npm_lint", parts[3:]
    if parts[:2] == ["git", "diff"]:
        return "git_diff", parts[2:]
    if parts[:2] == ["git", "status"]:
        return "git_status", []
    raise CommandPolicyError(f"command not allowlisted: {raw}")
