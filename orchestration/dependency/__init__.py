"""Dependency Resolution — validate execution DAG integrity."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DependencyReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    cycles: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_dependencies(
    plan: dict[str, Any],
    tasks: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    gates: list[dict[str, Any]],
) -> DependencyReport:
    errors: list[str] = []
    notes = [
        "References are not dependencies; only explicit depends_on / requires edges block."
    ]
    task_ids = {t["id"] for t in tasks}
    artifact_ids = {a["id"] for a in artifacts}
    gate_ids = {g["id"] for g in gates}
    graph: dict[str, set[str]] = {tid: set() for tid in task_ids}

    for t in tasks:
        for dep in t.get("depends_on_task_ids") or []:
            if dep not in task_ids:
                errors.append(f"missing task dependency {t['id']}->{dep}")
            else:
                graph[t["id"]].add(dep)
        for aid in (t.get("input_artifact_ids") or []) + (t.get("output_artifact_ids") or []):
            if aid not in artifact_ids:
                errors.append(f"task {t['id']} references missing artifact {aid}")

    for dep in plan.get("dependencies") or []:
        kind = dep.get("kind")
        frm, to = dep.get("from"), dep.get("to")
        if kind == "task_depends_on_task" and (frm not in task_ids or to not in task_ids):
            errors.append(f"invalid {kind} {frm}->{to}")
        if kind == "task_requires_artifact" and (frm not in task_ids or to not in artifact_ids):
            errors.append(f"invalid {kind} {frm}->{to}")
        if kind == "gate_requires_artifact" and (frm not in gate_ids or to not in artifact_ids):
            errors.append(f"invalid {kind} {frm}->{to}")

    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[str] = []

    def dfs(node: str) -> None:
        if node in visiting:
            cycles.append(node)
            return
        if node in visited:
            return
        visiting.add(node)
        for nxt in graph.get(node, ()):
            dfs(nxt)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        dfs(node)

    return DependencyReport(
        ok=not errors and not cycles, errors=errors, cycles=cycles, notes=notes
    )
