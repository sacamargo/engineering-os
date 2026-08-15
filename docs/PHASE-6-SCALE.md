# Phase 6 Scale Notes

| Dimension | Proven | Plausible | Unknown |
|---|---|---|---|
| 1 agent, few tasks | Yes (tests/fixtures) | | |
| 10 serial tasks | | Yes with current loop | |
| 100–1000 tasks | | Scheduler needed | Not measured |
| 10 agents | Definitions exist | | No swarm runtime |
| 100 agents | | | Unknown; lock model may serialize writers |

Do **not** claim horizontal scalability. Phase 6 proves correctness of one sandboxed execution loop.
