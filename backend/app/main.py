import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .routes.auth_routes import router as auth_router
from .routes.upload_routes import router as upload_router
from .routes.search_routes import router as search_router
from .routes.graph_routes import router as graph_router
from .routes.insight_routes import router as insight_router
from .services.seed_data import seed_initial_knowledge_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("research_kg")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed initial knowledge graph
    logger.info("Initializing Research Knowledge Graph System...")
    await seed_initial_knowledge_graph()
    yield
    # Shutdown
    logger.info("Shutting down Research Knowledge Graph System...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Automated Knowledge-Graph System for University Research with Vertex AI and AlloyDB/pgvector",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(upload_router, prefix=settings.API_PREFIX)
app.include_router(search_router, prefix=settings.API_PREFIX)
app.include_router(graph_router, prefix=settings.API_PREFIX)
app.include_router(insight_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "Live GCP / Vertex AI" if settings.GOOGLE_API_KEY else "Zero-Config Standalone Demo Mode",
        "gcp_project": settings.GCP_PROJECT_ID,
        "vertex_model": settings.VERTEX_AI_MODEL,
        "embed_model": settings.VERTEX_EMBED_MODEL,
        "storage": "GCS / Local Secure Vault"
    }

# Mount Frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
