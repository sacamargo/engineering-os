# Decision Model

A **Decision** records an important engineering choice with rationale, alternatives, and validation hooks.

This is a minimal decision record for Execution Layer traceability. It is not a mandate to adopt heavyweight ADR bureaucracy for every trivial choice.

Companions: [Evidence Model](EVIDENCE-MODEL.md), [Artifact Model](ARTIFACT-MODEL.md), [Project Model](PROJECT-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Important choices need durable reason trails for replan/audit. |
| Problem avoided | Silent plan mutation and forgotten alternatives. |
| If absent | Replanning and reviews cannot explain “why this path”. |
| Why not only chat history? | Chat is ephemeral and not gate-linkable. |

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Decision id |
| `project_id` | Project |
| `title` | Short decision name |
| `status` | `proposed` \| `accepted` \| `superseded` \| `rejected` |
| `choice` | What was decided |
| `reason` | Why |
| `alternatives` | Considered options |
| `evidence_ids` | Supporting evidence |
| `validation` | How the decision will be checked |
| `capability_ids` | Related intent classes (optional) |
| `artifact_ids` | Related artifacts (optional) |

---

## Example

```text
Decision: Use PostgreSQL as booking authority.
Reason: Need strong uniqueness/concurrency guarantees for reservations.
Alternatives: fully event-sourced booking; multiple shard-local authorities.
Evidence: concurrency requirement notes.
Validation: integration tests for double-booking prevention.
```

---

## Rules

1. Material architecture/security/delivery choices should create decision records.
2. Superseding a decision creates a new record (or explicit supersedes link); do not silently rewrite history.
3. Decisions do not replace Knowledge Units; they apply knowledge to a project.

---

## Non-Goals

- Requiring an ADR file for every lint tweak
- Full decision-management product
- Automatic decision making without recorded rationale for material choices
