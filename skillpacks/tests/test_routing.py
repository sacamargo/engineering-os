"""Skill routing tests including false-positive guards."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillpacks.routing import resolve_skills


def _write_pack(root: Path, folder: str, manifest: dict) -> None:
    d = root / "packs" / folder
    d.mkdir(parents=True)
    (d / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class SkillRoutingTests(unittest.TestCase):
    def _registry_with(self, packs: list[dict]) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        skills = []
        for p in packs:
            folder = p["id"].split(".")[-1]
            _write_pack(root, folder, p)
            skills.append({"id": p["id"], "status": p["status"], "path": f"packs/{folder}/manifest.json"})
        (root / "registry.json").write_text(
            json.dumps({"schema": "eos.skillpack.registry.v1", "skills": skills}),
            encoding="utf-8",
        )
        return root

    def test_payment_gateway_not_physical_gate(self) -> None:
        packs = [
            {
                "id": "eos.skillpack.physical.access-gate",
                "name": "Physical Access",
                "version": "1.0.0",
                "purpose": "Physical gate control",
                "category": "physical",
                "source": "test",
                "status": "experimental",
                "provenance": {
                    "origin": "test",
                    "source": "test",
                    "version": "1.0.0",
                    "unavailable_source_content": False,
                    "adaptation_status": "eos-native",
                },
                "triggers": [
                    {"signal_type": "domain", "value": "physical_access", "weight": 2.0, "polarity": "positive"},
                    {"signal_type": "keyword", "value": "gate", "weight": 1.0, "polarity": "positive"},
                ],
            },
            {
                "id": "eos.skillpack.payments.checkout",
                "name": "Payments",
                "version": "1.0.0",
                "purpose": "Payments",
                "category": "payments",
                "source": "test",
                "status": "experimental",
                "provenance": {
                    "origin": "test",
                    "source": "test",
                    "version": "1.0.0",
                    "unavailable_source_content": False,
                    "adaptation_status": "eos-native",
                },
                "triggers": [
                    {"signal_type": "domain", "value": "payments", "weight": 2.0, "polarity": "positive"},
                ],
            },
        ]
        root = self._registry_with(packs)
        intent = {
            "utterance": "Integrate a payment gateway for checkout",
            "possible_intents": ["build"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, [], registry_root=root, min_score=0.5)
        self.assertIn("eos.skillpack.payments.checkout", result.selected)
        self.assertNotIn("eos.skillpack.physical.access-gate", result.selected)

    def test_unavailable_not_silently_applied(self) -> None:
        packs = [
            {
                "id": "eos.skillpack.marketing.corey-haines",
                "name": "Marketing",
                "version": "0.0.0",
                "purpose": "Marketing",
                "category": "marketing",
                "source": "unavailable",
                "status": "unavailable",
                "provenance": {
                    "origin": "external",
                    "source": "unavailable",
                    "version": "0.0.0",
                    "unavailable_source_content": True,
                },
                "triggers": [
                    {"signal_type": "domain", "value": "marketing", "weight": 3.0, "polarity": "positive"},
                ],
            }
        ]
        root = self._registry_with(packs)
        intent = {
            "utterance": "Improve landing page conversion and marketing positioning",
            "possible_intents": ["design"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, [], registry_root=root, min_score=0.5)
        self.assertIn("eos.skillpack.marketing.corey-haines", result.unavailable)
        self.assertNotIn("eos.skillpack.marketing.corey-haines", result.selected)

    def test_api_build_does_not_force_ux_primary(self) -> None:
        packs = [
            {
                "id": "eos.skillpack.design.ui-ux-pro-max",
                "name": "UI UX",
                "version": "0.0.1",
                "purpose": "UX",
                "category": "design",
                "source": "test",
                "status": "experimental",
                "provenance": {
                    "origin": "test",
                    "source": "test",
                    "version": "0.0.1",
                    "unavailable_source_content": False,
                    "adaptation_status": "eos-native",
                },
                "triggers": [
                    {"signal_type": "domain", "value": "ux_ui", "weight": 2.0, "polarity": "positive"},
                ],
            }
        ]
        root = self._registry_with(packs)
        intent = {
            "utterance": "Build an API for order ingestion",
            "possible_intents": ["build"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, [], registry_root=root, min_score=0.75)
        self.assertNotIn("eos.skillpack.design.ui-ux-pro-max", result.selected)


if __name__ == "__main__":
    unittest.main()
