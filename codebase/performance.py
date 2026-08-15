"""Static performance signals — never claim measured runtime cost."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.fs_index import FilesystemIndex

NESTED_LOOP_RE = re.compile(r"(?m)^\s*for .+ in .+:\n(?:.*\n){0,8}^\s+for .+ in .+:", re.M)
QUERY_IN_LOOP_HINT = re.compile(
    r"(?i)for .+ in .+:[\s\S]{0,120}(\.execute\(|fetch\(|query\(|findOne\(|SELECT )"
)


@dataclass
class PerformanceSignal:
    id: str
    kind: str
    summary: str
    certainty: str
    path: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_performance_signals(root: str | Path, fs: FilesystemIndex) -> list[PerformanceSignal]:
    root_path = Path(root).resolve()
    signals: list[PerformanceSignal] = []
    for f in fs.files:
        if not f.content_readable or f.is_binary:
            continue
        if f.extension not in {".py", ".js", ".ts", ".tsx"}:
            continue
        try:
            text = (root_path / f.path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if NESTED_LOOP_RE.search(text):
            signals.append(
                PerformanceSignal(
                    id=f"eos.perf.nested.{abs(hash(f.path)) % 10**8}",
                    kind="nested_loop",
                    summary=f"Nested loop pattern in {f.path} (static heuristic)",
                    certainty="inferred",
                    path=f.path,
                    evidence=[f.path],
                )
            )
        if QUERY_IN_LOOP_HINT.search(text):
            signals.append(
                PerformanceSignal(
                    id=f"eos.perf.nplus1.{abs(hash(f.path)) % 10**8}",
                    kind="possible_n_plus_one",
                    summary=f"Possible query-in-loop pattern in {f.path}",
                    certainty="inferred",
                    path=f.path,
                    evidence=[f.path],
                )
            )
        if f.size > 500_000 and f.extension in {".js", ".ts"}:
            signals.append(
                PerformanceSignal(
                    id=f"eos.perf.largefile.{abs(hash(f.path)) % 10**8}",
                    kind="large_source_file",
                    summary=f"Large source file {f.path} ({f.size} bytes) may affect bundles",
                    certainty="inferred",
                    path=f.path,
                    evidence=[f"{f.path}:size={f.size}"],
                )
            )
    return signals
