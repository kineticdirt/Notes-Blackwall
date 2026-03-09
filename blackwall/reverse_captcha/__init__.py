"""
Reverse CAPTCHA: challenges that are trivial for AI/scripts but impossible for humans.

Used as a non-binding "smoking gun" signal that the respondent is automated.
All logic uses stdlib only (hashlib, time, secrets).
"""

from blackwall.reverse_captcha.challenges import (
    ReactionTimeChallenge,
    ProofOfWorkChallenge,
    ConsistencyChallenge,
)
from blackwall.reverse_captcha.gate import ReverseCaptchaGate, ChallengeResult

__all__ = [
    "ReactionTimeChallenge",
    "ProofOfWorkChallenge",
    "ConsistencyChallenge",
    "ReverseCaptchaGate",
    "ChallengeResult",
]
