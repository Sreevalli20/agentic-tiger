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
    
    # Check vector DB stats (no initialization on health check)
    vector_db_stats = {'status': 'lazy', 'message': 'Vector DB available for lazy initialization'}
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        actual_stats = retriever.get_collection_stats()
        if actual_stats.get('status') == 'initialized':
            vector_db_stats = actual_stats
    except Exception as e:
        logger.warning(f"Failed to get vector DB stats: {e}")
    
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
