# Execution Model

This document defines how Engineering OS coordinates engineering **work over time**.

It does **not** redefine knowledge units, Capabilities, or retrieval. Those remain owned by:

- [Knowledge Architecture](KNOWLEDGE-ARCHITECTURE.md)
- [Capability Model](CAPABILITY-MODEL.md)
- [Intent Resolution](INTENT-RESOLUTION.md)

Audit baseline: [docs/EXECUTION-LAYER-AUDIT.md](../docs/EXECUTION-LAYER-AUDIT.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| What problem does it solve? | Knowledge and Capability resolution do not record durable multi-step project work. |
| What problem does it prevent? | Treating playbooks as schedulers, or Capability relationships as execution DAGs. |
| What happens if it does not exist? | Agency behavior stays ephemeral chat; no plan, gates, blockers, or evidence trail. |
| Why are existing concepts insufficient? | Capabilities are intent; Knowledge Units are methodology; neither is a work graph. |

---

## Purpose

Separate:

| Layer | Question |
|---|---|
| **WHAT** | Which Capability / intent class applies? |
| **HOW** | Which Knowledge Units guide good engineering? |
| **EXECUTION** | What work must happen, in what order, with what evidence, until done? |

---

## Spine

```text
Intent
  ↓
Capability Resolution
  ↓
Execution Plan
  ↓
Milestone
  ↓
Task
  ↓
Artifact
  ↓
Validation Gate
  ↓
Completion
```

### Stage responsibilities

| Stage | Responsibility | Non-responsibility |
|---|---|---|
| **Intent** | Capture desired outcome and constraints | Choosing implementation details |
| **Capability Resolution** | Select catalog Capabilities; declare gaps | Scheduling tasks |
| **Execution Plan** | Derive milestones, tasks, artifacts, gates from resolved Capabilities + context | Owning methodology content |
| **Milestone** | Group outcomes that unlock a phase of work | Becoming a Capability taxonomy |
| **Task** | Represent concrete executable work with readiness | Storing reusable knowledge |
| **Artifact** | Represent produced results of work | Replacing Knowledge Units |
| **Validation Gate** | Authorize progress based on evidence | Soft opinion without criteria |
| **Completion** | Record that required gates passed and objectives are met | Claiming perpetual product success |

---

## Invariants

1. **Execution is not Knowledge.** Plans/tasks/artifacts do not become playbooks.
2. **Capabilities are not phases.** A Capability may inform many tasks; it is not a milestone by itself.
3. **Knowledge relationships are not execution dependencies.** `references` / `related_capability` never imply task order.
4. **Gates require evidence.** “Looks correct” is insufficient when a criterion exists.
5. **Gaps remain first-class.** Missing Capabilities/knowledge produce blocked or escalated work — never invented offers.
6. **Human escalation can stop progress.** Physical, legal, or regulated work may require approval before continuation.
7. **Plans are revisable with trace.** Replanning must not silently erase prior decisions/evidence.

---

## Relationship to Existing Layers

```text
Intent Resolution  →  which Capabilities apply
Knowledge Units    →  how to reason/produce well
Execution Model    →  how work is coordinated until validated completion
Delivery (later)   →  how results enter repositories/CI/deploy
Adapters (later)   →  how tools host executors
```

The future Orchestrator **implements** this model. It must not replace it with tool-specific workflows.

---

## Minimal Runtime Expectation (non-goals)

This document does **not** require:

- a database
- a queue system
- an agent fleet
- CI/CD automation
- Cursor-specific orchestration

Those may appear later as Delivery/Adapter/Agent concerns.

---

## Open Details Deferred to Sibling Models

| Concern | Document |
|---|---|
| Project container | PROJECT-MODEL |
| Artifacts | ARTIFACT-MODEL |
| Tasks | TASK-MODEL |
| Execution dependencies | DEPENDENCY-MODEL |
| Gates | VALIDATION-GATES |
| Roles | ROLE-MODEL |
| Plan shape / generation | EXECUTION-PLAN, PLAN-GENERATION |
| Escalation / evidence / decisions | HUMAN-ESCALATION, EVIDENCE-MODEL, DECISION-MODEL |
| Failure / replan | Failure + REPLANNING-MODEL (later tasks) |
| Orchestrator/Agent boundaries | ORCHESTRATOR-MODEL, AGENT-MODEL |

---

## Anti-Patterns

- Embedding a full SDLC checklist inside every Capability
- Creating an execution DAG across Capabilities
- Treating the Cursor agency skill as the Execution Model
- Storing methodology inside task descriptions instead of Knowledge Units
- Completing milestones without gate evidence
