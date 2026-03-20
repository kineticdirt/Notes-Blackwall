"""Minimal in-memory RAG store: nodes and chunks for eval. No workflow-canvas dependency."""
from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List, Optional

class Node:
    def __init__(self, node_id: str, node_type: str, content: Dict[str, Any], metadata: Optional[Dict] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.metadata = metadata or {}
        self.embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }

    def text(self) -> str:
        return json.dumps(self.content).lower()


class Store:
    """In-memory node store with edges for graph traversal."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[str]] = {}  # node_id -> [neighbor_id, ...]

    def add_node(self, node_type: str, content: Dict[str, Any], metadata: Optional[Dict] = None, node_id: Optional[str] = None) -> str:
        nid = node_id or str(uuid.uuid4())
        self.nodes[nid] = Node(nid, node_type, content, metadata)
        return nid

    def set_embedding(self, node_id: str, embedding: List[float]) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].embedding = embedding

    def add_edge(self, a: str, b: str) -> None:
        self.edges.setdefault(a, []).append(b)
        self.edges.setdefault(b, []).append(a)

    def get_neighbors(self, node_id: str) -> List[Node]:
        out = []
        for nid in self.edges.get(node_id, []):
            if nid in self.nodes:
                out.append(self.nodes[nid])
        return out

    def ingest_chunks(self, chunks: List[str], doc_id: str = "doc") -> List[str]:
        """Ingest text chunks; link doc -> chunks and chunk -> chunk. Returns chunk node ids."""
        doc_nid = self.add_node("document", {"id": doc_id, "chunks": len(chunks)})
        nids = []
        for i, text in enumerate(chunks):
            cid = self.add_node("chunk", {"chunk_index": i, "text": text, "document_id": doc_id})
            nids.append(cid)
            self.add_edge(doc_nid, cid)
            if i > 0:
                self.add_edge(nids[i - 1], cid)
        return nids
