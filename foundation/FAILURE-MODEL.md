# Failure Model

Defines how Engineering OS classifies and responds to execution failures.

**Not every failure is a retry.**

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Agency needs disciplined recovery choices. |
| Problem avoided | Blind retries that amplify damage or hide root cause. |
| If absent | Failures become chat noise; plans silently rot. |

---

## Failure Classes

| Class | Example | Default response |
|---|---|---|
| Task failure | Implementation task errors | analyze → retry / modify / replan |
| Validation failure | Gate evidence missing/failed | block dependents; fix evidence |
| Missing knowledge | No unit for needed method | gap + human/catalog work |
| Missing capability | Intent outside catalog | `insufficient_coverage`; do not invent |
| Dependency failure | Upstream task failed | block; reassess graph |
| Human rejection | Approver rejects decision/gate | replan or abort path |
| External service failure | CI/cloud/API outage | retry with backoff **or** escalate |

---

## Response Actions

| Action | When |
|---|---|
| `retry` | Transient external/infrastructure fault; same plan still valid |
| `replan` | Assumptions broken; task graph or artifacts must change |
| `escalate` | Professional / policy / destructive production boundary |
| `block` | Wait on dependency, evidence, or human |
| `abort` | Objective unsafe/impossible under constraints |

---

## Decision Rule

```text
Failure
  → classify
  → is plan still valid?
      yes → retry or block
      no  → replan (explicit) or abort
  → does domain require human?
      yes → escalate (do not autonomous-execute)
```

Silent mutation of accepted decisions is forbidden. See [REPLANNING-MODEL.md](REPLANNING-MODEL.md).
