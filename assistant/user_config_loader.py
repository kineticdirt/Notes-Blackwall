"""
Load user config from one file: API key and MCP servers.
Path: ASSISTANT_USER_CONFIG or assistant/config/user_config.yaml (relative to repo root).
Never log or return key values.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent


def _user_config_path() -> Path:
    path = os.environ.get("ASSISTANT_USER_CONFIG", "").strip()
    if path:
        p = Path(path)
        if p.startswith("~"):
            p = p.expanduser()
        return p.resolve()
    return REPO_ROOT / "assistant" / "config" / "user_config.yaml"


def _expand_path(s: str) -> Path:
    s = s.strip()
    if s.startswith("~"):
        s = os.path.expanduser(s)
    p = Path(s)
    if not p.is_absolute() and not s.startswith("~"):
        p = (REPO_ROOT / p).resolve()
    return p.resolve()


def load_user_config() -> Dict[str, Any]:
    """Load user_config.yaml. Returns dict with anthropic_api_key, anthropic_api_key_path, mcp_servers. Never log keys."""
    path = _user_config_path()
    if not path.exists():
        return {}
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        try:
            # Minimal fallback: no pyyaml, try to parse key and path only
            data = _parse_minimal_yaml(path)
        except Exception:
            return {}
    if not isinstance(data, dict):
        return {}
    return {
        "anthropic_api_key": (data.get("anthropic_api_key") or "").strip(),
        "anthropic_api_key_path": (data.get("anthropic_api_key_path") or "").strip(),
        "mcp_servers": data.get("mcp_servers") or {},
    }


def _parse_minimal_yaml(path: Path) -> Dict[str, Any]:
    """Minimal YAML-like parse for key and path only (no pyyaml)."""
    out = {}
    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k == "anthropic_api_key" and v:
                out["anthropic_api_key"] = v
            elif k == "anthropic_api_key_path" and v:
                out["anthropic_api_key_path"] = v
    if "mcp_servers" not in out:
        out["mcp_servers"] = {}
    return out


def apply_user_config_to_env() -> None:
    """
    Load user config and set env vars for the key. Idempotent; does not overwrite existing env.
    """
    cfg = load_user_config()
    if not cfg:
        return
    key = cfg.get("anthropic_api_key") or ""
    path = cfg.get("anthropic_api_key_path") or ""
    if key and not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("PI_LLM_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = key
        if not os.environ.get("PI_LLM_API_KEY"):
            os.environ["PI_LLM_API_KEY"] = key
    elif path:
        expanded = _expand_path(path)
        if not expanded.exists():
            return
        if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("PI_LLM_API_KEY"):
            return
        try:
            raw = expanded.read_text(encoding="utf-8").strip().splitlines()
            first = next((ln.strip() for ln in raw if ln.strip() and not ln.strip().startswith("#")), "")
            if first and "=" not in first:
                os.environ["ANTHROPIC_API_KEY"] = first
                os.environ["PI_LLM_API_KEY"] = first
                return
        except Exception:
            pass
        if not os.environ.get("CEQUENCE_SECRETS_FILE"):
            os.environ["CEQUENCE_SECRETS_FILE"] = str(expanded)


def get_user_config_mcp_servers() -> Dict[str, Any]:
    """Return MCP servers from user config in the same shape as .mcp.json (id -> { command, args, env? } or { url?, transport? })."""
    cfg = load_user_config()
    servers = cfg.get("mcp_servers") or {}
    if not isinstance(servers, dict):
        return {}
    out = {}
    for sid, val in servers.items():
        if not isinstance(val, dict):
            continue
        out[str(sid)] = dict(val)
    return out
