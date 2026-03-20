"""
Load real QA datasets (e.g. from Hugging Face) for retrieval-eval.
Each source yields (query, context, success_markers) per example.
Used as a permutation axis: dataset_source in DATASET_SOURCES.
"""
from __future__ import annotations
from typing import Iterator, List, Tuple

# External dataset IDs (HF path or config name). Internal names (default, work, cequence_cs) are handled by evals.py.
EXTERNAL_DATASET_SOURCES = ("squad", "squad_v2", "boolq", "race_middle")

# Cache: dataset_name -> list of (query, context, markers)
_cache: dict[str, List[Tuple[str, str, List[str]]]] = {}


def _squad_markers(answers: dict) -> List[str]:
    """Extract answer texts from SQuAD answers dict."""
    if not answers or "text" not in answers:
        return []
    texts = answers["text"]
    if isinstance(texts, list):
        return [t.strip() for t in texts if t and isinstance(t, str)]
    return [str(texts).strip()]


def _load_squad(split: str = "validation", max_examples: int = 500) -> List[Tuple[str, str, List[str]]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return []
    ds = load_dataset("rajpurkar/squad", split=split)
    out: List[Tuple[str, str, List[str]]] = []
    for i, row in enumerate(ds):
        if i >= max_examples:
            break
        q = (row.get("question") or "").strip()
        ctx = (row.get("context") or "").strip()
        markers = _squad_markers(row.get("answers") or {})
        if q and ctx:
            out.append((q, ctx, markers if markers else [""]))
    return out


def _load_squad_v2(split: str = "validation", max_examples: int = 500) -> List[Tuple[str, str, List[str]]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return []
    ds = load_dataset("rajpurkar/squad_v2", split=split)
    out: List[Tuple[str, str, List[str]]] = []
    for i, row in enumerate(ds):
        if i >= max_examples:
            break
        q = (row.get("question") or "").strip()
        ctx = (row.get("context") or "").strip()
        answers = row.get("answers") or {}
        markers = _squad_markers(answers)
        if q and ctx:
            out.append((q, ctx, markers if markers else [""]))
    return out


def _load_boolq(split: str = "validation", max_examples: int = 500) -> List[Tuple[str, str, List[str]]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return []
    try:
        ds = load_dataset("google/boolq", split=split)
    except Exception:
        return []
    out: List[Tuple[str, str, List[str]]] = []
    for i, row in enumerate(ds):
        if i >= max_examples:
            break
        q = (row.get("question") or "").strip()
        ctx = (row.get("passage") or "").strip()
        ans = row.get("answer")
        if ans is True:
            markers = ["true", "yes"]
        elif ans is False:
            markers = ["false", "no"]
        else:
            markers = [str(ans).lower()] if ans is not None else [""]
        if q and ctx:
            out.append((q, ctx, markers))
    return out


def _load_race(split: str = "validation", max_examples: int = 500) -> List[Tuple[str, str, List[str]]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return []
    try:
        ds = load_dataset("EleutherAI/race", "middle", split=split)
    except Exception:
        return []
    out: List[Tuple[str, str, List[str]]] = []
    for i, row in enumerate(ds):
        if i >= max_examples:
            break
        q = (row.get("question") or "").strip()
        ctx = (row.get("article") or "").strip()
        options = row.get("options") or []
        answer_idx = row.get("answer")
        if isinstance(answer_idx, (int, str)):
            idx = int(answer_idx) if isinstance(answer_idx, str) and answer_idx.isdigit() else answer_idx
            if 0 <= idx < len(options):
                markers = [options[idx]]
            else:
                markers = list(options) if options else [""]
        else:
            markers = list(options) if options else [""]
        if q and ctx:
            out.append((q, ctx, markers))
    return out


def _load_source(source: str, max_examples: int = 500) -> List[Tuple[str, str, List[str]]]:
    if source == "squad":
        return _load_squad(max_examples=max_examples)
    if source == "squad_v2":
        return _load_squad_v2(max_examples=max_examples)
    if source == "boolq":
        return _load_boolq(max_examples=max_examples)
    if source == "race_middle":
        return _load_race(max_examples=max_examples)
    return []


def get_external_example_count(dataset_source: str, max_examples: int = 500) -> int:
    """Number of examples available for this external source (capped by max_examples)."""
    if dataset_source not in EXTERNAL_DATASET_SOURCES:
        return 0
    key = f"{dataset_source}_{max_examples}"
    if key not in _cache:
        _cache[key] = _load_source(dataset_source, max_examples=max_examples)
    return len(_cache[key])


def iter_external_examples(
    dataset_source: str,
    max_examples: int = 500,
) -> Iterator[Tuple[str, str, List[str]]]:
    """Yield (query, context, success_markers) for each example."""
    if dataset_source not in EXTERNAL_DATASET_SOURCES:
        return
    key = f"{dataset_source}_{max_examples}"
    if key not in _cache:
        _cache[key] = _load_source(dataset_source, max_examples=max_examples)
    for t in _cache[key]:
        yield t


def get_external_example(
    dataset_source: str,
    example_index: int,
    max_examples: int = 500,
) -> Tuple[str, str, List[str]] | None:
    """Return (query, context, success_markers) for the given example index, or None if out of range."""
    if dataset_source not in EXTERNAL_DATASET_SOURCES:
        return None
    key = f"{dataset_source}_{max_examples}"
    if key not in _cache:
        _cache[key] = _load_source(dataset_source, max_examples=max_examples)
    examples = _cache[key]
    if example_index < 0 or example_index >= len(examples):
        return None
    return examples[example_index]
