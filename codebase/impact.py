"""Change impact from Codebase Intelligence dependency/test graphs.

Direct evidence vs inferred impact are labeled separately.
Does not claim semantic/runtime perfection.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from typing import Any

from codebase.architecture import ArchitectureSignal
from codebase.config_intel import ConfigIntelligence
from codebase.dependencies import DependencyGraph
from codebase.tests_intel import TestIntelligence


@dataclass
class ModuleImpactReport:
    changed_path: str
    direct_dependents: list[str] = field(default_factory=list)
    indirect_dependents: list[str] = field(default_factory=list)
    related_tests: list[str] = field(default_factory=list)
    related_entry_points: list[str] = field(default_factory=list)
    related_configurations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    certainty_notes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_internal_target(target: str, known_paths: set[str]) -> str | None:
    candidate = target.replace(".", "/") + ".py"
    if candidate in known_paths:
        return candidate
    for p in known_paths:
        if p.endswith("/" + candidate) or p.replace("/", ".").rstrip(".py") == target:
            return p
        if p.endswith(candidate):
            return p
    return None


def analyze_module_impact(
    changed_path: str,
    deps: DependencyGraph,
    tests: TestIntelligence,
    configs: ConfigIntelligence,
    signals: list[ArchitectureSignal],
    module_paths: set[str] | None = None,
) -> ModuleImpactReport:
    """If module X changes, what might be affected?

    direct_dependents: observed importers of X
    indirect_dependents: BFS over observed import edges (inferred impact radius)
    """
    known: set[str] = set(module_paths or ())
    for e in deps.edges:
        known.add(e.source_path)
        resolved = _resolve_internal_target(e.target, known)
        if resolved:
            known.add(resolved)

    reverse: dict[str, set[str]] = defaultdict(set)
    for e in deps.edges:
        if e.kind != "import" or e.external:
            continue
        tgt = _resolve_internal_target(e.target, known)
        if not tgt:
            continue
        reverse[tgt].add(e.source_path)

    direct = sorted(reverse.get(changed_path, set()))
    # BFS for indirect (exclude direct)
    seen = {changed_path}
    queue = deque(direct)
    indirect: set[str] = set()
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        if node not in direct:
            indirect.add(node)
        for parent in reverse.get(node, ()):
            if parent not in seen:
                queue.append(parent)

    related_tests = sorted(
        {
            t.path
            for t in tests.tests
            if changed_path in t.linked_targets
            or changed_path.split("/")[-1].replace(".py", "") in t.path
        }
    )

    entry_points = sorted(
        {
            e
            for s in signals
            if s.kind == "entry_point"
            for e in s.evidence
            if e == changed_path or e in direct or e in indirect
        }
    )

    related_cfg = sorted(
        {
            c.path
            for c in configs.configurations
            if c.path == changed_path
            or c.path.rsplit("/", 1)[0] == changed_path.rsplit("/", 1)[0]
        }
    )

    return ModuleImpactReport(
        changed_path=changed_path,
        direct_dependents=direct,
        indirect_dependents=sorted(indirect),
        related_tests=related_tests,
        related_entry_points=entry_points,
        related_configurations=related_cfg,
        notes=[
            "direct_dependents come from observed import edges.",
            "indirect_dependents are graph reachability (inferred impact).",
            "related_tests use approximate filename links when present.",
            "No runtime behavioral certainty is claimed.",
        ],
        certainty_notes={
            "direct_dependents": "observed",
            "indirect_dependents": "inferred",
            "related_tests": "inferred" if related_tests else "unknown",
            "related_entry_points": "inferred" if entry_points else "unknown",
            "related_configurations": "inferred" if related_cfg else "unknown",
        },
    )
