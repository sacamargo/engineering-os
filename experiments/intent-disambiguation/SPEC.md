# Disambiguation Experiment Spec

## Purpose

Prove that Engineering OS can represent Intent → Capability resolution without:

- inventing Capabilities
- collapsing routing to keywords
- executing fulfillment prematurely
- building an Orchestrator

## Case Record Schema

Each `cases/*.json` file must include:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable case id |
| `utterance` | yes | User request text |
| `frame` | yes | Structured intent reading |
| `candidates` | yes | List of `{id, rationale, confidence}` |
| `primary` | yes | Capability id or `null` |
| `secondary` | yes | List of capability ids (may be empty) |
| `related_suggested` | yes | Soft adjacency suggestions |
| `insufficient_coverage` | yes | List of catalog gaps |
| `clarifying_questions` | yes | Questions for ambiguous cases |
| `fulfillment_preview` | yes | Binding preview or `null` |

### `frame` required keys

`desired_outcome`, `object_of_work`, `intent_class_hint`, `domain_hints`, `constraints`, `risk_signals`, `multi_intent`, `notes`

## Evaluator Rules

`evaluate.py` fails a case when:

1. A candidate/primary/secondary/related id is not an existing Capability in the live catalog
2. `primary` is set but not present in `candidates`
3. A `secondary` id is not present in `candidates`
4. `fulfillment_preview` references unknown unit ids from the live catalog
5. `fulfillment_preview` is non-null while `primary` is null
6. Confidence not in `high|medium|low`
7. For gap cases, `insufficient_coverage` is empty while `primary` is null and candidates are empty — allowed only if clarifying questions exist; pure silence is invalid
8. Invented capability-shaped ids appear anywhere outside explicit documentation fields

The evaluator does **not** score whether the human analysis is “the only correct routing.” It enforces structural honesty against the catalog.

## Case Intent (Human Expectations)

| Case | Expectation |
|---|---|
| `01-saas-architecture` | Primary architecture |
| `02-security-audit` | Primary security review |
| `03-architecture-security-risks` | Primary security; architecture related/secondary |
| `04-secure-scalable-saas` | Multi-intent; clarify; do not force one primary |
| `05-slow-checkout-database` | Insufficient coverage; do not invent performance/data Capabilities |
