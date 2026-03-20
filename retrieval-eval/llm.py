"""Call Claude for answer; optional 'thinking' = reason then answer."""
from __future__ import annotations
import time
from typing import List

from store import Node

# Retries for transient connection/timeout errors
MAX_LLM_RETRIES = 3
RETRY_BACKOFF_SEC = [2, 4, 8]


def check_api_connectivity(api_key: str) -> None:
    """Verify API key and network reachability. Raises on failure."""
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=10,
        messages=[{"role": "user", "content": "Reply with the single word: OK"}],
    )


def answer_with_context(
    api_key: str,
    query: str,
    nodes: List[Node],
    thinking: bool,
) -> tuple[str, dict]:
    """
    Return (answer_string, usage_dict).
    usage_dict has input_tokens, output_tokens, total_tokens (0 on error).
    """
    context = "\n\n".join(
        n.content.get("text", str(n.content)) for n in nodes[:5]
    )
    if thinking:
        system = (
            "You are a precise assistant. Given the context below, reason step-by-step, "
            "then output exactly one line: Final answer: <your answer>"
        )
        user = f"Context:\n{context}\n\nQuestion: {query}\n\nReason step-by-step, then give one line: Final answer: ..."
    else:
        system = "Answer briefly based only on the given context."
        user = f"Context:\n{context}\n\nQuestion: {query}"

    from anthropic import Anthropic

    empty_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    last_error = None
    for attempt in range(MAX_LLM_RETRIES):
        try:
            client = Anthropic(api_key=api_key)
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = (msg.content[0].text if msg.content else "").strip()
            if thinking and "Final answer:" in text:
                text = text.split("Final answer:")[-1].strip()
            answer = text or "(no answer)"
            usage = empty_usage.copy()
            if getattr(msg, "usage", None) is not None:
                u = msg.usage
                usage["input_tokens"] = getattr(u, "input_tokens", 0) or 0
                usage["output_tokens"] = getattr(u, "output_tokens", 0) or 0
                usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
            return answer, usage
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_retryable = (
                "connection" in err_str
                or "timeout" in err_str
                or "timed out" in err_str
                or "interrupted" in err_str
            )
            if not is_retryable or attempt == MAX_LLM_RETRIES - 1:
                return f"(error: {e})", empty_usage
            time.sleep(RETRY_BACKOFF_SEC[attempt])
    return f"(error: {last_error})", empty_usage


def write_failure_report(
    api_key: str,
    error_message: str,
    context: dict,
) -> dict:
    """
    Ask the model to write a short failure report and meta-analysis of why the run failed.
    Returns {"failure_report": str, "failure_meta_analysis": str, "flag_for_investigation": True}
    or {"failure_report_error": str, "flag_for_investigation": True} if the report call itself fails.
    """
    from anthropic import Anthropic

    ctx_str = "\n".join(f"  {k}: {v}" for k, v in sorted(context.items()) if v is not None)
    user = (
        "A retrieval+LLM eval run failed. Your job: write a brief failure report and meta-analysis.\n\n"
        f"Error: {error_message}\n\nContext:\n{ctx_str}\n\n"
        "In 2–4 short sentences: (1) What went wrong? (2) Why might the system have failed "
        "(e.g. API/network, retrieval, prompt, or config)? Output exactly:\n"
        "REPORT: <your 1-2 sentence summary of what went wrong>\n"
        "META: <your 1-2 sentence analysis of why the system might have failed>"
    )
    try:
        client = Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system="You are an analyst summarizing eval failures. Be concise and factual.",
            messages=[{"role": "user", "content": user}],
        )
        text = (msg.content[0].text if msg.content else "").strip()
        report, meta = "", ""
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("REPORT:"):
                report = line.split(":", 1)[-1].strip()
            elif line.upper().startswith("META:"):
                meta = line.split(":", 1)[-1].strip()
        if not report and not meta:
            report = text[:500] if text else "(no report generated)"
        return {
            "failure_report": report or "(no report)",
            "failure_meta_analysis": meta or "(no meta-analysis)",
            "flag_for_investigation": True,
        }
    except Exception as e:
        return {
            "failure_report_error": str(e),
            "flag_for_investigation": True,
        }
