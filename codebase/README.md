# Codebase package

Phase 5 **Codebase Intelligence** — observe repositories as structured, evidential snapshots.

Not a Capability. Not an Orchestrator. Not a Cursor adapter.

See [foundation/CODEBASE-INTELLIGENCE.md](../foundation/CODEBASE-INTELLIGENCE.md) and [SPEC.md](SPEC.md).

## CLI

```bash
PYTHONPATH=. python3 -m codebase.cli analyze ./path/to/repo
PYTHONPATH=. python3 -m codebase.cli analyze ./path/to/repo --format json
PYTHONPATH=. python3 -m codebase.cli analyze ./path/to/repo --format both --out analysis.json
```

## Pipeline

```text
repository → snapshot → filesystem index → parsers → symbols → dependencies
→ tests → configuration → architecture signals → findings → evidence
```

Epistemic tags: `observed` | `inferred` | `unknown`.
