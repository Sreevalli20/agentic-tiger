"""Initialization endpoint for forcing corpus initialization."""
from fastapi import APIRouter
from app.retrieval.vector_retriever import VectorRetriever
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/initialize")
async def initialize_corpus():
    """Force initialize production corpus regardless of current state."""
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        logger.info("Force initializing production corpus")
        
        # Clear existing data first
        if retriever.collection:
            try:
                all_ids = retriever.collection.get()['ids']
                if all_ids:
                    retriever.collection.delete(ids=all_ids)
                    logger.info(f"Cleared existing vector collection ({len(all_ids)} documents)")
            except Exception as clear_error:
                logger.warning(f"Failed to clear collection: {clear_error}")
        
        # Use production corpus initialization
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        final_stats = retriever.get_collection_stats()
        
        logger.info(f"Force init result: success={success}, chunks={final_stats.get('document_count', 0)}")
        
        return {
            "success": success,
            "vector_db": final_stats,
            "document_count": final_stats.get('document_count', 0),
            "message": "Production corpus force initialized" if success else "Initialization failed"
        }
    except Exception as e:
        logger.error(f"Failed to force initialize production corpus: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Initialization failed"
        }
