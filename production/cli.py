#!/usr/bin/env python3
"""Production Operations CLI — fake/local only; no real deploy."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from production.adapters.local import BackendLocalAdapter, LocalFakeAdapter, WebLocalAdapter
from production.evidence import build_evidence_chain
from production.loop import run_production_operation
from production.model import DEFAULT_PRODUCTION_ENVIRONMENTS, DeploymentTarget
from production.rollback import execute_rollback
from production.adapters.base import AdapterRequest


def _parse_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    return json.loads(raw)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="production", description="Production Operations (fake/local only)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--rc-id", default="eos.rc.cli")
        sp.add_argument("--environment", default="local")
        sp.add_argument("--application", default="demo")
        sp.add_argument("--version", default="1.0.0")
        sp.add_argument("--artifact-id", default="eos.artifact.cli")
        sp.add_argument("--adapter", choices=["local", "web", "backend"], default="local")
        sp.add_argument("--permissions", default="PRODUCTION_READ,PRODUCTION_DEPLOY")
        sp.add_argument("--approver")
        sp.add_argument("--approval-decision")
        sp.add_argument("--previous-version")
        sp.add_argument("--auto-rollback", action="store_true")
        sp.add_argument("--force-health")
        sp.add_argument("--fail-deploy", action="store_true")

    for name in ("plan", "validate", "dry-run", "deploy", "verify"):
        sp = sub.add_parser(name)
        add_common(sp)

    health = sub.add_parser("health")
    add_common(health)

    rb = sub.add_parser("rollback")
    add_common(rb)
    rb.add_argument("--to-version", required=True)
    rb.add_argument("--reason", default="cli rollback")
    rb.add_argument("--authorized-by")

    sub.add_parser("show-environments")
    evidence = sub.add_parser("show-evidence")
    evidence.add_argument("--result-json", required=True)
    audit = sub.add_parser("show-audit")
    audit.add_argument("--result-json", required=True)
    return p


def _adapter(args: argparse.Namespace) -> LocalFakeAdapter:
    cls = {"local": LocalFakeAdapter, "web": WebLocalAdapter, "backend": BackendLocalAdapter}[args.adapter]
    return cls(force_health=args.force_health, fail_deploy=args.fail_deploy)


def _run(args: argparse.Namespace, *, dry_run: bool = False) -> dict[str, Any]:
    env = args.environment
    perms = [x.strip() for x in args.permissions.split(",") if x.strip()]
    # ensure env-required perms for convenience in CLI demos
    if env in DEFAULT_PRODUCTION_ENVIRONMENTS:
        for p in DEFAULT_PRODUCTION_ENVIRONMENTS[env].permissions_required:
            if p not in perms:
                perms.append(p)
    target = DeploymentTarget(
        id="eos.target.cli",
        application=args.application,
        environment=env,
        version=args.version,
        artifact_id=args.artifact_id,
        adapter=args.adapter,
    )
    rc = {"id": args.rc_id, "status": "ready", "readiness": "READY_FOR_DEPLOYMENT"}
    result = run_production_operation(
        release_candidate=rc,
        target=target,
        environment_name=env,
        granted_permissions=perms,
        approver=args.approver,
        approval_decision=args.approval_decision,
        dry_run=dry_run,
        adapter=_adapter(args),
        previous_version=args.previous_version,
        auto_rollback_allowed=args.auto_rollback,
    )
    return result.to_dict()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "show-environments":
        print(json.dumps({k: v.to_dict() for k, v in DEFAULT_PRODUCTION_ENVIRONMENTS.items()}, indent=2))
        return 0
    if args.cmd == "show-evidence":
        payload = json.loads(args.result_json)
        print(json.dumps(build_evidence_chain(payload).to_dict(), indent=2))
        return 0
    if args.cmd == "show-audit":
        payload = json.loads(args.result_json)
        print(json.dumps(payload.get("audit") or [], indent=2))
        return 0
    if args.cmd == "rollback":
        adapter = _adapter(args)
        # seed current version then rollback
        adapter.deploy(
            AdapterRequest("cli", {"version": args.version}, args.environment, args.artifact_id)
        )
        rb = execute_rollback(
            adapter,
            operation_id="cli",
            target={"version": args.version},
            environment=args.environment,
            artifact_id=args.artifact_id,
            from_version=args.version,
            to_version=args.to_version,
            reason=args.reason,
            policy="auto_allowed" if args.authorized_by else "human_required",
            authorized_by=args.authorized_by,
        )
        print(json.dumps(rb.to_dict(), indent=2))
        return 0 if rb.status in {"verified", "needs_human"} else 1
    if args.cmd in {"plan", "validate", "dry-run"}:
        out = _run(args, dry_run=True)
        print(json.dumps(out, indent=2))
        return 0 if out["operation"]["status"] == "succeeded" else 1
    if args.cmd in {"deploy", "verify", "health"}:
        out = _run(args, dry_run=False)
        print(json.dumps(out, indent=2))
        return 0 if out["operation"]["status"] == "succeeded" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
