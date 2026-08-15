"""Human-readable delivery report."""

from __future__ import annotations

from delivery.loop import DeliveryResult


def render_delivery_report(result: DeliveryResult) -> str:
    d = result.delivery
    lines = [
        "# Delivery Report",
        "",
        f"- Delivery: `{d.get('id')}`",
        f"- Status: **{result.status}**",
        f"- Readiness: **{result.readiness}**",
        f"- Project: `{d.get('project_id')}`",
        f"- ChangeSet: `{d.get('changeset_id')}`",
        f"- Environment: {d.get('environment')}",
        f"- Risk: {d.get('risk')}",
        "",
        "## What changed",
        f"- Build: `{result.build.get('id') if result.build else 'none'}`",
        f"- Artifacts: {len(result.artifacts)}",
        "",
        "## Validations",
    ]
    for v in result.validations:
        lines.append(f"- [{v.get('status')}] {v.get('kind')} `{v.get('id')}`")
    lines.append("")
    lines.append("## Gates")
    for g in result.gates:
        mark = "PASS" if g.get("passed") else "FAIL"
        lines.append(f"- [{mark}] {g.get('gate_id')} missing={g.get('missing')}")
    lines.append("")
    lines.append("## Release")
    if result.release_candidate:
        lines.append(f"- RC: `{result.release_candidate.get('id')}` v{result.release_candidate.get('version')}")
    else:
        lines.append("- none")
    if result.decision:
        lines.append(f"- Decision: {result.decision.get('decision')} by {result.decision.get('approver')}")
    lines.append("")
    lines.append("## Deployment boundary")
    if result.deployment_boundary:
        lines.append(f"- {result.deployment_boundary.get('status')}: {result.deployment_boundary.get('reason')}")
    else:
        lines.append("- not evaluated")
    lines.append("")
    lines.append("## Notes")
    for n in result.notes:
        lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)
