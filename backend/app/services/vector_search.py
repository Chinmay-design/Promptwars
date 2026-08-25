import time
import re
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.database import db
from ..models.schemas import (
    SearchRequest, SearchResponse, SearchResultItem, EntityType
)
from .vertex_ai import vertex_ai_service

class VectorSearchService:
    @staticmethod
    async def hybrid_search(req: SearchRequest) -> SearchResponse:
        start_time = time.time()
        query = req.query.strip()
        if not query:
            return SearchResponse(
                query=query,
                total_matches=0,
                results=[],
                execution_time_ms=0.0
            )

        # 1. Generate query embedding
        query_vec = await vertex_ai_service.generate_embedding(query)
        q_arr = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 0:
            q_arr = q_arr / q_norm

        # 2. Query expansion
        expanded_terms = VectorSearchService._expand_query(query)

        # 3. Score candidate nodes
        all_nodes = db.get_all_nodes()
        results: List[SearchResultItem] = []

        query_tokens = set(re.findall(r"\w+", query.lower()) + [t.lower() for t in expanded_terms])

        for node in all_nodes:
            # Apply Filters
            if req.filters:
                if req.filters.entity_types and node.type not in req.filters.entity_types:
                    continue
                if req.filters.departments and node.department and node.department not in req.filters.departments:
                    continue

            # Vector similarity calculation
            vector_sim = 0.0
            if node.id in db.vectors:
                doc_vec = db.vectors[node.id]
                d_norm = np.linalg.norm(doc_vec)
                if d_norm > 0:
                    vector_sim = float(np.dot(q_arr, doc_vec) / (q_norm * d_norm))
                    vector_sim = max(0.0, min(1.0, (vector_sim + 1.0) / 2.0))  # scale 0 to 1

            # Keyword relevance calculation (BM25 approximation)
            node_text = f"{node.name} {node.department or ''} {json_dumps_safe(node.properties)}".lower()
            matched_tokens = [tok for tok in query_tokens if tok in node_text]
            keyword_score = len(matched_tokens) / max(1, len(query_tokens))

            # Hybrid score combining vector and keyword
            alpha = req.hybrid_alpha
            combined_score = (alpha * vector_sim) + ((1.0 - alpha) * keyword_score)

            if combined_score > 0.15 or keyword_score > 0.3:
                snippet = node.properties.get("abstract") or node.properties.get("description") or f"Entity of type {node.type.value} in {node.department or 'General Research'}"
                if len(snippet) > 220:
                    snippet = snippet[:220] + "..."

                # Extract related methods & datasets
                neighbors = db.get_neighbors(node.id)
                matched_methods = [n["node"].name for n in neighbors if n["node"].type == EntityType.METHOD]
                matched_datasets = [n["node"].name for n in neighbors if n["node"].type == EntityType.DATASET]

                results.append(SearchResultItem(
                    id=node.id,
                    name=node.name,
                    type=node.type,
                    score=round(combined_score, 4),
                    vector_similarity=round(vector_sim, 4),
                    keyword_relevance=round(keyword_score, 4),
                    department=node.department,
                    snippet=snippet,
                    metadata=node.properties,
                    matched_methods=matched_methods,
                    matched_datasets=matched_datasets
                ))

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        top_results = results[:req.top_k]

        elapsed_ms = (time.time() - start_time) * 1000.0

        return SearchResponse(
            query=query,
            total_matches=len(results),
            results=top_results,
            query_expansion=expanded_terms,
            execution_time_ms=round(elapsed_ms, 2)
        )

    @staticmethod
    def _expand_query(query: str) -> List[str]:
        q_lower = query.lower()
        synonyms = {
            "transformer": ["attention mechanism", "BERT", "LLM", "deep sequence model"],
            "climate": ["atmospheric", "carbon emissions", "spatio-temporal kriging", "ERA5"],
            "cancer": ["genomics", "oncology", "RNA-Seq", "mutation locus", "TCGA"],
            "neuro": ["connectome", "fMRI", "cortex", "EEG", "cognitive dynamics"],
            "graph": ["GNN", "knowledge graph", "message passing", "network embedding"],
            "reinforcement": ["MARL", "policy gradient", "Q-learning", "agent coordination"]
        }
        expanded = []
        for key, terms in synonyms.items():
            if key in q_lower:
                expanded.extend(terms)
        return list(set(expanded))[:4]

def json_dumps_safe(obj: Any) -> str:
    try:
        import json
        return json.dumps(obj)
    except Exception:
        return str(obj)

vector_search_service = VectorSearchService()
