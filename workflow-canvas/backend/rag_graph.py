"""
Graph-based RAG (Retrieval Augmented Generation) storage system.
Uses graph structure to store and retrieve information for RAG workflows.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
import hashlib
import uuid


class GraphNode:
    """Node in the RAG graph."""
    
    def __init__(self, node_id: str, node_type: str, content: Dict[str, Any],
                 metadata: Optional[Dict] = None):
        """
        Initialize graph node.
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node (document, chunk, entity, relation, etc.)
            content: Node content/data
            metadata: Additional metadata
        """
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "embedding": self.embedding
        }
    
    def update(self, content: Optional[Dict] = None, metadata: Optional[Dict] = None):
        """Update node content or metadata."""
        if content:
            self.content.update(content)
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.now().isoformat()


class GraphEdge:
    """Edge in the RAG graph."""
    
    def __init__(self, edge_id: str, from_node: str, to_node: str,
                 edge_type: str, weight: float = 1.0, metadata: Optional[Dict] = None):
        """
        Initialize graph edge.
        
        Args:
            edge_id: Unique edge identifier
            from_node: Source node ID
            to_node: Target node ID
            edge_type: Type of relationship
            weight: Edge weight (for ranking)
            metadata: Additional metadata
        """
        self.edge_id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.edge_type = edge_type
        self.weight = weight
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "edge_id": self.edge_id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "edge_type": self.edge_type,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class RAGGraph:
    """
    Graph-based storage for RAG system.
    Stores information as nodes and relationships.
    """
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.node_edges: Dict[str, Set[str]] = {}  # node_id -> set of edge_ids
    
    def add_node(self, node_type: str, content: Dict[str, Any],
                 metadata: Optional[Dict] = None, node_id: Optional[str] = None) -> str:
        """
        Add a node to the graph.
        
        Args:
            node_type: Type of node
            content: Node content
            metadata: Additional metadata
            node_id: Optional node ID (generated if not provided)
            
        Returns:
            Node ID
        """
        if not node_id:
            node_id = str(uuid.uuid4())
        
        node = GraphNode(node_id, node_type, content, metadata)
        self.nodes[node_id] = node
        self.node_edges[node_id] = set()
        
        return node_id
    
    def add_edge(self, from_node: str, to_node: str, edge_type: str,
                 weight: float = 1.0, metadata: Optional[Dict] = None,
                 edge_id: Optional[str] = None) -> str:
        """
        Add an edge to the graph.
        
        Args:
            from_node: Source node ID
            to_node: Target node ID
            edge_type: Type of relationship
            weight: Edge weight
            metadata: Additional metadata
            edge_id: Optional edge ID (generated if not provided)
            
        Returns:
            Edge ID
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError("Both nodes must exist in the graph")
        
        if not edge_id:
            edge_id = str(uuid.uuid4())
        
        edge = GraphEdge(edge_id, from_node, to_node, edge_type, weight, metadata)
        self.edges[edge_id] = edge
        self.node_edges[from_node].add(edge_id)
        self.node_edges[to_node].add(edge_id)
        
        return edge_id
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str) -> List[GraphNode]:
        """Get neighboring nodes."""
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        for edge_id in self.node_edges.get(node_id, set()):
            edge = self.edges.get(edge_id)
            if edge:
                neighbor_id = edge.to_node if edge.from_node == node_id else edge.from_node
                neighbor = self.nodes.get(neighbor_id)
                if neighbor:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def search_nodes(self, query: str, node_type: Optional[str] = None,
                    limit: int = 10) -> List[GraphNode]:
        """
        Search nodes by content (simple text matching).
        In production, would use vector similarity search.
        
        Args:
            query: Search query
            node_type: Filter by node type (optional)
            limit: Maximum results
            
        Returns:
            List of matching nodes
        """
        query_lower = query.lower()
        matches = []
        
        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue
            
            # Simple text search in content
            content_str = json.dumps(node.content).lower()
            if query_lower in content_str:
                matches.append(node)
        
        return matches[:limit]
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict:
        """
        Get subgraph starting from a node.
        
        Args:
            node_id: Starting node ID
            depth: Maximum depth to traverse
            
        Returns:
            Dictionary with nodes and edges
        """
        if node_id not in self.nodes:
            return {"nodes": [], "edges": []}
        
        visited_nodes = set()
        visited_edges = set()
        
        def traverse(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited_nodes:
                return
            
            visited_nodes.add(current_id)
            node = self.nodes[current_id]
            
            for edge_id in self.node_edges.get(current_id, set()):
                if edge_id in visited_edges:
                    continue
                
                edge = self.edges.get(edge_id)
                if edge:
                    visited_edges.add(edge_id)
                    next_id = edge.to_node if edge.from_node == current_id else edge.from_node
                    if current_depth < depth:
                        traverse(next_id, current_depth + 1)
        
        traverse(node_id, 0)
        
        return {
            "nodes": [self.nodes[nid].to_dict() for nid in visited_nodes],
            "edges": [self.edges[eid].to_dict() for eid in visited_edges]
        }
    
    def ingest_document(self, document_id: str, content: str,
                       metadata: Optional[Dict] = None) -> str:
        """
        Ingest a document into the graph (BDH - Batch Dynamic Ingestion).
        Creates nodes and relationships automatically.
        
        Args:
            document_id: Document identifier
            content: Document content
            metadata: Document metadata
            
        Returns:
            Root node ID
        """
        # Create document node
        doc_node_id = self.add_node(
            "document",
            {"id": document_id, "content": content},
            metadata
        )
        
        # Split into chunks (simplified)
        chunks = self._chunk_text(content, chunk_size=500)
        
        chunk_nodes = []
        for i, chunk in enumerate(chunks):
            chunk_id = self.add_node(
                "chunk",
                {"chunk_index": i, "text": chunk, "document_id": document_id},
                {"chunk_size": len(chunk)}
            )
            chunk_nodes.append(chunk_id)
            
            # Link chunk to document
            self.add_edge(
                doc_node_id,
                chunk_id,
                "contains",
                weight=1.0
            )
            
            # Link consecutive chunks
            if i > 0:
                self.add_edge(
                    chunk_nodes[i-1],
                    chunk_id,
                    "next",
                    weight=0.5
                )
        
        return doc_node_id
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def to_dict(self) -> Dict:
        """Convert entire graph to dictionary."""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }
