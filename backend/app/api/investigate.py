"""Investigation endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import InvestigateRequest, InvestigateResponse, PipelineResult
from app.services.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest):
    """Investigate a question using the specified pipeline."""
    try:
        result = await orchestrator.run_pipeline(
            question=request.question,
            pipeline=request.pipeline
        )
        return InvestigateResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
