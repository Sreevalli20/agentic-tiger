"""Configuration endpoint."""
from fastapi import APIRouter
from app.core.config import settings
from app.models.schemas import HealthResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config")
async def get_config():
    """Get current configuration (without secrets)."""
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_configured": bool(settings.llm_api_key),
        "tigergraph_host": settings.tg_host,
        "tigergraph_port": settings.tg_port,
        "tigergraph_graph": settings.tg_graphname,
        "tigergraph_configured": bool(settings.tg_secret),
        "vector_db_path": settings.vector_db_path,
        "embedding_model": settings.embedding_model,
        "max_agent_iterations": settings.max_agent_iterations,
        "evidence_sufficiency_threshold": settings.evidence_sufficiency_threshold,
        "max_token_budget": settings.max_token_budget
    }
