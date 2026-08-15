# Phase 6 Execution Audit

Audit of what already exists before implementing Agent Execution Runtime.

**Rule:** Do not create a parallel Task/Evidence/Gate/Failure/Replan model. Reuse and extend.

---

## What exists (reuse)

| Area | Location | Status |
|---|---|---|
| Task model + states | `foundation/TASK-MODEL.md`, contracts | Sufficient — extend with `assigned`/`validating` only if needed as transitions notes |
| Artifact model | `foundation/ARTIFACT-MODEL.md` | Reuse |
| Evidence model | `foundation/EVIDENCE-MODEL.md`, `orchestration/evidence/` | Reuse; agents produce evidence records |
| Gates | `foundation/VALIDATION-GATES.md`, `orchestration/gates/` | Reuse; agents cannot bypass |
| Failure classification + actions | `foundation/FAILURE-MODEL.md`, `orchestration/failure/` | **Extend** classes for tool/permission/timeout |
| Replanning | `foundation/REPLANNING-MODEL.md`, `orchestration/replan/` | Reuse |
| Change impact | `foundation/CHANGE-IMPACT-MODEL.md`, `codebase/impact.py` | Reuse for pre-write consultation |
| Execution state machines | `foundation/EXECUTION-STATE-MACHINE.md` | **Extend** with Agent lifecycle (separate object) |
| Agent boundary (conceptual) | `foundation/AGENT-MODEL.md` | **Extend** — definition vs runtime |
| Agent assignment hints | `orchestration/boundaries/agent.py` | **Extend** — wire to real runtime |
| Role ≠ Agent | `orchestration/role/`, ROLE-MODEL | Preserve; `executor_hint` already exists |
| Human escalation | `orchestration/escalation/` | Reuse for professional scopes |
| Codebase Intelligence | `codebase/` | Feed context building; not an Agent |
| Planning Orchestrator | `orchestration/facade/` | Coordinates plans; must not become god executor |
| Delivery / Adapter | boundary docs only | Out of scope (Phase 7+) |

---

## What is missing (new in Phase 6)

| Gap | Planned home |
|---|---|
| Agent Definition vs Runtime Instance | `agents/` + extend AGENT-MODEL |
| Agent lifecycle state machine | `agents/lifecycle.py` |
| Tool model + permissions + risk | `agents/tools/` |
| Local tool runtime + sandbox | `agents/runtime/` |
| Controlled command allowlist | `agents/tools/commands.py` |
| File write control + ChangeSet | `agents/changeset.py` |
| Execution log / audit trail | `agents/log.py` |
| Execution loop (assign→execute→validate→gate) | `agents/loop.py` |
| Retry policy (max attempts, backoff) | `agents/retry.py` |
| Context builder + size bounds | `agents/context.py` |
| Dry-run mode | `agents/dry_run.py` |
| Deterministic coding agent (no LLM required) | `agents/coding.py` |
| Workspace rollback | `agents/rollback.py` |
| Human approval protocol | `agents/approval.py` |
| ExecutionResult JSON + human report | `agents/report.py` |
| LLM boundary (interface only) | `agents/llm_boundary.py` |
| Concurrency: one writer per workspace | `agents/concurrency.py` |

---

## What will be extended (not duplicated)

1. **AGENT-MODEL.md** — definition vs instance, tools, limits, lifecycle.
2. **EXECUTION-STATE-MACHINE.md** — Agent states; task transitions `ready→in_progress→validating→completed`.
3. **FAILURE-MODEL.md** / `orchestration/failure` — TOOL_FAILURE, PERMISSION_FAILURE, TIMEOUT, ENVIRONMENT_FAILURE, HUMAN_BLOCKED.
4. **orchestration/boundaries/agent.py** — suggest real agent definitions; still Role ≠ Agent.
5. **PROJECT-ROADMAP.md** — Phase 6 checklist (at closeout).

---

## Distinctions that must remain hard

```text
Capability ≠ Role ≠ Agent ≠ Task ≠ Tool ≠ Knowledge ≠ Evidence ≠ Artifact
```

- Orchestrator coordinates; Agents execute.
- Codebase Intelligence observes; Agents mutate only via authorized Tools.
- “done” is never Evidence.

---

## Non-goals confirmed

No swarm, no deploy, no CI/CD autonomy, no mandatory LLM/vendor, no unrestricted shell, no Phase 7.

---

## Implementation package

New runtime package: **`agents/`** (not inside Orchestrator).

Orchestrator may call `agents.loop.run_execution(...)` but must not own tools/sandbox.
