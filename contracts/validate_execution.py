#!/usr/bin/env python3
"""Validate Engineering OS Execution Layer bundles.

Pure Python 3 stdlib. See contracts/execution/SPEC.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

PROJECT_RE = re.compile(r"^eos\.project\.[a-z][a-z0-9-]*$")
TASK_RE = re.compile(r"^eos\.task\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
ARTIFACT_RE = re.compile(r"^eos\.artifact\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
PLAN_RE = re.compile(r"^eos\.plan\.[a-z][a-z0-9-]*$")
GATE_RE = re.compile(r"^eos\.gate\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
DECISION_RE = re.compile(r"^eos\.decision\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
ROLE_RE = re.compile(r"^eos\.role\.[a-z][a-z0-9-]*$")
CAPABILITY_RE = re.compile(
    r"^eos\.capability\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$"
)

PROJECT_STATUSES = {
    "discovered",
    "planned",
    "ready",
    "executing",
    "blocked",
    "validating",
    "completed",
    "failed",
    "cancelled",
}
TASK_STATUSES = {
    "pending",
    "ready",
    "in_progress",
    "blocked",
    "completed",
    "failed",
    "cancelled",
}
ARTIFACT_STATUSES = {
    "planned",
    "drafting",
    "ready_for_review",
    "approved",
    "superseded",
    "rejected",
}
GATE_RESULTS = {"pending", "passed", "failed", "waived"}
DECISION_STATUSES = {"proposed", "accepted", "superseded", "rejected"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_capability_ids(repo_root: Path) -> set[str]:
    caps: set[str] = set()
    cap_root = repo_root / "capabilities"
    if not cap_root.exists():
        return caps
    for path in cap_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                header = text[3:end]
                for line in header.splitlines():
                    if line.startswith("id:"):
                        caps.add(line.split(":", 1)[1].strip())
    return caps


def validate_bundle(bundle_dir: Path, capability_ids: set[str]) -> list[str]:
    errors: list[str] = []
    label = bundle_dir.name

    project_path = bundle_dir / "project.json"
    plan_path = bundle_dir / "plan.json"
    if not project_path.exists():
        return [f"{label}: missing project.json"]
    if not plan_path.exists():
        return [f"{label}: missing plan.json"]

    project = load_json(project_path)
    plan = load_json(plan_path)

    artifacts = {}
    tasks = {}
    gates = {}
    decisions = {}

    for path in sorted((bundle_dir / "artifacts").glob("*.json")) if (bundle_dir / "artifacts").exists() else []:
        obj = load_json(path)
        artifacts[obj.get("id")] = obj
    for path in sorted((bundle_dir / "tasks").glob("*.json")) if (bundle_dir / "tasks").exists() else []:
        obj = load_json(path)
        tasks[obj.get("id")] = obj
    for path in sorted((bundle_dir / "gates").glob("*.json")) if (bundle_dir / "gates").exists() else []:
        obj = load_json(path)
        gates[obj.get("id")] = obj
    for path in sorted((bundle_dir / "decisions").glob("*.json")) if (bundle_dir / "decisions").exists() else []:
        obj = load_json(path)
        decisions[obj.get("id")] = obj

    role_bindings: list[dict[str, Any]] = []
    roles_dir = bundle_dir / "roles"
    if roles_dir.exists():
        for path in sorted(roles_dir.glob("*.json")):
            obj = load_json(path)
            if isinstance(obj, dict) and isinstance(obj.get("bindings"), list):
                role_bindings.extend(b for b in obj["bindings"] if isinstance(b, dict))
            elif isinstance(obj, dict) and "capability_id" in obj and "role_ids" in obj:
                role_bindings.append(obj)
            else:
                errors.append(f"{label}: invalid role binding file '{path.name}'")

    # Project
    pid = project.get("id")
    if not isinstance(pid, str) or not PROJECT_RE.fullmatch(pid):
        errors.append(f"{label}: invalid project id '{pid}'")
    if project.get("status") not in PROJECT_STATUSES:
        errors.append(f"{label}: invalid project status '{project.get('status')}'")
    for key in ("title", "objective"):
        if not isinstance(project.get(key), str) or not project.get(key).strip():
            errors.append(f"{label}: project missing '{key}'")

    for rid in project.get("role_ids") or []:
        if not isinstance(rid, str) or not ROLE_RE.fullmatch(rid):
            errors.append(f"{label}: invalid role id '{rid}'")

    for cid in project.get("capability_ids") or []:
        if not isinstance(cid, str) or not CAPABILITY_RE.fullmatch(cid):
            errors.append(f"{label}: invalid capability id shape '{cid}'")
        elif capability_ids and cid not in capability_ids:
            errors.append(f"{label}: capability '{cid}' not in knowledge catalog")

    # Plan
    if not isinstance(plan.get("id"), str) or not PLAN_RE.fullmatch(plan.get("id")):
        errors.append(f"{label}: invalid plan id '{plan.get('id')}'")
    if plan.get("project_id") != pid:
        errors.append(f"{label}: plan.project_id mismatch")
    if not isinstance(plan.get("intent_summary"), str) or not plan.get("intent_summary").strip():
        errors.append(f"{label}: plan missing intent_summary")
    if not isinstance(plan.get("revision"), int) or plan.get("revision") < 1:
        errors.append(f"{label}: plan.revision must be integer >= 1")

    # Duplicate IDs
    all_ids = [pid, plan.get("id"), *artifacts.keys(), *tasks.keys(), *gates.keys(), *decisions.keys()]
    seen = set()
    for item in all_ids:
        if item in seen:
            errors.append(f"{label}: duplicate id '{item}'")
        seen.add(item)

    # Artifacts
    for aid, art in artifacts.items():
        if not isinstance(aid, str) or not ARTIFACT_RE.fullmatch(aid):
            errors.append(f"{label}: invalid artifact id '{aid}'")
        if art.get("project_id") != pid:
            errors.append(f"{label}: artifact '{aid}' project mismatch")
        if art.get("status") not in ARTIFACT_STATUSES:
            errors.append(f"{label}: artifact '{aid}' invalid status")
        for dep in art.get("depends_on_artifacts") or []:
            if dep not in artifacts:
                errors.append(f"{label}: artifact '{aid}' broken depends_on '{dep}'")

    # Tasks
    graph: dict[str, set[str]] = {tid: set() for tid in tasks}
    for tid, task in tasks.items():
        if not isinstance(tid, str) or not TASK_RE.fullmatch(tid):
            errors.append(f"{label}: invalid task id '{tid}'")
        if task.get("project_id") != pid:
            errors.append(f"{label}: task '{tid}' project mismatch")
        if task.get("status") not in TASK_STATUSES:
            errors.append(f"{label}: task '{tid}' invalid status")
        for key in ("title", "description", "objective"):
            if not isinstance(task.get(key), str) or not task.get(key).strip():
                errors.append(f"{label}: task '{tid}' missing '{key}'")
        for aid in task.get("input_artifact_ids") or []:
            if aid not in artifacts:
                errors.append(f"{label}: task '{tid}' missing input artifact '{aid}'")
        for aid in task.get("output_artifact_ids") or []:
            if aid not in artifacts:
                errors.append(f"{label}: task '{tid}' missing output artifact '{aid}'")
        for dep in task.get("depends_on_task_ids") or []:
            if dep not in tasks:
                errors.append(f"{label}: task '{tid}' missing dependency task '{dep}'")
            else:
                graph[tid].add(dep)
        for rid in task.get("role_ids") or []:
            if not isinstance(rid, str) or not ROLE_RE.fullmatch(rid):
                errors.append(f"{label}: task '{tid}' invalid role '{rid}'")
        for cid in task.get("capability_ids") or []:
            if capability_ids and cid not in capability_ids:
                errors.append(f"{label}: task '{tid}' unknown capability '{cid}'")

    # Cycle detection
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str, stack: list[str]) -> None:
        if node in visiting:
            errors.append(f"{label}: cyclic task dependency involving '{node}'")
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            dfs(nxt, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        dfs(node, [])

    # Gates
    for gid, gate in gates.items():
        if not isinstance(gid, str) or not GATE_RE.fullmatch(gid):
            errors.append(f"{label}: invalid gate id '{gid}'")
        if gate.get("project_id") != pid:
            errors.append(f"{label}: gate '{gid}' project mismatch")
        if gate.get("result") not in GATE_RESULTS:
            errors.append(f"{label}: gate '{gid}' invalid result")
        if not isinstance(gate.get("condition"), str) or not gate.get("condition").strip():
            errors.append(f"{label}: gate '{gid}' missing condition")
        evidence = gate.get("required_evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}: gate '{gid}' requires evidence list")
        else:
            for item in evidence:
                if isinstance(item, str) and item.startswith("eos.artifact.") and item not in artifacts:
                    errors.append(f"{label}: gate '{gid}' missing artifact evidence '{item}'")
                if isinstance(item, str) and item.startswith("eos.task.") and item not in tasks:
                    errors.append(f"{label}: gate '{gid}' missing task evidence '{item}'")

    # Decisions
    for did, decision in decisions.items():
        if not isinstance(did, str) or not DECISION_RE.fullmatch(did):
            errors.append(f"{label}: invalid decision id '{did}'")
        if decision.get("status") not in DECISION_STATUSES:
            errors.append(f"{label}: decision '{did}' invalid status")
        for key in ("title", "choice", "reason"):
            if not isinstance(decision.get(key), str) or not decision.get(key).strip():
                errors.append(f"{label}: decision '{did}' missing '{key}'")

    # Plan references
    for aid in plan.get("artifact_ids") or []:
        if aid not in artifacts:
            errors.append(f"{label}: plan references missing artifact '{aid}'")
    for tid in plan.get("task_ids") or []:
        if tid not in tasks:
            errors.append(f"{label}: plan references missing task '{tid}'")
    for gid in plan.get("gate_ids") or []:
        if gid not in gates:
            errors.append(f"{label}: plan references missing gate '{gid}'")

    for dep in plan.get("dependencies") or []:
        if not isinstance(dep, dict):
            errors.append(f"{label}: dependency must be object")
            continue
        kind = dep.get("kind")
        frm = dep.get("from")
        to = dep.get("to")
        if kind == "task_depends_on_task":
            if frm not in tasks or to not in tasks:
                errors.append(f"{label}: invalid task_depends_on_task {frm}->{to}")
        elif kind == "task_requires_artifact":
            if frm not in tasks or to not in artifacts:
                errors.append(f"{label}: invalid task_requires_artifact {frm}->{to}")
        elif kind == "gate_requires_artifact":
            if frm not in gates or to not in artifacts:
                errors.append(f"{label}: invalid gate_requires_artifact {frm}->{to}")
        elif kind == "gate_requires_task":
            if frm not in gates or to not in tasks:
                errors.append(f"{label}: invalid gate_requires_task {frm}->{to}")

    # Role bindings (Capability → Role expertise; Role ≠ Capability)
    for binding in role_bindings:
        cid = binding.get("capability_id")
        roles = binding.get("role_ids")
        if not isinstance(cid, str) or not CAPABILITY_RE.fullmatch(cid):
            errors.append(f"{label}: invalid role binding capability '{cid}'")
        elif capability_ids and cid not in capability_ids:
            errors.append(f"{label}: role binding unknown capability '{cid}'")
        if not isinstance(roles, list) or not roles:
            errors.append(f"{label}: role binding for '{cid}' requires non-empty role_ids")
        else:
            for rid in roles:
                if not isinstance(rid, str) or not ROLE_RE.fullmatch(rid):
                    errors.append(f"{label}: invalid role binding role id '{rid}'")

    return errors


def discover_bundles(examples_root: Path) -> list[Path]:
    if not examples_root.exists():
        return []
    bundles = []
    for path in sorted(examples_root.iterdir()):
        if path.is_dir() and (path / "project.json").exists():
            bundles.append(path)
    return bundles


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Execution Layer bundles")
    parser.add_argument("--repo-root", default=str(REPO))
    parser.add_argument("--examples", default=None, help="Examples root (default: <repo>/examples)")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    examples_root = Path(args.examples).resolve() if args.examples else repo_root / "examples"
    capability_ids = load_capability_ids(repo_root)
    bundles = discover_bundles(examples_root)

    if not bundles:
        print(f"OK — no execution bundles under {examples_root}")
        return 0

    all_errors: list[str] = []
    for bundle in bundles:
        all_errors.extend(validate_bundle(bundle, capability_ids))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(f"FAILED — {len(bundles)} bundle(s), {len(all_errors)} violation(s)", file=sys.stderr)
        return 1

    print(f"OK — validated {len(bundles)} execution bundle(s), 0 violation(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
