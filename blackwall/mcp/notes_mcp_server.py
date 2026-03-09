"""
MCP server for Cursor: persistent notes, progress persistence, and BDH-style beliefs.

- Progress: save_progress / read_progress so agents can save state and the next
  agent or session can resume without the user reprompting or manually reducing context.
- Parallel agents: shared notes and progress; read before starting, save when pausing/finishing.
- Tools: read_notes, append_note, read_progress, save_progress, read_beliefs, update_belief, get_role, set_role.
Data is stored in a single JSON file (default: .cursor/context/notes.json).
Run with stdio for Cursor: python -m blackwall.mcp.notes_mcp_server
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Default path; override with env CURSOR_NOTES_PATH
NOTES_PATH = os.environ.get("CURSOR_NOTES_PATH", ".cursor/context/notes.json")


def _resolve_path() -> Path:
    """Resolve notes path; prefer cwd so Cursor runs from workspace root."""
    p = Path(NOTES_PATH)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


def _load() -> dict:
    path = _resolve_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return _default_data()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "progress" not in data:
            data["progress"] = _default_data()["progress"]
        return data
    except (json.JSONDecodeError, OSError):
        return _default_data()


def _default_data() -> dict:
    return {
        "version": "1.0",
        "beliefs": [],
        "notes": [],
        "progress": {
            "last_summary": "",
            "next_steps": [],
            "completed": [],
            "updated_at": "",
        },
        "role": {"persona": "", "current_focus": ""},
    }


def _save(data: dict) -> None:
    path = _resolve_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _read_notes_impl(section: Optional[str] = None) -> str:
    """Read all notes, or only a section (e.g. overview, code_notes, discoveries)."""
    data = _load()
    notes = data.get("notes", [])
    if section:
        notes = [n for n in notes if n.get("section") == section]
    if not notes:
        return "No notes found." if section else "No notes yet."
    lines = []
    for n in notes:
        sec = n.get("section", "")
        content = n.get("content", "")
        ts = n.get("updated_at", "")
        lines.append(f"[{sec}] {ts}: {content}")
    return "\n".join(lines)


def _append_note_impl(content: str, section: str = "general", metadata: Optional[dict] = None) -> str:
    """Append a note. Section can be overview, code_notes, discoveries, todo, etc."""
    data = _load()
    notes = data.get("notes", [])
    notes.append({
        "content": content,
        "section": section,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata or {},
    })
    data["notes"] = notes[-500:]  # keep last 500
    _save(data)
    return "Note appended."


def _read_beliefs_impl(min_likelihood_percent: Optional[int] = None) -> str:
    """Read all beliefs (statement, likelihood_percent, evidence, logic). Optionally filter by min likelihood."""
    data = _load()
    beliefs = data.get("beliefs", [])
    if min_likelihood_percent is not None:
        beliefs = [b for b in beliefs if (b.get("likelihood_percent") or 0) >= min_likelihood_percent]
    if not beliefs:
        return "No beliefs stored."
    lines = []
    for b in beliefs:
        stmt = b.get("statement", "")
        pct = b.get("likelihood_percent", 0)
        ev = b.get("evidence", [])
        logic = b.get("logic", "")
        lines.append(f"- [{pct}%] {stmt}")
        if ev:
            lines.append(f"  Evidence: {ev}")
        if logic:
            lines.append(f"  Logic: {logic}")
    return "\n".join(lines)


def _update_belief_impl(
    id: str,
    statement: str,
    likelihood_percent: Optional[int] = None,
    evidence: Optional[list] = None,
    logic: Optional[str] = None,
) -> str:
    """Add or update a belief by id. Use likelihood_percent (0-100), evidence list, and logic for BDH-style context."""
    data = _load()
    beliefs = data.get("beliefs", [])
    now = datetime.utcnow().isoformat() + "Z"
    for b in beliefs:
        if b.get("id") == id:
            b["statement"] = statement
            if likelihood_percent is not None:
                b["likelihood_percent"] = max(0, min(100, likelihood_percent))
            if evidence is not None:
                b["evidence"] = evidence
            if logic is not None:
                b["logic"] = logic
            b["updated_at"] = now
            _save(data)
            return f"Updated belief '{id}'."
    beliefs.append({
        "id": id,
        "statement": statement,
        "likelihood_percent": max(0, min(100, likelihood_percent or 50)),
        "evidence": evidence or [],
        "logic": logic or "",
        "updated_at": now,
    })
    data["beliefs"] = beliefs
    _save(data)
    return f"Added belief '{id}'."


def _get_role_impl() -> str:
    """Get current role/persona and focus for roleplay context."""
    data = _load()
    role = data.get("role", {})
    persona = role.get("persona", "")
    focus = role.get("current_focus", "")
    if not persona and not focus:
        return "No role set. Use set_role to define persona and current_focus."
    return f"Persona: {persona}\nCurrent focus: {focus}"


def _set_role_impl(persona: str = "", current_focus: str = "") -> str:
    """Set roleplay persona and/or current focus. Pass empty string to leave unchanged."""
    data = _load()
    role = data.get("role", {"persona": "", "current_focus": ""})
    if persona:
        role["persona"] = persona
    if current_focus:
        role["current_focus"] = current_focus
    data["role"] = role
    _save(data)
    return "Role updated."


def _read_progress_impl() -> str:
    """Return last summary, next steps, and completed so an agent or new session can resume."""
    data = _load()
    p = data.get("progress", {})
    summary = p.get("last_summary", "")
    next_steps = p.get("next_steps", [])
    completed = p.get("completed", [])
    updated = p.get("updated_at", "")
    if not summary and not next_steps and not completed:
        return "No progress saved yet. Use save_progress to store a summary and next steps so the next agent or session can resume."
    lines = [f"Last updated: {updated}", f"Summary: {summary}"]
    if next_steps:
        lines.append("Next steps: " + "; ".join(next_steps))
    if completed:
        lines.append("Completed: " + "; ".join(completed))
    return "\n".join(lines)


def _save_progress_impl(
    summary: str = "",
    next_steps: Optional[list] = None,
    completed: Optional[list] = None,
) -> str:
    """Save progress (summary, next_steps, completed) so the next agent or session can resume without reprompting."""
    data = _load()
    p = data.get("progress", _default_data()["progress"])
    now = datetime.utcnow().isoformat() + "Z"
    if summary:
        p["last_summary"] = summary
    if next_steps is not None:
        p["next_steps"] = list(next_steps)[:50]
    if completed is not None:
        p["completed"] = list(completed)[:100]
    p["updated_at"] = now
    data["progress"] = p
    _save(data)
    return "Progress saved. Next agent or session can call read_progress to resume."


def _run_with_mcp() -> None:
    """Run MCP server over stdio using the official mcp package."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise SystemExit(
            "Install the MCP SDK: pip install mcp\n"
            "Then run: python -m blackwall.mcp.notes_mcp_server"
        )

    mcp = FastMCP(
        "cursor-notes",
        description="Persistent notes and BDH-style beliefs (likelihood + evidence) for Cursor.",
    )

    @mcp.tool()
    def read_notes(section: Optional[str] = None) -> str:
        """Read all notes, or only a section (overview, code_notes, discoveries, todo, general). Call early when you need context from other agents or prior work."""
        return _read_notes_impl(section=section)

    @mcp.tool()
    def append_note(content: str, section: str = "general") -> str:
        """Append a note. Use section like overview, code_notes, discoveries, todo."""
        return _append_note_impl(content=content, section=section)

    @mcp.tool()
    def read_beliefs(min_likelihood_percent: Optional[int] = None) -> str:
        """Read beliefs with optional min likelihood (0-100). Call when you need shared assumptions or evidence; keeps output consistent with current beliefs."""
        return _read_beliefs_impl(min_likelihood_percent=min_likelihood_percent)

    @mcp.tool()
    def update_belief(
        id: str,
        statement: str,
        likelihood_percent: Optional[int] = None,
        evidence: Optional[list] = None,
        logic: Optional[str] = None,
    ) -> str:
        """Add or update a belief. id=unique key, statement=claim, likelihood_percent=0-100, evidence=list of refs, logic=short reason."""
        return _update_belief_impl(
            id=id,
            statement=statement,
            likelihood_percent=likelihood_percent,
            evidence=evidence or None,
            logic=logic or None,
        )

    @mcp.tool()
    def get_role() -> str:
        """Get current roleplay persona and focus."""
        return _get_role_impl()

    @mcp.tool()
    def set_role(persona: str = "", current_focus: str = "") -> str:
        """Set roleplay persona and/or current focus. Empty string keeps existing value."""
        return _set_role_impl(persona=persona, current_focus=current_focus)

    @mcp.tool()
    def read_progress() -> str:
        """Read saved progress (last summary, next steps, completed). Call at the start of a task or new conversation to resume without the user reprompting."""
        return _read_progress_impl()

    @mcp.tool()
    def save_progress(
        summary: str = "",
        next_steps: Optional[list] = None,
        completed: Optional[list] = None,
    ) -> str:
        """Save progress: summary, next_steps (list), completed (list). Call before ending or pausing so the next turn or agent can continue immediately."""
        return _save_progress_impl(summary=summary, next_steps=next_steps, completed=completed)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    _run_with_mcp()
