# Agent Model

Defines what an **Agent** is — Definition vs Runtime — and what it is not.

**Do not create 20 rigid agents because ~20 roles exist.**

Authorities: [TASK-MODEL](TASK-MODEL.md), [EXECUTION-STATE-MACHINE](EXECUTION-STATE-MACHINE.md), [FAILURE-MODEL](FAILURE-MODEL.md), Phase 6 audit [`docs/PHASE-6-EXECUTION-AUDIT.md`](../docs/PHASE-6-EXECUTION-AUDIT.md).

Runtime package: `agents/`.

---

## Distinctions

| Concept | Meaning |
|---|---|
| Role | Specialization / responsibility metadata |
| Capability | Intent class |
| Agent | Executor that performs Tasks with authorized Tools |
| Knowledge Unit | Reusable method/knowledge |
| Task | Unit of work |
| Tool | Concrete operational action (read/write/execute) |
| Evidence | Inspectable support for claims |
| Artifact | Work product |

```text
Role = specialization
Capability = intention
Agent = executor
Tool = operational action
Knowledge = knowledge
Task = work
Evidence ≠ Artifact
```

**Role ≠ Agent.** A Role may be fulfilled by human, AI agent, or external specialist.

**Capability ≠ Agent.** Capabilities route intent; Agents execute tasks.

---

## Agent Definition vs Runtime Instance

| | Agent Definition | Agent Runtime Instance |
|---|---|---|
| Example | `coding-agent` | `coding-agent-run-123` |
| Lifetime | Catalog / config | One execution attempt / run |
| Contains | type, allowed tools, permissions, limits, risk ceiling | state, current task, context, evidence produced, metrics |

### Definition (minimum fields)

| Field | Purpose |
|---|---|
| `id` | Stable definition id (`eos.agent.<name>`) |
| `type` | `coding` \| `analysis` \| `human` \| `mock` \| … |
| `operational_capabilities` | What classes of work it may attempt (not Capability catalog IDs required) |
| `authorized_tools` | Tool ids allowed |
| `permissions` | READ / WRITE / EXECUTE / … (deny by default) |
| `limits` | timeout, max tool calls, max retries, max files modified |
| `risk_ceiling` | Max tool risk without extra gate |
| `notes` | Constraints |

### Runtime Instance (minimum fields)

| Field | Purpose |
|---|---|
| `id` | Run id (`eos.agent.run.<hex>`) |
| `definition_id` | Points to definition |
| `status` | Lifecycle state |
| `task_id` | Current task |
| `context_ref` | Built context id / pointer |
| `permissions` | Effective permissions (≤ definition) |
| `timeout_seconds` | Effective timeout |
| `evidence_ids` | Evidence produced this run |
| `tool_call_count` | Observability |
| `started_at` / `ended_at` | Timestamps |

---

## Lifecycle (summary)

```text
created → ready → running ⇄ waiting
                 ↘ blocked → escalated
                 ↘ succeeded | failed | cancelled
```

See [EXECUTION-STATE-MACHINE.md](EXECUTION-STATE-MACHINE.md) and `agents/lifecycle.py`.

---

## Rules

1. An Agent may use multiple Knowledge Units.
2. An Agent may execute multiple Tasks across runs — one task at a time per instance.
3. Agent ≠ Role. Prefer few flexible executors + role routing metadata.
4. Agent ≠ Capability.
5. Agent ≠ Orchestrator. Orchestrator assigns; Agent executes.
6. No god agent: not all tools, not all permissions, not unlimited risk.
7. Success without Evidence is forbidden.
8. LLM providers are optional adapters behind a boundary — never core-required.

---

## Earn-Its-Place

Without Agent as a distinct concept, Roles get mistaken for runnable personas and Capabilities get mistaken for bots.
Without Definition vs Instance, permissions and audit trails cannot be bound to a concrete run.
