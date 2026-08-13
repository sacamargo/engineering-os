# Role ↔ Capability Binding

This document defines how Capabilities relate to Roles without collapsing them.

Authorities:

- [Capability Model](CAPABILITY-MODEL.md) — intent classes
- [Role Model](ROLE-MODEL.md) — specializations
- [Task Model](TASK-MODEL.md) — where bindings usually apply

---

## Rule

```text
Capability = intent class (WHAT kind of help is offered)
Role       = specialization needed to execute work (WHO/WHAT expertise)
```

Bindings are **hints for planning**, not ownership of methodology.

---

## Binding Shape

```text
capability_id → role_ids[]
```

Optional reverse index for discovery:

```text
role_id → capability_ids[]
```

Neither direction creates an execution DAG.

---

## Initial Bindings (landed Capabilities)

| Capability | Typical roles |
|---|---|
| `eos.capability.design.system-architecture` | `eos.role.system-architect`, `eos.role.software-architect`, `eos.role.technical-lead` |
| `eos.capability.security.review` | `eos.role.security-engineer`, `eos.role.technical-lead` |
| `eos.capability.quality.test-planning` | `eos.role.qa-test-engineer`, `eos.role.technical-lead` |
| `eos.capability.operations.observability` | `eos.role.observability-engineer`, `eos.role.sre-reliability-engineer` |

These bindings are defaults for plan generation. Projects may add/omit roles with rationale.

---

## Future Capability Examples (not landed)

| Future intent class | Typical roles |
|---|---|
| Database design/selection | `eos.role.database-engineer` |
| Backend implementation | `eos.role.backend-engineer` |
| Frontend implementation | `eos.role.frontend-engineer` |
| Deployment/delivery | `eos.role.devops-engineer`, `eos.role.release-engineer` |
| Performance optimization | `eos.role.performance-engineer` |
| Incident investigation | `eos.role.incident-responder`, `eos.role.sre-reliability-engineer` |

Do **not** create those Capabilities solely to host roles.

---

## Task-Level Application

When generating tasks from a Capability:

1. Attach relevant `capability_ids`
2. Attach default `role_ids` from this binding table
3. Override when context demands (e.g., fullstack instead of split FE/BE)

---

## Anti-Patterns

- Treating binding as proof that a Capability “is” a role
- Requiring users to select roles
- Creating one Agent permanently per bound role
- Using bindings as hard execution dependencies between Capabilities
