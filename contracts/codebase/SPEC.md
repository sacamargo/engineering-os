# Codebase Intelligence Contracts

Validate structured analysis outputs produced by `codebase/`.

Authority: [foundation/CODEBASE-INTELLIGENCE.md](../foundation/CODEBASE-INTELLIGENCE.md)

## Objects

| Object | ID pattern | Required |
|---|---|---|
| Snapshot | `eos.snapshot.<hex>` | meta, epistemic unknowns allowed |
| Finding | `eos.finding.<kind>.<digits>` | evidence non-empty, confidence in {observed,inferred,unknown} |
| Evidence | `eos.evidence.*` | pointer non-empty |
| Dependency | `eos.dep.*` | source_path, target, kind, certainty |
| Symbol | `eos.symbol.<hex>` | path, name, kind, line_start |

## Invariants

1. Findings without evidence are invalid.
2. Symbols without location (path + line) are invalid.
3. Snapshot without meta.root is invalid.
4. Dependency kind must be `import` | `package` | `inferred_runtime`.
5. Certainty/confidence must be `observed` | `inferred` | `unknown`.
6. Coverage value `0` / `0%` without measured evidence is invalid (must be `unknown` or measured artifact).
7. `analysis_status` if present ∈ `not_run` | `deferred` | `complete` | `failed`.

## Validator

```bash
python3 contracts/validate_codebase.py path/to/analysis.json
python3 contracts/validate_codebase.py --self-check
```
