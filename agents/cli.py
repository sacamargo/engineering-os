"""CLI for agent execution demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agents.coding import DeterministicPlan
from agents.loop import run_execution
from agents.report import render_execution_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agents")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Run a deterministic plan JSON against a workspace")
    run.add_argument("workspace")
    run.add_argument("--task-json", required=True)
    run.add_argument("--plan-json", required=True)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        task = json.loads(Path(args.task_json).read_text(encoding="utf-8"))
        plan_data = json.loads(Path(args.plan_json).read_text(encoding="utf-8"))
        plan = DeterministicPlan(steps=list(plan_data.get("steps") or []))
        result = run_execution(args.workspace, task, plan, dry_run=args.dry_run)
        if args.format == "json":
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(render_execution_report(result))
        return 0 if result.status in {"SUCCESS", "DRY_RUN", "NEEDS_HUMAN", "NEEDS_INPUT"} else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
