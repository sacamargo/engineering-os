"""Tests for skillpack contract validator."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys_path_note = ROOT

import sys

sys.path.insert(0, str(ROOT))

from contracts.validate_skills import validate_path, validate_registry, validate_skillpack  # noqa: E402


class SkillContractTests(unittest.TestCase):
    def test_valid_fixture(self) -> None:
        path = ROOT / "contracts" / "skills" / "fixtures" / "valid" / "fixture-review.json"
        findings = validate_path(path, ROOT)
        self.assertEqual(findings, [], [f.format() for f in findings])

    def test_invalid_fixtures_fail(self) -> None:
        invalid = ROOT / "contracts" / "skills" / "fixtures" / "invalid"
        for path in invalid.glob("*.json"):
            with self.subTest(path=path.name):
                findings = validate_path(path, ROOT)
                self.assertTrue(findings, f"expected failures for {path.name}")

    def test_duplicate_registry_ids(self) -> None:
        pack = json.loads(
            (ROOT / "contracts" / "skills" / "fixtures" / "valid" / "fixture-review.json").read_text()
        )
        registry = {
            "skills": [
                {"id": pack["id"], "status": "experimental"},
                {"id": pack["id"], "status": "experimental"},
            ]
        }
        findings = validate_registry(registry, [pack])
        self.assertTrue(any(f.code == "duplicate_id" for f in findings))


if __name__ == "__main__":
    unittest.main()
