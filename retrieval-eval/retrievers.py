"""Pluggable retrievers: substring, vector, hybrid, graph. All operate on Store."""
from __future__ import annotations
from typing import List, Optional

from store import Node, Store

class BaseRetriever:
    def search(self, store: Store, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Node]:
        raise NotImplementedError

class SubstringRetriever(BaseRetriever):
    def search(self, store: Store, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Node]:
        q = query.lower()
        out = []
        for n in store.nodes.values():
            if node_type and n.node_type != node_type:
                continue
            if q in n.text():
                out.append(n)
        return out[:limit]

def _embedding_for(text: str) -> List[float]:
    try:
        from sentence_transformers import SentenceTransformer
        if not hasattr(_embedding_for, "_model"):
            _embedding_for._model = SentenceTransformer("all-MiniLM-L6-v2")
        return _embedding_for._model.encode(text, convert_to_numpy=True).tolist()
    except Exception:
        return []

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na * nb == 0:
        return 0.0
    return dot / (na * nb)

class VectorRetriever(BaseRetriever):
    def search(self, store: Store, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Node]:
        q_emb = _embedding_for(query)
        if not q_emb:
            return SubstringRetriever().search(store, query, node_type, limit)
        scored = []
        for n in store.nodes.values():
            if node_type and n.node_type != node_type:
                continue
            if n.node_type != "chunk":
                continue
            emb = n.embedding
            if not emb:
                emb = _embedding_for(n.content.get("text", ""))
                n.embedding = emb
            if emb:
                scored.append((_cosine(q_emb, emb), n))
        scored.sort(key=lambda x: -x[0])
        return [n for _, n in scored[:limit]]

def _rrf(ranks: List[List[Node]], k: int = 60) -> List[Node]:
    scores: dict = {}
    for run in ranks:
        for r, n in enumerate(run):
            nid = n.node_id
            scores[nid] = scores.get(nid, 0) + 1 / (k + r + 1)
    order = sorted(scores.keys(), key=lambda nid: -scores[nid])
    seen = set()
    out = []
    for nid in order:
        if nid in seen:
            continue
        seen.add(nid)
        for run in ranks:
            for n in run:
                if n.node_id == nid:
                    out.append(n)
                    break
        if len(out) >= 10:
            break
    return out[:10]

class HybridRetriever(BaseRetriever):
    def search(self, store: Store, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Node]:
        sub = SubstringRetriever().search(store, query, node_type, limit)
        vec = VectorRetriever().search(store, query, node_type, limit)
        return _rrf([sub, vec])[:limit]

class GraphRetriever(BaseRetriever):
    """Expand from first substring hit via edges (BFS)."""
    def search(self, store: Store, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Node]:
        sub = SubstringRetriever().search(store, query, node_type, limit=5)
        if not sub:
            return []
        out = list(sub)
        seen = {n.node_id for n in out}
        for n in sub:
            for neighbor in store.get_neighbors(n.node_id):
                if neighbor.node_id not in seen and (not node_type or neighbor.node_type == node_type):
                    seen.add(neighbor.node_id)
                    out.append(neighbor)
                    if len(out) >= limit:
                        return out[:limit]
        return out[:limit]

def get_retriever(name: str) -> BaseRetriever:
    if name == "substring":
        return SubstringRetriever()
    if name == "vector":
        return VectorRetriever()
    if name == "hybrid":
        return HybridRetriever()
    if name == "graph":
        return GraphRetriever()
    raise ValueError(f"unknown retriever: {name}")
