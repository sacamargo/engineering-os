# Phase 5 Self-Refutation

Attempt to break Codebase Intelligence before calling Phase 5 complete.

| Attack | Verdict | Notes / fix |
|---|---|---|
| Model too generic? | **Held with care** | Concepts earn place via consumers (impact, findings, orchestrator). No decorative entities. |
| Too AST-dependent? | **Partially held** | Python uses AST; JS/TS is lite; FS/config/git work without AST. Core not coupled to one parser. |
| Monoliths? | **Plausible** | Path/module graphs work; layer heuristics weak but labeled inferred. |
| Monorepos? | **Partial** | Inventory works; no first-class package graph across workspaces yet → unknown. |
| Microservices? | **Partial** | Multiple entry signals possible; no service boundary model → unknown. |
| Polyglot? | **Partial** | Python + JS/TS lite only; other languages inventory-only. |
| Infrastructure? | **Held** | Dockerfile/compose detected; physical scopes escalate (Padel). |
| Frontend? | **Partial** | JS module + package.json observed; framework semantics thin. |
| Legacy? | **Held** | legacy-chaos fixture surfaces cycles, eval, secrets, missing tests. |
| Enormous repos? | **Unproven** | Metrics exist; no 100k-file measurement. |
| Evidence vs inference? | **Held** | Mandatory certainty tags + contract rejects findings without evidence. |
| Feed Orchestration without coupling? | **Held** | Boundary adapter + `codebase_analysis` task; CI ≠ Capability. |
| God object? | **Held** | Pipeline modules stay separate; facade only coordinates. Fixed relative parse paths when impact broke. |

## Serious issues found and corrected during Phase 5

1. Parse results used absolute paths → dependency/impact graphs failed → normalized to repo-relative paths in symbol index.
2. Impact resolver seeded only edge sources → missed module targets → seed with module path set.
3. Security agency utterance missed audit intent → expanded `seguridad`/`security` phrases.

## Residual risks

- Heuristic architecture/security/performance over-trust by humans
- Incomplete gitignore semantics
- No claim of semantic refactor safety
