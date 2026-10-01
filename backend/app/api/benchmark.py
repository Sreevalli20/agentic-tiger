"""Benchmark endpoint."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import BenchmarkRun, BenchmarkResult
from app.benchmark.benchmark_runner import benchmark_runner
from app.models.schemas import PipelineType
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/benchmark/run")
async def run_benchmark(
    background_tasks: BackgroundTasks,
    pipelines: Optional[list[str]] = None,
    limit: Optional[int] = None,
    resume_from: Optional[str] = None
):
    """Run benchmark on evaluation questions."""
    try:
        # Convert pipeline strings to PipelineType enum
        pipeline_types = []
        if pipelines:
            for p in pipelines:
                try:
                    pipeline_types.append(PipelineType(p))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid pipeline: {p}")
        else:
            pipeline_types = [PipelineType.RAG, PipelineType.GRAPHRAG, PipelineType.AGENTIC]
        
        # Run benchmark directly (not in background for simpler deployment)
        # Use a small limit by default for web requests
        if limit is None:
            limit = 5
        
        result = await benchmark_runner.run_benchmark(
            pipelines=pipeline_types,
            limit=limit,
            resume_from=resume_from
        )
        
        return {
            "status": "completed",
            "run_id": result.run_id,
            "total_questions": result.total_questions,
            "completed_questions": result.completed_questions,
            "pipelines": [p.value for p in pipeline_types],
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to run benchmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/results")
async def get_benchmark_results():
    """Get all benchmark results."""
    try:
        runs = benchmark_runner.get_all_runs()
        return {"runs": runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/{run_id}")
async def get_benchmark_run(run_id: str):
    """Get specific benchmark run."""
    try:
        results = benchmark_runner.get_results(run_id)
        if results is None:
            raise HTTPException(status_code=404, detail="Benchmark run not found")
        
        metrics = benchmark_runner.calculate_metrics(run_id)
        
        return {
            "run_id": run_id,
            "results": results,
            "metrics": metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/{run_id}/metrics")
async def get_benchmark_metrics(run_id: str):
    """Get metrics for a specific benchmark run."""
    try:
        metrics = benchmark_runner.calculate_metrics(run_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Benchmark run not found or no metrics available")
        
        return {
            "run_id": run_id,
            "metrics": metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
