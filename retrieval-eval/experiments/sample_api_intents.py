"""
Intent suite for sample API MCP (real-world style: list, get, search).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SampleIntent:
    intent: str
    expected_tool: str
    expected_args_subset: dict[str, Any]


SAMPLE_INTENTS: list[SampleIntent] = [
    SampleIntent("List all posts.", "listPosts", {}),
    SampleIntent("Get post with id 1.", "getPost", {"id": 1}),
    SampleIntent("Show me post 3.", "getPost", {"id": 3}),
    SampleIntent("Search posts for the word API.", "searchPosts", {"q": "API"}),
    SampleIntent("Search for posts about REST.", "searchPosts", {"q": "REST"}),
    SampleIntent("List users.", "listUsers", {}),
    SampleIntent("Get user by id 2.", "getUser", {"id": 2}),
    SampleIntent("Show me user 1.", "getUser", {"id": 1}),
    SampleIntent("Find posts containing pagination.", "searchPosts", {"q": "pagination"}),
    SampleIntent("List the first 5 posts.", "listPosts", {"limit": 5}),
]


def get_sample_intents() -> list[SampleIntent]:
    return list(SAMPLE_INTENTS)
