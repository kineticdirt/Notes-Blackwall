"""
Reverse CAPTCHA gate: issue challenges and evaluate responses.

Returns a non-binding "bot_likely" / "human_likely" signal (smoking gun, not proof).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from blackwall.reverse_captcha.challenges import (
    ReactionTimeChallenge,
    ProofOfWorkChallenge,
    ConsistencyChallenge,
    HUMAN_MIN_REACTION_MS,
)


class Verdict(str, Enum):
    HUMAN_LIKELY = "human_likely"
    BOT_LIKELY = "bot_likely"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ChallengeResult:
    """Result of a single challenge or combined gate."""

    verdict: Verdict
    signals: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def is_bot_likely(self) -> bool:
        return self.verdict == Verdict.BOT_LIKELY


@dataclass
class ReverseCaptchaGate:
    """
    Issues and verifies reverse CAPTCHAs.
    Use as a single smoking gun: if any signal fires, treat as bot_likely.
    """

    reaction_threshold_ms: float = HUMAN_MIN_REACTION_MS
    pow_leading_zero_nibbles: int = 5
    # Require at least one smoking gun to say BOT_LIKELY
    require_any_signal: bool = True

    def evaluate_reaction_time(
        self,
        challenge_created_at_ns: int,
        response_received_at_ns: int,
    ) -> ChallengeResult:
        """Evaluate reaction time. Sub-threshold = bot signal."""
        c = ReactionTimeChallenge(created_at_ns=challenge_created_at_ns, threshold_ms=self.reaction_threshold_ms)
        if c.is_bot_likely(response_received_at_ns):
            return ChallengeResult(
                verdict=Verdict.BOT_LIKELY,
                signals=["reaction_time_sub_human"],
                details={"response_time_ms": c.response_time_ms(response_received_at_ns), "threshold_ms": self.reaction_threshold_ms},
            )
        return ChallengeResult(verdict=Verdict.HUMAN_LIKELY, signals=[], details={"response_time_ms": c.response_time_ms(response_received_at_ns)})

    def evaluate_pow(
        self,
        nonce: str,
        answer: str,
        leading_zero_nibbles: Optional[int] = None,
        challenge_created_at_ns: Optional[int] = None,
    ) -> ChallengeResult:
        """
        Evaluate proof-of-work. Valid solution is trivial for a script, impossible for human.
        So if they return a valid solution at all, we treat as bot signal (smoking gun).
        """
        n = leading_zero_nibbles if leading_zero_nibbles is not None else self.pow_leading_zero_nibbles
        c = ProofOfWorkChallenge(nonce=nonce, leading_zero_nibbles=n, created_at_ns=challenge_created_at_ns or 0)
        valid, reason = c.verify(answer, max_age_seconds=60.0 if challenge_created_at_ns else None)
        if not valid:
            return ChallengeResult(verdict=Verdict.INCONCLUSIVE, signals=[], details={"pow": reason})
        # Valid PoW submitted = strong bot signal (human cannot compute this)
        return ChallengeResult(
            verdict=Verdict.BOT_LIKELY,
            signals=["valid_pow_submitted"],
            details={"pow": "valid"},
        )

    def evaluate_consistency(self, question_a: str, question_b: str, answer_a: str, answer_b: str) -> ChallengeResult:
        """Identical answers to same question in different words = bot signal."""
        c = ConsistencyChallenge(question_a=question_a, question_b=question_b)
        if c.is_bot_likely(answer_a, answer_b):
            return ChallengeResult(
                verdict=Verdict.BOT_LIKELY,
                signals=["identical_answers"],
                details={"question_a": question_a[:50], "question_b": question_b[:50]},
            )
        return ChallengeResult(verdict=Verdict.HUMAN_LIKELY, signals=[], details={})

    def combine_results(self, results: list[ChallengeResult]) -> ChallengeResult:
        """If any result is BOT_LIKELY, overall is BOT_LIKELY (smoking gun)."""
        all_signals: list[str] = []
        all_details: dict = {}
        for r in results:
            all_signals.extend(r.signals)
            all_details.update(r.details)
        if any(r.verdict == Verdict.BOT_LIKELY for r in results):
            return ChallengeResult(verdict=Verdict.BOT_LIKELY, signals=all_signals, details=all_details)
        if all(r.verdict == Verdict.HUMAN_LIKELY for r in results):
            return ChallengeResult(verdict=Verdict.HUMAN_LIKELY, signals=[], details=all_details)
        return ChallengeResult(verdict=Verdict.INCONCLUSIVE, signals=all_signals, details=all_details)
