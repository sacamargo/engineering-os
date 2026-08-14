#!/usr/bin/env python3
"""CLI for the Planning Orchestrator demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration.facade import PlanningOrchestrator  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Engineering OS Planning Orchestrator")
    parser.add_argument("utterance", nargs="?", help="Engineering intent text")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    parser.add_argument("--repo-root", default=str(ROOT))
    args = parser.parse_args(argv)
    if not args.utterance:
        parser.error("utterance required")

    result = PlanningOrchestrator(Path(args.repo_root)).plan(args.utterance)
    data = result.to_dict()
    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    print("## Engineering OS Planning Result")
    print(f"Intent language: {data['intent']['language']}")
    print(f"Primary capability: {data['arbitration']['primary']}")
    print(f"Secondary: {', '.join(data['arbitration']['secondary']) or '-'}")
    print(f"Readiness: {data['readiness']['status']}")
    print(f"Tasks: {len(data['generated']['tasks'])}")
    print(f"Artifacts: {len(data['generated']['artifacts'])}")
    print(f"Gates: {len(data['generated']['gates'])}")
    print(f"Gaps: {len(data['gaps'])}")
    print(f"Escalations: {len(data['escalations'])}")
    if data["intent"]["clarifying_questions"]:
        print("Clarifying questions:")
        for q in data["intent"]["clarifying_questions"]:
            print(f"- {q}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
