"""Extract JSON bodies from defender CLI transcript (def-cterm.txt)."""
from __future__ import annotations

import json
import re
from pathlib import Path

URL_RE = re.compile(r"url=http://localhost:\d+/__cq/cache/([a-zA-Z0-9_-]+)")


def parse_cterm_transcript(path: Path) -> dict[str, dict]:
    """
    Map cache segment name -> JSON object (e.g. 'info', 'ip-map', 'policy-map', 'all').
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: dict[str, dict] = {}
    i = 0
    while i < len(lines):
        m = URL_RE.search(lines[i])
        if not m:
            i += 1
            continue
        key = m.group(1)
        while i < len(lines) and "===" not in lines[i]:
            i += 1
        if i >= len(lines):
            break
        i += 1
        buf: list[str] = []
        depth = 0
        started = False
        while i < len(lines):
            line = lines[i]
            for ch in line:
                if ch == "{":
                    depth += 1
                    started = True
                elif ch == "}":
                    depth -= 1
            buf.append(line)
            i += 1
            if started and depth == 0:
                break
        raw = "\n".join(buf).strip()
        if not raw:
            continue
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for cache key {key!r}: {e}") from e
    return out
