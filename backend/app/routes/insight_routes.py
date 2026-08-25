from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from ..models.schemas import InsightsResponse, User
from ..services.graph_service import graph_service
from ..services.auth import get_current_user
from ..models.database import db

router = APIRouter(prefix="/insights", tags=["Collaboration & Redundancy Insights"])

@router.get("", response_model=InsightsResponse)
async def get_research_insights():
    """
    Computes cross-disciplinary collaboration opportunities, identifies redundant studies,
    and analyzes university-wide dataset reuse patterns.
    """
    return graph_service.get_insights()

@router.get("/audit-logs")
async def get_audit_trail(current_user: User = Depends(get_current_user)):
    """
    Returns security audit log of ingestion, query, and extraction operations.
    """
    return {
        "total_events": len(db.audit_logs),
        "events": list(reversed(db.audit_logs[-50:]))
    }
