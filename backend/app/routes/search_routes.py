from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..models.schemas import SearchRequest, SearchResponse, SearchFilter, EntityType
from ..services.vector_search import vector_search_service
from ..models.database import db

router = APIRouter(prefix="/search", tags=["Vector & Research Search"])

@router.post("", response_model=SearchResponse)
async def perform_search(req: SearchRequest):
    """
    Executes hybrid semantic vector search + keyword matching with multi-attribute filtering.
    """
    return await vector_search_service.hybrid_search(req)

@router.get("/suggest")
async def get_search_suggestions(q: str = Query(..., min_length=1)):
    """
    Quick auto-complete suggestions for papers, methods, datasets, and authors.
    """
    q_lower = q.lower()
    matches = []
    for node in db.get_all_nodes():
        if q_lower in node.name.lower() or (node.department and q_lower in node.department.lower()):
            matches.append({
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "department": node.department
            })
            if len(matches) >= 8:
                break
    return matches
