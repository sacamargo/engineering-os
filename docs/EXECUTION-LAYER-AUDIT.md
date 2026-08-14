# Execution Layer Audit

**Phase 3 — Task 1**  
**Status:** audit only (no execution models implemented by this document)  
**Date context:** post agency MVP (`0bc6d00`)

This audit answers: what Engineering OS can do today, what it cannot, which concepts already exist, which are missing, which must not be invented, and what breaks when moving from Knowledge → Execution.

---

## 1. Current Capability

Engineering OS today is a **knowledge + intent-routing system** with a thin agency entry loop.

### What it can do

| Area | Evidence |
|---|---|
| Express durable intent classes | 4 Capabilities under `capabilities/` |
| Fulfill intents with methods/decision models | Playbooks + frameworks bound via `primary_fulfillment` / `fulfilled_by` |
| Frame user intent and resolve candidates | `foundation/INTENT-RESOLUTION.md` + `experiments/intent-disambiguation/` |
| Detect catalog gaps | `insufficient_coverage` in resolution records |
| Validate knowledge unit contracts | `contracts/validate.py` |
| Operate as a Cursor agency entrypoint | `.cursor/skills/engineering-os-agency` + `eos.skill.agency.capability-routing` |
| Soft-relate Capabilities | `related_capability` (not an execution DAG) |

### What it cannot do

| Gap | Consequence |
|---|---|
| Represent a multi-step engineering **project** as a first-class object | Work remains conversational / ephemeral |
| Represent **tasks** with readiness, blockers, owners | No executable work graph |
| Represent **artifacts** as project outputs distinct from Knowledge Units | Deliverables are not tracked, versioned, or gated |
| Represent **execution dependencies** (vs knowledge relationships) | Easy to confuse “references” with “must run after” |
| Represent **validation gates** with required evidence | “Looks good” can substitute for criteria |
| Represent **roles** as execution specialization distinct from Capabilities | Risk of Role = Capability drift |
| Represent **agents** as executors | No boundary between persona, role, and runtime |
| Produce a durable **execution plan** that can be replanned | Plans cannot fail/retry/escalate formally |
| Trace **evidence** and **decisions** across work | Weak auditability for agency claims |
| Coordinate delivery (code → CI → deploy) as a layer | Delivery is outside the model |
| Runtime orchestration | Orchestrator is named as future, not defined as a bounded component |

---

## 2. Existing Concepts (must reuse, not reinvent)

| Concept | Where it lives | Role |
|---|---|---|
| Capability | Capability Model + catalog | Intent class / routing facade |
| Knowledge Unit | Knowledge Architecture | Portable methodology/content |
| Relationship (knowledge) | Knowledge Architecture / Contracts | Graph for retrieval/composition |
| Intent Frame / Candidate / Selection | Intent Resolution | Demand → catalog matching |
| Insufficient coverage | Intent Resolution | Honest gap detection |
| Context package | Knowledge Architecture | Retrieval assembly (not project state) |
| Skill (portable) | Module type + agency skill | AI-operable procedure |
| Adaptation | Module type | Tool packaging |
| Contracts / Validator | `contracts/` | Enforce knowledge invariants |
| Agency routing skill | `skills/agency/capability-routing.md` | Manual/AI loop: frame→route→bind→emit |

---

## 3. Concept Disposition Table

Legend:

- **Exists** — already in repo with durable meaning
- **Missing** — needed for Execution Layer
- **Must exist** — required for coherent agency execution
- **Must avoid** — do not create / do not conflate

| Concept | Exists | Missing | Must exist | Must avoid |
|---|---|---|---|---|
| **Capability** | Yes | — | Keep as intent class | Becoming a role, agent, or project phase |
| **Fulfillment** (playbook/framework/…) | Yes | — | Keep as knowledge how-to | Becoming the execution scheduler |
| **Artifact** | No (only informal outputs) | Yes | Project-produced results with state/validation | Absorbing Knowledge Units |
| **Task** | No | Yes | Executable work units with readiness | Duplicating artifacts or playbooks |
| **Dependency** (execution) | No | Yes | Task/artifact prerequisites | Equating to knowledge `references`/`related_capability` |
| **Validation** (gate) | Partial (review language only) | Yes | Explicit gates + evidence | “Seems correct” as evidence |
| **Execution** (layer/plan) | No | Yes | Coordination of work over time | Second Knowledge Architecture |
| **Agent** | No (Cursor skill is adaptation/entry, not Agent model) | Yes (boundary doc first) | Runtime executor concept | 20 rigid agents = 20 roles |
| **Role** | No | Yes | Execution specialization metadata | Role = Capability; Role = Agent |
| **Project** | No | Yes | Minimal container for intent→plan→state | Giant database / PM suite clone |
| **Milestone** | No | Yes (lightweight) | Grouping of gates/outcomes | Parallel taxonomy competing with Capabilities |
| **Gate** | No | Yes | Progress authorization | Soft opinions without criteria |

---

## 4. Problems at the Knowledge → Execution Boundary

### P1 — Outputs are ephemeral

Playbooks say what to produce, but Engineering OS does not record produced Architecture / Security Review / Test Plan as addressable project artifacts with lifecycle.

### P2 — Relationships are the wrong dependency language

`related_capability`, `references`, and `composes` answer knowledge questions. They do not authorize:

```text
Implement Booking Core cannot start until Database Schema exists
```

Using knowledge relationships as an execution DAG would create a false orchestration graph (already forbidden for Capabilities).

### P3 — Multi-Capability work has no durable plan object

The agency skill can sequence viewpoints conversationally. It cannot represent blocked tasks, failed gates, replans, or progress across sessions.

### P4 — Coverage gaps stop routing, not projects

`insufficient_coverage` is correct for Capability resolution. Execution still needs a place to attach gaps, escalations, and blocked work inside a project.

### P5 — Professional / human escalation is narrative only

Playbooks mention professional validation (e.g., electrical). There is no first-class escalation object or gate outcome for “cannot proceed without human/specialist.”

### P6 — Roadmap naming tension (non-blocking)

`foundation/PROJECT-ROADMAP.md` currently labels Phase 3 as **Skills System**. This Phase 3 effort targets **Execution Model**. This is a documentation sequencing conflict to resolve when rewriting the roadmap — not a contradiction that invalidates existing Capabilities or Contracts.

### P7 — Risk of concept collapse

Without strict boundaries, future authors may:

- turn Roles into Capabilities
- turn Agents into Roles
- turn Tasks into Playbooks
- turn Orchestrator into a god object that owns methodology

The Execution Layer must coordinate work **without absorbing** Knowledge Architecture.

---

## 5. What Must Not Be Created

| Anti-design | Why |
|---|---|
| 20 Capabilities because ~20 roles exist | Breaks coarse Capability model |
| 20 permanent agents mapped 1:1 to roles | Rigid org chart, not problem composition |
| Mega-playbook “how to build any software” | Defeats modular knowledge |
| Execution DAG over Capabilities | Forbidden by Capability Model |
| Second metadata system that redefines Knowledge Units | Contracts/KA already own that |
| Premature runtime Orchestrator product | Model must exist before runtime |
| Premature database | Fixtures/docs first; store later if needed |
| Cursor-core coupling | Adaptations remain peripheral |

---

## 6. Minimum Concept Set Recommended for Phase 3

Earn-its-place shortlist (models, not runtime):

1. **Execution Model** — coordination spine
2. **Project Model** — durable work container
3. **Artifact Model** — produced results ≠ knowledge units
4. **Task Model** — executable work + readiness
5. **Dependency Model** — execution prerequisites ≠ knowledge relationships
6. **Validation Gates** — evidence-based progress
7. **Role Model** — specialization ≠ intent
8. **Execution Plan / Plan Generation** — intent → coordinated work
9. **Human Escalation + Evidence + Decision** — agency integrity
10. **Orchestrator / Agent / Adapter boundaries** — define without implementing runtime gods

Deferred as runtime (define boundaries only where listed later in Phase 3):

- live Orchestrator engine
- agent fleet
- CI/CD delivery automation
- full codebase indexer

---

## 7. Success Condition for Leaving This Audit

**Status (end of Phase 3):** Satisfied via models + fixtures (`examples/rivallium/`, `examples/padel-iot/`). Runtime orchestration remains future work.

Engineering OS can represent — as models and fixtures, not as autonomous runtime — a project such as Rivallium with:

- intent
- required Capabilities
- required knowledge
- required roles (as specialization, not Capabilities)
- artifacts
- tasks
- order / parallelism
- gates
- human escalation
- evidence of completion

without collapsing those concepts into prompts or into Knowledge Units.

---

## 8. Explicit Non-Goals of This Document

- Does not define schemas
- Does not extend the validator
- Does not create examples/fixtures
- Does not rewrite the roadmap
- Does not implement an Orchestrator

Those belong to subsequent Phase 3 tasks on dedicated branches.
