# Phase 3 Validation Evidence

Captured on closing validation pass.

## Commands

```bash
python3 contracts/validate.py
python3 contracts/validate_execution.py
python3 -m unittest discover -s contracts/tests -v
python3 -m unittest discover -s tests/agency -v
```

## Results

| Check | Result |
|---|---|
| Knowledge contracts | OK — 14 units, 0 violations |
| Execution bundles | OK — 2 bundles (`rivallium`, `padel-iot`), 0 violations |
| Contract unit tests | OK — 28 tests |
| Agency tests | OK — 19 tests |
| Duplicate IDs | none detected by validators |
| Invalid dependencies / cycles in live examples | none |
| Invented Capability IDs in fixtures | none |

## Evidence artifacts

- `examples/rivallium/`
- `examples/padel-iot/`
- `contracts/fixtures/execution/`
- `tests/agency/`
- `docs/PHASE-3-SELF-REFUTATION.md`
