"""Investigation endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import InvestigateRequest, InvestigateResponse, PipelineResult
from app.services.orchestrator import Orchestrator
from app.storage.storage_manager import storage_manager
from app.core.config import settings
import uuid
import asyncio

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/investigate")
async def investigate(request: InvestigateRequest):
    """Investigate a question using the specified pipeline with timeout protection."""
    try:
        # Add overall timeout protection for the entire investigation
        result = await asyncio.wait_for(
            orchestrator.run_pipeline(
                question=request.question,
                pipeline=request.pipeline
            ),
            timeout=30.0  # 30 second overall timeout
        )
        
        # Save investigation to persistent storage
        investigation_id = str(uuid.uuid4())
        storage_manager.save_investigation({
            'id': investigation_id,
            'question': result.question,
            'pipeline': result.pipeline.value,
            'answer': result.answer,
            'confidence': result.confidence,
            'evidence': [ev.model_dump() for ev in result.evidence],
            'citations': [cit.model_dump() for cit in result.citations],
            'metrics': result.metrics.model_dump(),
            'graph_context': result.graph_context.model_dump() if result.graph_context else {}
        })
        
        return {
            "result": result,
            "investigation_id": investigation_id,
            "run_id": investigation_id  # Add run_id for consistency with trace/evidence endpoints
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Investigation timed out. Please try a simpler question.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
