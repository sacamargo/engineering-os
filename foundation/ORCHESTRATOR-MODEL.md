# Orchestrator Model (Boundary)

Defines the Orchestrator’s **responsibility boundary**.

**Do not implement an Orchestrator runtime that executes product code in Phase 4.**

Phase 4 lands a **Planning Orchestrator** (`orchestration/`) that coordinates Intent → Plan.

It remains a coordinator facade over small modules. It still must not:

- Own Playbook methodology content
- Be the Capability catalog
- Be 20 hard-coded specialist agents
- Bypass Validation Gates
- Invent Capabilities
- Silently replan accepted decisions
- Depend on Cursor/vendor APIs

See `orchestration/SPEC.md` and `docs/PHASE-4-ORCHESTRATION-AUDIT.md`.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Need a future coordinator without a god object. |
| Problem avoided | Orchestrator containing all engineering knowledge. |
| If absent | Temptation to dump everything into one agent prompt. |

---

## Coordinates

```text
Intent
Capabilities
Knowledge (via Capability fulfillment)
Execution Plan
Tasks
Artifacts
Gates
Roles
Evidence
Human escalation
```

---

## Must Not

- Own Playbook methodology content
- Be the Capability catalog
- Be 20 hard-coded specialist agents
- Bypass Validation Gates
- Invent Capabilities
- Silently replan accepted decisions

---

## Principle

> The Orchestrator coordinates. It does not contain all engineering knowledge.

Knowledge stays in units. Intent stays in Capabilities. Work stays in Tasks. Specialization stays in Roles. Execution stays with Agents (later).
