"""Evidence endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import Evidence, GraphContext

router = APIRouter()


@router.get("/evidence/{run_id}", response_model=list[Evidence])
async def get_evidence(run_id: str):
    """Get evidence for a specific run."""
    # Placeholder - will be implemented with evidence storage
    raise HTTPException(status_code=501, detail="Evidence storage not yet implemented")


@router.get("/evidence/{run_id}/graph", response_model=GraphContext)
async def get_evidence_graph(run_id: str):
    """Get graph context for evidence."""
    # Placeholder - will be implemented with graph context storage
    raise HTTPException(status_code=501, detail="Graph context not yet implemented")
