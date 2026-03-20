"""
Intent suite for Defender mitigator cache API — uses shared test cases.
"""
from __future__ import annotations

from experiments.defender_cache_test_cases import DefenderTestCase, get_defender_test_cases


def get_defender_cache_intents() -> list[DefenderTestCase]:
    return get_defender_test_cases()
