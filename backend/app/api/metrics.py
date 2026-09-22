"""Metrics endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import MetricsSummary

router = APIRouter()


@router.get("/metrics", response_model=MetricsSummary)
async def get_metrics():
    """Get metrics summary for dashboard."""
    # Placeholder - will be implemented with metrics calculation
    raise HTTPException(status_code=501, detail="Metrics calculation not yet implemented")
