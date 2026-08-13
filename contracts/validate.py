#!/usr/bin/env python3
"""Validate Engineering OS knowledge unit contracts.

Pure Python 3 standard library. See contracts/SPEC.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

UNIT_TYPES = frozenset(
    {
        "capability",
        "playbook",
        "framework",
        "standard",
        "workflow",
        "skill",
        "template",
        "checklist",
        "adaptation",
    }
)
STATUSES = frozenset({"draft", "active", "deprecated", "retired"})
COMPLEXITIES = frozenset({"low", "medium", "high"})
RELATIONSHIP_TYPES = frozenset(
    {
        "references",
        "depends_on",
        "composes",
        "specializes",
        "alternative_to",
        "supersedes",
        "conflicts_with",
        "fulfilled_by",
        "primary_fulfillment",
        "related_capability",
    }
)
CAPABILITY_ONLY_RELS = frozenset(
    {"fulfilled_by", "primary_fulfillment", "related_capability"}
)
GRAPH_EDGE_RELS = frozenset({"depends_on", "composes"})
ID_RE = re.compile(
    r"^eos\.(capability|playbook|framework|standard|workflow|skill|template|checklist|adaptation)\.([a-z][a-z0-9-]*)\.([a-z][a-z0-9-]*)$"
)
DOMAIN_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DEFAULT_MODULE_DIRS = (
    "capabilities",
    "playbooks",
    "frameworks",
    "standards",
    "workflows",
    "skills",
    "templates",
    "checklists",
    "adaptations",
)
UNIVERSAL_REQUIRED = (
    "id",
    "type",
    "title",
    "summary",
    "purpose",
    "audience",
    "status",
    "applicability",
    "limits",
)


@dataclass
class Finding:
    path: str
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


@dataclass
class Unit:
    path: Path
    meta: dict[str, Any]
    findings: list[Finding] = field(default_factory=list)


class FrontMatterError(ValueError):
    pass


def parse_scalar(raw: str) -> Any:
    text = raw.strip()
    if text == "":
        return ""
    if text[0] in "'\"" and text[-1] == text[0] and len(text) >= 2:
        return text[1:-1]
    lower = text.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower == "null" or lower == "~":
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def parse_simple_yaml(text: str) -> Any:
    """Parse the constrained YAML subset used by Engineering OS unit metadata."""

    lines = text.splitlines()
    n = len(lines)

    def indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_block(index: int, min_indent: int) -> tuple[Any, int]:
        while index < n and (not lines[index].strip() or lines[index].lstrip().startswith("#")):
            index += 1
        if index >= n:
            return {}, index

        line = lines[index]
        ind = indent_of(line)
        if ind < min_indent:
            return {}, index

        if line.lstrip().startswith("- "):
            items: list[Any] = []
            while index < n:
                line = lines[index]
                if not line.strip() or line.lstrip().startswith("#"):
                    index += 1
                    continue
                ind = indent_of(line)
                if ind < min_indent:
                    break
                if not line.lstrip().startswith("- "):
                    break
                item_content = line.lstrip()[2:]
                item_indent = ind + 2
                if ":" in item_content and not item_content.strip().startswith("{"):
                    # Mapping entry starting on the list dash line.
                    key, _, rest = item_content.partition(":")
                    mapping: dict[str, Any] = {}
                    rest = rest.strip()
                    if rest:
                        mapping[key.strip()] = parse_scalar(rest)
                        index += 1
                    else:
                        index += 1
                        nested, index = parse_block(index, item_indent)
                        mapping[key.strip()] = nested
                    # Continuation keys for this list mapping.
                    while index < n:
                        cont = lines[index]
                        if not cont.strip() or cont.lstrip().startswith("#"):
                            index += 1
                            continue
                        cind = indent_of(cont)
                        if cind < item_indent or cont.lstrip().startswith("- "):
                            break
                        if ":" not in cont:
                            raise FrontMatterError(f"invalid mapping line: {cont!r}")
                        ckey, _, crest = cont.partition(":")
                        crest = crest.strip()
                        if crest:
                            mapping[ckey.strip()] = parse_scalar(crest)
                            index += 1
                        else:
                            index += 1
                            nested, index = parse_block(index, cind + 1)
                            mapping[ckey.strip()] = nested
                    items.append(mapping)
                else:
                    items.append(parse_scalar(item_content))
                    index += 1
            return items, index

        mapping: dict[str, Any] = {}
        while index < n:
            line = lines[index]
            if not line.strip() or line.lstrip().startswith("#"):
                index += 1
                continue
            ind = indent_of(line)
            if ind < min_indent:
                break
            if line.lstrip().startswith("- "):
                break
            if ":" not in line:
                raise FrontMatterError(f"invalid mapping line: {line!r}")
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest:
                mapping[key] = parse_scalar(rest)
                index += 1
            else:
                index += 1
                nested, index = parse_block(index, ind + 1)
                mapping[key] = nested
        return mapping, index

    value, index = parse_block(0, 0)
    while index < n:
        if lines[index].strip() and not lines[index].lstrip().startswith("#"):
            raise FrontMatterError(f"unexpected trailing content: {lines[index]!r}")
        index += 1
    return value


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise FrontMatterError("missing opening front matter delimiter")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontMatterError("missing opening front matter delimiter")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise FrontMatterError("missing closing front matter delimiter")
    meta_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    meta = parse_simple_yaml(meta_text)
    if not isinstance(meta, dict):
        raise FrontMatterError("front matter must be a mapping")
    return meta, body


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def require_string_list(meta: dict[str, Any], field_name: str, findings: list[Finding], path: str, *, min_items: int | None = None) -> None:
    if field_name not in meta:
        if min_items is not None:
            findings.append(Finding(path, "missing_field", f"missing required field '{field_name}'"))
        return
    value = meta[field_name]
    if not isinstance(value, list):
        findings.append(Finding(path, "invalid_type", f"'{field_name}' must be a list of strings"))
        return
    if min_items is not None and len(value) < min_items:
        findings.append(Finding(path, "missing_field", f"'{field_name}' must contain at least {min_items} item(s)"))
    for i, item in enumerate(value):
        if not non_empty_string(item):
            findings.append(Finding(path, "invalid_type", f"'{field_name}[{i}]' must be a non-empty string"))


def validate_unit_local(unit: Unit) -> None:
    path = str(unit.path)
    meta = unit.meta
    findings = unit.findings

    for key in UNIVERSAL_REQUIRED:
        if key not in meta:
            findings.append(Finding(path, "missing_field", f"missing required field '{key}'"))

    unit_id = meta.get("id")
    unit_type = meta.get("type")
    status = meta.get("status")

    if "id" in meta and not non_empty_string(unit_id):
        findings.append(Finding(path, "invalid_id", "id must be a non-empty string"))
    elif non_empty_string(unit_id):
        match = ID_RE.fullmatch(unit_id)
        if not match:
            findings.append(Finding(path, "invalid_id", f"id '{unit_id}' does not match eos.<type>.<domain>.<name>"))
        else:
            id_type, id_domain, _ = match.groups()
            if non_empty_string(unit_type) and unit_type != id_type:
                findings.append(
                    Finding(
                        path,
                        "invalid_id",
                        f"id type segment '{id_type}' does not match type '{unit_type}'",
                    )
                )
            domain = meta.get("domain")
            if domain is not None:
                if not isinstance(domain, str) or not DOMAIN_RE.fullmatch(domain):
                    findings.append(Finding(path, "invalid_metadata", "domain must match ^[a-z][a-z0-9-]*$"))
                elif domain != id_domain:
                    findings.append(
                        Finding(
                            path,
                            "invalid_metadata",
                            f"domain '{domain}' does not match id domain '{id_domain}'",
                        )
                    )

    if "type" in meta:
        if unit_type not in UNIT_TYPES:
            findings.append(Finding(path, "invalid_metadata", f"invalid type '{unit_type}'"))

    for field_name in ("title", "summary", "purpose", "audience", "applicability", "limits"):
        if field_name in meta and not non_empty_string(meta.get(field_name)):
            findings.append(Finding(path, "invalid_metadata", f"'{field_name}' must be a non-empty string"))

    if "status" in meta and status not in STATUSES:
        findings.append(Finding(path, "invalid_status", f"invalid status '{status}'"))

    if unit_type == "capability":
        if "inputs" in meta:
            findings.append(Finding(path, "invalid_metadata", "capabilities must not declare inputs"))
        if "outputs" in meta:
            findings.append(Finding(path, "invalid_metadata", "capabilities must not declare outputs"))
    elif unit_type in UNIT_TYPES:
        require_string_list(meta, "inputs", findings, path, min_items=1)
        require_string_list(meta, "outputs", findings, path, min_items=1)

    for optional_list in ("principles", "tags", "entry_signals"):
        require_string_list(meta, optional_list, findings, path)

    if "complexity" in meta and meta["complexity"] not in COMPLEXITIES:
        findings.append(Finding(path, "invalid_metadata", f"invalid complexity '{meta['complexity']}'"))

    if "language" in meta and meta["language"] != "en":
        findings.append(Finding(path, "invalid_metadata", "canonical language must be 'en' when present"))

    if "version" in meta and not non_empty_string(meta["version"]):
        findings.append(Finding(path, "invalid_metadata", "version must be a non-empty string when present"))

    for optional_string in ("estimated_effort", "outcome_expectations", "arbitration"):
        if optional_string in meta and not non_empty_string(meta[optional_string]):
            findings.append(Finding(path, "invalid_metadata", f"'{optional_string}' must be a non-empty string when present"))

    relationships = meta.get("relationships")
    if relationships is None:
        return
    if not isinstance(relationships, list):
        findings.append(Finding(path, "invalid_relationship", "relationships must be a list"))
        return

    for i, rel in enumerate(relationships):
        prefix = f"relationships[{i}]"
        if not isinstance(rel, dict):
            findings.append(Finding(path, "invalid_relationship", f"{prefix} must be a mapping"))
            continue
        rel_type = rel.get("type")
        target = rel.get("target")
        if rel_type not in RELATIONSHIP_TYPES:
            findings.append(Finding(path, "invalid_relationship", f"{prefix}.type is invalid: '{rel_type}'"))
        if not non_empty_string(target):
            findings.append(Finding(path, "invalid_relationship", f"{prefix}.target must be a non-empty string"))
        elif not ID_RE.fullmatch(str(target)):
            findings.append(Finding(path, "invalid_relationship", f"{prefix}.target has invalid id '{target}'"))
        if rel_type in CAPABILITY_ONLY_RELS and unit_type != "capability":
            findings.append(
                Finding(
                    path,
                    "invalid_relationship",
                    f"{prefix}: '{rel_type}' is only allowed on capability units",
                )
            )


def validate_catalog(units: list[Unit]) -> list[Finding]:
    findings: list[Finding] = []
    by_id: dict[str, Unit] = {}

    for unit in units:
        findings.extend(unit.findings)
        unit_id = unit.meta.get("id")
        if not non_empty_string(unit_id):
            continue
        if unit_id in by_id:
            findings.append(
                Finding(
                    str(unit.path),
                    "duplicate_id",
                    f"duplicate id '{unit_id}' also defined in {by_id[unit_id].path}",
                )
            )
        else:
            by_id[unit_id] = unit

    for unit in units:
        relationships = unit.meta.get("relationships") or []
        if not isinstance(relationships, list):
            continue
        source_type = unit.meta.get("type")
        for i, rel in enumerate(relationships):
            if not isinstance(rel, dict):
                continue
            rel_type = rel.get("type")
            target = rel.get("target")
            if not non_empty_string(target):
                continue
            target_unit = by_id.get(str(target))
            if target_unit is None:
                findings.append(
                    Finding(
                        str(unit.path),
                        "broken_reference",
                        f"relationships[{i}] target '{target}' does not exist in catalog",
                    )
                )
                continue
            target_type = target_unit.meta.get("type")
            if rel_type in {"fulfilled_by", "primary_fulfillment"} and target_type == "capability":
                findings.append(
                    Finding(
                        str(unit.path),
                        "invalid_relationship",
                        f"relationships[{i}] '{rel_type}' cannot target a capability",
                    )
                )
            if rel_type == "related_capability" and target_type != "capability":
                findings.append(
                    Finding(
                        str(unit.path),
                        "invalid_relationship",
                        f"relationships[{i}] related_capability must target a capability",
                    )
                )
            if (
                rel_type in GRAPH_EDGE_RELS
                and source_type != "adaptation"
                and target_type == "adaptation"
            ):
                findings.append(
                    Finding(
                        str(unit.path),
                        "invalid_relationship",
                        f"relationships[{i}] non-adaptation units cannot {rel_type} an adaptation",
                    )
                )

    # Cycle detection on depends_on ∪ composes
    graph: dict[str, set[str]] = {unit_id: set() for unit_id in by_id}
    for unit_id, unit in by_id.items():
        relationships = unit.meta.get("relationships") or []
        if not isinstance(relationships, list):
            continue
        for rel in relationships:
            if not isinstance(rel, dict):
                continue
            if rel.get("type") not in GRAPH_EDGE_RELS:
                continue
            target = rel.get("target")
            if target in graph:
                graph[unit_id].add(str(target))

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycle_start = stack.index(node)
            cycle = " -> ".join(stack[cycle_start:] + [node])
            findings.append(
                Finding(
                    str(by_id[node].path),
                    "invalid_relationship",
                    f"cycle detected in depends_on/composes: {cycle}",
                )
            )
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

    return findings


def load_unit(path: Path) -> Unit:
    text = path.read_text(encoding="utf-8")
    try:
        meta, _body = split_front_matter(text)
    except FrontMatterError as exc:
        unit = Unit(path=path, meta={})
        unit.findings.append(Finding(str(path), "invalid_metadata", f"front matter error: {exc}"))
        return unit
    unit = Unit(path=path, meta=meta)
    validate_unit_local(unit)
    return unit


def discover_markdown(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        if root.is_file() and root.suffix == ".md":
            files.append(root)
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name.upper() == "README.MD":
                continue
            files.append(path)
    return files


def default_roots(repo_root: Path) -> list[Path]:
    return [repo_root / name for name in DEFAULT_MODULE_DIRS]


def validate_paths(paths: list[Path]) -> list[Finding]:
    units = [load_unit(path) for path in paths]
    return validate_catalog(units)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Engineering OS knowledge unit contracts")
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        default=[],
        help="Directory or Markdown file to validate (repeatable). Defaults to module directories if present.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root used to resolve default module directories",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    roots = [Path(raw) for raw in args.roots]
    if not roots:
        roots = [path for path in default_roots(repo_root) if path.exists()]

    try:
        files = discover_markdown(roots)
        findings = validate_paths(files)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not findings:
        print(f"OK — validated {len(files)} unit file(s), 0 violation(s)")
        knowledge_rc = 0
    else:
        for finding in findings:
            print(finding.format(), file=sys.stderr)
        print(f"FAILED — validated {len(files)} unit file(s), {len(findings)} violation(s)", file=sys.stderr)
        knowledge_rc = 1

    # Also validate Execution Layer bundles when present.
    exec_validator = Path(__file__).resolve().parent / "validate_execution.py"
    execution_rc = 0
    if exec_validator.exists():
        import validate_execution

        execution_rc = validate_execution.main(["--repo-root", str(repo_root)])

    if knowledge_rc == 0 and execution_rc == 0:
        return 0
    return 1 if knowledge_rc or execution_rc else 0


if __name__ == "__main__":
    sys.exit(main())
