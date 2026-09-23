"""Agent trace endpoint."""
from fastapi import APIRouter, HTTPException
from app.storage.storage_manager import storage_manager

router = APIRouter()


@router.get("/trace/{run_id}")
async def get_trace(run_id: str):
    """Get agent trace for a specific run."""
    try:
        # First try to get as agent trace
        trace = storage_manager.get_agent_trace(run_id)
        if trace:
            return trace
        
        # If not found as trace, try to get as investigation and return minimal trace info
        investigation = storage_manager.get_investigation(run_id)
        if investigation:
            # Return investigation data as trace-like structure
            return {
                'trace_id': run_id,
                'run_id': run_id,
                'question': investigation.get('question'),
                'steps': [],
                'tools_used': [],
                'evidence_collected': investigation.get('evidence', []),
                'strategy_changes': [],
                'stop_reason': 'Investigation completed',
                'timing': investigation.get('metrics', {}),
                'total_tokens': investigation.get('metrics', {}).get('total_tokens', 0),
                'evidence_count': len(investigation.get('evidence', []))
            }
        
        raise HTTPException(status_code=404, detail="Trace not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
