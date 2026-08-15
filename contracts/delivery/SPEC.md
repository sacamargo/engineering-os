# Delivery Layer Contracts

Validate Delivery JSON objects produced by `delivery/`.

## Objects

| Object | ID pattern |
|---|---|
| Delivery | `eos.delivery.<hex>` |
| Build | `eos.build.<hex>` |
| Delivery Artifact | `eos.dartifact.<type>.<hex>` |
| Validation | `eos.validation.<kind>.<hex>` |
| Release Candidate | `eos.rc.<hex>` |

## Invariants

1. Build `succeeded` requires non-empty evidence
2. Validation status ∈ NOT_RUN|PASSED|FAILED|BLOCKED|UNKNOWN
3. NOT_RUN ≠ PASSED
4. Release without artifact digest is invalid
5. security_status unknown cannot auto-release
6. Delivery status transitions must follow state machine
