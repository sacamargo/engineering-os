# Role Model

A **Role** is an execution specialization — the kind of expertise a task may require.

**Role ≠ Capability.**  
**Role ≠ Agent.**  
**Role ≠ Knowledge Unit.**

Users ask for outcomes. Engineering OS may compose roles internally. Users must not be forced to assemble specialist menus.

Sibling models: [Capability Model](CAPABILITY-MODEL.md), [Task Model](TASK-MODEL.md), [Agent Model](AGENT-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Tasks need specialization metadata without exploding Capabilities. |
| Problem avoided | “20 roles ⇒ 20 Capabilities ⇒ 20 agents”. |
| If absent | Hard to explain who/what expertise a task needs; temptation to encode roles as intents. |
| Why not Capability? | Capability is demand-side intent class; Role is supply-side specialization. |

---

## Decision: What a Role Is

| Option | Verdict |
|---|---|
| Capability | Rejected |
| Persona prompt | Rejected as architecture |
| Agent identity | Rejected (Agent is executor; see Agent Model) |
| Execution specialization metadata | **Accepted** |

A Role may be referenced by tasks, projects, and (later) agents. It does not own methodology.

---

## Initial Role Catalog (non-exhaustive)

Stable ids use `eos.role.<name>`.

### Core engineering roles

1. `eos.role.product-engineer`
2. `eos.role.product-manager`
3. `eos.role.requirements-engineer`
4. `eos.role.system-architect`
5. `eos.role.software-architect`
6. `eos.role.frontend-engineer`
7. `eos.role.backend-engineer`
8. `eos.role.fullstack-engineer`
9. `eos.role.database-engineer`
10. `eos.role.api-integration-engineer`
11. `eos.role.devops-engineer`
12. `eos.role.cloud-engineer`
13. `eos.role.infrastructure-engineer`
14. `eos.role.qa-test-engineer`
15. `eos.role.security-engineer`
16. `eos.role.performance-engineer`
17. `eos.role.sre-reliability-engineer`
18. `eos.role.observability-engineer`
19. `eos.role.ai-engineer`
20. `eos.role.legacy-migration-engineer`

### Additional evaluated roles

21. `eos.role.technical-lead`
22. `eos.role.engineering-manager`
23. `eos.role.release-engineer`
24. `eos.role.incident-responder`

These are **catalog labels for specialization**, not mandatory permanent agents.

### External / professional specializations

Roles may also denote human professional lanes (example: electrical engineer) for escalation — without inventing Engineering OS Capabilities for regulated practice.

---

## Minimal Role Fields

| Field | Purpose |
|---|---|
| `id` | Stable role id |
| `title` | Human name |
| `summary` | What specialization this covers |
| `non_goals` | What it is not |
| `related_capability_ids` | Optional hints (not ownership) |

---

## Composition Rules

1. A Project/Task may list multiple roles.
2. Multiple roles may support one Capability.
3. One role may support many Capabilities over time.
4. Absence of a role in a fixture does not forbid work; progressive adoption applies.
5. Never require users to name roles to start.

---

## Anti-Patterns

- Creating a Capability per role
- Creating a permanent Agent per role by default
- Using role lists as the product navigation surface
- Hiding methodology inside role descriptions instead of Knowledge Units
