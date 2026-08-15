# Delivery Role Bindings (conceptual)

Role ≠ Agent ≠ Capability.

| Role | Delivery responsibility |
|---|---|
| QA / Test Engineer | test validation evidence |
| Security Engineer | security validation / blockers |
| Release Engineer | release candidate preparation |
| DevOps Engineer | pipeline / delivery coordination |
| SRE | operational readiness signals |
| Human Approver | high-risk / production approval |
| Electrical Engineer | physical power scopes (escalate — never auto) |
| Physical Security Specialist | access hardware scopes (escalate) |

Agents are executors that may be assigned tasks informed by these roles.
Do **not** spawn one agent per role.
