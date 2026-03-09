"""Subprocess dispatcher — runs commands in the target project directory."""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console()

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent


def dispatch(project_dir: str, cmd: list[str], env: dict | None = None) -> int:
    """Run a command in the given project directory under the workspace root."""
    target = WORKSPACE_ROOT / project_dir
    if not target.exists():
        console.print(f"[red]Directory not found: {target}[/red]")
        return 1

    full_cmd = [sys.executable] + cmd if cmd[0] != sys.executable else cmd

    console.print(f"[dim]→ {target.name}/ $ {' '.join(full_cmd)}[/dim]")
    result = subprocess.run(full_cmd, cwd=str(target), env=env)
    return result.returncode
