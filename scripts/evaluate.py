#!/usr/bin/env python3
"""Evaluation script for calculating metrics from benchmark results."""
import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluator for calculating metrics from benchmark results."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.results_path = Path(settings.benchmark_output_path)
    
    def load_run(self, run_id: str) -> Dict[str, Any]:
        """Load benchmark run from file."""
        run_file = self.results_path / f"benchmark_{run_id}.json"
        if not run_file.exists():
            logger.error(f"Benchmark run not found: {run_file}")
            return None
        
        with open(run_file, 'r') as f:
            return json.load(f)
    
    def calculate_metrics(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate metrics from benchmark run."""
        results = run.get("results", [])
        
        if not results:
            logger.warning("No results to evaluate")
            return {}
        
        # Group by pipeline
        pipeline_results = {}
        for result in results:
            pipeline = result.get("pipeline")
            if pipeline not in pipeline_results:
                pipeline_results[pipeline] = []
            pipeline_results[pipeline].append(result)
        
        # Calculate metrics per pipeline
        metrics = {}
        for pipeline, results_list in pipeline_results.items():
            metrics[pipeline] = self._calculate_pipeline_metrics(results_list)
        
        # Calculate overall classification
        metrics["classification"] = self._classify_questions(results)
        
        return metrics
    
    def _calculate_pipeline_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for a specific pipeline."""
        total = len(results)
        
        # Placeholder metrics - will be calculated from actual evaluation
        # These would normally come from correctness evaluation against ground truth
        accuracy = 0.0  # Will be calculated from ground truth comparison
        completeness = 0.0  # Will be calculated from expected facts
        
        # Calculate aggregate metrics from pipeline results
        total_latency = sum(r.get("result", {}).get("metrics", {}).get("total_latency_ms", 0) for r in results)
        total_tokens = sum(r.get("result", {}).get("metrics", {}).get("total_tokens", 0) for r in results)
        total_evidence = sum(len(r.get("result", {}).get("evidence", [])) for r in results)
        
        avg_latency = total_latency / total if total > 0 else 0
        avg_tokens = total_tokens / total if total > 0 else 0
        avg_evidence = total_evidence / total if total > 0 else 0
        
        return {
            "total_questions": total,
            "accuracy": accuracy,
            "completeness": completeness,
            "avg_latency_ms": avg_latency,
            "avg_tokens": avg_tokens,
            "avg_evidence": avg_evidence,
            "total_latency_ms": total_latency,
            "total_tokens": total_tokens
        }
    
    def _classify_questions(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Classify questions based on which pipeline was most effective."""
        # Placeholder classification logic
        # This would analyze the results to determine:
        # - RAG sufficient (simple questions)
        # - GraphRAG useful (relationship questions)
        # - Agentic useful (complex multi-hop questions)
        
        return {
            "rag_sufficient": 0,
            "graphrag_useful": 0,
            "agentic_useful": 0
        }
    
    def generate_report(self, run_id: str) -> str:
        """Generate evaluation report."""
        run = self.load_run(run_id)
        if not run:
            return None
        
        metrics = self.calculate_metrics(run)
        
        report = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": run.get("configuration", {}),
            "metrics": metrics
        }
        
        # Save report
        report_file = self.results_path / f"report_{run_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Generated report: {report_file}")
        return str(report_file)


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate benchmark results")
    parser.add_argument("run_id", help="Benchmark run ID to evaluate")
    parser.add_argument("--output", help="Output directory for report")
    
    args = parser.parse_args()
    
    evaluator = Evaluator()
    
    if args.output:
        evaluator.results_path = Path(args.output)
    
    report_path = evaluator.generate_report(args.run_id)
    
    if report_path:
        print(f"Evaluation report generated: {report_path}")
        return True
    else:
        print("Evaluation failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
