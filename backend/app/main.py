"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import investigate, compare, benchmark, health, trace, evidence, metrics, config, ingest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting GraphProbe AI backend...")
    
    # Don't initialize at startup - do it lazily on first request
    # This avoids timeout issues on Render and allows fallback corpus creation
    logger.info("Skipping startup initialization - will initialize on first request")
    
    yield
    logger.info("Shutting down GraphProbe AI backend...")


app = FastAPI(
    title="GraphProbe AI",
    description="Explainable benchmarking and investigation platform for RAG, GraphRAG, and Agentic GraphRAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(investigate.router, prefix="/api", tags=["investigate"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(benchmark.router, prefix="/api", tags=["benchmark"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(trace.router, prefix="/api", tags=["trace"])
app.include_router(evidence.router, prefix="/api", tags=["evidence"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GraphProbe AI",
        "version": "1.0.0",
        "description": "Investigate. Connect. Verify. Know When to Stop.",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
