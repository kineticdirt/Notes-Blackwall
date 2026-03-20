#!/usr/bin/env python3
"""
Microsearch architecture smoke probe — runs alongside main retrieval-eval without using Anthropic.

Flow: quest -> score chunks (lexical) -> optional Ollama micro-summarizer -> print answer + metadata.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def score_chunk(query_terms: set[str], chunk: str) -> float:
    if not query_terms:
        return 0.0
    terms = set(tokenize(chunk))
    if not terms:
        return 0.0
    overlap = len(query_terms & terms)
    return overlap / (len(query_terms) ** 0.5 + 1e-6)


def default_chunks() -> list[str]:
    return [
        "Microsearch uses a small local model for routing, summarization, and tool intent.",
        "The main LLM can defer retrieval and CLI planning to reduce token use.",
        "If MCP is unavailable, direct filesystem and subprocess tools still work.",
        "Retrieval-eval run_sequential.py measures needle-in-haystack and answer quality with Claude.",
    ]


def load_corpus(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"\n\s*\n", raw.strip())
    chunks = [p.strip() for p in parts if p.strip()]
    return chunks if chunks else [raw.strip()]


def retrieve(query: str, chunks: list[str], k: int) -> list[tuple[float, int, str]]:
    q_terms = set(tokenize(query))
    scored = [(score_chunk(q_terms, c), i, c) for i, c in enumerate(chunks)]
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def heuristic_answer(query: str, top_chunks: list[str]) -> str:
    """No LLM: first sentence-ish line from best chunk."""
    if not top_chunks:
        return "(no context)"
    text = top_chunks[0]
    for line in text.split("\n"):
        s = line.strip()
        if len(s) > 20:
            return s[:500]
    return text[:500]


def ollama_summarize(model: str, query: str, context: str, host: str) -> tuple[str, int]:
    """Returns (text, latency_ms). Raises on failure."""
    url = f"{host.rstrip('/')}/api/generate"
    prompt = (
        "You are a compact assistant. Answer ONLY from the context. "
        "One or two sentences. If unknown, say you cannot tell from context.\n\n"
        f"Context:\n{context[:6000]}\n\nQuestion: {query}\n\nAnswer:"
    )
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": 256}}
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    ms = int((time.perf_counter() - t0) * 1000)
    return (data.get("response") or "").strip(), ms


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsearch probe (local retrieval + optional Ollama).")
    parser.add_argument("--query", "-q", required=True, help="User question (quest).")
    parser.add_argument("--k", type=int, default=3, help="Top-k chunks to pass to summarizer.")
    parser.add_argument("--corpus", type=Path, default=None, help="Optional text file (paragraphs = chunks).")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama for micro answer (not Anthropic).")
    parser.add_argument(
        "--ollama-host",
        default="http://127.0.0.1:11434",
        help="Ollama API base URL.",
    )
    args = parser.parse_args()

    chunks = load_corpus(args.corpus) if args.corpus else default_chunks()
    ranked = retrieve(args.query, chunks, args.k)
    top_texts = [c for _, _, c in ranked if _ > 0] or [c for _, _, c in ranked]
    context_block = "\n\n---\n\n".join(top_texts)

    print("=== Microsearch probe (no Claude) ===", flush=True)
    print(f"Chunks: {len(chunks)} | top-k scores: {[round(s, 3) for s, _, _ in ranked]}", flush=True)

    model = __import__("os").environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")

    if args.ollama:
        try:
            ans, ms = ollama_summarize(model, args.query, context_block, args.ollama_host)
            print(f"Micro-model ({model}) latency_ms: {ms}", flush=True)
            print(f"Answer:\n{ans}", flush=True)
        except urllib.error.URLError as e:
            print(f"Ollama unavailable ({e}); falling back to heuristic.", file=sys.stderr, flush=True)
            print(f"Answer (heuristic):\n{heuristic_answer(args.query, top_texts)}", flush=True)
    else:
        print("(pass --ollama + running Ollama for true micro-LLM path)", flush=True)
        print(f"Answer (heuristic):\n{heuristic_answer(args.query, top_texts)}", flush=True)

    print("\n--- Top chunks (for manual 'final ask') ---", flush=True)
    for i, (sc, _, txt) in enumerate(ranked, 1):
        preview = txt.replace("\n", " ")[:200]
        print(f"  {i}. score={sc:.3f} | {preview}...", flush=True)


if __name__ == "__main__":
    main()
