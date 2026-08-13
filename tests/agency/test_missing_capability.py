#!/usr/bin/env python3
"""Missing Capability tests — never invent Capability IDs."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPS = ROOT / "capabilities"
EXAMPLES = ROOT / "examples"

CAP_ID_RE = re.compile(r"^eos\.capability\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")


def live_capability_ids() -> set[str]:
    ids: set[str] = set()
    for path in CAPS.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end == -1:
            continue
        for line in text[3:end].splitlines():
            if line.startswith("id:"):
                ids.add(line.split(":", 1)[1].strip())
    return ids


class MissingCapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live = live_capability_ids()

    def test_live_catalog_non_empty(self) -> None:
        self.assertGreaterEqual(len(self.live), 4)

    def test_electrical_certification_insufficient(self) -> None:
        """Conceptual response for: Certify this installation electrically."""
        case = json.loads(
            (Path(__file__).parent / "scenarios" / "missing-electrical-certification.json").read_text()
        )
        self.assertEqual(case["outcome"], "insufficient_capability")
        self.assertTrue(case["professional_validation_required"])
        self.assertEqual(case["capabilities_resolved"], [])
        self.assertFalse(case.get("invented_capability"))
        for cid in case.get("forbidden_invented_ids", []):
            self.assertNotIn(cid, self.live)

    def test_fixtures_do_not_reference_unknown_capabilities(self) -> None:
        for project_path in EXAMPLES.glob("*/project.json"):
            project = json.loads(project_path.read_text())
            for cid in project.get("capability_ids", []):
                self.assertIn(cid, self.live, f"{project_path}: unknown {cid}")
                self.assertTrue(CAP_ID_RE.fullmatch(cid))
            for gap in project.get("insufficient_coverage", []):
                area = gap.get("area", "")
                self.assertFalse(
                    area.startswith("eos.capability."),
                    f"gap area must not be a capability id: {area}",
                )

    def test_agency_scenarios_do_not_invent_capabilities(self) -> None:
        for path in (Path(__file__).parent / "scenarios").glob("*.json"):
            data = json.loads(path.read_text())
            for cid in data.get("capabilities_resolved", []):
                self.assertIn(cid, self.live, f"{path.name}: invented {cid}")


if __name__ == "__main__":
    unittest.main()
