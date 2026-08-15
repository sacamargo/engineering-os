# Phase 6 Self-Refutation

| Attack | Verdict | Mitigation |
|---|---|---|
| God Agent | **Held** | `validate_not_god`; analysis vs coding permission split |
| God Tool / arbitrary shell | **Held** | Allowlist + no `shell=True`; injection tokens rejected |
| God Orchestrator | **Held** | Facade delegates to `agents.loop`; does not own tools |
| Permission bypass | **Held** | Tool auth + agent authorized_tools check |
| Infinite retries | **Held** | `RetryPolicy.max_attempts` |
| Context explosion | **Held** | `max_context_bytes` + truncation flag |
| Workspace escape | **Held** | `Workspace.resolve` + traversal tests |
| Fake success / zero tests | **Fixed** | Gate rejects `Ran 0 tests` and requires runner OK |
| Hidden mutations | **Held** | ChangeSet + write_log + evidence |
| Concurrent writers | **Held** | One lock per workspace |
| Vendor lock-in / LLM required | **Held** | Deterministic agent + NullLLM boundary |
| Role/Agent confusion | **Held** | Explicit assignment; human executor distinct |
| No rollback | **Held** | `rollback_changeset` on failed attempts |
| Fake evidence (“done”) | **Held** | `task_may_complete` requires evidence objects |

## Serious fixes during Phase 6

1. unittest module-level functions produced exit 0 with 0 tests → false SUCCESS → gate hardened.
2. Titles containing “analyze” stole coding assignment → coding/bugfix precedence fixed.
3. Rivallium fixture tests converted to `unittest.TestCase`.
