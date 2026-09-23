"""Benchmark endpoint."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import BenchmarkRun, BenchmarkResult
from app.benchmark.benchmark_runner import benchmark_runner
from app.models.schemas import PipelineType
from typing import Optional

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
        
        # Run benchmark in background
        def run_task():
            import asyncio
            asyncio.run(benchmark_runner.run_benchmark(
                pipelines=pipeline_types,
                limit=limit,
                resume_from=resume_from
            ))
        
        background_tasks.add_task(run_task)
        
        return {
            "status": "started",
            "message": "Benchmark started in background",
            "pipelines": [p.value for p in pipeline_types],
            "limit": limit
        }
    except Exception as e:
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
