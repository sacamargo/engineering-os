"""CLI for Codebase Intelligence analysis.

Example:
  PYTHONPATH=. python3 -m codebase.cli analyze ./path/to/repo
  PYTHONPATH=. python3 -m codebase.cli analyze ./path/to/repo --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codebase.analyze import analyze_repository
from codebase.report import bundle_to_machine_json, render_human_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codebase", description="Engineering OS Codebase Intelligence")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a repository into a structured snapshot")
    analyze.add_argument("root", type=str, help="Repository root path")
    analyze.add_argument(
        "--format",
        choices=("human", "json", "both"),
        default="human",
        help="Output format",
    )
    analyze.add_argument(
        "--out",
        type=str,
        default="",
        help="Optional path to write JSON (when format is json or both)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        root = Path(args.root)
        if not root.exists():
            print(f"error: path not found: {root}", file=sys.stderr)
            return 2
        bundle = analyze_repository(root)
        payload = bundle_to_machine_json(bundle)
        if args.format in {"human", "both"}:
            print(render_human_report(bundle))
        if args.format in {"json", "both"}:
            text = json.dumps(payload, indent=2, sort_keys=True)
            if args.out:
                Path(args.out).write_text(text + "\n", encoding="utf-8")
                print(f"Wrote JSON to {args.out}", file=sys.stderr)
            if args.format == "json":
                print(text)
            elif args.out == "":
                # both without --out: print JSON after human report separator
                print("\n--- JSON ---\n")
                print(text)
        return 0
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
