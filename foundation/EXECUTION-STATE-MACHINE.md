# Execution State Machine

Defines **distinct** lifecycle states for Project, Task, Artifact, and Gate objects.

These machines coordinate execution. They are **not** a Knowledge Architecture and must not absorb Capability or Playbook semantics.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Prevent collapsing “project progressing” with “task blocked” or “gate failed”. |
| Problem avoided | One mega-status enum that lies about what is wrong. |
| If absent | Operators cannot tell whether to replan, retry, or escalate. |
| Why not reuse Knowledge status? | Knowledge lifecycle (`draft`/`active`/…) describes catalog units, not work. |

---

## Project States

```text
discovered → planned → ready → executing ⇄ blocked
                              ↓
                         validating → completed
                              ↓
                           failed | cancelled
```

| State | Meaning |
|---|---|
| `discovered` | Intent captured; coverage/gaps not yet finalized |
| `planned` | Execution Plan exists |
| `ready` | Preconditions met to start work |
| `executing` | One or more tasks in progress |
| `blocked` | Progress stopped (dependency, gap, escalation, failure) |
| `validating` | Gates under evaluation |
| `completed` | Objective met with required evidence |
| `failed` | Unrecoverable without explicit replan/abort decision |
| `cancelled` | Stopped by human/policy |

---

## Task States

```text
pending → ready → assigned → in_progress → validating → completed
                              ↘ blocked
                              ↘ failed
                              ↘ cancelled

failed → ready   (explicit retry re-arm only)
```

Phase 6 adds `assigned` (executor bound) and `validating` (gates evaluating agent outputs).
See [TASK-MODEL.md](TASK-MODEL.md) and `agents/task_states.py`.

Agent success maps to task `validating`, **not** `completed`. Completion requires gate evidence.

---

## Agent States (Phase 6)

Separate object from Task/Project/Gate — see [AGENT-MODEL.md](AGENT-MODEL.md).

```text
created → ready → running ⇄ waiting
                 ↘ blocked → escalated
                 ↘ succeeded | failed | cancelled
```

| Coupling rule | Meaning |
|---|---|
| Agent `succeeded` | Task may enter `validating` — never auto-`completed` |
| Agent `failed` | Task `failed` (then retry/replan/escalate via Failure Model) |
| Agent `escalated` | Task `blocked` + human escalation |

Runtime: `agents/lifecycle.py`, `agents/task_states.py`.

---

## Artifact States

```text
planned → drafting → ready_for_review → approved
                                      ↘ rejected
                         approved → superseded
```

See [ARTIFACT-MODEL.md](ARTIFACT-MODEL.md).

---

## Gate States (result)

```text
pending → passed | failed | waived
```

See [VALIDATION-GATES.md](VALIDATION-GATES.md).

---

## Non-Mixing Rule

| Object | Owns |
|---|---|
| Project | Overall agency progress |
| Task | Unit of work |
| Artifact | Work product maturity |
| Gate | Advancement permission |

Forbidden: encoding gate failure only as project `failed` without a gate result; encoding missing Capability as task `completed`.

---

## Transitions That Require Evidence

- Project `validating` → `completed` requires required gates `passed` or explicitly `waived` with recorded reason.
- Task `in_progress` → `completed` requires declared output artifacts in acceptable state **or** explicit exception recorded as evidence.
- Gate `pending` → `passed` requires listed evidence objects, not “looks correct”.
