# Padel IoT — Agency Scenario

## Intent

> I want to automate a full padel court, including access, lighting, and remote mobile control, without depending on local Wi-Fi.

## Detected domains

| Domain | Coverage |
|---|---|
| Software architecture | Known Capability |
| Security | Known Capability |
| Testing | Known Capability |
| Observability / reliability (partial) | Known observability Capability; reliability gap |
| IoT | Missing Capability |
| Networking | Missing Capability |
| Cloud / Mobile | Missing Capability |
| Physical access | Missing Capability + **professional validation required** |
| Electrical engineering | Missing Capability + **professional validation required** |

## Can reason vs can execute

| Area | Can reason | Can execute autonomously |
|---|---|---|
| Software/cloud architecture sketches | Yes | Plan only in this phase |
| Threat modeling for remote control | Yes | Plan only |
| Electrical installation | Scope only | **No** — licensed professional |
| Physical locks/gates install | Scope only | **No** — specialist approval |

## Escalations

- `eos.escalation.padel-iot.electrical`
- `eos.escalation.padel-iot.physical-access`

Engineering OS must **not invent** Capabilities for regulated physical work.

## Machine bundle

See `project.json`, `plan.json`, and sibling folders. Validate with `python3 contracts/validate_execution.py`.
