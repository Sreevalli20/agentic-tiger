"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import investigate, compare, benchmark, health, trace, evidence, metrics, config, ingest, initialize, tigergraph_ingest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting GraphProbe AI backend...")
    
    # Initialize TigerGraph automatically on startup if credentials are available
    try:
        if settings.tg_secret:
            logger.info("TigerGraph credentials found - attempting automatic initialization")
            from app.tigergraph.graph_service import GraphService
            graph_service = GraphService()
            
            # Try to initialize graph if needed (idempotent)
            if graph_service.conn:
                logger.info("TigerGraph connection established - checking graph status")
                try:
                    from pathlib import Path
                    backend_dir = Path(__file__).parent.parent
                    
                    # Try multiple corpus paths for deployment flexibility
                    corpus_paths = [
                        backend_dir / "corpus_production.jsonl",
                        backend_dir / "app" / "corpus_production.jsonl",
                        Path.cwd() / "corpus_production.jsonl",
                    ]
                    
                    corpus_path = None
                    for path in corpus_paths:
                        if path.exists():
                            corpus_path = str(path)
                            logger.info(f"Found corpus at: {corpus_path}")
                            break
                    
                    if corpus_path:
                        logger.info(f"Initializing TigerGraph with corpus: {corpus_path}")
                        initialized = await graph_service.initialize_graph_if_needed(corpus_path)
                        if initialized:
                            logger.info("TigerGraph initialization completed successfully")
                        else:
                            logger.warning("TigerGraph initialization failed - will retry on first request")
                    else:
                        logger.warning("Corpus file not found - TigerGraph will initialize on first request")
                except Exception as init_error:
                    logger.warning(f"TigerGraph initialization failed: {init_error} - will retry on first request")
            else:
                logger.info("TigerGraph connection not available - will initialize on first request")
        else:
            logger.info("TigerGraph credentials not configured - skipping automatic initialization")
    except Exception as e:
        logger.warning(f"TigerGraph auto-initialization error: {e} - will continue without it")
    
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
app.include_router(initialize.router, prefix="/api", tags=["initialize"])
app.include_router(tigergraph_ingest.router, prefix="/api", tags=["tigergraph_ingest"])


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
