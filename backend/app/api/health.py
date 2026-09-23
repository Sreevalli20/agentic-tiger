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
    
    # Check vector DB stats and initialize if empty in production
    vector_db_stats = {'status': 'lazy', 'message': 'Vector DB available for lazy initialization'}
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        actual_stats = retriever.get_collection_stats()
        
        # If vector DB is empty in production mode, initialize it
        if settings.production_mode and actual_stats.get('document_count', 0) == 0:
            logger.info("Production mode: Vector DB empty, initializing corpus")
            retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
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
