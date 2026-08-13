# Artifact Model

An **Artifact** is a result produced (or required) by project work.

Artifacts are **not** Knowledge Units. Knowledge Units teach how to work; Artifacts are situational outputs of a Project.

Sibling models: [Execution Model](EXECUTION-MODEL.md), [Project Model](PROJECT-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Agency outputs need identity, state, validation, and dependencies. |
| Problem avoided | Confusing reusable playbooks with one-off deliverables. |
| If absent | No way to gate “implementation depends on architecture artifact”. |
| Why not Knowledge Unit? | KUs are catalog methodology; artifacts are project products. |

---

## Examples

```text
Architecture
Security Review
Test Plan
Observability Plan
Database Schema
API Contract
Implementation
Migration Plan
Deployment Plan
Incident Report
Decision Record
```

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Stable artifact id (`eos.artifact.<project>.<name>` recommended) |
| `type` | Artifact type token (open vocabulary initially) |
| `title` | Human-readable name |
| `project_id` | Owning project |
| `origin` | Producing task id and/or Capability id |
| `status` | Artifact lifecycle |
| `depends_on_artifacts` | Artifact prerequisites |
| `validation` | Criteria / gate references |
| `version` | Revision marker |
| `relationships` | Optional typed links to other artifacts |
| `evidence_ids` | Supporting evidence |
| `path` | Optional location in repo/workspace |

---

## Artifact States

```text
planned → drafting → ready_for_review → approved → superseded → rejected
```

Artifact state ≠ task state ≠ project state.

---

## Invariants

1. An Artifact must not redefine Knowledge Unit contracts.
2. Approving an Artifact may unlock tasks/gates; it does not publish catalog knowledge.
3. Superseding keeps history; do not silently rewrite prior approved meaning without a new version/id policy.
4. Missing required artifacts block dependent tasks.

---

## Non-Goals

- File format standards for every artifact type
- Replacing Git blobs as storage engine
- Turning every chat paragraph into an artifact
