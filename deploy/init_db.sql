-- Enable pgvector extension for AlloyDB / PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;

-- Nodes Table (Papers, Authors, Methods, Datasets, Departments)
CREATE TABLE IF NOT EXISTS kg_nodes (
    id VARCHAR(128) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(64) NOT NULL,
    department VARCHAR(128),
    properties JSONB DEFAULT '{}'::jsonb,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Edges Table (Co-authored, Uses_Dataset, Applies_Method, etc.)
CREATE TABLE IF NOT EXISTS kg_edges (
    id VARCHAR(128) PRIMARY KEY,
    source VARCHAR(128) REFERENCES kg_nodes(id) ON DELETE CASCADE,
    target VARCHAR(128) REFERENCES kg_nodes(id) ON DELETE CASCADE,
    relation VARCHAR(64) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    properties JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HNSW Vector Index for sub-millisecond approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS kg_nodes_embedding_hnsw_idx 
ON kg_nodes USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Audit Trail Table
CREATE TABLE IF NOT EXISTS kg_audit_trail (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    action VARCHAR(64) NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    document_id VARCHAR(128),
    details JSONB DEFAULT '{}'::jsonb
);
