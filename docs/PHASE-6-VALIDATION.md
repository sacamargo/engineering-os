# Phase 6 Validation Evidence

## Objective

Demonstrate the first **real** Agent Execution loop:

```text
Task → Agent → Tools → Repository → Change → Tests → Evidence → Gate → Continue/Replan/Escalate
```

**Not Phase 7:** no CI/CD autonomy, deploy, swarm, mandatory LLM, or production control plane.

## Architecture

Package: `agents/` (runtime). Orchestrator assigns; Agents execute. Codebase Intelligence feeds context.

```text
Capability ≠ Role ≠ Agent ≠ Task ≠ Tool ≠ Knowledge ≠ Evidence ≠ Artifact
```

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s agents/tests -v
PYTHONPATH=. python3 -m unittest discover -s orchestration/tests -v
PYTHONPATH=. python3 -m unittest discover -s codebase/tests -v
PYTHONPATH=. python3 -m unittest discover -s contracts/tests -v
python3 contracts/validate.py
python3 contracts/validate_execution.py
PYTHONPATH=. python3 contracts/validate_codebase.py --self-check
```

## Results (closeout)

All of the above must pass on `main` at Phase 6 completion.

## Delivered capabilities

| Area | Status |
|---|---|
| Agent Definition vs Instance | Done |
| Lifecycle + task state coupling | Done |
| Tools + permissions + risk | Done |
| Sandbox + allowlisted commands | Done |
| Execution loop + evidence gates | Done |
| Retry / rollback / dry-run | Done |
| Human executor / approval hooks | Done |
| Deterministic coding agent (no LLM) | Done |
| Agency scenarios (Rivallium/legacy/Padel/bugfix) | Done |
| Security (traversal, env write, injection) | Done |

## Limitations

- Deterministic plans required unless a future LLM adapter is bound
- No multi-agent swarm / parallel writers
- No git push / deploy tools
- unittest must use TestCase classes (zero-test runs rejected)
- Command allowlist is small by design

## Unknowns

- LLM-assisted planning quality
- 100+ concurrent agents
- Large monorepo write contention beyond one-writer lock

## Next step

**Stop.** Review before Phase 7 (Delivery / CI/CD).
