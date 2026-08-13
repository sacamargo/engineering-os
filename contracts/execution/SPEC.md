# Execution Contracts

Machine-readable contracts for Execution Layer objects.

Architectural authority remains in Foundation:

- PROJECT-MODEL, TASK-MODEL, ARTIFACT-MODEL
- EXECUTION-PLAN, VALIDATION-GATES
- DECISION-MODEL, ROLE-MODEL, ROLE-CAPABILITY-BINDING
- DEPENDENCY-MODEL, EVIDENCE-MODEL, HUMAN-ESCALATION

These contracts formalize **encoding and structural invariants**. They do not redefine knowledge unit contracts in `contracts/SPEC.md`.

---

## Scope

In scope:

- Project, Task, Artifact, Execution Plan, Gate, Decision, Role binding records
- ID formats
- Required fields
- Status enums
- Reference integrity across an execution bundle
- Execution dependency cycle detection

Out of scope:

- Runtime orchestrator behavior
- Knowledge Unit validation (see parent `contracts/SPEC.md`)
- Vendor adapters

---

## On-Disk Encoding

Execution fixtures use JSON for reliable stdlib parsing:

```text
examples/<project>/project.json
examples/<project>/plan.json
examples/<project>/artifacts/*.json
examples/<project>/tasks/*.json
examples/<project>/gates/*.json
examples/<project>/decisions/*.json
examples/<project>/roles/*.json   # optional explicit role records
```

Markdown narrative files may accompany fixtures but are not the machine contract.

---

## ID Patterns

| Object | Pattern |
|---|---|
| Project | `^eos\.project\.[a-z][a-z0-9-]*$` |
| Task | `^eos\.task\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |
| Artifact | `^eos\.artifact\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |
| Plan | `^eos\.plan\.[a-z][a-z0-9-]*$` |
| Gate | `^eos\.gate\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |
| Decision | `^eos\.decision\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |
| Role | `^eos\.role\.[a-z][a-z0-9-]*$` |
| Evidence | `^eos\.evidence\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |
| Escalation | `^eos\.escalation\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$` |

Capability IDs referenced from execution objects must match existing knowledge catalog IDs when validated together.

---

## Status Enums

### Project

`discovered|planned|ready|executing|blocked|validating|completed|failed|cancelled`

### Task

`pending|ready|in_progress|blocked|completed|failed|cancelled`

### Artifact

`planned|drafting|ready_for_review|approved|superseded|rejected`

### Gate

`pending|passed|failed|waived`

### Decision

`proposed|accepted|superseded|rejected`

---

## Bundle Integrity Rules

When validating a project bundle:

1. No duplicate IDs across the bundle
2. Task `project_id` matches project
3. Task input/output artifact ids exist
4. Task dependency task ids exist
5. Gate required artifacts/tasks exist
6. Plan references exist
7. Capability ids referenced should exist in knowledge catalog when available
8. Role ids should match `eos.role.*` pattern
9. Execution task dependency graph must be acyclic
10. Invented capability-shaped ids are rejected

---

## Schemas

JSON Schema mirrors (documentation + tooling):

- `schemas/project.schema.json`
- `schemas/task.schema.json`
- `schemas/artifact.schema.json`
- `schemas/plan.schema.json`
- `schemas/gate.schema.json`
- `schemas/decision.schema.json`
- `schemas/role-binding.schema.json`

Executable validation: `contracts/validate_execution.py` (Task 17).
