# Orchestration Package

Phase 4 **Planning Orchestrator** — converts high-level engineering intent into a structured Execution Plan.

This package coordinates. It does **not** contain engineering methodology, invent Capabilities, call Cursor APIs, or execute product code.

See [SPEC.md](SPEC.md) and [docs/PHASE-4-ORCHESTRATION-AUDIT.md](../docs/PHASE-4-ORCHESTRATION-AUDIT.md).

## Demo

```bash
PYTHONPATH=. python3 -m orchestration.cli "Build a booking SaaS that is secure, testable, and observable."
PYTHONPATH=. python3 -m orchestration.cli --json "Audita este sistema por vulnerabilidades."
PYTHONPATH=. python3 -m unittest discover -s orchestration/tests -v
```

## Design rule

Thin facade + focused modules. Adding a Capability must not require editing a giant switch in the facade.
