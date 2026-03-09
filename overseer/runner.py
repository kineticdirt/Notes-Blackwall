"""
One overseer cycle: monitor → decide → execute → save state → report.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .config import OverseerConfig
from .state import OverseerState
from .monitor import monitor_workspace
from .policy import decide_actions
from .executor import execute_actions


def run_cycle(config: OverseerConfig) -> Dict[str, Any]:
    """
    Run one oversight cycle. Returns report dict for logging or larger AI.
    """
    root = config.workspace_path
    state_dir = root / config.state_dir
    state_path = state_dir / "state.json"

    # Load previous state
    state = OverseerState.load(state_path)
    state.goal = config.goal

    # Monitor
    observations = monitor_workspace(root, config.scope_dirs)
    state.observations_summary = {
        "file_count": observations.get("file_count"),
        "git_branch": observations.get("git_branch"),
        "git_dirty": observations.get("git_dirty"),
        "timestamp": observations.get("timestamp"),
    }

    # Decide
    actions = decide_actions(
        root,
        config.goal,
        observations,
        config.max_changes_per_run,
    )

    # Execute
    results = execute_actions(root, actions, config.dry_run)
    state.applied_changes = [r for r in results if r.get("applied")]
    state.last_run = datetime.now().isoformat()
    state.save(state_path)

    report = {
        "goal": config.goal,
        "dry_run": config.dry_run,
        "observations": state.observations_summary,
        "actions_decided": len(actions),
        "actions_applied": [r for r in results if r.get("applied")],
        "actions_skipped": [r for r in results if not r.get("applied")],
        "state_path": str(state_path),
    }
    return report
