"""Agent trace endpoint."""
from fastapi import APIRouter, HTTPException
from app.storage.storage_manager import storage_manager

router = APIRouter()


@router.get("/trace/{run_id}")
async def get_trace(run_id: str):
    """Get agent trace for a specific run."""
    try:
        trace = storage_manager.get_agent_trace(run_id)
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        return trace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
