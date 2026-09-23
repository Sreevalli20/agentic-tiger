"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.retrieval.vector_retriever import VectorRetriever
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with lightweight status checks."""
    # Check LLM (prefer GOOGLE_API_KEY, fallback to LLM_API_KEY)
    llm_configured = bool(settings.google_api_key or settings.llm_api_key)
    
    # Check TigerGraph configuration (don't actually connect to avoid heavy initialization)
    tigergraph_configured = bool(settings.tg_host and settings.tg_secret)
    
    # Check vector DB stats and initialize if empty in production mode
    vector_db_stats = {'status': 'lazy', 'message': 'Vector DB available for lazy initialization'}
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        actual_stats = retriever.get_collection_stats()
        
        # If vector DB is empty and in production mode, initialize it
        if settings.production_mode and actual_stats.get('document_count', 0) == 0:
            logger.info("Production mode: Vector DB empty, initializing on health check")
            retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
            actual_stats = retriever.get_collection_stats()
            logger.info(f"After initialization: {actual_stats}")
        
        if actual_stats.get('status') == 'initialized':
            vector_db_stats = actual_stats
    except Exception as e:
        logger.warning(f"Failed to get/initialize vector DB stats: {e}")
    
    return HealthResponse(
        status="healthy",
        tigergraph_connected=tigergraph_configured,
        vector_db_connected=True,
        llm_configured=llm_configured,
        vector_db_stats=vector_db_stats
    )


@router.post("/health/initialize")
async def initialize_production():
    """Initialize production corpus if vector database is empty.
    
    Returns:
        Initialization status and statistics
    """
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        stats = retriever.get_collection_stats()
        
        if stats.get('document_count', 0) == 0:
            logger.info("Vector DB empty, initializing production corpus")
            success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
            final_stats = retriever.get_collection_stats()
            return {
                "success": success,
                "vector_db": final_stats,
                "message": "Production corpus initialized" if success else "Initialization failed"
            }
        else:
            return {
                "success": True,
                "vector_db": stats,
                "message": f"Vector DB already has {stats.get('document_count', 0)} chunks"
            }
    except Exception as e:
        logger.error(f"Failed to initialize production corpus: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Initialization failed"
        }


@router.get("/health/debug")
async def health_debug():
    """Debug endpoint to check corpus file availability and vector DB status."""
    try:
        from pathlib import Path
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        # Check corpus file locations
        backend_dir = Path(__file__).parent.parent.parent
        project_root = Path(__file__).parent.parent.parent.parent
        
        corpus_locations = {
            "backend_corpus_production": str(backend_dir / "corpus_production.jsonl"),
            "backend_hackathon_resources": str(backend_dir / "hackathon-resources" / "corpus" / "corpus_production.jsonl"),
            "project_root_corpus_production": str(project_root / "hackathon-resources" / "corpus" / "corpus_production.jsonl"),
            "project_root_corpus_full": str(project_root / "hackathon-resources" / "corpus" / "corpus.jsonl")
        }
        
        corpus_status = {}
        for name, path in corpus_locations.items():
            corpus_status[name] = {
                "path": path,
                "exists": Path(path).exists()
            }
        
        stats = retriever.get_collection_stats()
        
        return {
            "production_mode": settings.production_mode,
            "production_max_docs": settings.production_max_docs,
            "vector_db_stats": stats,
            "corpus_file_status": corpus_status,
            "embedding_model_type": retriever.embedding_type
        }
    except Exception as e:
        logger.error(f"Health debug failed: {e}")
        return {
            "error": str(e)
        }


@router.get("/health/status")
async def health_status():
    """Get detailed health status including actual vector DB stats."""
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        stats = retriever.get_collection_stats()
        
        return {
            "status": "healthy",
            "llm_configured": bool(settings.google_api_key or settings.llm_api_key),
            "tigergraph_configured": bool(settings.tg_host and settings.tg_secret),
            "vector_db": stats
        }
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
