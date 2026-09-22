"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        tigergraph_connected=False,  # Will be updated when TigerGraph service is implemented
        vector_db_connected=False,  # Will be updated when vector service is implemented
        llm_configured=bool(settings.llm_api_key)
    )
