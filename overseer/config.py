"""
Overseer config: goal, scope, limits. From env or file.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class OverseerConfig:
    """Config for one overseer run. Goal drives mild changes toward a known target."""

    workspace_path: Path
    goal: str
    scope_dirs: List[str] = field(default_factory=lambda: [".", "blackwall", "agent-system", "workflow-canvas"])
    max_changes_per_run: int = 3
    dry_run: bool = False
    state_dir: str = ".overseer"
    scratchpad_file: str = ".overseer/scratchpad.md"

    @classmethod
    def from_env(cls, workspace_path: Optional[Path] = None) -> "OverseerConfig":
        """Load from environment. OVERSEE_GOAL required; rest optional."""
        root = workspace_path or Path(os.getenv("OVERSEE_WORKSPACE", ".")).resolve()
        goal = os.getenv("OVERSEE_GOAL", "Keep documentation and entrypoints in sync; suggest small fixes only.")
        scope = os.getenv("OVERSEE_SCOPE", "")
        scope_dirs = [s.strip() for s in scope.split(",") if s.strip()] or [".", "blackwall", "agent-system", "workflow-canvas"]
        max_changes = int(os.getenv("OVERSEE_MAX_CHANGES", "3"))
        dry_run = os.getenv("OVERSEE_DRY_RUN", "").lower() in ("1", "true", "yes")
        return cls(
            workspace_path=root,
            goal=goal,
            scope_dirs=scope_dirs,
            max_changes_per_run=max_changes,
            dry_run=dry_run,
        )
