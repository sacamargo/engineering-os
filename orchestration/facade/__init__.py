"""Thin Planning Orchestrator facade — delegates to focused modules.

Anti-god-object: this class must stay a coordinator, not own catalog/methodology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestration.boundaries.agent import suggest_executor
from orchestration.boundaries.codebase import NullCodebaseIntelligence
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
from orchestration.state import can_transition


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class PlanningResult:
    intent: dict[str, Any]
    capability_resolution: dict[str, Any]
    arbitration: dict[str, Any]
    roles: dict[str, Any]
    knowledge: dict[str, Any]
    generated: dict[str, Any]
    dependencies: dict[str, Any]
    gaps: list[dict[str, Any]]
    escalations: list[dict[str, Any]]
    gates: list[dict[str, Any]]
    readiness: dict[str, Any]
    decisions: list[dict[str, Any]]
    executor_suggestions: list[dict[str, Any]]
    delivery: dict[str, Any]
    adapter_policy: dict[str, Any]
    codebase: dict[str, Any]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "capability_resolution": self.capability_resolution,
            "arbitration": self.arbitration,
            "roles": self.roles,
            "knowledge": self.knowledge,
            "generated": self.generated,
            "dependencies": self.dependencies,
            "gaps": self.gaps,
            "escalations": self.escalations,
            "gates": self.gates,
            "readiness": self.readiness,
            "decisions": self.decisions,
            "executor_suggestions": self.executor_suggestions,
            "delivery": self.delivery,
            "adapter_policy": self.adapter_policy,
            "codebase": self.codebase,
            "notes": self.notes,
        }


class PlanningOrchestrator:
    """Facade only. LOC should stay small; logic lives in modules."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or ROOT
        self.codebase = NullCodebaseIntelligence()

    def plan(self, utterance: str, context: dict[str, Any] | None = None) -> PlanningResult:
        intent = intake_intent(utterance, context)
        resolution = resolve_capabilities(intent, self.repo_root)
        arbitration = arbitrate_capabilities(intent, resolution)
        roles = resolve_roles(intent, arbitration)
        knowledge = resolve_knowledge(arbitration, self.repo_root)
        generated = generate_plan(intent, arbitration, roles, knowledge)
        deps = resolve_dependencies(
            generated.plan, generated.tasks, generated.artifacts, generated.gates
        )
        escalations = build_escalations(generated.project, generated.tasks)
        from orchestration.readiness import evaluate_readiness

        readiness = evaluate_readiness(
            generated.project,
            generated.tasks,
            deps.ok,
            [e.to_dict() for e in escalations],
        )
        gaps = detect_gaps(
            generated.project,
            generated.tasks,
            [r.to_dict() for r in roles.roles],
            [s.unit_id for s in knowledge.selected],
        )
        gate_evals = evaluate_gates(generated.gates, generated.artifacts, generated.tasks)
        decisions = decisions_from_plan(generated.decisions)
        executors = [suggest_executor(t).to_dict() for t in generated.tasks]
        notes = [
            "PlanningOrchestrator delegates; it does not own Capability catalog content.",
            "Phase 4 is planning-only; no code execution/deploy.",
            f"Project state planned valid from discovered: {can_transition('discovered', 'planned')}",
        ]
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
            codebase=self.codebase.inspect(str(self.repo_root)).to_dict(),
            notes=notes,
        )

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
