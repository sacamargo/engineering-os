#!/usr/bin/env python3
"""Validate Integrated Skill (skillpack) manifests and registries."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SKILLPACK_ID_RE = re.compile(r"^eos\.skillpack\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
CAPABILITY_ID_RE = re.compile(r"^eos\.capability\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
ROLE_ID_RE = re.compile(r"^eos\.role\.[a-z][a-z0-9-]*$")
STATUS = frozenset({"active", "experimental", "deprecated", "unavailable"})
FORBIDDEN_META = frozenset(
    {
        "grants_permissions",
        "grants_tools",
        "bypass_gates",
        "auto_approve",
        "deploy_execute",
        "elevate_privileges",
    }
)


@dataclass
class Finding:
    path: str
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


def _load_known_capabilities(repo_root: Path) -> set[str]:
    ids: set[str] = set()
    cap_root = repo_root / "capabilities"
    if not cap_root.is_dir():
        return ids
    for path in cap_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("\n---", 3)
            front = text[3:end] if end != -1 else ""
            for line in front.splitlines():
                if line.startswith("id:"):
                    ids.add(line.split(":", 1)[1].strip())
    return ids


def _load_known_roles(repo_root: Path) -> set[str]:
    ids: set[str] = set()
    # From ROLE-MODEL prose ids + bindings
    role_model = repo_root / "foundation" / "ROLE-MODEL.md"
    if role_model.is_file():
        for m in re.finditer(r"`(eos\.role\.[a-z][a-z0-9-]*)`", role_model.read_text(encoding="utf-8")):
            ids.add(m.group(1))
    bindings = repo_root / "orchestration" / "role" / "bindings.json"
    if bindings.is_file():
        data = json.loads(bindings.read_text(encoding="utf-8"))
        for b in data.get("bindings") or []:
            ids.update(b.get("role_ids") or [])
        for roles in (data.get("gap_area_roles") or {}).values():
            ids.update(roles)
        ids.update(data.get("human_required_roles") or [])
    return ids


def validate_skillpack(
    data: dict[str, Any],
    *,
    path: str = "$",
    known_capabilities: set[str] | None = None,
    known_roles: set[str] | None = None,
    known_tools: set[str] | None = None,
    known_skill_ids: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    sid = str(data.get("id") or "")
    if not SKILLPACK_ID_RE.match(sid):
        findings.append(Finding(f"{path}.id", "malformed_id", f"invalid skillpack id: {sid}"))
    for field in ("name", "version", "purpose", "category", "source"):
        if not str(data.get(field) or "").strip():
            findings.append(Finding(f"{path}.{field}", "missing_field", f"{field} required"))
    status = data.get("status")
    if status not in STATUS:
        findings.append(Finding(f"{path}.status", "invalid_status", f"bad status: {status}"))
    prov = data.get("provenance")
    if not isinstance(prov, dict):
        findings.append(Finding(f"{path}.provenance", "missing_provenance", "provenance object required"))
        prov = {}
    else:
        for field in ("origin", "source", "version"):
            if not str(prov.get(field) or "").strip():
                findings.append(Finding(f"{path}.provenance.{field}", "missing_provenance", f"{field} required"))
    if status == "unavailable" and not prov.get("unavailable_source_content"):
        findings.append(
            Finding(
                f"{path}.provenance",
                "unavailable_without_flag",
                "unavailable status requires unavailable_source_content=true",
            )
        )
    if status == "active" and prov.get("unavailable_source_content"):
        findings.append(
            Finding(f"{path}", "active_with_missing_source", "active cannot claim unavailable source")
        )
    meta = data.get("metadata") or {}
    if isinstance(meta, dict):
        for key in meta:
            if key in FORBIDDEN_META:
                findings.append(Finding(f"{path}.metadata.{key}", "privilege_escalation", "forbidden field"))
    for key in FORBIDDEN_META:
        if key in data:
            findings.append(Finding(f"{path}.{key}", "privilege_escalation", "forbidden field"))
    for i, rule in enumerate(data.get("composition_rules") or []):
        if rule.get("implies_task_dependency"):
            findings.append(
                Finding(
                    f"{path}.composition_rules[{i}]",
                    "hidden_dag",
                    "composition must not imply task dependency",
                )
            )
        for j, other in enumerate(rule.get("with_skill_ids") or []):
            if known_skill_ids is not None and other not in known_skill_ids and other != sid:
                # allow forward refs within same validation batch via known_skill_ids
                if not SKILLPACK_ID_RE.match(str(other)):
                    findings.append(
                        Finding(
                            f"{path}.composition_rules[{i}].with_skill_ids[{j}]",
                            "malformed_id",
                            f"bad composed skill id: {other}",
                        )
                    )
    caps = data.get("capability_relationships") or []
    for i, cap in enumerate(caps):
        if not CAPABILITY_ID_RE.match(str(cap)):
            findings.append(Finding(f"{path}.capability_relationships[{i}]", "malformed_id", str(cap)))
        elif known_capabilities is not None and cap not in known_capabilities:
            findings.append(
                Finding(f"{path}.capability_relationships[{i}]", "unknown_capability", str(cap))
            )
    roles = data.get("role_relationships") or []
    for i, role in enumerate(roles):
        if not ROLE_ID_RE.match(str(role)):
            findings.append(Finding(f"{path}.role_relationships[{i}]", "malformed_id", str(role)))
        elif known_roles is not None and role not in known_roles:
            findings.append(Finding(f"{path}.role_relationships[{i}]", "unknown_role", str(role)))
    tools = data.get("tool_requirements") or []
    if known_tools is not None:
        for i, tool in enumerate(tools):
            if tool not in known_tools:
                findings.append(Finding(f"{path}.tool_requirements[{i}]", "unknown_tool", str(tool)))
    # Model-level shape via skillpacks when importable
    try:
        from skillpacks.model import skillpack_from_dict

        pack = skillpack_from_dict(data)
        for err in pack.validate_shape():
            findings.append(Finding(path, "model_invalid", err))
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding(path, "model_invalid", str(exc)))
    return findings


def validate_registry(
    registry: dict[str, Any],
    packs: list[dict[str, Any]],
    *,
    path: str = "$",
    known_capabilities: set[str] | None = None,
    known_roles: set[str] | None = None,
    known_tools: set[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    entries = registry.get("skills") or registry.get("skillpacks") or []
    ids = [str(e.get("id") or "") for e in entries]
    if len(ids) != len(set(ids)):
        findings.append(Finding(f"{path}", "duplicate_id", "duplicate skill ids in registry"))
    pack_by_id = {str(p.get("id")): p for p in packs}
    known_skill_ids = set(pack_by_id) | set(ids)
    for i, entry in enumerate(entries):
        eid = str(entry.get("id") or "")
        if not SKILLPACK_ID_RE.match(eid):
            findings.append(Finding(f"{path}.skills[{i}].id", "malformed_id", eid))
        if eid and eid not in pack_by_id:
            findings.append(Finding(f"{path}.skills[{i}]", "missing_manifest", f"no manifest for {eid}"))
    for pid, pack in pack_by_id.items():
        findings.extend(
            validate_skillpack(
                pack,
                path=f"{path}.packs[{pid}]",
                known_capabilities=known_capabilities,
                known_roles=known_roles,
                known_tools=known_tools,
                known_skill_ids=known_skill_ids,
            )
        )
    return findings


def validate_path(manifest_path: Path, repo_root: Path) -> list[Finding]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    caps = _load_known_capabilities(repo_root)
    roles = _load_known_roles(repo_root)
    return validate_skillpack(data, path=str(manifest_path), known_capabilities=caps, known_roles=roles)


def validate_source(data: dict[str, Any], *, path: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    try:
        from skillpacks.sources.model import source_from_dict

        src = source_from_dict(data)
        for err in src.validate_shape():
            code = "source_invalid"
            if "provenance" in err or "origin" in err:
                code = "missing_provenance"
            elif "locator" in err:
                code = "missing_locator"
            elif "content_hash" in err:
                code = "missing_hash"
            elif "skillpack" in err:
                code = "missing_skill_target"
            elif "status" in err:
                code = "invalid_status"
            elif "untrusted" in err or "unavailable_placeholder" in err:
                code = "activation_without_evidence"
            elif "forbidden" in err:
                code = "privilege_escalation"
            elif "source_id" in err:
                code = "malformed_id"
            findings.append(Finding(path, code, err))
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding(path, "source_invalid", str(exc)))
    # Reject fake activation claims without evidence markers
    if data.get("status") == "active" and not data.get("content_hash"):
        findings.append(Finding(path, "activation_without_evidence", "active requires content_hash"))
    if data.get("status") == "active" and data.get("source_type") == "unavailable_placeholder":
        findings.append(
            Finding(path, "activation_without_evidence", "placeholder cannot activate skill")
        )
    return findings


def validate_source_path(source_path: Path) -> list[Finding]:
    data = json.loads(source_path.read_text(encoding="utf-8"))
    return validate_source(data, path=str(source_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate skillpack and skill source contracts")
    parser.add_argument("paths", nargs="*", type=Path, help="Manifest or source JSON files")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        ok = True
        fixtures = ROOT / "contracts" / "skills" / "fixtures"
        for path in (fixtures / "valid").glob("*.json"):
            findings = validate_path(path, args.repo_root)
            if findings:
                print(f"UNEXPECTED FAIL {path}", file=sys.stderr)
                for f in findings:
                    print(f.format(), file=sys.stderr)
                ok = False
        for path in (fixtures / "invalid").glob("*.json"):
            findings = validate_path(path, args.repo_root)
            if not findings:
                print(f"UNEXPECTED PASS {path}", file=sys.stderr)
                ok = False
        src_fix = ROOT / "contracts" / "skills" / "source" / "fixtures"
        for path in (src_fix / "valid").glob("*.json"):
            findings = validate_source_path(path)
            if findings:
                print(f"UNEXPECTED FAIL {path}", file=sys.stderr)
                for f in findings:
                    print(f.format(), file=sys.stderr)
                ok = False
        for path in (src_fix / "invalid").glob("*.json"):
            findings = validate_source_path(path)
            if not findings:
                print(f"UNEXPECTED PASS {path}", file=sys.stderr)
                ok = False
        if not ok:
            return 1
        print("skill contracts self-check OK")
        return 0
    if not args.paths:
        print("pass paths or --self-check", file=sys.stderr)
        return 2
    all_findings: list[Finding] = []
    for p in args.paths:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if "source_id" in raw:
            all_findings.extend(validate_source(raw, path=str(p)))
        elif isinstance(raw.get("sources"), list):
            for i, item in enumerate(raw["sources"]):
                all_findings.extend(validate_source(item, path=f"{p}.sources[{i}]"))
        else:
            all_findings.extend(validate_path(p, args.repo_root))
    for f in all_findings:
        print(f.format(), file=sys.stderr)
    if all_findings:
        print(f"FAIL — {len(all_findings)} finding(s)", file=sys.stderr)
        return 1
    print("OK — skill contracts valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
