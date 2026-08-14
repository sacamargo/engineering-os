# Replanning Model

Defines when and how an Execution Plan may change after failure or new evidence.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Plans must adapt without erasing traceability. |
| Problem avoided | Silent rewrites of decisions/artifacts. |
| If absent | Either brittle plans or unaccountable mutation. |

---

## Flow

```text
Task failure (or material new evidence)
  ↓
Analyze cause
  ↓
Determine whether plan remains valid
  ↓
retry | modify task | create task | replan | escalate | abort
```

---

## Rules

1. Increment `plan.revision` on material plan changes.
2. Supersede artifacts/decisions explicitly (`superseded`), do not overwrite history in place when status was `accepted`/`approved`.
3. Record evidence linking old plan revision → cause → new revision.
4. Do not silently change accepted architectural decisions; open a new Decision or supersede with reason.
5. Replanning is not Knowledge editing. Catalog changes are separate.

---

## Validity Check

Plan remains valid if:

- Capability set still covers required intents (or gaps still accurately listed)
- Dependency graph still reflects reality
- Gates still match risk posture

Otherwise replan.
