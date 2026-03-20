"""
MvM Phase 3: Curated intent suite for Atlassian MCP.
Each intent has: intent (user text), expected_tool, expected_args_subset (keys that must be present/valid).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiIntent:
    intent: str
    expected_tool: str
    expected_args_subset: dict[str, Any]  # minimal keys; values can be placeholder like "<need cloudId>"


# 5–10 intents for Atlassian MCP (getAccessibleAtlassianResources, getJiraIssue, searchJiraIssuesUsingJql, getConfluenceSpaces, etc.)
ATLASSIAN_INTENTS: list[ApiIntent] = [
    ApiIntent(
        intent="What Atlassian resources can I access?",
        expected_tool="getAccessibleAtlassianResources",
        expected_args_subset={},
    ),
    ApiIntent(
        intent="List my accessible Atlassian resources.",
        expected_tool="getAccessibleAtlassianResources",
        expected_args_subset={},
    ),
    ApiIntent(
        intent="List Confluence spaces.",
        expected_tool="getConfluenceSpaces",
        expected_args_subset={},
    ),
    ApiIntent(
        intent="Get Confluence spaces I can access.",
        expected_tool="getConfluenceSpaces",
        expected_args_subset={},
    ),
    ApiIntent(
        intent="Search Jira for recent issues.",
        expected_tool="searchJiraIssuesUsingJql",
        expected_args_subset={"cloudId": "<need cloudId>", "jql": None},  # jql present
    ),
    ApiIntent(
        intent="Find recent Jira issues.",
        expected_tool="searchJiraIssuesUsingJql",
        expected_args_subset={"cloudId": "<need cloudId>"},
    ),
    ApiIntent(
        intent="Get Jira issue PROJ-123.",
        expected_tool="getJiraIssue",
        expected_args_subset={"cloudId": "<need cloudId>", "issueIdOrKey": "PROJ-123"},
    ),
    ApiIntent(
        intent="Fetch Jira issue AF-42.",
        expected_tool="getJiraIssue",
        expected_args_subset={"cloudId": "<need cloudId>", "issueIdOrKey": "AF-42"},
    ),
    ApiIntent(
        intent="What Jira projects do I have access to?",
        expected_tool="getAccessibleAtlassianResources",
        expected_args_subset={},
    ),
    ApiIntent(
        intent="Show me Confluence spaces.",
        expected_tool="getConfluenceSpaces",
        expected_args_subset={},
    ),
]


def get_intents() -> list[ApiIntent]:
    return list(ATLASSIAN_INTENTS)
