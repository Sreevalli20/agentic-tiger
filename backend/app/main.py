"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import investigate, compare, benchmark, health, trace, evidence, metrics, config, ingest, initialize
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting GraphProbe AI backend...")
    
    # Initialize vector database in production mode
    if settings.production_mode:
        logger.info("Production mode: Initializing vector database on startup")
        try:
            from app.retrieval.vector_retriever import VectorRetriever
            retriever = VectorRetriever()
            retriever._ensure_initialized()
            retriever._ensure_embedding_model()
            
            # Always initialize corpus in production mode (in-memory DB needs data on startup)
            logger.info("Loading production corpus into in-memory vector DB")
            success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
            final_stats = retriever.get_collection_stats()
            logger.info(f"Startup initialization complete: success={success}, chunks={final_stats.get('document_count', 0)}")
            if not success or final_stats.get('document_count', 0) == 0:
                logger.error("FAILED: Production corpus initialization did not load any documents")
        except Exception as e:
            logger.error(f"Production mode initialization failed: {e}")
            import traceback
            traceback.print_exc()
            try:
                final_stats = retriever.get_collection_stats()
                logger.info(f"Startup initialization complete: {final_stats.get('document_count', 0)} chunks")
            except:
                pass
    
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
