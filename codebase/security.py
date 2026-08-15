"""Static security signals — not a full security scanner."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.boundary import may_read_content
from codebase.findings import CodebaseFinding, _finding
from codebase.fs_index import FilesystemIndex

SECRET_LINE_RE = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|private_key)\s*[:=]\s*['\"][^'\"]{8,}"
)
UNSAFE_CONFIG_RE = re.compile(r"(?i)(debug\s*=\s*true|ssl\s*=\s*false|verify\s*=\s*false)")
DANGEROUS_IMPORT_RE = re.compile(r"(?i)^\s*(import\s+pickle|from\s+pickle\s+import|eval\(|exec\()")


@dataclass
class SecuritySignal:
    id: str
    kind: str
    summary: str
    certainty: str
    path: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_security_signals(root: str | Path, fs: FilesystemIndex) -> tuple[list[SecuritySignal], list[CodebaseFinding]]:
    root_path = Path(root).resolve()
    signals: list[SecuritySignal] = []
    findings: list[CodebaseFinding] = []

    for f in fs.files:
        if f.sensitive:
            signals.append(
                SecuritySignal(
                    id=f"eos.sec.sensitive.{abs(hash(f.path)) % 10**8}",
                    kind="potential_secret_path",
                    summary=f"Sensitive path observed (content not read): {f.path}",
                    certainty="observed",
                    path=f.path,
                    evidence=[f.path],
                )
            )
            continue
        if not f.content_readable or f.is_binary or not may_read_content(f.path):
            continue
        if f.extension not in {".py", ".js", ".ts", ".tsx", ".json", ".yml", ".yaml", ".env.example", ".toml", ".cfg", ".ini"}:
            continue
        try:
            text = (root_path / f.path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines()[:400], start=1):
            if SECRET_LINE_RE.search(line) and ".example" not in f.path:
                signals.append(
                    SecuritySignal(
                        id=f"eos.sec.secretline.{abs(hash((f.path, i))) % 10**8}",
                        kind="potential_secret",
                        summary=f"Possible hardcoded secret pattern at {f.path}:{i}",
                        certainty="inferred",
                        path=f.path,
                        evidence=[f"{f.path}:{i}"],
                    )
                )
                findings.append(
                    _finding(
                        kind="insecure_pattern",
                        severity="high",
                        confidence="inferred",
                        explanation=f"Possible hardcoded secret pattern at {f.path}:{i}",
                        location=f"{f.path}:{i}",
                        potential_impact="Credential exposure if committed.",
                        evidence=[f"{f.path}:{i}"],
                    )
                )
            if UNSAFE_CONFIG_RE.search(line):
                signals.append(
                    SecuritySignal(
                        id=f"eos.sec.unsafe.{abs(hash((f.path, i))) % 10**8}",
                        kind="unsafe_configuration",
                        summary=f"Unsafe configuration pattern at {f.path}:{i}",
                        certainty="inferred",
                        path=f.path,
                        evidence=[f"{f.path}:{i}"],
                    )
                )
            if DANGEROUS_IMPORT_RE.search(line):
                signals.append(
                    SecuritySignal(
                        id=f"eos.sec.danger.{abs(hash((f.path, i))) % 10**8}",
                        kind="dangerous_pattern",
                        summary=f"Dangerous construct observed at {f.path}:{i}",
                        certainty="observed",
                        path=f.path,
                        evidence=[f"{f.path}:{i}"],
                    )
                )
                findings.append(
                    _finding(
                        kind="insecure_pattern",
                        severity="medium",
                        confidence="observed",
                        explanation=f"Dangerous construct at {f.path}:{i}",
                        location=f"{f.path}:{i}",
                        potential_impact="May enable RCE/deserialization issues depending on usage.",
                        evidence=[f"{f.path}:{i}"],
                    )
                )

    return signals, findings
