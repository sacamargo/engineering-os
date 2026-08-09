#!/usr/bin/env python3
"""Evaluate authored intent-resolution cases against the live Capability catalog.

This does not classify free-text utterances. See foundation/INTENT-RESOLUTION.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EXPERIMENT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
CONTRACTS_ROOT = REPO_ROOT / "contracts"
sys.path.insert(0, str(CONTRACTS_ROOT))

from validate import DEFAULT_MODULE_DIRS, discover_markdown, load_unit  # noqa: E402

CONFIDENCES = frozenset({"high", "medium", "low"})
CAPABILITY_ID_RE = re.compile(
    r"^eos\.capability\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$"
)
FRAME_KEYS = (
    "desired_outcome",
    "object_of_work",
    "intent_class_hint",
    "domain_hints",
    "constraints",
    "risk_signals",
    "multi_intent",
    "notes",
)


def load_catalog(repo_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    roots = [repo_root / name for name in DEFAULT_MODULE_DIRS if (repo_root / name).exists()]
    units = [load_unit(path) for path in discover_markdown(roots)]
    by_id = {
        unit.meta["id"]: unit.meta
        for unit in units
        if isinstance(unit.meta.get("id"), str) and not unit.findings
    }
    capabilities = {
        unit_id: meta
        for unit_id, meta in by_id.items()
        if meta.get("type") == "capability"
    }
    return capabilities, by_id


def iter_cases(cases_dir: Path) -> list[Path]:
    return sorted(cases_dir.glob("*.json"))


def evaluate_case(
    case: dict[str, Any],
    capabilities: dict[str, dict[str, Any]],
    units: dict[str, dict[str, Any]],
    path: Path,
) -> list[str]:
    errors: list[str] = []
    label = f"{path.name}"

    for key in (
        "id",
        "utterance",
        "frame",
        "candidates",
        "primary",
        "secondary",
        "related_suggested",
        "insufficient_coverage",
        "clarifying_questions",
        "fulfillment_preview",
    ):
        if key not in case:
            errors.append(f"{label}: missing field '{key}'")
    if errors:
        return errors

    frame = case["frame"]
    if not isinstance(frame, dict):
        errors.append(f"{label}: frame must be an object")
    else:
        for key in FRAME_KEYS:
            if key not in frame:
                errors.append(f"{label}: frame missing '{key}'")

    candidates = case["candidates"]
    if not isinstance(candidates, list):
        errors.append(f"{label}: candidates must be a list")
        return errors

    candidate_ids: list[str] = []
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"{label}: candidates[{i}] must be an object")
            continue
        cid = candidate.get("id")
        conf = candidate.get("confidence")
        rationale = candidate.get("rationale")
        if not isinstance(cid, str) or not cid:
            errors.append(f"{label}: candidates[{i}].id must be a non-empty string")
        else:
            candidate_ids.append(cid)
            if cid not in capabilities:
                errors.append(f"{label}: candidate '{cid}' is not an active catalog Capability")
            elif capabilities[cid].get("status") not in {"active", "deprecated"}:
                errors.append(f"{label}: candidate '{cid}' has non-routable status '{capabilities[cid].get('status')}'")
        if conf not in CONFIDENCES:
            errors.append(f"{label}: candidates[{i}].confidence must be high|medium|low")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"{label}: candidates[{i}].rationale must be a non-empty string")

    primary = case["primary"]
    if primary is not None:
        if not isinstance(primary, str):
            errors.append(f"{label}: primary must be a string or null")
        else:
            if primary not in capabilities:
                errors.append(f"{label}: primary '{primary}' is not a catalog Capability")
            if primary not in candidate_ids:
                errors.append(f"{label}: primary '{primary}' must appear in candidates")

    secondary = case["secondary"]
    if not isinstance(secondary, list):
        errors.append(f"{label}: secondary must be a list")
    else:
        for sid in secondary:
            if sid not in capabilities:
                errors.append(f"{label}: secondary '{sid}' is not a catalog Capability")
            if sid not in candidate_ids:
                errors.append(f"{label}: secondary '{sid}' must appear in candidates")

    related = case["related_suggested"]
    if not isinstance(related, list):
        errors.append(f"{label}: related_suggested must be a list")
    else:
        for rid in related:
            if rid not in capabilities:
                errors.append(f"{label}: related_suggested '{rid}' is not a catalog Capability")

    gaps = case["insufficient_coverage"]
    questions = case["clarifying_questions"]
    if not isinstance(gaps, list) or not isinstance(questions, list):
        errors.append(f"{label}: insufficient_coverage and clarifying_questions must be lists")
    else:
        for i, gap in enumerate(gaps):
            if not isinstance(gap, dict):
                errors.append(f"{label}: insufficient_coverage[{i}] must be an object")
                continue
            if not gap.get("missing_intent_class") or not gap.get("reason"):
                errors.append(f"{label}: insufficient_coverage[{i}] needs missing_intent_class and reason")

        if primary is None and not candidate_ids and not gaps and not questions:
            errors.append(
                f"{label}: empty resolution with no gaps and no clarifying questions is invalid"
            )

    preview = case["fulfillment_preview"]
    if preview is None:
        if primary is not None and not gaps and not questions:
            # Allowed to omit preview only when clarifying; otherwise prefer bindings.
            pass
    else:
        if primary is None:
            errors.append(f"{label}: fulfillment_preview requires a primary Capability")
        if not isinstance(preview, dict):
            errors.append(f"{label}: fulfillment_preview must be an object or null")
        else:
            primary_unit = preview.get("primary_unit")
            also = preview.get("also", [])
            if not isinstance(primary_unit, str) or primary_unit not in units:
                errors.append(f"{label}: fulfillment_preview.primary_unit must be a catalog unit id")
            if not isinstance(also, list):
                errors.append(f"{label}: fulfillment_preview.also must be a list")
            else:
                for uid in also:
                    if uid not in units:
                        errors.append(f"{label}: fulfillment_preview.also unknown unit '{uid}'")

            if primary in capabilities:
                bindings = {
                    rel.get("target")
                    for rel in capabilities[primary].get("relationships", [])
                    if isinstance(rel, dict)
                    and rel.get("type") in {"primary_fulfillment", "fulfilled_by"}
                }
                if isinstance(primary_unit, str) and primary_unit not in bindings:
                    errors.append(
                        f"{label}: fulfillment_preview.primary_unit '{primary_unit}' is not bound to primary Capability"
                    )

    # Reject invented capability-shaped ids hidden in gap reasons? Not required.
    # Reject capability-shaped strings in utterance analysis fields that look selected.
    for field_name in ("primary",):
        value = case.get(field_name)
        if isinstance(value, str) and CAPABILITY_ID_RE.fullmatch(value) and value not in capabilities:
            errors.append(f"{label}: invented Capability id '{value}'")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate intent-disambiguation experiment cases")
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root containing capabilities/ and other module dirs",
    )
    parser.add_argument(
        "--cases",
        default=str(EXPERIMENT_ROOT / "cases"),
        help="Directory of authored resolution JSON cases",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    cases_dir = Path(args.cases).resolve()
    capabilities, units = load_catalog(repo_root)

    all_errors: list[str] = []
    case_files = iter_cases(cases_dir)
    if not case_files:
        print(f"error: no cases found in {cases_dir}", file=sys.stderr)
        return 2

    for path in case_files:
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            all_errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        all_errors.extend(evaluate_case(case, capabilities, units, path))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(
            f"FAILED — {len(case_files)} case(s), {len(all_errors)} violation(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK — evaluated {len(case_files)} case(s) against {len(capabilities)} Capability(ies), 0 violation(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
