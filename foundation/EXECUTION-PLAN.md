# Execution Plan

An **Execution Plan** is the project-specific coordination object that connects Capabilities to artifacts, tasks, dependencies, and gates.

It is derived from Intent Resolution + context. It is not a Knowledge Unit and not a universal template.

Authorities: [Execution Model](EXECUTION-MODEL.md), [Project Model](PROJECT-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Multi-capability work needs one inspectable plan object. |
| Problem avoided | Ad-hoc chat sequences with no blockers, parallelism, or replan trace. |
| If absent | Cannot show order, gates, or progress across sessions. |
| Why not Playbook? | Playbooks teach methods; plans schedule situational work. |

---

## Shape

```text
Project
  ↓
Capabilities (resolved)
  ↓
Artifacts (required/produced)
  ↓
Tasks
  ↓
Dependencies (execution)
  ↓
Validation Gates
```

---

## Minimal Fields

| Field | Purpose |
|---|---|
| `id` | Plan id |
| `project_id` | Owning project |
| `intent_summary` | Framed intent |
| `capability_ids` | Selected Capabilities |
| `insufficient_coverage` | Gaps |
| `milestones` | Optional phase groups |
| `artifact_ids` | Plan artifacts |
| `task_ids` | Plan tasks |
| `dependencies` | Execution dependency list |
| `gate_ids` | Gates |
| `status` | Plan lifecycle |
| `revision` | Monotonic plan revision for replans |

---

## Supported Dynamics

The plan model must allow representing:

- parallel tasks (no mutual dependency)
- sequential tasks (explicit dependency)
- blocked tasks (unmet dependency or escalation)
- failed tasks
- retries (new attempt / revised task, with trace)
- validation gate outcomes
- plan changes (new revision; prior revision retained as evidence)

---

## Invariants

1. Plans must not invent Capability IDs.
2. Knowledge relationships are not copied in as execution dependencies by default.
3. A plan may be partial when coverage is incomplete; gaps must be explicit.
4. Replanning increments `revision` and preserves decision/evidence links.

---

## Non-Goals

- Runtime orchestrator implementation
- Automatic optimal scheduling solver
- Vendor workflow encoding (Jira/Linear schemas)
