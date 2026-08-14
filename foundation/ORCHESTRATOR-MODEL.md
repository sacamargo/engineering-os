# Orchestrator Model (Boundary)

Defines the Orchestrator’s **responsibility boundary**.

**Do not implement an Orchestrator runtime in Phase 3.**

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
