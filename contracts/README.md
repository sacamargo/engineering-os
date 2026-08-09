# Contracts

Phase 1 contracts make Knowledge Architecture and Capability Model **enforceable**.

| Artifact | Role |
|---|---|
| [SPEC.md](SPEC.md) | Human-readable contract invariants |
| [unit.schema.json](unit.schema.json) | Machine-readable single-unit metadata shape |
| [validate.py](validate.py) | Executable catalog validator |
| `fixtures/` | Valid/invalid examples used by tests |
| `tests/` | Contract behavior tests |

## Validate

From the repository root:

```bash
python3 contracts/validate.py
python3 contracts/validate.py --root path/to/units
python3 -m unittest discover -s contracts/tests -v
```

With no module directories present, validation succeeds with zero units (progressive adoption).

## Design Intent

Contracts exist so a future Orchestrator can discover units by stable IDs, trust metadata for routing, and assemble relationship graphs without repository folklore.

They deliberately do **not** create Capabilities, playbooks, skills, or adapters.
