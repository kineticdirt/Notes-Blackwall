"""
Curated prompt injection patterns for rule-based detection.

Enterprise-safe: patterns derived from published attack taxonomies
and common LLM jailbreak/injection phrases. Kept minimal to reduce false positives.
"""

import re
from typing import List, Tuple

# High-confidence phrases (instruction override / role hijack)
INSTRUCTION_OVERRIDE_PHRASES: List[str] = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget your instructions",
    "forget everything above",
    "ignore the above",
    "disregard the above",
    "new instructions:",
    "override:",
    "system:",
    "you are now",
    "act as if",
    "pretend you are",
    "from now on you",
    "your new role is",
    "no longer an ai",
    "stop being",
    "do not follow",
    "bypass your",
    "override your",
    "ignore your",
    "disregard your",
    "forget your",
    "jailbreak",
    "dan mode",
    "developer mode",
    "unfiltered mode",
]

# Delimiter-style attacks (fake system/user boundaries)
DELIMITER_PATTERNS: List[Tuple[str, str]] = [
    (r"\[system\]", "system bracket"),
    (r"<system>", "system angle"),
    (r"###\s*system\s*:", "system markdown"),
    (r"---\s*new\s*instructions\s*---", "new instructions delimiter"),
    (r"\[INST\]\s*.*?\[/INST\]", "instruction tag"),
    (r"<\|im_start\|>system", "chatml system"),
    (r"<\|system\|>", "system pipe"),
    (r"\{\{\s*system\s*\}\}", "system template"),
]

# Regex compiled once
_COMPILED_DELIMITERS: List[Tuple[re.Pattern, str]] = [
    (re.compile(p, re.IGNORECASE), name) for p, name in DELIMITER_PATTERNS
]


def match_instruction_override(text: str) -> List[Tuple[int, int, str]]:
    """
    Return list of (start, end, phrase) for instruction-override phrase matches.
    """
    text_lower = text.lower()
    matches: List[Tuple[int, int, str]] = []
    for phrase in INSTRUCTION_OVERRIDE_PHRASES:
        start = 0
        while True:
            idx = text_lower.find(phrase, start)
            if idx == -1:
                break
            matches.append((idx, idx + len(phrase), phrase))
            start = idx + 1
    return matches


def match_delimiter_attacks(text: str) -> List[Tuple[int, int, str]]:
    """
    Return list of (start, end, pattern_name) for delimiter-style injection matches.
    """
    matches: List[Tuple[int, int, str]] = []
    for pattern, name in _COMPILED_DELIMITERS:
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end(), name))
    return matches


def get_all_matches(text: str) -> List[Tuple[int, int, str]]:
    """
    All rule-based matches: instruction override + delimiter.
    Each item is (start, end, label).
    """
    out: List[Tuple[int, int, str]] = []
    out.extend(match_instruction_override(text))
    out.extend(match_delimiter_attacks(text))
    out.sort(key=lambda x: (x[0], x[1]))
    return out
