# Task Model

A **Task** is concrete executable work inside a Project.

Tasks consume and produce Artifacts, may reference Capabilities and Roles, and become ready only when execution dependencies are satisfied.

Sibling models: [Execution Model](EXECUTION-MODEL.md), [Artifact Model](ARTIFACT-MODEL.md), [Dependency Model](DEPENDENCY-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Agency needs schedulable work units with readiness and outcomes. |
| Problem avoided | Treating playbooks as tasks, or tasks as reusable knowledge. |
| If absent | No blocked/ready/failed semantics; no parallel/serial work graph. |
| Why not Artifact? | Artifacts are results; tasks are the work that creates/changes them. |

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Stable task id |
| `title` | Short name |
| `description` | What to do |
| `objective` | Why it matters |
| `project_id` | Owning project |
| `capability_ids` | Intent classes informing the work (optional, non-empty when known) |
| `role_ids` | Required specializations |
| `input_artifact_ids` | Required inputs |
| `output_artifact_ids` | Expected outputs |
| `depends_on_task_ids` | Execution predecessors |
| `validation` | Done criteria / gate links |
| `status` | Task state |
| `priority` | Relative urgency |
| `risk` | Risk notes |
| `owner` | Human or agent assignee (optional) |

---

## Task States

```text
pending
ready
in_progress
blocked
completed
failed
cancelled
```

### Readiness rule

A task may move to `ready` only when:

1. All `depends_on_task_ids` are `completed` (or waived with evidence)
2. All required `input_artifact_ids` are in an acceptable state (typically `approved` or explicitly `ready_for_review` per gate policy)
3. No open blocking escalation forbids start

---

## Invariants

1. Tasks must not embed full Knowledge Unit bodies; they may reference unit IDs.
2. Completing a task should produce/update declared output artifacts (or record why not).
3. `failed` requires a cause; recovery uses retry/replan/escalate — not silent success.
4. Task state ≠ project/artifact/gate state.

---

## Non-Goals

- Full workflow engine semantics
- Human HR assignment system
- Automatic code generation as a task type taxonomy
