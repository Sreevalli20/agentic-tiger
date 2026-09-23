"""Metrics endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import MetricsSummary
from app.benchmark.benchmark_runner import benchmark_runner
from app.retrieval.vector_retriever import VectorRetriever
from typing import Dict, Any

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """Get metrics summary for dashboard."""
    try:
        # Get vector DB status
        retriever = VectorRetriever()
        vector_stats = retriever.get_collection_stats()
        
        # Get available benchmark runs
        runs = benchmark_runner.get_all_runs()
        
        # Determine overall status
        if vector_stats.get('document_count', 0) < 100:
            status = "PARTIAL CORPUS INDEXED"
            status_message = f"Only {vector_stats.get('document_count', 0)} chunks indexed (partial corpus)"
        elif not runs:
            status = "NO BENCHMARK RUNS"
            status_message = "Vector DB ready but no benchmark data available"
        else:
            status = "BENCHMARK PARTIALLY EXECUTED"
            status_message = f"{len(runs)} benchmark run(s) available with partial data"
        
        return {
            "status": status,
            "status_message": status_message,
            "vector_db": {
                "document_count": vector_stats.get('document_count', 0),
                "embedding_model": vector_stats.get('embedding_model', 'unknown'),
                "status": vector_stats.get('status', 'unknown')
            },
            "benchmark_runs": len(runs),
            "latest_run": runs[0] if runs else None,
            "note": "Full corpus benchmark not completed due to time constraints. Using partial indexed data for demo."
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "status_message": f"Failed to get metrics: {str(e)}",
            "vector_db": {"status": "error"},
            "benchmark_runs": 0,
            "note": "Metrics collection failed"
        }
