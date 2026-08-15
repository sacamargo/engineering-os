"""Architecture signals — observed/inferred/unknown, never asserted as truth."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any

from codebase.dependencies import DependencyGraph
from codebase.fs_index import FilesystemIndex
from codebase.symbols import SymbolIndex

LAYER_HINTS = {
    "controllers": "controller",
    "controller": "controller",
    "services": "service",
    "service": "service",
    "repositories": "repository",
    "repository": "repository",
    "adapters": "adapter",
    "adapter": "adapter",
    "domain": "domain",
    "api": "api",
    "web": "frontend",
    "frontend": "frontend",
    "backend": "backend",
    "infra": "infrastructure",
    "infrastructure": "infrastructure",
}


@dataclass
class ArchitectureSignal:
    id: str
    kind: str
    summary: str
    certainty: str
    evidence: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_architecture_signals(
    fs: FilesystemIndex,
    symbols: SymbolIndex,
    deps: DependencyGraph,
) -> list[ArchitectureSignal]:
    signals: list[ArchitectureSignal] = []
    dirs = {d.path for d in fs.directories}

    # layer directory hints
    for d in sorted(dirs):
        base = d.split("/")[-1].lower()
        if base in LAYER_HINTS:
            signals.append(
                ArchitectureSignal(
                    id=f"eos.archsig.layer.{base}",
                    kind="layer_directory",
                    summary=f"Directory '{d}' matches common {LAYER_HINTS[base]} naming",
                    certainty="inferred",
                    evidence=[d],
                    details={"role": LAYER_HINTS[base]},
                )
            )

    # entry points
    for f in fs.files:
        name = f.path.split("/")[-1]
        if name in {"main.py", "app.py", "index.js", "index.ts", "server.js", "manage.py", "cli.py"}:
            signals.append(
                ArchitectureSignal(
                    id=f"eos.archsig.entry.{abs(hash(f.path)) % 10**8}",
                    kind="entry_point",
                    summary=f"Possible entry point file {f.path}",
                    certainty="inferred",
                    evidence=[f.path],
                )
            )

    # circular imports among internal observed imports (simple)
    graph: dict[str, set[str]] = defaultdict(set)
    path_set = {m.path for m in symbols.modules}
    for e in deps.edges:
        if e.kind != "import" or e.external:
            continue
        # map target module to path if possible
        target_path = None
        candidate = e.target.replace(".", "/") + ".py"
        for p in path_set:
            if p == candidate or p.endswith("/" + candidate) or p.replace("/", ".").startswith(e.target):
                target_path = p
                break
        if target_path:
            graph[e.source_path].add(target_path)

    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[tuple[str, str]] = []

    def dfs(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycles.append((stack[-1], node))
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for nxt in graph.get(node, ()):
            dfs(nxt, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for n in list(graph):
        dfs(n, [])

    for a, b in cycles[:20]:
        signals.append(
            ArchitectureSignal(
                id=f"eos.archsig.cycle.{abs(hash((a, b))) % 10**8}",
                kind="circular_dependency",
                summary=f"Possible circular import involving {a} and {b}",
                certainty="inferred",
                evidence=[a, b],
            )
        )

    # orphan modules: no inbound and no outbound internal
    inbound = {t for targets in graph.values() for t in targets}
    for m in symbols.modules:
        if m.path not in graph and m.path not in inbound and m.path.endswith(".py"):
            if m.path.split("/")[-1] in {"__init__.py"}:
                continue
            signals.append(
                ArchitectureSignal(
                    id=f"eos.archsig.orphan.{abs(hash(m.path)) % 10**8}",
                    kind="orphan_module",
                    summary=f"Module {m.path} has no observed internal import edges",
                    certainty="inferred",
                    evidence=[m.path],
                )
            )

    if not signals:
        signals.append(
            ArchitectureSignal(
                id="eos.archsig.unknown.architecture",
                kind="architecture_unknown",
                summary="Insufficient signals to describe architecture",
                certainty="unknown",
                evidence=[],
            )
        )

    return signals
