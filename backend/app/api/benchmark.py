"""Benchmark endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import BenchmarkRun, BenchmarkResult
from typing import Optional

router = APIRouter()


@router.post("/benchmark/run", response_model=BenchmarkRun)
async def run_benchmark():
    """Run benchmark on evaluation questions."""
    # Placeholder - will be implemented with benchmark runner
    raise HTTPException(status_code=501, detail="Benchmark runner not yet implemented")


@router.get("/benchmark/results")
async def get_benchmark_results():
    """Get all benchmark results."""
    # Placeholder - will be implemented with benchmark runner
    raise HTTPException(status_code=501, detail="Benchmark results not yet implemented")


@router.get("/benchmark/{run_id}")
async def get_benchmark_run(run_id: str):
    """Get specific benchmark run."""
    # Placeholder - will be implemented with benchmark runner
    raise HTTPException(status_code=501, detail="Benchmark run not yet implemented")
