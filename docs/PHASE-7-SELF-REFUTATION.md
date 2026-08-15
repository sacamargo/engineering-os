# Phase 7 Self-Refutation

| Attack | Verdict | Mitigation |
|---|---|---|
| Fake success / NOT_RUN as pass | **Held** | Gate treats NOT_RUN/zero tests as failure |
| Gate bypass → released | **Held** | State machine forbids validating→released; gates required |
| Release without artifact digest | **Held** | Artifact gate + contracts |
| Unknown security → release | **Held** | security_unknown blocks |
| Agent self-approval | **Fixed** | Reject `approver` starting with `agent:` |
| Analysis profile escalate to release | **Held** | Permission deny |
| Real deploy via core | **Held** | Null adapter UNSUPPORTED |
| Path escape on artifacts | **Held** | Workspace sandbox for artifact writes |
| Concurrent corruption | **Held** | workspace_lock reused |

## Serious fix during Phase 7

Production path with `approval_granted=True` and `approver=agent:*` previously reached READY_FOR_DEPLOYMENT — corrected to NEEDS_HUMAN.
