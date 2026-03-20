#!/usr/bin/env python3
"""
Post-router validation: reject hallucinated tool names and invalid args before MCP calls.
Complements SFT; aligns with H-Neurons goal (catch bad generations) without neuron surgery.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any


def normalize_cloud_id(args: dict) -> dict:
    out = dict(args)
    cid = os.environ.get("ATLASSIAN_CLOUD_ID", "").strip()
    if cid and out.get("cloudId") in ("<cloudId>", "<need cloudId>", "", None):
        out["cloudId"] = cid
    return out


def validate_tool_name(tool: str, allowed: set[str]) -> bool:
    return tool in allowed


def required_args_for_tool(tool: str, tools_schema: list[dict]) -> list[str]:
    for t in tools_schema:
        if t.get("name") != tool:
            continue
        schema = t.get("inputSchema") or t.get("arguments") or {}
        return list(schema.get("required") or [])
    return []


def args_satisfy_required(tool: str, arguments: dict, tools_schema: list[dict]) -> tuple[bool, str]:
    req = required_args_for_tool(tool, tools_schema)
    for k in req:
        v = arguments.get(k)
        if v is None or v == "" or v in ("<cloudId>", "<need cloudId>"):
            return False, f"missing_or_placeholder:{k}"
    return True, ""


def guard_route(
    tool: str | None,
    arguments: dict | None,
    tools_schema: list[dict],
) -> tuple[str | None, dict, list[str]]:
    """
    Returns (tool, args, issues). If issues non-empty, caller should not call MCP (or escalate).
    """
    issues: list[str] = []
    allowed = {t.get("name") for t in tools_schema if t.get("name")}
    if not tool:
        return None, {}, ["no_tool"]
    if not validate_tool_name(tool, allowed):
        issues.append(f"unknown_tool:{tool}")
        return None, {}, issues
    args = normalize_cloud_id(dict(arguments or {}))
    ok, msg = args_satisfy_required(tool, args, tools_schema)
    if not ok:
        issues.append(msg)
    return tool, args, issues
