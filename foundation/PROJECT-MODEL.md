# Project Model

A **Project** is the minimal durable container for coordinated engineering work in Engineering OS.

It binds an intent to Capability resolution, an execution plan, artifacts, tasks, gates, risks, and progress — without becoming a project-management product database.

Sibling: [Execution Model](EXECUTION-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Multi-step work needs a durable object beyond a chat transcript. |
| Problem avoided | Scattering plan state across prompts with no recovery/trace. |
| If absent | Agency cannot answer “what is blocked / done / waiting on humans?” |
| Why not Capability/Knowledge Unit? | Those are reusable catalog objects; a Project is situational work. |

---

## Definition

A Project represents **one coherent engineering engagement** derived from a user intent (and optional repository/system context).

Projects are not Knowledge Units. They may *use* Knowledge Units and Capabilities.

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Stable project identity (`eos.project.<slug>` recommended) |
| `title` | Human-readable name |
| `objective` | Desired outcome |
| `context` | System/repo/business context summary |
| `constraints` | Hard limits |
| `status` | Project lifecycle state |
| `capability_ids` | Resolved Capabilities (from Intent Resolution) |
| `insufficient_coverage` | Declared catalog/knowledge gaps |
| `role_ids` | Required execution specializations (not Capabilities) |
| `artifact_ids` | Produced/required artifacts |
| `milestone_ids` | Lightweight phase groupings |
| `task_ids` | Concrete work items |
| `gate_ids` | Validation gates |
| `risks` | Known risks |
| `decision_ids` | Important decisions |
| `escalations` | Human/professional escalations |
| `evidence_ids` | Trace anchors for key claims |
| `created_at` / `updated_at` | Audit timestamps (optional in fixtures) |

Keep optional fields optional. Progressive adoption applies.

---

## Project States

Aligned with the Execution Layer state machine (detailed later):

```text
discovered → planned → ready → executing → blocked → validating → completed
                                                              ↘ failed
                                                              ↘ cancelled
```

Project state is **not** task state, artifact state, or gate state.

---

## Invariants

1. A Project must not invent Capability IDs.
2. `insufficient_coverage` may leave a Project `blocked` or require escalation.
3. Completion requires required gates to pass (or explicit waiver with evidence).
4. Roles listed on a Project are specialization needs, not Capabilities.
5. Projects may be represented as Markdown/YAML fixtures before any database exists.

---

## Non-Goals

- Full PM suite (Gantt, resource leveling, billing)
- Replacing Git issues/PRs
- Storing methodology bodies inside the project file
