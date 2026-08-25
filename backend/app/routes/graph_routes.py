from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models.schemas import KnowledgeGraphTopology, Node, EntityType
from ..models.database import db
from ..services.graph_service import graph_service

router = APIRouter(prefix="/graph", tags=["Knowledge Graph Visualizer"])

@router.get("/topology", response_model=KnowledgeGraphTopology)
async def get_graph_topology(
    department: Optional[str] = Query(None, description="Filter nodes by department"),
    entity_types: Optional[List[EntityType]] = Query(None, description="Filter by node entity types")
):
    """
    Returns full or filtered graph topology with calculated node degrees and community clusters.
    """
    return graph_service.get_topology(dept_filter=department, type_filter=entity_types)

@router.get("/node/{node_id}")
async def get_node_details(node_id: str):
    """
    Retrieves full properties, metadata, and 1-hop / 2-hop connected entities for a specific node.
    """
    node = db.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in knowledge graph.")
    
    neighbors = db.get_neighbors(node_id)
    return {
        "node": node,
        "connections": neighbors,
        "connection_count": len(neighbors)
    }

@router.get("/stats")
async def get_graph_stats():
    """
    Returns overall graph metrics, count by entity type, and department breakdown.
    """
    topology = graph_service.get_topology()
    return topology.stats
