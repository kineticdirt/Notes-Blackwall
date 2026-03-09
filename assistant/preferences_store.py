"""
Persistent preferences for the general-purpose assistant.
Stored as JSON; accumulated over the assistant's lifetime.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _preferences_path() -> Path:
    default = Path(__file__).resolve().parent / "data" / "preferences.json"
    path = os.environ.get("PI_PREFERENCES_PATH", str(default))
    return Path(path).resolve()


def _ensure_dir() -> Path:
    p = _preferences_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def read_preferences() -> Dict[str, Any]:
    """Load all saved preferences. Returns dict; empty if file missing or invalid."""
    path = _preferences_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_preference(key: str, value: Any) -> str:
    """Save a single preference (merge into existing). Key can be dotted, e.g. 'theme.dark'."""
    path = _ensure_dir()
    prefs = read_preferences()
    keys = key.split(".")
    target = prefs
    for k in keys[:-1]:
        if k not in target or not isinstance(target[k], dict):
            target[k] = {}
        target = target[k]
    target[keys[-1]] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
    return f"Saved preference: {key}"


def format_preferences_for_prompt(prefs: Dict[str, Any]) -> str:
    """Format preferences as a short string for inclusion in system prompt."""
    if not prefs:
        return "No saved preferences yet."
    return json.dumps(prefs, indent=2)
