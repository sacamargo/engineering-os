# Phase 4 Orchestration Audit

Baseline: `main` @ `5671fd8` (Phase 3 complete).

This audit is the Phase 4 Task 1 deliverable. Repository is the source of truth.

---

## What Phase 3 Already Provides (do not rebuild)

| Concern | Authority |
|---|---|
| Intent framing protocol | `foundation/INTENT-RESOLUTION.md` + `experiments/intent-disambiguation/` |
| Execution spine | `foundation/EXECUTION-MODEL.md` |
| Project / Task / Artifact / Plan | foundation models + `contracts/execution/` |
| Dependencies vs knowledge links | `DEPENDENCY-MODEL.md` |
| Gates / Evidence / Decisions | foundation + schemas |
| Roles / bindings | `ROLE-MODEL.md`, `ROLE-CAPABILITY-BINDING.md` |
| Plan generation protocol | `PLAN-GENERATION.md` (protocol only — not code) |
| Gaps / escalation | `GAP-DETECTION.md`, `HUMAN-ESCALATION.md` |
| State machines | `EXECUTION-STATE-MACHINE.md` |
| Failure / replan / impact | foundation models |
| Orchestrator / Agent / Delivery / Adapter / Codebase | **boundaries only** |
| Fixtures | `examples/rivallium/`, `examples/padel-iot/` |
| Validators | `contracts/validate.py`, `validate_execution.py` |
| Agency scenario shapes | `tests/agency/` (structural, not behavioral planner) |

---

## What Phase 4 Must Add

A **Planning Orchestrator** that is code — not chat folklore — composed of small modules:

```text
Intent Intake
→ Capability Resolution (+ arbitration)
→ Role Resolution
→ Knowledge Selection
→ Plan Generation
→ Dependency Resolution
→ Gap Detection
→ Human Escalation
→ Gate Evaluation
→ Readiness Evaluation
→ (modeled) Failure / Replan / Change Impact / Evidence / Decision
→ Boundaries: Codebase / Agent / Delivery / Adapter
```

First demo success criterion:

> Input: “Quiero construir una SaaS de reservas… segura, testeable y observable.”  
> Output: structured Execution Plan with capabilities, roles, knowledge, tasks, artifacts, deps, gates, gaps, readiness — **without executing product code**.

---

## Architectural Decisions Locked Before Coding

### 1. Facade, not God Object

`PlanningOrchestrator` may be a thin facade that **delegates** to focused modules. It must not own catalog content, playbook bodies, or vendor APIs.

### 2. Catalog-driven Capability discovery

Resolvers load live `capabilities/**/*.md` metadata (reuse contracts loader patterns). No giant hard-coded Capability switch inside the orchestrator.

### 3. Dependencies from Artifacts, not Capability chains

Multi-capability routing may select Architecture + Security + Testing + Observability as primary/secondary.

Execution order comes from artifact prerequisites (e.g., threat model depends on architecture artifact), **not** from `related_capability` edges.

### 4. Role ≠ Agent ≠ Capability

Role resolution attaches specialization metadata and human/agent executor hints. No automatic agent fleet.

### 5. Reuse Phase 3 state machine

Do **not** invent a parallel project state enum.

Map planning-orchestrator vocabulary onto existing states:

| Phase 4 phrase | Phase 3 project status |
|---|---|
| draft | `discovered` |
| planned | `planned` |
| ready | `ready` |
| running | `executing` |
| blocked | `blocked` |
| waiting_human | `blocked` + open escalation / readiness `needs_human` |
| replanning | plan `revision` bump + project may stay `blocked`/`planned` while replan record exists |
| failed / completed / cancelled | same |

Readiness statuses (`ready`, `blocked`, `needs_input`, `needs_human`, `missing_capability`, `invalid`, `partially_ready`) are **plan evaluation results**, not a second project lifecycle.

### 6. Deterministic planning brain first

No LLM runtime, embeddings, RAG, or Cursor APIs in Core. Matching uses catalog metadata (`entry_signals`, `applicability`, `limits`, tags, domains) + explicit gap/escalation rules.

### 7. Honesty over coverage

Missing Capabilities → `missing_capability` gaps. Regulated physical work → `human_required`. Never invent Capability IDs.

---

## Contradictions Checked

| Potential conflict | Verdict |
|---|---|
| New project states vs EXECUTION-STATE-MACHINE | Avoided via mapping above |
| Intent-disambiguation experiment is case-authored, not free-text | Phase 4 adds free-text intake + resolver; experiment remains valid structural checker |
| Agency tests are fixture-shaped | Phase 4 adds behavioral tests against planner output |
| ORCHESTRATOR-MODEL says “do not implement runtime in Phase 3” | Phase 4 implements **planning** coordination only |

No Phase 3 architectural rollback required to start.

---

## Package Layout (planned)

```text
orchestration/
  README.md
  SPEC.md
  catalog/          # load capabilities + units
  intent/           # intake
  capability/       # resolve + arbitrate
  role/             # resolve + binding apply
  knowledge/        # progressive disclosure selection
  plan/             # generate execution plan objects
  dependency/       # DAG checks
  readiness/        # evaluate startability
  gates/            # evaluate gate records
  gaps/             # detect coverage holes
  escalation/       # human required logic
  state/            # transition validation against Phase 3 machine
  evidence/         # claim vs evidence
  decision/         # decision records
  failure/          # failure classification (modeled)
  replan/           # partial replan (modeled)
  impact/           # change impact (modeled)
  boundaries/       # codebase, agent, delivery, adapter interfaces
  facade/           # PlanningOrchestrator thin coordinator
  cli.py            # local demo entrypoint
```

---

## Non-Goals (reconfirmed)

LLM runtime, vector DB, multi-agent swarm, autonomous coding, CI/CD engine, deploy, production monitoring, product UI/auth/billing.

---

## Implementation Order

Follow Phase 4 prompt §35 task list: intake → resolve → plan → readiness → scenarios → anti-god-object → self-refutation → docs → final validation.

One logical task = one branch = merge to `main`.
