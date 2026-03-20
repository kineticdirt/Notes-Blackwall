"""Needle-in-haystack eval: build haystack, inject needle, ingest, search, measure hit@k and optional LLM answer."""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List, Optional, Tuple

from store import Store
from retrievers import get_retriever

if TYPE_CHECKING:
    from retrievers import BaseRetriever

HAYSTACK_SENTENCES = (
    "The weather today is mild and pleasant.",
    "Project timelines require careful planning.",
    "Data analysis can reveal important patterns.",
    "Communication between teams improves outcomes.",
    "Security best practices should be followed.",
    "Documentation helps maintain long-term clarity.",
    "Testing reduces the risk of regressions.",
    "Code reviews catch many issues early.",
)

# Computer Science & Cequence-themed haystack (legacy; prefer "work" for Jira/Confluence).
CEQUENCE_CS_SENTENCES = (
    "Distributed systems require consensus and fault tolerance.",
    "API rate limiting protects backends from abuse.",
    "Jira and Confluence integrate via Atlassian for Rovo.",
    "Documentation and design docs live in Confluence spaces.",
    "Enterprise auth uses JWT and least-privilege access.",
    "Validation at API returns 400 when required fields are missing.",
    "The gateway returns 401 when JWT is invalid or missing at request time.",
    "Project timelines and issue types are managed in Jira.",
    "Confluence spaces organize pages by team or product.",
    "Velocity Manager exports detection data to Splunk.",
    "Issue types include Task, Bug, Story, Epic, and Subtask.",
    "Spaces like XAN, PM, API, CSD contain product and support docs.",
)

# Work-themed haystack: Jira, Confluence, API/gateway, validation (no BlackWall/local workshop).
# Expanded from WORK_EVAL_PROJECTS_AND_PRODUCTS.md to hit needle/reasoning/explanation criteria.
WORK_SENTENCES = (
    "Jira projects have keys like AF, AR, ASJCI, ATC, CEE, CEP and contain issues of type Task, Bug, Story, Epic.",
    "Confluence spaces have keys like XAN, PM, API, CSD, VM, SS, POV, DSMP and contain pages and documentation.",
    "API validation rejects requests with missing required fields and returns 400.",
    "The gateway returns 401 when the JWT is invalid or missing at request time.",
    "Outbound header source types include access_key, which must not have a prefix set.",
    "Forward Inbound Header forbids using authorization or cookie as the source header.",
    "OAuth2 Service Account uses a single service token; On Behalf of User uses token exchange.",
    "Design documents and High Level Architecture are linked from the Documentation page in XAN.",
    "Velocity Manager installs Splunk universal forwarder; export config is under data-export.",
    "Project API Fury has key AF; Armor has key AR; API Security JIRA Connector Integration has key ASJCI.",
    "API Test Cases project key is ATC; CQAI Efficacy Engineering is CEE; Customer Engineering Projects is CEP.",
    "Product Management space key is PM; CQ - API Security space key is API; Stealth SUPPORT space key is SS.",
    "Velocity Manager 0.1 space key is VM; Proof Of Value space key is POV; Digital Skimming Protection space is DSMP.",
    "CQ-Service Desk space key is CSD; CQ - Service Desk 2 is CSD2.",
    "Required fields and issue type metadata are available via Jira project issue types API.",
    "Defender project key is DEF; Platform is PLAT; Proof Of Value Jira project key is POV.",
)

NEEDLE = "The secret code for this eval is NEEDLE-42."
NEEDLE_QUERY = "What is the secret code?"

# CS/Cequence needle: inject passphrase into themed haystack.
CEQUENCE_CS_NEEDLE = "The Cequence BlackWall retrieval eval passphrase is NEEDLE-CS-42."
CEQUENCE_CS_QUERY = "What is the Cequence BlackWall retrieval eval passphrase?"


def get_sentences(dataset: str) -> Tuple[str, ...]:
    """Return haystack sentence set for dataset."""
    if dataset == "cequence_cs":
        return CEQUENCE_CS_SENTENCES
    if dataset == "work":
        return WORK_SENTENCES
    return HAYSTACK_SENTENCES


def get_dataset_config(dataset: str) -> tuple:
    """Return (sentences, needle, query, answer_marker) for dataset name (needle eval only)."""
    if dataset == "cequence_cs":
        return (CEQUENCE_CS_SENTENCES, CEQUENCE_CS_NEEDLE, CEQUENCE_CS_QUERY, "NEEDLE-CS-42")
    if dataset == "work":
        return (WORK_SENTENCES, "The Jira project key for API Fury is AF.", "What is the Jira project key for API Fury?", "AF")
    return (HAYSTACK_SENTENCES, NEEDLE, NEEDLE_QUERY, "NEEDLE-42")

def _haystack_length(gravity: str) -> int:
    lengths = {
        "tiny": 20,
        "short": 40,
        "medium": 120,
        "long": 250,
        "xlong": 400,
    }
    return lengths.get(gravity, 250)


def get_haystack_length(gravity: str) -> int:
    """Public hook for dataset_builder: haystack length for a given gravity."""
    return _haystack_length(gravity)

NEEDLE_POSITIONS = ("start", "middle", "end")

def _position_to_index(position: str, length: int) -> int:
    if position == "start":
        return 0
    if position == "end":
        return length - 1
    return length // 2

def build_haystack(
    gravity: str,
    needle: str = NEEDLE,
    position: str = "middle",
    sentences: Tuple[str, ...] = HAYSTACK_SENTENCES,
) -> Tuple[str, int]:
    """Build haystack text with needle at position. Returns (full_text, chunk_index_where_needle)."""
    length = _haystack_length(gravity)
    out: List[str] = []
    for _ in range(length):
        out.append(random.choice(sentences))
    idx = _position_to_index(position, length)
    out[idx] = needle
    return " ".join(out), idx


def build_haystack_multi(
    gravity: str,
    needles: List[Tuple[str, str]],
    sentences: Tuple[str, ...],
    rng: Optional[random.Random] = None,
) -> Tuple[str, List[int]]:
    """
    Build haystack with multiple needles at distinct positions.
    needles: list of (needle_text, position) with position in NEEDLE_POSITIONS.
    Returns (full_text, list of sentence indices where each needle was placed).
    Uses distinct positions; if more needles than positions, later needles use middle.
    """
    if rng is None:
        rng = random
    length = _haystack_length(gravity)
    out: List[str] = []
    for _ in range(length):
        out.append(rng.choice(sentences))
    used: List[int] = []
    positions_used: List[int] = []
    for needle_text, pos in needles:
        idx = _position_to_index(pos, length)
        if idx in positions_used:
            idx = length // 2
            while idx in positions_used and idx < length:
                idx += 1
            if idx >= length:
                idx = length // 2
        positions_used.append(idx)
        out[idx] = needle_text
        used.append(idx)
    return " ".join(out), used

def chunk_text(text: str, chunk_size: int = 200) -> List[str]:
    words = text.split()
    chunks = []
    current, size = [], 0
    for w in words:
        if size + len(w) + 1 > chunk_size and current:
            chunks.append(" ".join(current))
            current, size = [], 0
        current.append(w)
        size += len(w) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks

def run_needle_eval(
    search_type: str,
    gravity: str,
    k: int = 5,
    dataset: str = "default",
    needle: str | None = None,
    query: str | None = None,
    position: str = "middle",
    chunk_size: int = 200,
) -> dict:
    """Run one retrieval run (needle-in-haystack). Returns metrics dict (hit, rank, etc.)."""
    sentences = get_sentences(dataset)
    if needle is None or query is None:
        _, default_needle, default_query, _ = get_dataset_config(dataset)
        needle = needle or default_needle
        query = query or default_query
    haystack, _ = build_haystack(gravity, needle=needle, position=position, sentences=sentences)
    chunks = chunk_text(haystack, chunk_size=chunk_size)
    needle_chunk = next((c for c in chunks if needle in c), None)
    if not needle_chunk:
        return {
            "search_type": search_type,
            "gravity": gravity,
            "dataset": dataset,
            "hit_at_k": False,
            "rank": None,
            "k": k,
            "num_chunks": len(chunks),
        }

    store = Store()
    store.ingest_chunks(chunks, doc_id="haystack")

    retriever = get_retriever(search_type)
    results = retriever.search(store, query, node_type="chunk", limit=k)

    hit = False
    rank = -1
    for i, n in enumerate(results):
        if needle in (n.content.get("text") or ""):
            hit = True
            rank = i + 1
            break

    return {
        "search_type": search_type,
        "gravity": gravity,
        "dataset": dataset,
        "hit_at_k": hit,
        "rank": rank if hit else None,
        "k": k,
        "num_chunks": len(chunks),
    }


def retrieval_metrics_on_store(
    store: Store,
    retriever: "BaseRetriever",
    query: str,
    needle: str,
    k: int = 5,
    search_type: str = "substring",
    gravity: str = "medium",
    dataset: str = "work",
) -> dict:
    """Compute hit@k and rank when searching an existing store (e.g. from prebuilt corpus)."""
    results = retriever.search(store, query, node_type="chunk", limit=k)
    hit = False
    rank = -1
    for i, n in enumerate(results):
        if needle in (n.content.get("text") or ""):
            hit = True
            rank = i + 1
            break
    return {
        "search_type": search_type,
        "gravity": gravity,
        "dataset": dataset,
        "hit_at_k": hit,
        "rank": rank if hit else None,
        "k": k,
        "num_chunks": len(store.nodes),
    }
