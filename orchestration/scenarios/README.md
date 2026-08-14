# Phase 4 Agency Scenarios

Behavioral scenarios exercised by `PlanningOrchestrator` (planning only).

Run:

```bash
PYTHONPATH=. python3 -m orchestration.cli "<utterance>"
PYTHONPATH=. python3 -m unittest orchestration.tests.test_planning_orchestrator -v
```

| ID | Intent | Expected |
|---|---|---|
| A | Build booking SaaS secure/testable/observable | Architecture primary; security/test/observability secondary; artifact deps; gaps for backend/db/fe/devops; clarifying payments |
| B | Padel court automation | Cross-domain gaps; HUMAN escalations for electrical/physical; partially_ready |
| C | Security audit | security.review primary |
| D | Refactor without breaking | architecture + test planning candidates; codebase boundary noted |
| E | Production 500 | observability candidate; production escalation |
| F | Electrical certification | MISSING_CAPABILITY; no invented IDs |
