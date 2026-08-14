# Orchestration SPEC

## Purpose

Provide a deterministic, vendor-neutral **planning brain** for Engineering OS.

## Facade

`PlanningOrchestrator.plan(utterance, context?) -> PlanningResult`

Delegates to modules listed in Phase 4 audit. Must stay thin.

## Invariants

1. Catalog-bound Capability IDs only
2. Artifact-based execution dependencies (not Capability DAGs)
3. Role ≠ Agent ≠ Capability
4. Claim ≠ Evidence
5. Reuse Phase 3 project/task/artifact/gate state machines
6. Core ≠ Adapter

## Module ownership

| Module | Owns |
|---|---|
| `intent` | Structured Intent from utterance |
| `capability` | Candidates + arbitration |
| `role` | Role selection + executor hints |
| `knowledge` | Progressive disclosure selection |
| `plan` | Execution plan object generation |
| `dependency` | DAG integrity |
| `readiness` | Startability evaluation |
| `gates` | Gate record evaluation |
| `gaps` | Coverage holes |
| `escalation` | Human-required stops |
| `state` | Transition validation |
| `evidence` / `decision` | Records |
| `failure` / `replan` / `impact` | Modeled recovery |
| `boundaries/*` | Future integration seams |
