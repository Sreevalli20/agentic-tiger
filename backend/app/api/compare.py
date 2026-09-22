"""Comparison endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import CompareRequest, CompareResponse
from app.services.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/compare", response_model=CompareResponse)
async def compare_pipelines(request: CompareRequest):
    """Compare multiple pipelines on the same question."""
    try:
        results = {}
        for pipeline in request.pipelines:
            result = await orchestrator.run_pipeline(
                question=request.question,
                pipeline=pipeline
            )
            results[pipeline] = result
        
        # Generate comparison
        comparison = {
            "latency_comparison": {
                pipeline: result.metrics.total_latency_ms
                for pipeline, result in results.items()
            },
            "token_comparison": {
                pipeline: result.metrics.total_tokens
                for pipeline, result in results.items()
            },
            "evidence_count": {
                pipeline: len(result.evidence)
                for pipeline, result in results.items()
            }
        }
        
        return CompareResponse(
            question=request.question,
            results=results,
            comparison=comparison
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
