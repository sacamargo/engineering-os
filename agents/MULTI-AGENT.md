# Multi-Agent Model (conceptual — no swarm runtime)

Phase 6 supports **multiple Agent Definitions**, not a multi-agent swarm.

## Intent

```text
Architect Agent   — analysis / design artifacts (read-heavy)
Security Agent    — review tools (read + gated writes to reports)
Coding Agent      — modify + test
Testing Agent     — run_tests focused
Human Executor    — professional / approval
```

## Rules

1. Do **not** spawn one agent per Role automatically.
2. Orchestrator assigns Task → compatible Definition (least privilege).
3. Parallelism is allowed only for non-conflicting read-only work; **one writer per workspace**.
4. No shared god agent with all tools/permissions.
5. Swarm orchestration, debate protocols, and autonomous fleets are **Phase 6+ deferred** (not implemented).

## Serial dependency

```text
Task A → Artifact → Gate → Task B
```

Task B cannot start until required artifacts/gates are satisfied (Execution Plan / task_states).
