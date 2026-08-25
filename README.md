# Automated University Research Knowledge Graph & Vector Search

A full-stack intelligence system for academic institutions that ingests siloed research papers (PDFs), Markdown notes, and code repositories, automatically extracts structured scientific entities and relationships using **Vertex AI (Gemini + Embeddings)**, indexes them into **AlloyDB / PostgreSQL + pgvector**, and delivers an **Interactive Multi-Modal Knowledge Graph & Vector Search** interface.

---

## Key Capabilities

1. **Secure University SSO & Role-Based Access Control**:
   - Integrated with Shibboleth / OAuth2 simulation with role profiles: *Researcher*, *Department Chair*, *Grant Reviewer*, and *Administrator*.
2. **Multi-Format Secure Document Ingestion**:
   - Drag & drop PDF research papers, Markdown notes, Python/R code.
   - Computes SHA-256 integrity hashes, audits storage, and performs deep text/metadata extraction.
3. **Vertex AI Scientific Extraction Pipeline**:
   - Extracts Authors, University Departments, Datasets (size, license, format), Methods/Models, and Relationships (`CO_AUTHORED`, `USES_DATASET`, `APPLIES_METHOD`, `CITES`).
   - Generates 768-dimensional dense vector embeddings for semantic retrieval.
4. **Hybrid & Vector Research Search**:
   - Hybrid ranking combining BM25 keyword relevance and cosine vector similarity with adjustable alpha weights.
   - Query expansion with scientific domain synonyms.
5. **Interactive 2D Knowledge Graph Visualization**:
   - Physics-driven force simulation canvas with zoom, pan, node drag, and community clustering.
   - Slide-out inspection drawer displaying abstracts, metrics, and direct neighborhood subgraphs.
6. **Cross-Department Synergy & Redundancy Insights**:
   - **Hidden Collaboration Finder**: Surfaces researchers across different faculties using identical mathematical methods or datasets who haven't co-authored yet.
   - **Redundant Study Detector**: Identifies overlapping research across laboratories to consolidate grant efforts.
   - **Dataset Reuse Distribution**: Lineage tracking and adoption metrics for university-held datasets.
7. **GCP Production Architecture**:
   - Fully containerized for **Google Cloud Run**, with schema definitions for **AlloyDB / PostgreSQL (pgvector)** and **GCS**.

---

## Quick Start (Local Development)

### 1. Run with `uv` (Zero-Config Mode)

```bash
cd /Users/s/.gemini/antigravity/scratch/research-knowledge-graph

# Run with local virtualenv
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open your browser to **[http://localhost:8000](http://localhost:8000)**.

### 2. Run with Docker Compose (PostgreSQL + pgvector)

```bash
cd deploy
docker compose up --build
```

---

## Project Structure

```
research-knowledge-graph/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI entrypoint & static mount
│       ├── config.py                # GCP, Vertex AI, and database configuration
│       ├── models/
│       │   ├── schemas.py           # Pydantic schemas for graph, search, auth
│       │   └── database.py          # In-memory & AlloyDB/pgvector manager
│       ├── services/
│       │   ├── auth.py              # University SSO & JWT service
│       │   ├── storage.py           # GCS / secure storage & audit hashes
│       │   ├── pdf_parser.py        # PDF & code repository parser
│       │   ├── vertex_ai.py         # Vertex AI (Gemini + Embeddings) extraction
│       │   ├── vector_search.py     # Hybrid vector search engine
│       │   ├── graph_service.py     # Graph topology & synergy discovery
│       │   └── seed_data.py         # Cross-departmental sample dataset seed
│       └── routes/
│           ├── auth_routes.py       # SSO login & faculty directory
│           ├── upload_routes.py     # Ingestion & Vertex AI trigger
│           ├── search_routes.py     # Semantic & hybrid search
│           ├── graph_routes.py      # Topology & node inspector
│           └── insight_routes.py    # Collaboration & redundancy reports
├── frontend/
│   ├── index.html                   # Modern SPA shell
│   ├── css/
│   │   └── styles.css               # Theme & canvas graph styling
│   └── js/
│       ├── app.js                   # Application state & SSO switcher
│       ├── graph_viz.js             # Canvas force-directed graph renderer
│       ├── search.js                # Vector search UI handler
│       ├── upload.js                # Ingestion dropzone & pipeline animator
│       └── insights.js              # Collaboration & redundancy cards
├── deploy/
│   ├── Dockerfile                   # Cloud Run container definition
│   ├── docker-compose.yml           # Local dev with pgvector container
│   ├── deploy-cloud-run.sh          # Cloud Run automated deployment script
│   └── init_db.sql                  # AlloyDB / pgvector table & index schemas
└── README.md
```
