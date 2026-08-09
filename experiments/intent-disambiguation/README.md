# Intent → Capability Disambiguation Experiment

Minimal experiment for Capability candidate resolution.

This is **not** an Orchestrator, embedding index, or keyword router.

It demonstrates and validates the shape of:

```text
utterance → intent frame → candidates → primary/secondary → related → fulfillment preview
```

Protocol authority: [foundation/INTENT-RESOLUTION.md](../../foundation/INTENT-RESOLUTION.md)

## Contents

| Path | Role |
|---|---|
| `SPEC.md` | Experiment rules |
| `cases/*.json` | Authored resolution records for representative utterances |
| `evaluate.py` | Structural validator against the live Capability catalog |
| `tests/test_evaluate.py` | Tests for evaluator behavior |

## Run

```bash
python3 experiments/intent-disambiguation/evaluate.py
python3 -m unittest discover -s experiments/intent-disambiguation/tests -v
```

## Important

Cases are **authored analyses**, not model outputs.

Automatic utterance classification remains deferred.
