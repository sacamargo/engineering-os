# Agency scenarios — Codebase Intelligence + Orchestration

Each scenario shows:

Intent → Capability candidates → Codebase Intelligence → Evidence → Plan → Readiness → Gaps → Escalation

Fixtures: `codebase/fixtures/rivallium-mini`, `padel-iot-mini`, `legacy-chaos`.

Run:

```bash
PYTHONPATH=. python3 -m codebase.scenarios.agency
```

| # | Utterance | Expectation |
|---|---|---|
| 1 | Analyze this repository | `codebase_analysis` task; analysis produces snapshot |
| 2 | Audit architecture | analysis required; architecture signals are inferred not asserted |
| 3 | Find security problems | security signals + findings with confidence labels |
| 4 | Refactor this module | no blind impl plan; readiness waits on evidence |
| 5 | Migrate this system | codebase_analysis before migrate work; unknowns listed |
| 6 | Investigate this bug | analysis + observability candidates; no invented root cause |
