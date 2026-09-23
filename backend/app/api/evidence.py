"""Evidence endpoint."""
from fastapi import APIRouter, HTTPException
from app.storage.storage_manager import storage_manager
from app.models.schemas import GraphContext

router = APIRouter()


@router.get("/evidence/{run_id}")
async def get_evidence(run_id: str):
    """Get evidence for a specific run."""
    try:
        # Get investigation data which contains evidence
        investigation = storage_manager.get_investigation(run_id)
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        return investigation.get('evidence', [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evidence/{run_id}/graph", response_model=GraphContext)
async def get_evidence_graph(run_id: str):
    """Get graph context for evidence."""
    try:
        # Get investigation data which contains graph context
        investigation = storage_manager.get_investigation(run_id)
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        return investigation.get('graph_context', {})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
