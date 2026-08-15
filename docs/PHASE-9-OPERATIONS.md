# Phase 9 — Operations Guide

**Package:** `production/`  
**Input:** Delivery `ReleaseCandidate` (`READY_FOR_DEPLOYMENT`)  
**Adapters:** fake/local only in core (`LocalFakeAdapter`, `WebLocalAdapter`, `BackendLocalAdapter`)

## Distinctions

```text
ProductionOperation ≠ Deployment ≠ Release ≠ ReleaseCandidate
≠ Environment ≠ Incident ≠ Rollback ≠ ValidationRun ≠ Evidence
Alert ≠ Incident
Configuration ≠ Secret
Delivery ≠ Deployment
```

## Lifecycle

```text
prepare → validate → approval → deploy → health → evidence → finalize
```

If deploy succeeds but health ≠ `healthy` → **not** `succeeded`.

## Environments

| Name | Risk | Approval | Rollback default |
|---|---|---|---|
| local | low | none | auto_allowed |
| development | low | none | auto_allowed |
| test | medium | optional | auto_allowed |
| staging | high | human_required | human_required |
| production | **critical** | **human_required** | **human_required** |

## CLI (fake/local only)

```bash
PYTHONPATH=. python3 -m production show-environments
PYTHONPATH=. python3 -m production dry-run --environment production
PYTHONPATH=. python3 -m production deploy --environment local
PYTHONPATH=. python3 -m production deploy --environment production \
  --approver human:alice --approval-decision approved
PYTHONPATH=. python3 -m production rollback --to-version 1.0.0 --authorized-by human:alice
```

No real cloud/App Store/Play Store publish commands exist.

## Mobile / Web / Backend

- `BackendRelease` / `WebRelease` / `MobileRelease` / `ReleaseBundle`
- App Store & Play Store = **external boundaries** (`publish_allowed=False` by default)
- Engineering OS prepares checklists/evidence only

## Incidents → Orchestration

`incident_to_orchestration` emits investigation / rollback / remediation / human_escalation / replan work items.  
**Incident ≠ Capability ≠ Skill.**
