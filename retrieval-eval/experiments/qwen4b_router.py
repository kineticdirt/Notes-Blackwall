"""
4B Qwen instruct model for intent → tool + arguments (routing / predigestion).
Text-to-text only: no images. Uses processor + chat template + generate.

Model: JIULANG/unsloth-Qwen3.5-4B-Instruct-CitationMarker-LM (used with text-only messages).
Optional: set QWEN4B_MODEL_ID env to a text-only 4B instruct (e.g. Qwen/Qwen2.5-3B-Instruct) if you prefer.
"""
from __future__ import annotations

import json
import os
import re

QWEN4B_MODEL = os.environ.get("QWEN4B_MODEL_ID", "JIULANG/unsloth-Qwen3.5-4B-Instruct-CitationMarker-LM")

_model = None
_processor = None
_lora_path_loaded: str | None = None


def _tools_line(tools: list[dict]) -> str:
    names = [t.get("name") for t in tools if t.get("name")]
    return "Available tools: " + ", ".join(sorted(names)) + "."


def _router_prompt(intent: str, tools: list[dict]) -> str:
    sys_p = (
        'You are an MCP router. Reply with ONLY a JSON object with keys '
        '"tool" (exact tool name) and "arguments" (object). No markdown, no explanation.\n'
    )
    return sys_p + _tools_line(tools) + f'\nUser request: {intent}\nJSON:'


def _get_model():
    """Text-to-text only: processor + model, no image pipeline. Optional DEFENDER_QWEN4B_LORA PeFT adapter."""
    global _processor, _model, _lora_path_loaded
    lora_path = os.environ.get("DEFENDER_QWEN4B_LORA", "").strip()
    if _model is not None and lora_path and lora_path != _lora_path_loaded:
        _model = None
        _processor = None
        _lora_path_loaded = None
    if _model is None:
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            _processor = AutoProcessor.from_pretrained(QWEN4B_MODEL, trust_remote_code=True)
            _model = AutoModelForCausalLM.from_pretrained(
                QWEN4B_MODEL,
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception as e1:
            try:
                from transformers import AutoProcessor, AutoModelForImageTextToText
                _processor = AutoProcessor.from_pretrained(QWEN4B_MODEL, trust_remote_code=True)
                _model = AutoModelForImageTextToText.from_pretrained(
                    QWEN4B_MODEL,
                    device_map="auto",
                    trust_remote_code=True,
                )
            except Exception as e2:
                raise RuntimeError(
                    f"Qwen 4B load failed (tried CausalLM and ImageTextToText). Error: {e1}; fallback: {e2}"
                ) from e2
        if lora_path:
            from pathlib import Path
            if Path(lora_path).is_dir():
                try:
                    from peft import PeftModel
                    _model = PeftModel.from_pretrained(_model, lora_path)
                    _lora_path_loaded = lora_path
                except Exception as e:
                    raise RuntimeError(f"Failed to load DEFENDER_QWEN4B_LORA={lora_path}: {e}") from e
            else:
                _lora_path_loaded = ""
        else:
            _lora_path_loaded = ""
        _model.eval()
    return _model, _processor


def intent_to_tool(
    intent: str,
    tools: list[dict],
    max_new_tokens: int = 256,
) -> tuple[str | None, dict]:
    """
    Map user intent to (tool_name, arguments) using the 4B instruct model. Text-to-text only.
    """
    prompt = _router_prompt(intent, tools)
    model, processor = _get_model()
    messages = [{"role": "user", "content": prompt}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    gen = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    prompt_len = inputs["input_ids"].shape[-1]
    out_text = processor.decode(gen[0][prompt_len:], skip_special_tokens=True)

    text = out_text.strip()
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
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
        obj = json.loads(m.group(0)) if m else {}
    name = obj.get("tool") or obj.get("name")
    args = obj.get("arguments") or obj.get("args") or {}
    if not name or not isinstance(args, dict):
        return None, {}
    return str(name), args


def answer_from_context(context: str, query: str, max_new_tokens: int = 256) -> str:
    """
    Answer the question from the given context only. Text-to-text. Use for retrieval answer path.
    """
    model, processor = _get_model()
    prompt = (
        "Answer the question using ONLY the context below. Be brief. If the context does not contain the answer, say so.\n\n"
        f"Context:\n{context[:6000]}\n\nQuestion: {query}\n\nAnswer:"
    )
    messages = [{"role": "user", "content": prompt}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    gen = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    prompt_len = inputs["input_ids"].shape[-1]
    return processor.decode(gen[0][prompt_len:], skip_special_tokens=True).strip()


def refine_context(context: str, query: str, max_new_tokens: int = 512) -> str:
    """
    Predigestion: summarize or organize context for the main model. Text-to-text only.
    """
    model, processor = _get_model()
    prompt = (
        "Summarize the following context in a few clear sentences so that the next model can answer the question. "
        "Keep only information relevant to the question. No preamble.\n\n"
        f"Context:\n{context[:8000]}\n\nQuestion: {query}\n\nSummary:"
    )
    messages = [{"role": "user", "content": prompt}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    gen = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    prompt_len = inputs["input_ids"].shape[-1]
    return processor.decode(gen[0][prompt_len:], skip_special_tokens=True).strip()
