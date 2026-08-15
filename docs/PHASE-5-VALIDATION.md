# Phase 5 Validation Evidence

## Objective

Build the first real **Codebase Intelligence** implementation: observe a repository as a structured, evidential, epistemic snapshot that Orchestration can require before blind change plans.

**Not Phase 6:** no agent fleet, no autonomous code mutation, no CI/CD autonomy, no mandatory LLM.

## Architecture

```text
repository
→ git provenance
→ filesystem index (boundary + gitignore best-effort)
→ language parsers (extensible; Python AST + JS/TS lite)
→ symbols / modules
→ dependency graph (import/package; no fake runtime deps)
→ tests / configuration
→ architecture signals
→ findings + security/performance heuristics
→ evidence records
→ human report + JSON (eos.codebase.analysis.v1)
→ Orchestrator: codebase_analysis task + readiness gating
```

Authorities: `foundation/CODEBASE-INTELLIGENCE.md`, `foundation/CODEBASE-BOUNDARY.md`, `codebase/SPEC.md`, `contracts/codebase/SPEC.md`.

**Codebase Intelligence ≠ Capability ≠ Orchestrator.**

## Tasks completed (Phase 5)

Conceptual model, snapshot, FS index, parser abstraction, symbols, dependencies, tests, configuration, architecture signals, findings, evidence, change impact, analyze pipeline, human report, JSON, orchestration + readiness integration, Rivallium/Padel/legacy fixtures, security/performance signals, uncertainty, incremental diff, git intel, boundary policy, indexer metrics, contracts/validators, tests, agency scenarios, self-refutation, scale notes, documentation.

## Key decisions

| Decision | Why |
|---|---|
| Epistemic tags mandatory | Prevent invented architecture |
| Coverage defaults to `unknown` | Never emit fake `0%` |
| CI is not a Capability | Evidence infrastructure for Execution |
| Deferred inspect + explicit analysis task | Avoid coupling every plan() to full index |
| Relative parse paths | Fix dependency/impact graph resolution |
| Fake secrets only in fixtures | Demonstrate boundary without exfiltration |

## Commands

```bash
PYTHONPATH=. python3 -m unittest discover -s codebase/tests -v
PYTHONPATH=. python3 -m unittest discover -s orchestration/tests -v
PYTHONPATH=. python3 -m unittest discover -s contracts/tests -v
python3 contracts/validate.py
python3 contracts/validate_execution.py
python3 contracts/validate_codebase.py --self-check
PYTHONPATH=. python3 -m codebase.cli analyze codebase/fixtures/rivallium-mini --format human
PYTHONPATH=. python3 -m codebase.scenarios.agency
```

## Results

Recorded at Phase 5 closeout (see final validation commit notes). Expected:

| Check | Result |
|---|---|
| Codebase unit/integration/fixture tests | OK |
| Orchestration + CI integration tests | OK |
| Contract validators (knowledge/execution/codebase) | OK |
| Agency scenarios (6) | OK — analysis tasks + readiness gating |
| Rivallium mini real analyze | structure/deps/tests/config/signals/findings/evidence |
| Padel IoT mini | infra detected; physical/electrical escalate via Orchestrator |
| Legacy chaos | describes cycles/secrets/eval; does not pretend order |

## Limitations

- gitignore matcher is best-effort, not full git semantics
- JS/TS parser is regex-lite, not a full AST
- Architecture signals are heuristics, never authoritative architecture
- Impact analysis is import-graph reachability, not semantic/runtime certainty
- Security/performance detectors are static heuristics only
- Monorepos/microservices represented only as multi-path inventories (no service mesh model)
- Large-repo performance measured only on small fixtures + package trees

## Risks

- Users may treat inferred signals as facts
- Over-indexing secrets if boundary policy regresses
- Orchestrator god-object creep if analysis logic moves into facade
- Polyglot repos beyond Python/JS remain shallow

## Unknowns

- True runtime behavior, authz effectiveness, production performance
- Exact test coverage without measured reports
- Full historical git intelligence
- Whether incremental analysis stays cheap at 100k files

## Self-refutation

See [PHASE-5-SELF-REFUTATION.md](PHASE-5-SELF-REFUTATION.md).

## Scale

See [PHASE-5-SCALE.md](PHASE-5-SCALE.md).

## Next step

**Stop.** Do not start Phase 6 automatically. Review this evidence before deciding Agent Execution scope.
