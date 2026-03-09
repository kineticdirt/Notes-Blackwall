"""
Lightweight workspace monitoring: file presence, recency, optional git. No heavy analysis.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess


def monitor_workspace(workspace_path: Path, scope_dirs: List[str]) -> Dict[str, Any]:
    """
    Gather lightweight observations. No heavy analysis.
    Returns: file_count, recent_files (paths + mtime), git_branch, git_dirty (if git available).
    """
    root = Path(workspace_path).resolve()
    observations: Dict[str, Any] = {
        "file_count": 0,
        "recent_files": [],
        "scope_dirs": [],
        "git_branch": None,
        "git_dirty": None,
        "timestamp": datetime.now().isoformat(),
    }

    # Collect paths under scope (shallow: first level of each scope dir)
    collected: List[Path] = []
    for scope in scope_dirs:
        base = (root / scope).resolve() if scope != "." else root
        if not base.exists():
            observations["scope_dirs"].append({"path": str(base), "exists": False})
            continue
        observations["scope_dirs"].append({"path": str(base), "exists": True})
        if base.is_file():
            collected.append(base)
        else:
            for p in base.rglob("*"):
                if p.is_file() and _is_trackable(p):
                    collected.append(p)

    # Limit to recent (by mtime) for brevity
    with_mtime = [(p, p.stat().st_mtime) for p in collected]
    with_mtime.sort(key=lambda x: x[1], reverse=True)
    observations["recent_files"] = [
        {"path": str(p.relative_to(root)), "mtime": datetime.fromtimestamp(m).isoformat()}
        for p, m in with_mtime[:50]
    ]
    observations["file_count"] = len(collected)

    # Optional git
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if r.returncode == 0 and r.stdout:
            observations["git_branch"] = r.stdout.strip()
        r2 = subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=2,
        )
        observations["git_dirty"] = bool(r2.stdout.strip()) if r2.returncode == 0 else None
    except Exception:
        pass

    return observations


def _is_trackable(p: Path) -> bool:
    skip = {".git", "__pycache__", "node_modules", ".venv", "venv", ".overseer"}
    parts = p.parts
    if any(part in skip for part in parts):
        return False
    suf = p.suffix.lower()
    return suf in (".py", ".md", ".json", ".yaml", ".yml", ".js", ".ts", ".html", ".css", ".txt") or p.name in ("Dockerfile", "Makefile")
