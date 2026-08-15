"""Runtime control tests (gates, evidence, failure, security, conflicts, agent bridge)."""

from __future__ import annotations

import unittest

from skillpacks.agent_bridge import bind_skills_to_agent
from skillpacks.conflicts import arbitrate_conflicts
from skillpacks.evidence import record_skill_evidence
from skillpacks.failures import classify_skill_failure
from skillpacks.gates import evaluate_skill_gates
from skillpacks.registry import load_registry
from skillpacks.security import check_skill_security


class SkillRuntimeControlTests(unittest.TestCase):
    def test_skill_authority_not_evidence(self) -> None:
        with self.assertRaises(ValueError):
            record_skill_evidence(
                skill_id="eos.skillpack.quality.stop-slop",
                skill_version="0.0.0",
                provenance={"origin": "x"},
                reasoning_summary="Skill says this is correct",
                findings=[],
            )

    def test_unavailable_blocks_gates(self) -> None:
        pack = load_registry().get("eos.skillpack.design.ui-ux-pro-max")
        assert pack is not None
        results = evaluate_skill_gates(pack, inputs_present=True, outputs_present=True, evidence_attached=True)
        self.assertTrue(any(r.status == "blocked" for r in results))

    def test_source_missing_not_retried(self) -> None:
        f = classify_skill_failure("SKILL_SOURCE_MISSING", "eos.skillpack.marketing.corey-haines")
        self.assertFalse(f.retryable)
        self.assertEqual(f.disposition, "needs_input")

    def test_security_rejects_privilege(self) -> None:
        v = check_skill_security({"id": "x", "metadata": {"grant_tools": True, "grants_tools": ["shell"]}})
        self.assertFalse(v.allowed)

    def test_conflicts_escalate_arbitrary(self) -> None:
        conflicts = arbitrate_conflicts(
            [
                {"skill_id": "a", "topic": "visual", "stance": "maximize impact", "kind": "method"},
                {"skill_id": "b", "topic": "visual", "stance": "reduce complexity", "kind": "review"},
            ]
        )
        self.assertTrue(conflicts[0].escalated)

    def test_agent_binding_records_version(self) -> None:
        binding = bind_skills_to_agent(
            task={"id": "eos.task.t1"},
            capability_ids=["eos.capability.design.system-architecture"],
            skill_ids=["eos.skillpack.context.engineering", "eos.skillpack.marketing.corey-haines"],
            role_ids=["eos.role.technical-lead"],
            agent_type="analysis",
            tool_permissions=["READ"],
        )
        self.assertIn("eos.skillpack.context.engineering", binding.skill_ids)
        self.assertIn("eos.skillpack.marketing.corey-haines", binding.rejected)
        self.assertTrue(any(e.get("skill_version") for e in binding.evidence))


if __name__ == "__main__":
    unittest.main()
