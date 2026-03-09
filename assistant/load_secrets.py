"""
Load secrets from env files without exposing them in the repo.
Runs before the rest of the assistant so keys are available via os.environ only.

Two steps:
1. Project .env (cwd) if present — non-secret config.
2. If CEQUENCE_SECRETS_FILE is set, load that file and override (so real keys live only there).
   ~ in the path is expanded (e.g. ~/.cequence-rnd/.env).

Never read or log the contents of the secrets file; only set os.environ.
"""

from __future__ import annotations

import os
import re
from pathlib import Path


def _expand_path(path: str) -> Path:
    s = path.strip()
    if s.startswith("~"):
        s = os.path.expanduser(s)
    return Path(s).resolve()


def _parse_env_line(line: str) -> tuple[str, str] | None:
    """Parse a single KEY=value line. Returns (key, value) or None if not a binding."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
    if not m:
        return None
    key, value = m.group(1), m.group(2)
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1].replace('\\"', '"')
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1].replace("\\'", "'")
    return (key, value.strip())


def _load_file_into_env(path: Path, override: bool = True) -> None:
    """Load KEY=value lines from path into os.environ. If override=True, existing keys are overwritten."""
    if not path.exists():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = _parse_env_line(line)
                if parsed:
                    key, value = parsed
                    if override or key not in os.environ:
                        os.environ[key] = value
    except OSError:
        pass


def load_secrets() -> None:
    """
    Load environment in three steps:
    1. Project .env (cwd) if present.
    2. User config file (assistant/config/user_config.yaml): apply anthropic_api_key or path.
    3. If CEQUENCE_SECRETS_FILE is set, load that file and override.
    Also: if ANTHROPIC_API_KEY is set and PI_LLM_API_KEY is not, set PI_LLM_API_KEY from it.
    """
    cwd = Path.cwd()
    project_env = cwd / ".env"
    if project_env.exists():
        _load_file_into_env(project_env, override=False)

    try:
        from assistant.user_config_loader import apply_user_config_to_env
        apply_user_config_to_env()
    except Exception:
        pass

    secrets_file = os.environ.get("CEQUENCE_SECRETS_FILE", "").strip()
    if secrets_file:
        path = _expand_path(secrets_file)
        _load_file_into_env(path, override=True)

    if os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("PI_LLM_API_KEY"):
        os.environ["PI_LLM_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
