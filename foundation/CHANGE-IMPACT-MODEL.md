# Change Impact Model

Defines how a material change propagates across Execution Layer objects.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Prevent local edits from silently invalidating dependent work. |
| Problem avoided | “Just change the schema” without test/security/deploy ripple. |
| If absent | Incomplete replans and false completion. |

---

## Impact Fan-out (example)

```text
Change database model
  ↓
API affected
  ↓
Backend affected
  ↓
Tests affected
  ↓
Migration required
  ↓
Deployment gate affected
```

---

## Impact Dimensions

| Dimension | What to reassess |
|---|---|
| Artifacts | Dependent artifacts may need draft/supersede |
| Tasks | New tasks, blocked tasks, retries |
| Capabilities | Coverage still sufficient? new gaps? |
| Tests | Strategy and evidence still valid? |
| Security | Threat model still accurate? |
| Deployment | Delivery/gates still safe? |

---

## Procedure

1. Identify changed object (artifact/decision/requirement).
2. Walk **execution** dependencies (not knowledge `related_to` alone).
3. Mark impacted tasks/artifacts/gates.
4. Decide: modify in place (only if not accepted) vs supersede vs new task.
5. Record evidence of impact analysis.
6. Replan if graph assumptions break.

Knowledge relationships may hint at impact but never substitute for execution dependency analysis.
