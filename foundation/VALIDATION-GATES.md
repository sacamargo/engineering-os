# Validation Gates

A **Validation Gate** authorizes progress in an Execution Plan based on **evidence**, not vibes.

Sibling models: [Execution Model](EXECUTION-MODEL.md), [Artifact Model](ARTIFACT-MODEL.md), [Evidence Model](EVIDENCE-MODEL.md) (later)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Agency must know when it may advance stages. |
| Problem avoided | “Looks correct” substituting for verifiable criteria. |
| If absent | Projects complete without proof; failures hide in chat. |
| Why not Task status alone? | Completion of work ≠ authorization to proceed. |

---

## Example Gates

```text
Architecture Gate
Security Gate
Test Gate
Implementation Gate
Deployment Gate
Release Gate
```

Gate names are project-local. Do not invent a mandatory universal gate catalog for every project.

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Stable gate id |
| `title` | Human name |
| `project_id` | Owning project |
| `condition` | What must be true |
| `required_evidence` | Evidence/artifact/task references |
| `result` | `pending` \| `passed` \| `failed` \| `waived` |
| `approver` | Human role/agent/policy allowed to pass/waive |
| `on_failure` | Block / replan / escalate / abort guidance |

---

## Rules

1. If a verifiable criterion exists, subjective confidence is insufficient.
2. `waived` requires recorded rationale and authority.
3. Failed gates block dependent milestones/tasks until resolved.
4. Gates do not contain methodology; they reference artifacts/evidence produced via Knowledge Units.

---

## Relationship to Capabilities

A Security Gate often consumes artifacts produced under `eos.capability.security.review`, but the Capability is not the Gate.

---

## Anti-Patterns

- One mega-gate that rubber-stamps everything
- Gates that require unavailable evidence with no escalation path
- Passing gates by rewriting criteria after the fact without trace
