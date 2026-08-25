import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.database import db
from backend.app.services.seed_data import seed_initial_knowledge_graph

client = TestClient(app)

def setup_module(module):
    # Ensure seed data is populated
    asyncio.run(seed_initial_knowledge_graph())

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Vertex AI" in data["mode"] or "Standalone" in data["mode"]

def test_sso_login():
    res = client.post("/api/auth/login", json={"email": "elena.vance@university.edu"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["name"] == "Dr. Elena Vance"
    assert data["user"]["department"] == "Computer Science & AI"

def test_graph_topology():
    res = client.get("/api/graph/topology")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0
    assert "density" in data["stats"]
    assert data["stats"]["total_nodes"] == len(data["nodes"])

def test_hybrid_search():
    res = client.post("/api/search", json={
        "query": "transformer cross-attention for somatic mutations",
        "hybrid_alpha": 0.7,
        "top_k": 5
    })
    assert res.status_code == 200
    data = res.json()
    assert data["total_matches"] > 0
    assert len(data["results"]) > 0
    assert data["results"][0]["vector_similarity"] > 0

def test_document_upload_and_extraction():
    sample_content = b"""
    Title: Multi-Scale Neural Operators for Ocean Circulation Dynamics
    Authors: Prof. Sarah Lin, Dr. David Chen
    Department: Earth & Climate Sciences
    Abstract: Ocean circulation models suffer from sub-grid kinetic dissipation. We propose OceanPINN using Latent Flow Matching on ERA5 datasets.
    Methods: Physics-Informed Neural Operators (PINO), Latent Flow Matching & SDEs
    Datasets: ERA5-Atmospheric-Reanalysis
    """
    res = client.post(
        "/api/upload",
        files={"file": ("ocean_pinn.txt", sample_content, "text/plain")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED_AND_INDEXED"
    assert data["extracted_entities"]["title"] != ""
    assert data["nodes_created"] >= 1
    assert data["edges_created"] >= 1

def test_insights():
    res = client.get("/api/insights")
    assert res.status_code == 200
    data = res.json()
    assert "collaboration_opportunities" in data
    assert "dataset_reuse_distribution" in data
    assert len(data["dataset_reuse_distribution"]) > 0
