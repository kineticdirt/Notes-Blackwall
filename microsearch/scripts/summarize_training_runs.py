#!/usr/bin/env python3
"""Print summary of microsearch/results/training_runs.jsonl (latest last)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

MS_ROOT = Path(__file__).resolve().parent.parent
RUNS = MS_ROOT / "results" / "training_runs.jsonl"


def main() -> None:
    if not RUNS.exists():
        print("No training runs yet. Use record_training_run.py first.", file=sys.stderr)
        sys.exit(0)
    rows = []
    for line in RUNS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not rows:
        print("File empty.", file=sys.stderr)
        return
    print("=== MicroSearch training runs (chronological) ===\n")
    total_train = 0.0
    total_gen = 0.0
    for r in rows:
        total_train += float(r.get("training_duration_seconds") or 0)
        g = r.get("training_data_generation_seconds")
        if g is not None:
            total_gen += float(g)
        print(f"  {r.get('recorded_at')}: duration={r.get('training_duration_seconds')}s  examples={r.get('num_training_examples')}  ops={r.get('num_openapi_operations')}  backend={r.get('training_backend')}")
    print(f"\nCumulative training_duration_seconds: {total_train:.1f}")
    if total_gen:
        print(f"Cumulative training_data_generation_seconds: {total_gen:.1f}")
    latest = rows[-1]
    print("\nLatest run full record:")
    print(json.dumps(latest, indent=2))


if __name__ == "__main__":
    main()
