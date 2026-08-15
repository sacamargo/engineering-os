# Phase 9 — Security

## Deny-by-default permissions

`PRODUCTION_READ`, `PRODUCTION_DEPLOY`, `PRODUCTION_ROLLBACK`,  
`PRODUCTION_CONFIG_READ`, `PRODUCTION_CONFIG_WRITE`, `PRODUCTION_INCIDENT_MANAGE`

Agent profile grants **READ only**.

## Human approval

Production (and staging) require `HUMAN_APPROVAL_REQUIRED`.

Forbidden approvers:

- `agent:*`
- `skill:*`
- `orchestrator`
- `delivery-runtime`
- `system:auto`

An agent cannot approve its own deployment.

## Safety gate

`PRODUCTION_OPERATION_ALLOWED` requires:

- ReleaseCandidate id
- readiness ready
- permissions
- for production (non dry-run): human approver + approved decision

Never authorized by `if environment == "production": True` alone.

## Secrets

- Secret values never stored in core (`SecretRef` = external reference only)
- Evidence/logs scrubbed; `assert_no_secrets` fails closed
- Tests cover secret / evidence leakage attempts

## Attack scenarios (fail-closed)

Covered in `production/tests/test_security.py`:

privilege escalation, production without approval, agent/skill/orchestrator self-approval,  
secret leakage, wrong environment, artifact substitution, unknown rollback target,  
health spoofing (UNKNOWN ≠ success), evidence spoofing, permission bypass.

## UNKNOWN ≠ PASSED

Missing tests/security/compatibility/health evidence yields `UNKNOWN` / `NEEDS_HUMAN`, never auto-PASS.
