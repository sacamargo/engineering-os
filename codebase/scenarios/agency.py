"""Agency scenario runner for Phase 5 Codebase Intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codebase.analyze import analyze_repository
from codebase.report import bundle_to_machine_json
from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

SCENARIOS = [
    {
        "id": "analyze-repo",
        "utterance": "Analiza este repositorio.",
        "fixture": "rivallium-mini",
        "run_analysis": True,
    },
    {
        "id": "audit-architecture",
        "utterance": "Audita la arquitectura de este sistema.",
        "fixture": "rivallium-mini",
        "run_analysis": True,
    },
    {
        "id": "security-problems",
        "utterance": "Encuentra problemas de seguridad en este repositorio.",
        "fixture": "legacy-chaos",
        "run_analysis": True,
    },
    {
        "id": "refactor-module",
        "utterance": "Quiero refactorizar el módulo de reservas.",
        "fixture": "rivallium-mini",
        "run_analysis": False,
    },
    {
        "id": "migrate-system",
        "utterance": "Quiero migrar este sistema legado.",
        "fixture": "legacy-chaos",
        "run_analysis": False,
    },
    {
        "id": "investigate-bug",
        "utterance": "Investiga este bug en el gateway IoT.",
        "fixture": "padel-iot-mini",
        "run_analysis": False,
    },
]


def run_scenario(spec: dict[str, Any]) -> dict[str, Any]:
    fixture_root = FIXTURES / spec["fixture"]
    orch = PlanningOrchestrator(ROOT)
    context: dict[str, Any] = {"fixture": spec["fixture"]}
    plan = orch.plan(spec["utterance"], context).to_dict()
    analysis = None
    if spec.get("run_analysis"):
        analysis = bundle_to_machine_json(analyze_repository(fixture_root))
    return {
        "id": spec["id"],
        "utterance": spec["utterance"],
        "fixture": spec["fixture"],
        "intent": plan["intent"]["possible_intents"],
        "capabilities": plan["arbitration"]["selected"],
        "codebase_status": plan["codebase"].get("analysis_status"),
        "has_codebase_analysis_task": any(
            t.get("task_kind") == "codebase_analysis" for t in plan["generated"]["tasks"]
        ),
        "readiness": plan["readiness"]["status"],
        "gaps": [g.get("kind") for g in plan["gaps"]],
        "escalations": [e.get("domain") for e in plan.get("escalations") or []],
        "analysis_snapshot_id": (analysis or {}).get("snapshot", {}).get("id"),
        "analysis_findings": len((analysis or {}).get("snapshot", {}).get("findings") or []),
        "analysis_unknowns": (analysis or {}).get("snapshot", {}).get("unknowns"),
        "notes": [
            "Codebase Intelligence is evidence infrastructure, not a Capability.",
            "Findings are not decisions.",
        ],
    }


def main() -> None:
    results = [run_scenario(s) for s in SCENARIOS]
    print(json.dumps({"scenarios": results}, indent=2))


if __name__ == "__main__":
    main()
