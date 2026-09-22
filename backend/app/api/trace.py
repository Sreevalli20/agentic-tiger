"""Agent trace endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentTrace

router = APIRouter()


@router.get("/trace/{run_id}", response_model=AgentTrace)
async def get_trace(run_id: str):
    """Get agent trace for a specific run."""
    # Placeholder - will be implemented with trace storage
    raise HTTPException(status_code=501, detail="Trace storage not yet implemented")
