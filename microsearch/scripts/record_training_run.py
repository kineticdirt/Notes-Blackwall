#!/usr/bin/env python3
"""
Append one training-run record to microsearch/results/training_runs.jsonl.
Use after dataset generation and/or fine-tune to include training time in the framework.

Example:
  python3 record_training_run.py --duration-seconds 1800 \\
    --spec ../specs/my-api.json \\
    --dataset ../training/intents.jsonl \\
    --tools ../generated/tools_catalog.json \\
    --backend hf_jobs \\
    --frontier claude-sonnet-4-20250514
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

MS_ROOT = Path(__file__).resolve().parent.parent
RESULTS = MS_ROOT / "results"


def _sha256_file(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def _count_jsonl(p: Path) -> int:
    if not p.exists():
        return 0
    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            json.loads(line)
            n += 1
        except json.JSONDecodeError:
            continue
    return n


def _load_spec(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            return {}
        return yaml.safe_load(raw) or {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _count_openapi_ops(spec_path: Path) -> int:
    spec = _load_spec(spec_path)
    paths = spec.get("paths") or {}
    n = 0
    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            if method in path_item and isinstance(path_item[method], dict):
                n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Record MicroSearch training run (duration + provenance).")
    parser.add_argument("--duration-seconds", type=float, required=True, help="Wall-clock training duration")
    parser.add_argument("--generation-seconds", type=float, default=None, help="Optional: frontier-only JSONL generation time")
    parser.add_argument("--spec", type=Path, action="append", dest="specs", help="OpenAPI spec path (repeatable)")
    parser.add_argument("--dataset", type=Path, help="Training JSONL path")
    parser.add_argument("--tools", type=Path, help="tools_catalog.json path")
    parser.add_argument("--backend", default="unspecified", help="e.g. jsonl_only, hf_jobs, local_lora")
    parser.add_argument("--frontier", dest="frontier_model_training_data", help="Model that generated examples")
    parser.add_argument("--micro-model", dest="micro_model", help="e.g. SmolLM3-3B")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS / "training_runs.jsonl"

    openapi_paths = []
    if args.specs:
        openapi_paths = [str(p.resolve()) for p in args.specs]

    openapi_sha256 = None
    num_ops = 0
    if args.specs and len(args.specs) == 1:
        openapi_sha256 = _sha256_file(args.specs[0])
        try:
            num_ops = _count_openapi_ops(args.specs[0])
        except Exception as e:
            print(f"Warning: could not count operations: {e}", file=sys.stderr)

    num_examples = _count_jsonl(args.dataset) if args.dataset else 0

    record = {
        "run_id": str(uuid.uuid4()),
        "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
        "training_duration_seconds": args.duration_seconds,
        "training_data_generation_seconds": args.generation_seconds,
        "openapi_spec_paths": openapi_paths,
        "openapi_sha256": openapi_sha256,
        "num_openapi_operations": num_ops,
        "num_training_examples": num_examples,
        "tools_catalog_path": str(args.tools.resolve()) if args.tools else None,
        "training_dataset_path": str(args.dataset.resolve()) if args.dataset else None,
        "training_backend": args.backend,
        "frontier_model_training_data": args.frontier_model_training_data,
        "micro_model": args.micro_model,
        "notes": args.notes,
    }

    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Appended training run to {out_path}", file=sys.stderr)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
