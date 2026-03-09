"""
Tests for reverse CAPTCHA: verify bot-like behavior is flagged, human-like is not.

Run from repo root: python -m pytest blackwall/reverse_captcha/test_reverse_captcha.py -v
"""

import time
import pytest
from blackwall.reverse_captcha.challenges import (
    ReactionTimeChallenge,
    ProofOfWorkChallenge,
    ConsistencyChallenge,
    HUMAN_MIN_REACTION_MS,
)
from blackwall.reverse_captcha.gate import ReverseCaptchaGate, Verdict, ChallengeResult


# --- Reaction time ---


def test_reaction_time_bot_likely_when_sub_threshold():
    """If response comes in < 100ms, signal bot (impossible for human)."""
    c = ReactionTimeChallenge(created_at_ns=time.perf_counter_ns(), threshold_ms=HUMAN_MIN_REACTION_MS)
    # Simulate response 10ms later (bot speed)
    responded_ns = c.created_at_ns + 10 * 1_000_000
    assert c.is_bot_likely(responded_ns) is True
    assert c.response_time_ms(responded_ns) < HUMAN_MIN_REACTION_MS


def test_reaction_time_human_likely_when_above_threshold():
    """If response comes in > 100ms, no bot signal."""
    c = ReactionTimeChallenge(created_at_ns=time.perf_counter_ns(), threshold_ms=HUMAN_MIN_REACTION_MS)
    responded_ns = c.created_at_ns + 250 * 1_000_000  # 250ms
    assert c.is_bot_likely(responded_ns) is False
    assert c.response_time_ms(responded_ns) >= HUMAN_MIN_REACTION_MS


def test_gate_evaluate_reaction_time_bot():
    """Gate returns BOT_LIKELY when reaction is sub-human."""
    gate = ReverseCaptchaGate()
    created = time.perf_counter_ns()
    responded = created + 15 * 1_000_000  # 15ms
    r = gate.evaluate_reaction_time(created, responded)
    assert r.verdict == Verdict.BOT_LIKELY
    assert "reaction_time_sub_human" in r.signals


def test_gate_evaluate_reaction_time_human():
    """Gate returns HUMAN_LIKELY when reaction is above threshold."""
    gate = ReverseCaptchaGate()
    created = time.perf_counter_ns()
    responded = created + 300 * 1_000_000  # 300ms
    r = gate.evaluate_reaction_time(created, responded)
    assert r.verdict == Verdict.HUMAN_LIKELY
    assert not r.signals


# --- Proof of work ---


def test_pow_solve_and_verify():
    """PoW is solvable by script; verification accepts correct answer."""
    c = ProofOfWorkChallenge.create(leading_zero_nibbles=4)  # keep test fast
    answer = c.solve()
    valid, reason = c.verify(answer, max_age_seconds=None)
    assert valid is True
    assert reason == "ok"


def test_pow_reject_invalid():
    """PoW rejects wrong answer."""
    c = ProofOfWorkChallenge.create(leading_zero_nibbles=4)
    valid, reason = c.verify("wrong", max_age_seconds=None)
    assert valid is False
    assert reason == "invalid_pow"


def test_gate_evaluate_pow_valid_is_bot_signal():
    """Submitting valid PoW is treated as bot (human cannot compute)."""
    gate = ReverseCaptchaGate(pow_leading_zero_nibbles=4)
    c = ProofOfWorkChallenge.create(leading_zero_nibbles=4)
    answer = c.solve()
    r = gate.evaluate_pow(c.nonce, answer, leading_zero_nibbles=4, challenge_created_at_ns=None)
    assert r.verdict == Verdict.BOT_LIKELY
    assert "valid_pow_submitted" in r.signals


def test_gate_evaluate_pow_invalid_inconclusive():
    """Invalid PoW submission does not imply human (inconclusive)."""
    gate = ReverseCaptchaGate()
    c = ProofOfWorkChallenge.create(leading_zero_nibbles=4)
    r = gate.evaluate_pow(c.nonce, "garbage", leading_zero_nibbles=4)
    assert r.verdict == Verdict.INCONCLUSIVE


# --- Consistency ---


def test_consistency_identical_answers_bot_signal():
    """Identical answers to same question (different wording) = bot signal."""
    c = ConsistencyChallenge(question_a="What is 2+2?", question_b="Compute 2 plus 2.")
    assert c.is_bot_likely("4", "4") is True


def test_consistency_different_answers_human_likely():
    """Different answers = no bot signal."""
    c = ConsistencyChallenge(question_a="What is 2+2?", question_b="Compute 2 plus 2.")
    assert c.is_bot_likely("4", "Four") is False
    assert c.is_bot_likely("4", "5") is False


def test_gate_evaluate_consistency_bot():
    """Gate returns BOT_LIKELY for identical answers."""
    gate = ReverseCaptchaGate()
    r = gate.evaluate_consistency("2+2?", "two plus two?", "4", "4")
    assert r.verdict == Verdict.BOT_LIKELY
    assert "identical_answers" in r.signals


def test_gate_evaluate_consistency_human():
    """Gate returns HUMAN_LIKELY for different answers."""
    gate = ReverseCaptchaGate()
    r = gate.evaluate_consistency("2+2?", "two plus two?", "4", "Four")
    assert r.verdict == Verdict.HUMAN_LIKELY


# --- Combined ---


def test_combine_results_any_bot_is_bot():
    """One BOT_LIKELY in combined results yields BOT_LIKELY."""
    gate = ReverseCaptchaGate()
    created = time.perf_counter_ns()
    fast = gate.evaluate_reaction_time(created, created + 10 * 1_000_000)
    slow = gate.evaluate_reaction_time(created, created + 300 * 1_000_000)
    combined = gate.combine_results([slow, fast])
    assert combined.verdict == Verdict.BOT_LIKELY
    assert combined.is_bot_likely


def test_combine_results_all_human_is_human():
    """All HUMAN_LIKELY yields HUMAN_LIKELY."""
    gate = ReverseCaptchaGate()
    r1 = gate.evaluate_consistency("A?", "B?", "x", "y")
    created = time.perf_counter_ns()
    r2 = gate.evaluate_reaction_time(created, created + 200 * 1_000_000)
    combined = gate.combine_results([r1, r2])
    assert combined.verdict == Verdict.HUMAN_LIKELY
