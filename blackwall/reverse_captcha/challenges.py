"""
Reverse CAPTCHA challenges: easy for machines, impossible for humans.

- Reaction time: humans cannot respond in < ~100ms; bots can.
- Proof-of-work: humans cannot compute hash puzzles in seconds; scripts can.
- Consistency: same question twice, different wording; identical answers suggest bot.
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional


# Human minimum simple reaction time is ~150–250ms; we flag sub-100ms as bot.
HUMAN_MIN_REACTION_MS = 100

# PoW difficulty: number of leading zero nibbles (4 bits each). 5 = 20 bits.
DEFAULT_POW_LEADING_ZERO_NIBBLES = 5


@dataclass
class ReactionTimeChallenge:
    """Challenge that only a bot can "pass" by responding too fast."""

    created_at_ns: int = field(default_factory=lambda: time.perf_counter_ns())
    threshold_ms: float = HUMAN_MIN_REACTION_MS

    def response_time_ms(self, responded_at_ns: Optional[int] = None) -> float:
        responded_at_ns = responded_at_ns or time.perf_counter_ns()
        return (responded_at_ns - self.created_at_ns) / 1e6

    def is_bot_likely(self, responded_at_ns: Optional[int] = None) -> bool:
        """True if response was faster than humanly possible (smoking gun)."""
        return self.response_time_ms(responded_at_ns) < self.threshold_ms


@dataclass
class ProofOfWorkChallenge:
    """
    Client must find x such that hash(nonce || x) starts with N zero nibbles.
    Trivial for a script; impossible for a human in reasonable time.
    """

    nonce: str
    leading_zero_nibbles: int = DEFAULT_POW_LEADING_ZERO_NIBBLES
    created_at_ns: int = field(default_factory=lambda: time.perf_counter_ns())

    @classmethod
    def create(cls, leading_zero_nibbles: int = DEFAULT_POW_LEADING_ZERO_NIBBLES) -> "ProofOfWorkChallenge":
        return cls(nonce=secrets.token_hex(16), leading_zero_nibbles=leading_zero_nibbles)

    def _hash(self, x: str) -> str:
        return hashlib.sha256(f"{self.nonce}:{x}".encode()).hexdigest()

    def verify(self, answer: str, max_age_seconds: Optional[float] = 60.0) -> tuple[bool, str]:
        """
        Returns (valid, reason).
        If valid, that's a bot signal (human cannot compute this).
        Pass max_age_seconds=None to skip expiry check.
        """
        h = self._hash(answer)
        prefix = "0" * self.leading_zero_nibbles
        if not h.startswith(prefix):
            return False, "invalid_pow"
        if max_age_seconds is not None and self.created_at_ns > 0:
            age_seconds = (time.perf_counter_ns() - self.created_at_ns) / 1e9
            if age_seconds > max_age_seconds:
                return False, "expired"
        return True, "ok"

    def solve(self) -> str:
        """Solve the puzzle (for bots / testing). Do not call in human path."""
        x = 0
        prefix = "0" * self.leading_zero_nibbles
        while True:
            candidate = str(x)
            if self._hash(candidate).startswith(prefix):
                return candidate
            x += 1


@dataclass
class ConsistencyChallenge:
    """
    Two semantically identical questions with different wording.
    Character-identical answers are a bot signal (LLMs often reproduce token-by-token).
    """

    question_a: str
    question_b: str
    # Optional: if we have expected "human" variance (e.g. edit distance), we could use it.

    def is_bot_likely(self, answer_a: str, answer_b: str) -> bool:
        """True if answers are identical (normalized). Strong bot signal."""
        a = answer_a.strip().lower()
        b = answer_b.strip().lower()
        if not a or not b:
            return False
        return a == b
