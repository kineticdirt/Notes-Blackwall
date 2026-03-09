"""
Executor: apply mild changes only. Append to log/scratchpad; no bulk rewrites.
"""

from pathlib import Path
from typing import List, Dict, Any


def execute_actions(
    workspace_path: Path,
    actions: List[Dict[str, Any]],
    dry_run: bool,
) -> List[Dict[str, Any]]:
    """
    Apply each action. Returns list of { action, applied: bool, path }.
    Mild only: append_log, append_scratchpad; suggest is no-op (logged only).
    """
    root = Path(workspace_path).resolve()
    applied: List[Dict[str, Any]] = []

    for action in actions:
        kind = action.get("kind", "")
        target = action.get("target", "")
        content = action.get("content", "")
        reason = action.get("reason", "")

        if dry_run:
            applied.append({"action": kind, "target": target, "reason": reason, "applied": False, "dry_run": True})
            continue

        path = (root / target).resolve()
        if not path.is_absolute() or not str(path).startswith(str(root)):
            path = root / target
        path.parent.mkdir(parents=True, exist_ok=True)

        if kind == "append_log":
            try:
                with open(path, "a") as f:
                    f.write(content)
                applied.append({"action": kind, "target": target, "reason": reason, "applied": True})
            except Exception as e:
                applied.append({"action": kind, "target": target, "reason": reason, "applied": False, "error": str(e)})
        elif kind == "append_scratchpad":
            try:
                with open(path, "a") as f:
                    f.write(content)
                applied.append({"action": kind, "target": target, "reason": reason, "applied": True})
            except Exception as e:
                applied.append({"action": kind, "target": target, "reason": reason, "applied": False, "error": str(e)})
        elif kind == "suggest":
            applied.append({"action": kind, "target": target, "reason": reason, "applied": False, "suggested": True})
        else:
            applied.append({"action": kind, "target": target, "reason": reason, "applied": False, "skipped": "unknown kind"})

    return applied
