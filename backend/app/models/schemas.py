from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    PAPER = "paper"
    AUTHOR = "author"
    DATASET = "dataset"
    METHOD = "method"
    DEPARTMENT = "department"
    DOMAIN = "domain"

class RelationType(str, Enum):
    CO_AUTHORED = "CO_AUTHORED"
    USES_DATASET = "USES_DATASET"
    PROPOSES_METHOD = "PROPOSES_METHOD"
    APPLIES_METHOD = "APPLIES_METHOD"
    CITES = "CITES"
    AFFILIATED_WITH = "AFFILIATED_WITH"
    BELONGS_TO_DOMAIN = "BELONGS_TO_DOMAIN"
    POTENTIAL_COLLABORATION = "POTENTIAL_COLLABORATION"
    REDUNDANT_OVERLAP = "REDUNDANT_OVERLAP"

class UserRole(str, Enum):
    RESEARCHER = "researcher"
    DEPARTMENT_CHAIR = "department_chair"
    GRANT_REVIEWER = "grant_reviewer"
    ADMIN = "admin"

class User(BaseModel):
    id: str
    name: str
    email: str
    department: str
    role: UserRole
    avatar_url: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class Node(BaseModel):
    id: str
    name: str
    type: EntityType
    department: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    degree: int = 0
    community_id: Optional[int] = None

class Edge(BaseModel):
    id: str
    source: str
    target: str
    relation: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeGraphTopology(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    stats: Dict[str, Any] = Field(default_factory=dict)

class ExtractedEntities(BaseModel):
    title: str
    abstract: str
    year: int
    doi: Optional[str] = None
    departments: List[str] = Field(default_factory=list)
    authors: List[str] = Field(default_factory=list)
    datasets: List[Dict[str, Any]] = Field(default_factory=list)
    methods: List[Dict[str, Any]] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    file_type: str
    file_size_bytes: int
    extracted_entities: ExtractedEntities
    nodes_created: int
    edges_created: int
    vector_indexed: bool
    audit_log: Dict[str, Any]

class SearchFilter(BaseModel):
    departments: Optional[List[str]] = None
    entity_types: Optional[List[EntityType]] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    methods: Optional[List[str]] = None
    datasets: Optional[List[str]] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilter] = None
    top_k: int = 10
    hybrid_alpha: float = 0.7  # 1.0 = purely vector, 0.0 = purely keyword

class SearchResultItem(BaseModel):
    id: str
    name: str
    type: EntityType
    score: float
    vector_similarity: float
    keyword_relevance: float
    department: Optional[str] = None
    snippet: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    matched_methods: List[str] = Field(default_factory=list)
    matched_datasets: List[str] = Field(default_factory=list)

class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: List[SearchResultItem]
    query_expansion: Optional[List[str]] = None
    execution_time_ms: float

class CollaborationOpportunity(BaseModel):
    id: str
    author_a: str
    dept_a: str
    author_b: str
    dept_b: str
    shared_methods: List[str]
    shared_datasets: List[str]
    synergy_score: float
    rationale: str

class RedundancyAlert(BaseModel):
    id: str
    paper_a_id: str
    paper_a_title: str
    dept_a: str
    paper_b_id: str
    paper_b_title: str
    dept_b: str
    similarity_score: float
    overlapping_methods: List[str]
    overlapping_datasets: List[str]
    description: str

class InsightsResponse(BaseModel):
    collaboration_opportunities: List[CollaborationOpportunity]
    redundancy_alerts: List[RedundancyAlert]
    dataset_reuse_distribution: List[Dict[str, Any]]
    cross_department_synergies: List[Dict[str, Any]]
