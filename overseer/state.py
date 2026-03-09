"""
Overseer state: persistent snapshot of last run and applied changes.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class OverseerState:
    """State for oversight cycle: last run, observations summary, applied changes."""

    last_run: Optional[str] = None
    observations_summary: Dict[str, Any] = field(default_factory=dict)
    applied_changes: List[Dict[str, Any]] = field(default_factory=list)
    goal: str = ""

    def save(self, state_path: Path) -> None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, state_path: Path) -> "OverseerState":
        if not state_path.exists():
            return cls()
        with open(state_path) as f:
            d = json.load(f)
        return cls(
            last_run=d.get("last_run"),
            observations_summary=d.get("observations_summary", {}),
            applied_changes=d.get("applied_changes", []),
            goal=d.get("goal", ""),
        )
