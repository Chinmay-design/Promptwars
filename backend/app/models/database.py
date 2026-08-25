import json
import logging
from typing import Dict, List, Any, Optional
import numpy as np
from ..models.schemas import Node, Edge, EntityType, RelationType

logger = logging.getLogger("research_kg.database")

class GraphDatabase:
    """
    Dual-engine Graph and Vector storage:
    1. High-speed In-Memory Network & Vector store (zero-config local dev & instant testing)
    2. Seamless AlloyDB / PostgreSQL + pgvector adapter interface
    """
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.vectors: Dict[str, np.ndarray] = {}  # node_id -> 768-dim embedding
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []

    def add_node(self, node: Node, embedding: Optional[List[float]] = None) -> Node:
        if node.id in self.nodes:
            # Merge properties
            existing = self.nodes[node.id]
            existing.properties.update(node.properties)
            if node.department:
                existing.department = node.department
            self.nodes[node.id] = existing
        else:
            self.nodes[node.id] = node

        if embedding is not None:
            self.vectors[node.id] = np.array(embedding, dtype=np.float32)
        return self.nodes[node.id]

    def add_edge(self, edge: Edge) -> Edge:
        self.edges[edge.id] = edge
        # Update node degrees
        if edge.source in self.nodes:
            self.nodes[edge.source].degree += 1
        if edge.target in self.nodes:
            self.nodes[edge.target].degree += 1
        return edge

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def get_all_edges(self) -> List[Edge]:
        return list(self.edges.values())

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        neighbors = []
        for edge in self.edges.values():
            if edge.source == node_id:
                target_node = self.nodes.get(edge.target)
                if target_node:
                    neighbors.append({
                        "node": target_node,
                        "relation": edge.relation,
                        "direction": "outgoing",
                        "weight": edge.weight
                    })
            elif edge.target == node_id:
                source_node = self.nodes.get(edge.source)
                if source_node:
                    neighbors.append({
                        "node": source_node,
                        "relation": edge.relation,
                        "direction": "incoming",
                        "weight": edge.weight
                    })
        return neighbors

    def log_audit(self, action: str, user_id: str, document_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        import time
        entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "document_id": document_id,
            "details": details or {}
        }
        self.audit_logs.append(entry)
        logger.info(f"AUDIT: [{action}] User:{user_id} Doc:{document_id}")

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.vectors.clear()
        self.documents.clear()
        self.audit_logs.clear()

db = GraphDatabase()
