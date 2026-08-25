import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated University Research Knowledge Graph"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # GCP & Vertex AI Configuration
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID", "university-research-ai")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY", None)
    VERTEX_AI_MODEL: str = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash")
    VERTEX_EMBED_MODEL: str = os.getenv("VERTEX_EMBED_MODEL", "text-embedding-004")
    
    # Storage & Upload Configuration
    GCS_BUCKET_NAME: Optional[str] = os.getenv("GCS_BUCKET_NAME", "university-research-vault")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/Users/s/.gemini/antigravity/scratch/research-knowledge-graph/data/uploads")
    
    # Database / AlloyDB & Vector Store
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/research_kg"
    )
    USE_IN_MEMORY_STORE: bool = os.getenv("USE_IN_MEMORY_STORE", "true").lower() == "true"
    
    # Security & SSO
    SECRET_KEY: str = os.getenv("SECRET_KEY", "university-super-secret-sso-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
