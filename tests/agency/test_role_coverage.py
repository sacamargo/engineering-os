#!/usr/bin/env python3
"""Role coverage tests — roles compose without becoming Capabilities."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROLE_MODEL = (ROOT / "foundation" / "ROLE-MODEL.md").read_text(encoding="utf-8")
EXAMPLES = ROOT / "examples"

ROLE_RE = re.compile(r"`(eos\.role\.[a-z][a-z0-9-]*)`")
CAP_RE = re.compile(r"^eos\.capability\.")


class RoleCoverageTests(unittest.TestCase):
    def catalog_roles(self) -> set[str]:
        return set(ROLE_RE.findall(ROLE_MODEL))

    def test_catalog_has_core_roles(self) -> None:
        roles = self.catalog_roles()
        required = {
            "eos.role.system-architect",
            "eos.role.backend-engineer",
            "eos.role.frontend-engineer",
            "eos.role.database-engineer",
            "eos.role.security-engineer",
            "eos.role.qa-test-engineer",
            "eos.role.devops-engineer",
            "eos.role.sre-reliability-engineer",
            "eos.role.observability-engineer",
            "eos.role.cloud-engineer",
        }
        self.assertTrue(required.issubset(roles), roles)

    def test_roles_are_not_capabilities(self) -> None:
        for role in self.catalog_roles():
            self.assertFalse(CAP_RE.match(role))
            self.assertTrue(role.startswith("eos.role."))

    def test_saas_composes_specialists(self) -> None:
        project = json.loads((EXAMPLES / "rivallium" / "project.json").read_text())
        roles = set(project["role_ids"])
        for needed in (
            "eos.role.system-architect",
            "eos.role.backend-engineer",
            "eos.role.frontend-engineer",
            "eos.role.database-engineer",
            "eos.role.security-engineer",
            "eos.role.qa-test-engineer",
            "eos.role.devops-engineer",
            "eos.role.sre-reliability-engineer",
        ):
            self.assertIn(needed, roles)
        # No role id masquerading as capability
        for cid in project["capability_ids"]:
            self.assertTrue(cid.startswith("eos.capability."))
            self.assertNotIn(cid, roles)

    def test_iot_composes_specialists(self) -> None:
        project = json.loads((EXAMPLES / "padel-iot" / "project.json").read_text())
        roles = set(project["role_ids"])
        for needed in (
            "eos.role.system-architect",
            "eos.role.cloud-engineer",
            "eos.role.security-engineer",
            "eos.role.observability-engineer",
            "eos.role.sre-reliability-engineer",
            "eos.role.electrical-engineer-professional",
        ):
            self.assertIn(needed, roles)
        bindings = json.loads((EXAMPLES / "padel-iot" / "roles" / "bindings.json").read_text())
        for b in bindings["bindings"]:
            self.assertTrue(b["capability_id"].startswith("eos.capability."))
            for rid in b["role_ids"]:
                self.assertTrue(rid.startswith("eos.role."))
                self.assertNotEqual(b["capability_id"], rid)


if __name__ == "__main__":
    unittest.main()
