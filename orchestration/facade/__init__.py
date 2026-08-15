"""Thin Planning Orchestrator facade — delegates to focused modules.

Anti-god-object: this class must stay a coordinator, not own catalog/methodology.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestration.boundaries.agent import suggest_executor
from agents.assignment import assign_agent
from orchestration.boundaries.codebase import (
    LocalCodebaseIntelligence,
    intent_requires_codebase,
)
from orchestration.boundaries.delivery import delivery_boundary
from orchestration.boundaries.adapter import core_adapter_policy
from orchestration.capability import resolve_capabilities
from orchestration.capability.arbitration import arbitrate_capabilities
from orchestration.decision import decisions_from_plan
from orchestration.dependency import resolve_dependencies
from orchestration.escalation import build_escalations
from orchestration.evidence import record_claim
from orchestration.failure import classify_failure
from orchestration.gaps import detect_gaps
from orchestration.gates import evaluate_gates
from orchestration.impact import analyze_change_impact
from orchestration.intent import intake_intent
from orchestration.knowledge import resolve_knowledge
from orchestration.plan import generate_plan
from orchestration.replan import replan_after_task_failure
from orchestration.role import resolve_roles
from orchestration.skill import resolve_skill_candidates
from orchestration.state import can_transition
from orchestration.facade.result import PlanningResult

__all__ = ["PlanningOrchestrator", "PlanningResult"]

ROOT = Path(__file__).resolve().parents[2]


class PlanningOrchestrator:
    """Facade only. LOC should stay small; logic lives in modules."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or ROOT
        self.codebase = LocalCodebaseIntelligence()

    def plan(self, utterance: str, context: dict[str, Any] | None = None) -> PlanningResult:
        context = context or {}
        intent = intake_intent(utterance, context)
        resolution = resolve_capabilities(intent, self.repo_root)
        arbitration = arbitrate_capabilities(intent, resolution)
        cap_ids = [
            c
            for c in [arbitration.primary, *(arbitration.secondary or []), *(arbitration.related or [])]
            if c
        ]
        if not cap_ids:
            cap_ids = [c.capability_id for c in resolution.candidates]
        skill_resolution = resolve_skill_candidates(
            intent.to_dict(),
            cap_ids,
            registry_root=self.repo_root / "skillpacks",
        )
        roles = resolve_roles(intent, arbitration)
        knowledge = resolve_knowledge(arbitration, self.repo_root)
        needs_cb = intent_requires_codebase(intent.possible_intents, context)
        generated = generate_plan(
            intent,
            arbitration,
            roles,
            knowledge,
            require_codebase_analysis=needs_cb,
        )
        deps = resolve_dependencies(
            generated.plan, generated.tasks, generated.artifacts, generated.gates
        )
        escalations = build_escalations(generated.project, generated.tasks)

        # Optionally run analysis now (still planning-time evidence, not code mutation).
        if context.get("run_codebase_analysis") or (
            needs_cb and "analyze" in intent.possible_intents and context.get("analyze_now", False)
        ):
            payload = self.codebase.analyze(str(self.repo_root))
            codebase_view = self.codebase.summarize_analysis(payload).to_dict()
            codebase_view["full_analysis"] = {
                "snapshot_id": codebase_view.get("snapshot_id"),
                "findings_count": codebase_view.get("findings_count"),
                "schema": payload.get("schema"),
            }
        else:
            codebase_view = self.codebase.inspect(str(self.repo_root)).to_dict()

        from orchestration.readiness import evaluate_readiness

        readiness = evaluate_readiness(
            generated.project,
            generated.tasks,
            deps.ok,
            [e.to_dict() for e in escalations],
            codebase=codebase_view,
        )
        gaps = detect_gaps(
            generated.project,
            generated.tasks,
            [r.to_dict() for r in roles.roles],
            [s.unit_id for s in knowledge.selected],
        )
        if needs_cb and codebase_view.get("analysis_status") != "complete":
            from orchestration.gaps import Gap

            gaps.append(
                Gap(
                    kind="MISSING_CODEBASE_EVIDENCE",
                    area="codebase_intelligence",
                    severity="high",
                    blocking=True,
                    reason="Intent requires repository evidence before safe change planning",
                    affected_tasks=[
                        t["id"]
                        for t in generated.tasks
                        if t.get("task_kind") != "codebase_analysis"
                    ],
                    possible_resolution="Run codebase_analysis task / LocalCodebaseIntelligence.analyze",
                )
            )
        gate_evals = evaluate_gates(generated.gates, generated.artifacts, generated.tasks)
        decisions = decisions_from_plan(generated.decisions)
        executors = []
        for t in generated.tasks:
            hint = suggest_executor(t).to_dict()
            assignment = assign_agent(t).to_dict()
            executors.append({**hint, "runtime_assignment": assignment})
        notes = [
            "PlanningOrchestrator delegates; it does not own Capability catalog content.",
            "Phase 6: planning can assign Agent Definitions; execution lives in agents/ runtime.",
            f"Project state planned valid from discovered: {can_transition('discovered', 'planned')}",
            "Codebase Intelligence is not a Capability. Role ≠ Agent.",
            "Skills are registry-driven candidates after Capabilities; Skill ≠ Capability.",
        ]
        if needs_cb:
            notes.append("Plan requires codebase_analysis before dependent refactor/audit/migrate work.")
        # Example claim (not evidence)
        _ = record_claim(
            f"eos.evidence.{generated.project['id'].split('.')[-1]}.plan-created",
            "Planner claims plan created",
            task_id=None,
        )
        return PlanningResult(
            intent=intent.to_dict(),
            capability_resolution=resolution.to_dict(),
            arbitration=arbitration.to_dict(),
            skill_resolution=skill_resolution.to_dict(),
            roles=roles.to_dict(),
            knowledge=knowledge.to_dict(),
            generated=generated.to_dict(),
            dependencies=deps.to_dict(),
            gaps=[g.to_dict() for g in gaps],
            escalations=[e.to_dict() for e in escalations],
            gates=[g.to_dict() for g in gate_evals],
            readiness=readiness.to_dict(),
            decisions=[d.to_dict() for d in decisions],
            executor_suggestions=executors,
            delivery=delivery_boundary(generated.project["id"]).to_dict(),
            adapter_policy=core_adapter_policy().to_dict(),
            codebase=codebase_view,
            notes=notes,
        )

    def execute_task(self, workspace: str, task: dict[str, Any], plan_steps: list[dict[str, Any]], **kwargs):
        """Delegate Task execution to agents runtime (Orchestrator does not own tools)."""
        from agents.coding import DeterministicPlan
        from agents.loop import run_execution

        return run_execution(workspace, task, DeterministicPlan(steps=plan_steps), **kwargs)

    def classify_failure(self, task_id: str, error_kind: str, message: str = ""):
        return classify_failure(task_id, error_kind, message)

    def replan(self, result: PlanningResult, failed_task_id: str):
        gen = result.generated
        return replan_after_task_failure(
            gen["plan"], gen["tasks"], gen["artifacts"], failed_task_id
        )

    def impact(self, result: PlanningResult, changed_artifact_id: str):
        gen = result.generated
        return analyze_change_impact(
            changed_artifact_id, gen["artifacts"], gen["tasks"], gen["gates"]
        )
