#!/usr/bin/env python3
"""
Pipeline: MCP → Tool calls → Contents → Train nano on all and continue.
1. Load MCP config from .mcp.json, connect to Atlassian MCP
2. Run tool calls (resources, spaces, Jira search, user info, etc.), save to JSONL
3. Format contents as corpus and train nano model (unsupervised on tool-call text)
4. Optionally run nano again using the trained model (if --continue)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPERIMENTS = Path(__file__).resolve().parent


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="MCP → tool calls → contents → train nano.")
    parser.add_argument("--no-train", action="store_true", help="Only collect, do not train")
    parser.add_argument("--no-collect", action="store_true", help="Only train on existing mcp_tool_calls.jsonl")
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--lora", action="store_true", help="Use LoRA for training")
    parser.add_argument("--continue-after", action="store_true", help="After training, run one nano query (optional)")
    parser.add_argument("--quick", action="store_true", help="Collect only 2 tools (resources + user info) for fast POC")
    args = parser.parse_args()

    env = os.environ.copy()
    env.setdefault("NANO_POC_SSL_VERIFY", "0")

    if not args.no_collect:
        print("Step 1: Collect MCP tool calls...", flush=True)
        cmd = [sys.executable, str(EXPERIMENTS / "mcp_collect_tool_calls.py"), "--out", str(EXPERIMENTS / "mcp_tool_calls.jsonl")]
        if args.quick:
            cmd.append("--quick")
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
        if r.returncode != 0:
            print("Collect failed.", file=sys.stderr)
            sys.exit(r.returncode)
    else:
        print("Skipping collect (--no-collect).", flush=True)

    if not args.no_train:
        print("Step 2: Train nano on tool-call contents...", flush=True)
        cmd = [sys.executable, str(EXPERIMENTS / "train_nano_on_tool_calls.py"), "--epochs", str(args.epochs)]
        if args.lora:
            cmd.append("--lora")
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env)
        if r.returncode != 0:
            print("Train failed.", file=sys.stderr)
            sys.exit(r.returncode)
    else:
        print("Skipping train (--no-train).", flush=True)

    if args.continue_after:
        print("Step 3: Run nano with trained context...", flush=True)
        r = subprocess.run(
            [sys.executable, str(EXPERIMENTS / "run_nano_from_mcp_json.py"), "what resources can I access?"],
            cwd=str(REPO_ROOT),
            env=env,
        )
        if r.returncode != 0:
            sys.exit(r.returncode)
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
