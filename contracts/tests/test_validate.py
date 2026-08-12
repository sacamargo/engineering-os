#!/usr/bin/env python3
"""Tests for Engineering OS contract validation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

CONTRACTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CONTRACTS))

from validate import load_unit, main, validate_paths  # noqa: E402

VALID = CONTRACTS / "fixtures" / "valid"
INVALID = CONTRACTS / "fixtures" / "invalid"


class ValidateContractsTests(unittest.TestCase):
    def test_valid_catalog(self) -> None:
        files = sorted(VALID.glob("*.md"))
        findings = validate_paths(files)
        self.assertEqual(findings, [], "\n".join(f.format() for f in findings))

    def test_invalid_id(self) -> None:
        findings = validate_paths([INVALID / "bad-id.md"])
        self.assertTrue(any(f.code == "invalid_id" for f in findings))

    def test_missing_required_fields(self) -> None:
        findings = validate_paths([INVALID / "missing-fields.md"])
        self.assertTrue(any(f.code == "missing_field" for f in findings))

    def test_invalid_status(self) -> None:
        findings = validate_paths([INVALID / "bad-status.md"])
        self.assertTrue(any(f.code == "invalid_status" for f in findings))

    def test_module_cannot_use_fulfilled_by(self) -> None:
        # Include targets so failure is ownership, not broken reference.
        findings = validate_paths(
            [
                INVALID / "module-fulfilled-by.md",
                VALID / "skill-trade-off.md",
                VALID / "framework-option-comparison.md",
            ]
        )
        self.assertTrue(any(f.code == "invalid_relationship" for f in findings))
        self.assertTrue(any("fulfilled_by" in f.message for f in findings))

    def test_broken_reference(self) -> None:
        findings = validate_paths([INVALID / "broken-reference.md"])
        self.assertTrue(any(f.code == "broken_reference" for f in findings))

    def test_capability_cannot_declare_io(self) -> None:
        findings = validate_paths([INVALID / "capability-with-io.md"])
        self.assertTrue(any(f.code == "invalid_metadata" for f in findings))
        self.assertTrue(any("inputs" in f.message or "outputs" in f.message for f in findings))

    def test_duplicate_ids(self) -> None:
        findings = validate_paths(
            [
                VALID / "skill-trade-off.md",
                VALID / "framework-option-comparison.md",
                INVALID / "duplicate-id.md",
            ]
        )
        self.assertTrue(any(f.code == "duplicate_id" for f in findings))

    def test_cycle_detection(self) -> None:
        findings = validate_paths(
            [
                INVALID / "cycle-a.md",
                INVALID / "cycle-b.md",
            ]
        )
        self.assertTrue(any("cycle detected" in f.message for f in findings))

    def test_canonical_cannot_depend_on_adaptation(self) -> None:
        findings = validate_paths(
            [
                INVALID / "canonical-depends-on-adaptation.md",
                INVALID / "adaptation-target.md",
            ]
        )
        self.assertTrue(any(f.code == "invalid_relationship" for f in findings))
        self.assertTrue(any("adaptation" in f.message for f in findings))

    def test_id_type_mismatch(self) -> None:
        text = """---
id: eos.skill.design.mismatch
type: playbook
title: Mismatch
summary: Type segment mismatch.
purpose: Trigger invalid_id type mismatch.
audience: Testers
status: draft
applicability: Fixture only
limits: Fixture only
inputs:
  - x
outputs:
  - y
---
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mismatch.md"
            path.write_text(text, encoding="utf-8")
            unit = load_unit(path)
            self.assertTrue(any(f.code == "invalid_id" for f in unit.findings))

    def test_empty_catalog_ok(self) -> None:
        findings = validate_paths([])
        self.assertEqual(findings, [])

    def test_cli_defaults_to_ok_without_modules(self) -> None:
        code = main(["--repo-root", str(CONTRACTS.parent)])
        self.assertEqual(code, 0)

    def test_cli_fails_on_invalid_fixture(self) -> None:
        code = main(["--root", str(INVALID / "bad-id.md")])
        self.assertEqual(code, 1)

    def test_cli_passes_valid_fixtures(self) -> None:
        code = main(["--root", str(VALID)])
        self.assertEqual(code, 0)

    def test_live_catalog_validates(self) -> None:
        repo_root = CONTRACTS.parent
        code = main(["--repo-root", str(repo_root)])
        self.assertEqual(code, 0)
        findings = validate_paths(
            [
                repo_root / "capabilities" / "design" / "system-architecture.md",
                repo_root / "capabilities" / "security" / "review.md",
                repo_root / "capabilities" / "quality" / "test-planning.md",
                repo_root / "capabilities" / "operations" / "observability.md",
                repo_root / "playbooks" / "design" / "system-architecture.md",
                repo_root / "playbooks" / "security" / "application-review.md",
                repo_root / "playbooks" / "quality" / "test-planning.md",
                repo_root / "playbooks" / "operations" / "observability-design.md",
                repo_root / "frameworks" / "design" / "architecture-trade-offs.md",
                repo_root / "frameworks" / "security" / "risk-prioritization.md",
                repo_root / "frameworks" / "quality" / "test-risk-prioritization.md",
                repo_root / "frameworks" / "operations" / "signal-prioritization.md",
                repo_root / "skills" / "agency" / "capability-routing.md",
                repo_root / "adaptations" / "cursor" / "engineering-os-agency.md",
            ]
        )
        self.assertEqual(findings, [], "\n".join(f.format() for f in findings))

    def test_related_capability_is_soft_adjacency(self) -> None:
        repo_root = CONTRACTS.parent
        architecture = load_unit(repo_root / "capabilities" / "design" / "system-architecture.md")
        security = load_unit(repo_root / "capabilities" / "security" / "review.md")
        arch_rels = {(r.get("type"), r.get("target")) for r in architecture.meta.get("relationships", [])}
        sec_rels = {(r.get("type"), r.get("target")) for r in security.meta.get("relationships", [])}
        self.assertIn(("related_capability", "eos.capability.security.review"), arch_rels)
        self.assertIn(("related_capability", "eos.capability.design.system-architecture"), sec_rels)
        self.assertNotIn(("depends_on", "eos.capability.security.review"), arch_rels)
        self.assertNotIn(("depends_on", "eos.capability.design.system-architecture"), sec_rels)


if __name__ == "__main__":
    unittest.main()
