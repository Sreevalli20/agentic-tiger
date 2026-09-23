"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.retrieval.vector_retriever import VectorRetriever
from app.tigergraph.graph_service import GraphService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with actual connection status."""
    # Check vector DB
    vector_retriever = VectorRetriever()
    vector_stats = vector_retriever.get_collection_stats()
    vector_db_connected = vector_stats.get('status') == 'initialized'
    
    # Check TigerGraph with actual connection test
    graph_service = GraphService()
    tigergraph_connected = False
    if graph_service.conn:
        try:
            # Try to get schema to verify actual connectivity
            schema = graph_service.conn.getSchema()
            tigergraph_connected = schema is not None
            logger.info(f"TigerGraph connection test: {'SUCCESS' if tigergraph_connected else 'FAILED'}")
        except Exception as e:
            logger.error(f"TigerGraph connection test failed: {e}")
            tigergraph_connected = False
    
    # Check LLM (prefer GOOGLE_API_KEY, fallback to LLM_API_KEY)
    llm_configured = bool(settings.google_api_key or settings.llm_api_key)
    
    return HealthResponse(
        status="healthy",
        tigergraph_connected=tigergraph_connected,
        vector_db_connected=vector_db_connected,
        llm_configured=llm_configured,
        vector_db_stats=vector_stats
    )
