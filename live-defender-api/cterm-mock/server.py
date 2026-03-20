"""
Serve /__cq/cache/* from JSON captured in def-cterm.txt (no Kubernetes).

httpbin.org cannot host fixed mitigator shapes; this app replays the transcript.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from parser import parse_cterm_transcript

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CTERM = REPO_ROOT / "def-cterm.txt"


@lru_cache(maxsize=1)
def _load_fixtures() -> dict[str, dict]:
    path = Path(os.environ.get("DEF_CTERM_PATH", str(DEFAULT_CTERM))).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Transcript not found: {path}")
    return parse_cterm_transcript(path)


app = FastAPI(title="Defender cache mock (from def-cterm.txt)", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    _load_fixtures()


@app.get("/__cq/cache/help")
def cache_help():
    fx = _load_fixtures()
    apis = [f"/__cq/cache/{k}" for k in sorted(fx.keys())]
    return {"cache-info-apis": apis}


@app.get("/__cq/cache/{segment:path}")
def cache_segment(segment: str):
    segment = segment.strip("/")
    fx = _load_fixtures()
    if segment not in fx:
        raise HTTPException(404, f"No fixture for {segment!r}; have {sorted(fx.keys())}")
    return JSONResponse(content=fx[segment])


@app.get("/health")
def health():
    return {"ok": True, "fixtures": sorted(_load_fixtures().keys())}
