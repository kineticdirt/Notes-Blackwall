"""
Policy: decide mild actions from observations + goal. Rule-based; no heavy AI here.
Mild = append-only or small, scoped edits; max N per run.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def decide_actions(
    workspace_path: Path,
    goal: str,
    observations: Dict[str, Any],
    max_changes: int,
) -> List[Dict[str, Any]]:
    """
    Produce a small list of mild actions toward the goal. No bulk rewrites.
    Each action: { "kind": "append_log" | "append_scratchpad" | "suggest", "target": path, "content": str, "reason": str }
    """
    root = Path(workspace_path).resolve()
    actions: List[Dict[str, Any]] = []
    goal_lower = goal.lower()

    # Always log that we ran (mild: append to overseer log)
    actions.append({
        "kind": "append_log",
        "target": ".overseer/overseer.log",
        "content": f"[{datetime.now().isoformat()}] cycle run goal={goal[:60]}... file_count={observations.get('file_count', 0)} git_branch={observations.get('git_branch')} git_dirty={observations.get('git_dirty')}\n",
        "reason": "record oversight cycle",
    })

    # If goal mentions docs/README and we have a README, suggest a check (mild: append to scratchpad)
    if "readme" in goal_lower or "documentation" in goal_lower or "doc" in goal_lower:
        readme_candidates = list(root.rglob("README.md")) + list(root.rglob("README"))
        if readme_candidates:
            rel = readme_candidates[0].relative_to(root)
            actions.append({
                "kind": "append_scratchpad",
                "target": ".overseer/scratchpad.md",
                "content": f"\n---\n[{datetime.now().isoformat()}] Overseer: Goal mentions docs/README. Consider reviewing `{rel}` for alignment with current entrypoints.\n",
                "reason": "goal mentions documentation",
            })

    # If goal mentions "sync" or "entrypoints", add a generic note
    if "sync" in goal_lower or "entrypoint" in goal_lower:
        actions.append({
            "kind": "append_scratchpad",
            "target": ".overseer/scratchpad.md",
            "content": f"\n[{datetime.now().isoformat()}] Overseer: Goal suggests keeping entrypoints in sync. Check main scripts (e.g. cli.py, *_cli.py) and README quick-start sections.\n",
            "reason": "goal mentions sync/entrypoints",
        })

    return actions[:max_changes]
