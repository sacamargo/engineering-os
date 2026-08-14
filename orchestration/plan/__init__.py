"""Plan Generation — build an Execution Plan from resolved intent/capabilities/roles/knowledge.

Dependencies are artifact/task semantic edges, not Capability chains.
Capability→artifact templates load from templates.json (extensible without code edits).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from orchestration.capability.arbitration import ArbitrationResult
from orchestration.intent import StructuredIntent
from orchestration.knowledge import KnowledgeResolution
from orchestration.role import RoleResolution

TEMPLATES_PATH = Path(__file__).resolve().parent / "templates.json"


def load_capability_templates(path: Path | None = None) -> dict[str, Any]:
    data = json.loads((path or TEMPLATES_PATH).read_text(encoding="utf-8"))
    return dict(data.get("capability_templates") or {})


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:40] or "project"


@dataclass
class GeneratedPlan:
    project: dict[str, Any]
    plan: dict[str, Any]
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    tasks: list[dict[str, Any]] = field(default_factory=list)
    gates: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def asdict_fact(fact: Any) -> dict[str, Any]:
    return {
        "key": fact.key,
        "value": fact.value,
        "certainty": fact.certainty,
        "reason": fact.reason,
    }


def generate_plan(
    intent: StructuredIntent,
    arbitration: ArbitrationResult,
    roles: RoleResolution,
    knowledge: KnowledgeResolution,
    project_slug: str | None = None,
    templates: dict[str, Any] | None = None,
) -> GeneratedPlan:
    cap_artifacts = templates if templates is not None else load_capability_templates()
    slug = project_slug or _slugify(
        next(
            (f.value for f in intent.context if f.key == "product_class"),
            intent.possible_intents[0] if intent.possible_intents else "plan",
        )
    )
    project_id = f"eos.project.{slug}"
    plan_id = f"eos.plan.{slug}"

    role_by_cap: dict[str, list[str]] = {}
    for role in roles.roles:
        for cap in role.capability_ids:
            role_by_cap.setdefault(cap, []).append(role.role_id)

    artifacts: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    dependencies: list[dict[str, Any]] = []
    notes = [
        "Plan generated need-based from selected Capabilities.",
        "Task order follows artifact prerequisites, not Capability related edges.",
        "Capability artifact templates are data-driven (templates.json).",
    ]

    artifact_ids_by_slug: dict[str, str] = {}
    task_ids_by_slug: dict[str, str] = {}

    if "build" in intent.possible_intents or "design" in intent.possible_intents:
        req_id = f"eos.artifact.{slug}.requirements"
        artifacts.append(
            {
                "id": req_id,
                "type": "requirements",
                "title": "Requirements specification",
                "project_id": project_id,
                "status": "planned",
            }
        )
        artifact_ids_by_slug["requirements"] = req_id
        req_task = f"eos.task.{slug}.define-requirements"
        tasks.append(
            {
                "id": req_task,
                "title": "Define requirements",
                "description": "Capture known requirements and explicit unknowns without inventing facts.",
                "objective": "Requirements artifact ready for architecture",
                "project_id": project_id,
                "capability_ids": [],
                "role_ids": ["eos.role.requirements-engineer", "eos.role.product-manager"],
                "input_artifact_ids": [],
                "output_artifact_ids": [req_id],
                "depends_on_task_ids": [],
                "status": "ready",
                "priority": "high",
                "risk": "medium",
                "knowledge_unit_ids": [],
            }
        )
        task_ids_by_slug["define-requirements"] = req_task

    for cap_id in arbitration.selected:
        spec = cap_artifacts.get(cap_id)
        if not spec:
            notes.append(f"No default artifact template for {cap_id}; skipped structural generation.")
            continue
        art_id = f"eos.artifact.{slug}.{spec['artifact_slug']}"
        task_id = f"eos.task.{slug}.{spec['task_slug']}"
        artifact_ids_by_slug[spec["artifact_slug"]] = art_id
        task_ids_by_slug[spec["task_slug"]] = task_id

        depends_art_slug = spec.get("depends_on_artifact")
        input_arts: list[str] = []
        depends_tasks: list[str] = []
        if depends_art_slug and depends_art_slug in artifact_ids_by_slug:
            input_arts.append(artifact_ids_by_slug[depends_art_slug])
        if spec["artifact_slug"] == "architecture" and "requirements" in artifact_ids_by_slug:
            input_arts.append(artifact_ids_by_slug["requirements"])
            depends_tasks.append(task_ids_by_slug["define-requirements"])
            dependencies.append(
                {
                    "kind": "task_depends_on_task",
                    "from": task_id,
                    "to": task_ids_by_slug["define-requirements"],
                }
            )
            dependencies.append(
                {
                    "kind": "task_requires_artifact",
                    "from": task_id,
                    "to": artifact_ids_by_slug["requirements"],
                }
            )

        if depends_art_slug:
            producer = None
            for other_cap, other_spec in cap_artifacts.items():
                if (
                    other_spec["artifact_slug"] == depends_art_slug
                    and other_cap in arbitration.selected
                ):
                    producer = task_ids_by_slug.get(other_spec["task_slug"])
                    break
            if producer:
                depends_tasks.append(producer)
                dependencies.append(
                    {"kind": "task_depends_on_task", "from": task_id, "to": producer}
                )
                dependencies.append(
                    {
                        "kind": "task_requires_artifact",
                        "from": task_id,
                        "to": artifact_ids_by_slug[depends_art_slug],
                    }
                )

        artifacts.append(
            {
                "id": art_id,
                "type": spec["artifact_type"],
                "title": spec["title"] + " artifact",
                "project_id": project_id,
                "status": "planned",
                "depends_on_artifacts": list(input_arts),
            }
        )

        knowledge_ids = [s.unit_id for s in knowledge.selected if s.capability_id == cap_id]
        status = "pending" if depends_tasks else "ready"
        tasks.append(
            {
                "id": task_id,
                "title": spec["title"],
                "description": f"Produce {art_id} using selected knowledge units.",
                "objective": f"Approved or review-ready {spec['artifact_type']}",
                "project_id": project_id,
                "capability_ids": [cap_id],
                "role_ids": role_by_cap.get(cap_id, []),
                "input_artifact_ids": input_arts,
                "output_artifact_ids": [art_id],
                "depends_on_task_ids": depends_tasks,
                "status": status,
                "priority": "high",
                "risk": "medium",
                "knowledge_unit_ids": knowledge_ids,
            }
        )

        gate_id = f"eos.gate.{slug}.{spec['gate']}"
        gates.append(
            {
                "id": gate_id,
                "title": f"{spec['gate'].title()} Gate",
                "project_id": project_id,
                "condition": f"{spec['artifact_type']} evidence exists and meets review criteria.",
                "required_evidence": [art_id, task_id],
                "result": "pending",
                "approver": (role_by_cap.get(cap_id) or ["eos.role.technical-lead"])[0],
                "on_failure": "block_dependent_tasks",
            }
        )
        dependencies.append({"kind": "gate_requires_artifact", "from": gate_id, "to": art_id})

    for gap in arbitration.insufficient:
        area = gap["area"]
        if area not in {
            "backend_implementation",
            "frontend_implementation",
            "database_engineering",
            "devops_delivery",
            "iot_device_engineering",
            "networking",
            "cloud_mobile",
            "electrical_engineering",
            "physical_access_control",
            "payments_billing",
        }:
            continue
        art_id = f"eos.artifact.{slug}.{area.replace('_', '-')}-scope"
        task_id = f"eos.task.{slug}.scope-{area.replace('_', '-')}"
        human = area in {"electrical_engineering", "physical_access_control"}
        artifacts.append(
            {
                "id": art_id,
                "type": "professional_scope" if human else "gap_scope",
                "title": f"Scope for {area}",
                "project_id": project_id,
                "status": "planned",
                "professional_validation_required": human,
            }
        )
        arch_task = task_ids_by_slug.get("design-architecture")
        tasks.append(
            {
                "id": task_id,
                "title": f"Scope {area} (gap)",
                "description": gap["reason"],
                "objective": f"Record gap scope for {area}",
                "project_id": project_id,
                "capability_ids": [],
                "role_ids": [
                    r.role_id
                    for r in roles.roles
                    if r.source.startswith(f"gap:{area}") or (human and r.human_required)
                ][:3],
                "input_artifact_ids": [artifact_ids_by_slug["architecture"]]
                if "architecture" in artifact_ids_by_slug
                else [],
                "output_artifact_ids": [art_id],
                "depends_on_task_ids": [arch_task] if arch_task else [],
                "status": "blocked",
                "block_reason": "professional_validation_required"
                if human
                else "missing_capability_coverage",
                "priority": "high",
                "risk": "critical" if human else "high",
                "can_reason": True,
                "can_execute": False,
                "requires_professional_approval": human,
            }
        )
        if arch_task:
            dependencies.append({"kind": "task_depends_on_task", "from": task_id, "to": arch_task})
        if human:
            gates.append(
                {
                    "id": f"eos.gate.{slug}.professional-{area.replace('_', '-')}",
                    "title": f"Professional Gate: {area}",
                    "project_id": project_id,
                    "condition": "Licensed/qualified professional approves scope before physical execution.",
                    "required_evidence": [art_id],
                    "result": "pending",
                    "approver": "licensed_professional",
                    "on_failure": "block_physical_execution",
                    "autonomous_pass_forbidden": True,
                }
            )

    decisions: list[dict[str, Any]] = []
    if any(u.key == "payments_required" for u in intent.uncertainties):
        decisions.append(
            {
                "id": f"eos.decision.{slug}.payments-unknown",
                "title": "Payments requirement unresolved",
                "choice": "Do not select a PSP yet",
                "reason": "Utterance does not state payment requirement; inventing Stripe/PSP is forbidden",
                "status": "proposed",
                "project_id": project_id,
                "alternatives": ["Clarify with human", "Assume no payments until confirmed"],
                "reversibility": "high",
            }
        )

    project = {
        "id": project_id,
        "title": intent.objective[:120],
        "objective": intent.objective,
        "context": intent.utterance,
        "constraints": intent.constraints,
        "status": "planned",
        "capability_ids": list(arbitration.selected),
        "insufficient_coverage": arbitration.insufficient,
        "role_ids": [r.role_id for r in roles.roles],
        "artifact_ids": [a["id"] for a in artifacts],
        "task_ids": [t["id"] for t in tasks],
        "gate_ids": [g["id"] for g in gates],
        "decision_ids": [d["id"] for d in decisions],
        "uncertainties": [asdict_fact(u) for u in intent.uncertainties],
        "clarifying_questions": intent.clarifying_questions,
        "risk_signals": intent.risk_signals,
    }

    plan = {
        "id": plan_id,
        "project_id": project_id,
        "intent_summary": intent.objective,
        "capability_ids": list(arbitration.selected),
        "insufficient_coverage": arbitration.insufficient,
        "artifact_ids": [a["id"] for a in artifacts],
        "task_ids": [t["id"] for t in tasks],
        "gate_ids": [g["id"] for g in gates],
        "dependencies": dependencies,
        "knowledge_unit_ids": [s.unit_id for s in knowledge.selected],
        "status": "draft",
        "revision": 1,
        "execution_mode": "planning_only",
        "assumptions": [f.value for f in intent.context if f.certainty == "assumed"],
        "unknowns": [u.key for u in intent.uncertainties],
    }

    return GeneratedPlan(
        project=project,
        plan=plan,
        artifacts=artifacts,
        tasks=tasks,
        gates=gates,
        decisions=decisions,
        dependencies=dependencies,
        notes=notes,
    )
