"""
CLI for workspace overseer. Directed by goal (env or --goal). One cycle per run.
"""

import argparse
import json
import os
from pathlib import Path

from .config import OverseerConfig
from .runner import run_cycle


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Workspace overseer: lightweight monitoring + mild goal-directed changes."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run"],
        help="run = one oversight cycle",
    )
    parser.add_argument(
        "--goal",
        "-g",
        default=os.getenv("OVERSEE_GOAL", "Keep documentation and entrypoints in sync; suggest small fixes only."),
        help="Known goal for this run (or set OVERSEE_GOAL)",
    )
    parser.add_argument(
        "--workspace",
        "-w",
        default=os.getenv("OVERSEE_WORKSPACE", "."),
        help="Workspace root (or set OVERSEE_WORKSPACE)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.getenv("OVERSEE_DRY_RUN", "").lower() in ("1", "true", "yes"),
        help="Do not write; only report what would be done",
    )
    parser.add_argument(
        "--max-changes",
        type=int,
        default=int(os.getenv("OVERSEE_MAX_CHANGES", "3")),
        help="Max mild changes per run (default 3)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON",
    )
    args = parser.parse_args()

    if args.command != "run":
        return

    config = OverseerConfig(
        workspace_path=Path(args.workspace).resolve(),
        goal=args.goal,
        scope_dirs=[".", "blackwall", "agent-system", "workflow-canvas", "overseer", "compendium"],
        max_changes_per_run=args.max_changes,
        dry_run=args.dry_run,
    )
    report = run_cycle(config)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Overseer cycle complete.")
        print(f"  Goal: {report['goal'][:70]}...")
        print(f"  Dry run: {report['dry_run']}")
        print(f"  Observations: file_count={report['observations'].get('file_count')} git_branch={report['observations'].get('git_branch')} git_dirty={report['observations'].get('git_dirty')}")
        print(f"  Actions decided: {report['actions_decided']}")
        for r in report["actions_applied"]:
            print(f"    Applied: {r.get('action', r.get('kind'))} -> {r.get('target')}")
        for r in report["actions_skipped"]:
            if r.get("dry_run"):
                print(f"    Would have: {r.get('action', r.get('kind'))} -> {r.get('target')}")


if __name__ == "__main__":
    main()
