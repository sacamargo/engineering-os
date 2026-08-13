# Evidence Model

**Evidence** links claims in a Project to inspectable support.

It enables auditability, debugging, explanation, rollback rationale, and learning.

Companions: [Validation Gates](VALIDATION-GATES.md), [Decision Model](DECISION-MODEL.md), [Artifact Model](ARTIFACT-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Agency claims need traceable support. |
| Problem avoided | Ungrounded “done” and unverifiable gate passes. |
| If absent | Cannot audit why a plan advanced. |
| Why not only artifacts? | Artifacts are products; evidence can also be test runs, approvals, logs, commits. |

---

## Trace Pattern

```text
Requirement / Intent
  ↓
Decision (optional)
  ↓
Artifact / Task outcome
  ↓
Validation
  ↓
Evidence record
```

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Evidence id |
| `project_id` | Project |
| `claim` | What is being supported |
| `kind` | `artifact` \| `test` \| `approval` \| `commit` \| `log` \| `external` \| `other` |
| `pointer` | Path, URL, artifact id, commit sha, etc. |
| `produced_by` | Task/agent/human |
| `related_gate_ids` | Gates this supports |
| `timestamp` | When captured |

---

## Rules

1. Gate passes should reference evidence ids when criteria are verifiable.
2. Evidence should be retrievable by a future reader.
3. Missing evidence blocks gate passage (unless waiver with escalation/authority).

---

## Non-Goals

- Full forensic storage platform
- Mandatory evidence for trivial editorial tasks
- Replacing Git history
