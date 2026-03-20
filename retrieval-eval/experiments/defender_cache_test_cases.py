"""
Shared Defender cache test intents (same as training/eval set).
Import from defender_intent_router_dataset and defender_cache_intents.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DefenderTestCase:
    intent: str
    expected_tool: str
    expected_args_subset: dict[str, Any]


# Single source of truth for eval + dataset generation.
#
# Each case exercises: (1) natural phrasing toward one of four MCP tools, (2) args {} as in prod
# for these read-only cache endpoints. Expand here + re-run defender_intent_router_dataset.py
# before LoRA; add paraphrases to stress keyword and micro models toward ~MCP parity.
DEFENDER_TEST_CASES: list[DefenderTestCase] = [
    # --- cacheInfo: summary / counts only (not full dump) ---
    DefenderTestCase("mitigator cache info", "cacheInfo", {}),
    DefenderTestCase("Get mitigator cache info.", "cacheInfo", {}),
    DefenderTestCase("Show cache summary.", "cacheInfo", {}),
    DefenderTestCase("What's in the mitigator cache summary?", "cacheInfo", {}),
    DefenderTestCase("Give me high-level cache stats.", "cacheInfo", {}),
    DefenderTestCase("How many entries are in the policy map and ip map?", "cacheInfo", {}),
    DefenderTestCase("Show cache-summary counts.", "cacheInfo", {}),
    DefenderTestCase("defender cache overview", "cacheInfo", {}),
    DefenderTestCase("mitigator cache info please", "cacheInfo", {}),
    DefenderTestCase("mitigator __cq cache summary counts only", "cacheInfo", {}),
    DefenderTestCase("Read cache-summary without dumping bodies", "cacheInfo", {}),
    DefenderTestCase("What are the fpv2-map and policy-map counts?", "cacheInfo", {}),
    # --- cacheIpMap: IPv4/IPv6 entries and per-IP policies ---
    DefenderTestCase("mitigator cache ip-map", "cacheIpMap", {}),
    DefenderTestCase("Get the IP map from the cache.", "cacheIpMap", {}),
    DefenderTestCase("Show IPv4 and IPv6 map.", "cacheIpMap", {}),
    DefenderTestCase("List blocked IPs and their policies.", "cacheIpMap", {}),
    DefenderTestCase("Which IP addresses are in the cache?", "cacheIpMap", {}),
    DefenderTestCase("Show ip-addresses from mitigator cache.", "cacheIpMap", {}),
    DefenderTestCase("mitigator cache ip map", "cacheIpMap", {}),
    DefenderTestCase("Get ipv4-map from cache", "cacheIpMap", {}),
    DefenderTestCase("IP policies per address", "cacheIpMap", {}),
    DefenderTestCase("What IPs are currently cached in the mitigator?", "cacheIpMap", {}),
    DefenderTestCase("Show me the ipv4-map with time-left per policy", "cacheIpMap", {}),
    DefenderTestCase("List mitigator ip-address entries and correlation ids", "cacheIpMap", {}),
    DefenderTestCase("Which clients are in the IP cache?", "cacheIpMap", {}),
    # --- cachePolicyMap: rules, match-criteria, actions ---
    DefenderTestCase("mitigator cache policy-map", "cachePolicyMap", {}),
    DefenderTestCase("Get policy map.", "cachePolicyMap", {}),
    DefenderTestCase("List policies in the cache.", "cachePolicyMap", {}),
    DefenderTestCase("Show all expression and fingerprint policies.", "cachePolicyMap", {}),
    DefenderTestCase("What policies are configured in the mitigator?", "cachePolicyMap", {}),
    DefenderTestCase("correlation-id list from cache", "cachePolicyMap", {}),
    DefenderTestCase("mitigator cache policy map", "cachePolicyMap", {}),
    DefenderTestCase("Get policy-map with match-criteria", "cachePolicyMap", {}),
    DefenderTestCase("Show policy-type and action for each policy", "cachePolicyMap", {}),
    DefenderTestCase("Pull all expression policies with block vs redirect actions", "cachePolicyMap", {}),
    DefenderTestCase("Mitigator WAF policy list from __cq", "cachePolicyMap", {}),
    DefenderTestCase("What rate-limit and challenge policies exist in cache?", "cachePolicyMap", {}),
    # --- cacheAll: full mitigator-info blob ---
    DefenderTestCase("mitigator cache all", "cacheAll", {}),
    DefenderTestCase("Dump full cache.", "cacheAll", {}),
    DefenderTestCase("Get all cache data.", "cacheAll", {}),
    DefenderTestCase("Export entire mitigator cache JSON.", "cacheAll", {}),
    DefenderTestCase("Show everything in __cq cache", "cacheAll", {}),
    DefenderTestCase("mitigator cache all dump", "cacheAll", {}),
    DefenderTestCase("Full cache snapshot", "cacheAll", {}),
    DefenderTestCase("Retrieve complete cache state", "cacheAll", {}),
    DefenderTestCase("Give me ip-map policy-map and templates in one response", "cacheAll", {}),
    DefenderTestCase("Single GET equivalent of all __cq cache endpoints combined", "cacheAll", {}),
]


def get_defender_test_cases() -> list[DefenderTestCase]:
    return list(DEFENDER_TEST_CASES)
