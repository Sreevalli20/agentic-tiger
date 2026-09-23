"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.retrieval.vector_retriever import VectorRetriever
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(force_init: bool = False):
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
        
        # In production mode, always initialize if empty
        if settings.production_mode and actual_stats.get('document_count', 0) == 0:
            logger.info(f"Production mode: Vector DB empty, initializing with production corpus")
            try:
                success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
                actual_stats = retriever.get_collection_stats()
                logger.info(f"After production initialization (success={success}): {actual_stats}")
                vector_db_stats = actual_stats
            except Exception as init_error:
                logger.error(f"Production initialization failed: {init_error}")
                logger.info(f"Returning current stats despite init failure: {actual_stats}")
                vector_db_stats = actual_stats
        elif force_init:
            logger.info(f"Force init requested, clearing and reinitializing")
            try:
                if retriever.collection:
                    retriever.collection.delete()
                    logger.info("Cleared existing vector collection")
                success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
                actual_stats = retriever.get_collection_stats()
                logger.info(f"After force initialization (success={success}): {actual_stats}")
                vector_db_stats = actual_stats
            except Exception as init_error:
                logger.error(f"Force initialization failed: {init_error}")
                vector_db_stats = actual_stats
        else:
            # Return actual stats if we have documents
            if actual_stats.get('document_count', 0) > 0:
                vector_db_stats = actual_stats
            elif actual_stats.get('status') == 'initialized':
                vector_db_stats = actual_stats
    except Exception as e:
        logger.warning(f"Failed to get/initialize vector DB stats: {e}")
        vector_db_stats = {'status': 'error', 'error': str(e)}
    
    return HealthResponse(
        status="healthy",
        tigergraph_connected=tigergraph_configured,
        vector_db_connected=True,
        llm_configured=llm_configured,
        vector_db_stats=vector_db_stats
    )


@router.get("/health/init")
async def init_corpus():
    """Initialize corpus on demand."""
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        # Clear existing data
        if retriever.collection:
            try:
                retriever.collection.delete()
                logger.info("Cleared existing vector collection")
            except Exception as clear_error:
                logger.warning(f"Failed to clear collection: {clear_error}")
        
        # Create production corpus
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        stats = retriever.get_collection_stats()
        
        return {
            "success": success,
            "vector_db_stats": stats,
            "message": "Corpus initialization completed"
        }
    except Exception as e:
        logger.error(f"Corpus initialization failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Corpus initialization failed"
        }


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


@router.post("/health/force-init")
async def force_initialize():
    """Force initialize production corpus regardless of current state.
    
    Returns:
        Initialization status and statistics
    """
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        logger.info("Force initializing production corpus")
        # Clear existing data first
        if retriever.collection:
            try:
                retriever.collection.delete()
                logger.info("Cleared existing vector collection")
            except Exception as clear_error:
                logger.warning(f"Failed to clear collection: {clear_error}")
        
        # Use production corpus initialization
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        final_stats = retriever.get_collection_stats()
        
        # Force return actual stats
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


@router.post("/health/test-fallback")
async def test_fallback():
    """Test fallback corpus creation."""
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        logger.info("Testing fallback corpus creation")
        success = retriever._create_fallback_corpus(max_docs=10)
        stats = retriever.get_collection_stats()
        
        return {
            "success": success,
            "vector_db_stats": stats,
            "message": "Fallback corpus created" if success else "Fallback corpus creation failed"
        }
    except Exception as e:
        logger.error(f"Failed to create fallback corpus: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Fallback corpus creation failed"
        }


@router.get("/health/debug")
async def health_debug():
    """Debug endpoint to check corpus file availability and vector DB status."""
    try:
        from pathlib import Path
        import os
        
        # Check corpus file locations
        backend_dir = Path(__file__).parent.parent.parent
        project_root = Path(__file__).parent.parent.parent.parent
        cwd = Path.cwd()
        
        corpus_locations = {
            "cwd_corpus_production": str(cwd / "corpus_production.jsonl"),
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
        
        # List files in current directory
        cwd_files = []
        try:
            cwd_files = [f for f in os.listdir(cwd) if f.endswith('.jsonl')]
        except:
            pass
        
        # Get vector DB stats
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        stats = retriever.get_collection_stats()
        
        return {
            "production_mode": settings.production_mode,
            "production_max_docs": settings.production_max_docs,
            "cwd": str(cwd),
            "cwd_jsonl_files": cwd_files,
            "vector_db_stats": stats,
            "corpus_file_status": corpus_status,
            "embedding_model_type": retriever.embedding_type
        }
    except Exception as e:
        logger.error(f"Health debug failed: {e}")
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
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
