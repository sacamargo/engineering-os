# Dependency Model

This document distinguishes **knowledge relationships** from **execution dependencies**.

Sibling models: [Knowledge Architecture](KNOWLEDGE-ARCHITECTURE.md), [Task Model](TASK-MODEL.md), [Artifact Model](ARTIFACT-MODEL.md), [Execution Model](EXECUTION-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Teams conflate “related knowledge” with “must run after”. |
| Problem avoided | Capability/knowledge DAGs pretending to be schedulers. |
| If absent | False ordering, blocked parallelism, brittle orchestration. |
| Why not reuse `depends_on` on Knowledge Units? | KU `depends_on` means methodological prerequisite for understanding/composition — not project scheduling. |

---

## Two Graphs

### Knowledge relationship graph

Owned by Knowledge Architecture / Contracts.

Examples:

- `references`
- `composes`
- `related_capability`
- KU `depends_on` / `composes` (method completeness)

Meaning: how knowledge connects for retrieval and authorship.

### Execution dependency graph

Owned by the Execution Layer.

Examples:

- Task B `depends_on` Task A
- Task C requires Artifact X approved
- Gate Y requires Artifacts {X,Z}

Meaning: what must be true before work may start or progress may continue.

---

## Critical Example

```text
Architecture Knowledge Unit references Security Playbook
```

does **NOT** mean:

```text
Security tasks must execute after Architecture tasks
```

While:

```text
Task: Implement Booking Core
depends_on_artifacts: [Database Schema]
```

**does** mean execution cannot honestly start without that artifact in an acceptable state.

---

## Allowed Execution Dependency Kinds

| Kind | From → To | Meaning |
|---|---|---|
| `task_depends_on_task` | Task → Task | Predecessor must complete |
| `task_requires_artifact` | Task → Artifact | Input must be acceptable |
| `gate_requires_artifact` | Gate → Artifact | Evidence for gate |
| `gate_requires_task` | Gate → Task | Required work completed |
| `milestone_requires_gate` | Milestone → Gate | Phase exit condition |

Do not invent deep cross-Capability call stacks.

---

## Cycle Policy

- Execution dependency cycles among tasks are **forbidden**.
- Soft knowledge adjacency cycles that are not execution edges are a separate concern.
- If a cycle is detected in execution dependencies, the plan is invalid until broken.

---

## Parallelism

Absence of an execution dependency means work **may** proceed in parallel, subject to resource/role constraints (outside this minimal model).

---

## Anti-Patterns

- Encoding task order inside Capability relationships
- Using `related_capability` as a scheduler
- Creating dependencies “for neatness” without semantic need
- Hiding dependencies only in prose
