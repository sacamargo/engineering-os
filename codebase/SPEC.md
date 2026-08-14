# Codebase Intelligence SPEC

## Pipeline

```text
repository
→ snapshot
→ filesystem index
→ language parsers
→ symbols
→ dependencies
→ tests
→ configuration
→ architecture signals
→ findings
→ evidence
```

## Epistemic tags

Every non-trivial field should carry `certainty`: `observed` | `inferred` | `unknown`.

## Invariants

1. Observation ≠ interpretation ≠ decision
2. Findings require evidence pointers
3. Coverage unknown ≠ 0%
4. Core ≠ Adapter (no Cursor APIs)
5. Parser plugins are replaceable
6. Secrets / `.env` real files are excluded by boundary policy
