"""
Nano model (SmolLM3-3B) for intent → tool + arguments.
Uses Hugging Face transformers pipeline; optional dependency.

Set ATLASSIAN_NANO_ADAPTER to a LoRA dir from train_atlassian_intent_nano.py to use
Atlassian-only SFT (JSON-only routing prompt; matches atlassian_intent_router_dataset).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

SMOL_MODEL = "HuggingFaceTB/SmolLM3-3B-Base"

_pipe = None
_adapter_path_loaded: str | None = None


def _get_pipeline():
    global _pipe, _adapter_path_loaded
    adapter = os.environ.get("ATLASSIAN_NANO_ADAPTER", "").strip()
    if adapter and not Path(adapter).is_dir():
        adapter = ""
    if _pipe is not None and adapter == (_adapter_path_loaded or ""):
        return _pipe
    _pipe = None
    _adapter_path_loaded = adapter or None
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        if adapter:
            tok = AutoTokenizer.from_pretrained(adapter, trust_remote_code=True)
            if tok.pad_token is None:
                tok.pad_token = tok.eos_token
            base = AutoModelForCausalLM.from_pretrained(SMOL_MODEL, device_map="auto", trust_remote_code=True)
            from peft import PeftModel
            model = PeftModel.from_pretrained(base, adapter)
            model.eval()
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tok,
                device_map="auto",
            )
        else:
            _pipe = pipeline("text-generation", model=SMOL_MODEL, device_map="auto")
    except Exception as e:
        raise RuntimeError(
            f"SmolLM3 not available. Install: pip install transformers torch accelerate peft. Error: {e}"
        ) from e
    return _pipe


def _tools_to_prompt_section(tools: list[dict]) -> str:
    lines = []
    for t in tools[:30]:  # cap to avoid overflow
        name = t.get("name", "")
        desc = (t.get("description") or "").strip()
        schema = t.get("inputSchema", t.get("arguments", {}))
        req = schema.get("required", [])
        props = schema.get("properties", {})
        args_desc = ", ".join(f"{k}" + (" (required)" if k in req else "") for k in (list(props.keys())[:8]))
        lines.append(f"- {name}: {desc[:200]}. Args: {args_desc}")
    return "\n".join(lines) if lines else "No tools."


def intent_to_tool(intent: str, tools: list[dict], max_new_tokens: int = 256) -> tuple[str | None, dict]:
    """
    Use SmolLM3-3B to map user intent to one tool name and arguments (JSON).
    Returns (tool_name, arguments) or (None, {}) if parse fails.
    """
    pipe = _get_pipeline()
    names = [t.get("name") for t in tools if t.get("name")]
    if os.environ.get("ATLASSIAN_NANO_ADAPTER", "").strip() and Path(
        os.environ["ATLASSIAN_NANO_ADAPTER"]
    ).is_dir():
        tools_line = "Available tools: " + ", ".join(sorted(names)) + "."
        prompt = (
            'You are an Atlassian MCP router. Reply with ONLY a JSON object with keys '
            '"tool" (exact tool name) and "arguments" (object). No markdown, no explanation.\n'
            + tools_line
            + f'\nUser request: {intent}\nJSON:'
        )
    else:
        tools_blob = _tools_to_prompt_section(tools)
        prompt = f"""You are a router. Given the user intent, output exactly one JSON object with "tool" (exact tool name) and "arguments" (object). Only use these tools:
{tools_blob}

User intent: {intent}

Output only valid JSON, no markdown. Example: {{"tool":"getJiraIssue","arguments":{{"cloudId":"x","issueIdOrKey":"PROJ-1"}}}}
JSON:"""
    out = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
        truncation=True,
        max_length=2048,
    )
    if not out or not isinstance(out, list):
        return None, {}
    text = out[0].get("generated_text", "") if isinstance(out[0], dict) else str(out[0])
    if not text:
        return None, {}
    # Strip prompt from response (model echoes input)
    if prompt in text:
        text = text[len(prompt):]
    text = text.strip()
    # Extract JSON
    for start in ("{", "```json"):
        i = text.find(start)
        if i != -1:
            text = text[i:]
            if text.startswith("```"):
                text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
            break
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # Try to find first {...}
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
        if m:
            try:
                obj = json.loads(m.group(0))
            except json.JSONDecodeError:
                return None, {}
        else:
            return None, {}
    name = obj.get("tool") or obj.get("name")
    args = obj.get("arguments") or obj.get("args") or {}
    if not name or not isinstance(args, dict):
        return None, {}
    return str(name), args
