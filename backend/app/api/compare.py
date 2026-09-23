"""Comparison endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import CompareRequest, CompareResponse
from app.services.orchestrator import Orchestrator
from app.storage.storage_manager import storage_manager
import uuid

router = APIRouter()
orchestrator = Orchestrator()


@router.post("/compare")
async def compare_pipelines(request: CompareRequest):
    """Compare multiple pipelines on the same question."""
    try:
        results = {}
        comparison_id = str(uuid.uuid4())
        
        for pipeline in request.pipelines:
            result = await orchestrator.run_pipeline(
                question=request.question,
                pipeline=pipeline
            )
            results[pipeline] = result
            
            # Save each comparison result to storage
            storage_manager.save_investigation({
                'id': f"{comparison_id}_{pipeline.value}",
                'question': result.question,
                'pipeline': result.pipeline.value,
                'answer': result.answer,
                'confidence': result.confidence,
                'evidence': [ev.model_dump() for ev in result.evidence],
                'citations': [cit.model_dump() for cit in result.citations],
                'metrics': result.metrics.model_dump(),
                'graph_context': result.graph_context.model_dump() if result.graph_context else {}
            })
        
        # Generate comparison
        comparison = {
            "latency_comparison": {
                pipeline.value: result.metrics.total_latency_ms
                for pipeline, result in results.items()
            },
            "token_comparison": {
                pipeline.value: result.metrics.total_tokens
                for pipeline, result in results.items()
            },
            "evidence_count": {
                pipeline.value: len(result.evidence)
                for pipeline, result in results.items()
            }
        }
        
        return {
            "question": request.question,
            "results": results,
            "comparison": comparison,
            "comparison_id": comparison_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
