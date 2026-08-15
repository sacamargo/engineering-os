"""CLI: python3 -m delivery.cli deliver <workspace>"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from delivery.loop import run_delivery
from delivery.report import render_delivery_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="delivery")
    sub = parser.add_subparsers(dest="cmd", required=True)
    deliver = sub.add_parser("deliver", help="Run local delivery validation pipeline")
    deliver.add_argument("workspace")
    deliver.add_argument("--project-id", default="eos.project.local")
    deliver.add_argument("--environment", default="local")
    deliver.add_argument("--changeset-id", default="eos.changeset.local")
    deliver.add_argument("--test-command", default="python3 -m unittest discover -s . -p test_*.py -v")
    deliver.add_argument("--approval-granted", action="store_true")
    deliver.add_argument("--approver", default="")
    deliver.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    if args.cmd == "deliver":
        root = Path(args.workspace)
        if not root.exists():
            print(f"error: workspace not found: {root}", file=sys.stderr)
            return 2
        result = run_delivery(
            root,
            project_id=args.project_id,
            environment=args.environment,
            changeset_id=args.changeset_id,
            test_command=args.test_command,
            approval_granted=args.approval_granted,
            approver=args.approver or None,
        )
        if args.format == "json":
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(render_delivery_report(result))
        return 0 if result.readiness in {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"} else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
