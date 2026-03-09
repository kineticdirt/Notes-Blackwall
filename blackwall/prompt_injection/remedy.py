"""
Remedy strategies when prompt injection is detected.

- Block: do not pass input to main model; return a safe response.
- Sanitize: remove or mask matched spans, then pass remainder to main model.
"""

from dataclasses import dataclass
from typing import List, Tuple

from .patterns import get_all_matches


@dataclass
class RemedyResult:
    """Result of applying a remedy to user input."""

    safe_text: str
    was_modified: bool
    removed_spans: List[Tuple[int, int, str]]


def merge_overlapping(spans: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
    """Merge overlapping (start, end, label) spans."""
    if not spans:
        return []
    sorted_spans = sorted(spans, key=lambda x: (x[0], x[1]))
    merged = [sorted_spans[0]]
    for s, e, label in sorted_spans[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e), merged[-1][2])
        else:
            merged.append((s, e, label))
    return merged


def sanitize(text: str) -> RemedyResult:
    """
    Remove detected injection spans from text. Non-overlapping removal
    from end to start to preserve indices.
    """
    matches = get_all_matches(text)
    merged = merge_overlapping(matches)
    if not merged:
        return RemedyResult(safe_text=text, was_modified=False, removed_spans=[])

    # Build result by taking segments that are not in any span
    result_parts: List[str] = []
    pos = 0
    for s, e, label in merged:
        if s > pos:
            result_parts.append(text[pos:s])
        pos = e
    if pos < len(text):
        result_parts.append(text[pos:])

    safe_text = "".join(result_parts).strip()
    return RemedyResult(
        safe_text=safe_text,
        was_modified=True,
        removed_spans=merged,
    )


def block_message() -> str:
    """Default message returned when input is blocked (no safe_text passed to main model)."""
    return (
        "Your message could not be processed due to a security policy. "
        "Please rephrase and avoid instruction-like or system-style text."
    )
