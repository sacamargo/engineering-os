# Agent Model (Boundary)

Defines what an **Agent** is — and what it is not.

**Do not create 20 rigid agents because ~20 roles exist.**

---

## Distinctions

| Concept | Meaning |
|---|---|
| Role | Specialization metadata |
| Capability | Intent class |
| Agent | Executor that performs work |
| Knowledge Unit | Reusable method/knowledge |
| Task | Unit of work |

```text
Role = specialization
Capability = intention
Agent = executor
Knowledge = knowledge
Task = work
```

---

## Rules

1. An Agent may use multiple Knowledge Units.
2. An Agent may execute multiple Tasks.
3. Agent ≠ Role. Multiple agents might serve one role label; one agent might cover several roles temporarily.
4. Agent ≠ Capability.
5. Prefer few flexible executors + role routing metadata over a zoo of fixed personas.
6. Phase 3 defines the boundary; runtime agents land in later phases.

---

## Earn-Its-Place

Without Agent as a distinct concept, Roles get mistaken for runnable personas and Capabilities get mistaken for bots.
