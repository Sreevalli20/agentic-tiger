#!/usr/bin/env python3
"""Benchmark runner for GraphProbe AI."""
import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.config import settings
from app.models.schemas import PipelineType, BenchmarkQuestion, BenchmarkResult, BenchmarkRun
from app.services.orchestrator import Orchestrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Benchmark runner for evaluating pipelines."""
    
    def __init__(self):
        """Initialize benchmark runner."""
        self.orchestrator = Orchestrator()
        self.results_path = Path(settings.benchmark_output_path)
        self.results_path.mkdir(parents=True, exist_ok=True)
    
    def load_questions(self, questions_file: str) -> List[BenchmarkQuestion]:
        """Load evaluation questions from file."""
        file_path = Path(questions_file)
        if not file_path.exists():
            logger.error(f"Questions file not found: {file_path}")
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        questions = [
            BenchmarkQuestion(**q) if isinstance(q, dict) else BenchmarkQuestion(question_id=str(i), question=q)
            for i, q in enumerate(data)
        ]
        
        logger.info(f"Loaded {len(questions)} questions")
        return questions
    
    async def run_benchmark(
        self,
        questions: List[BenchmarkQuestion],
        pipelines: List[PipelineType] = None,
        limit: int = None,
        resume: bool = False
    ) -> BenchmarkRun:
        """Run benchmark on questions."""
        if pipelines is None:
            pipelines = [PipelineType.RAG, PipelineType.GRAPHRAG, PipelineType.AGENTIC]
        
        if limit:
            questions = questions[:limit]
        
        run_id = str(uuid.uuid4())
        benchmark_run = BenchmarkRun(
            run_id=run_id,
            total_questions=len(questions),
            completed_questions=0,
            status="in_progress",
            configuration={
                "pipelines": [p.value for p in pipelines],
                "limit": limit,
                "resume": resume
            }
        )
        
        logger.info(f"Starting benchmark run {run_id}")
        logger.info(f"Questions: {len(questions)}")
        logger.info(f"Pipelines: {[p.value for p in pipelines]}")
        
        # Run each question through each pipeline
        for i, question in enumerate(questions):
            logger.info(f"Processing question {i+1}/{len(questions)}: {question.question[:50]}...")
            
            for pipeline in pipelines:
                try:
                    result = await self.orchestrator.run_pipeline(
                        question.question,
                        pipeline
                    )
                    
                    benchmark_result = BenchmarkResult(
                        run_id=run_id,
                        question_id=question.question_id,
                        question=question.question,
                        pipeline=pipeline,
                        result=result
                    )
                    
                    benchmark_run.results.append(benchmark_result)
                    
                except Exception as e:
                    logger.error(f"Failed to run {pipeline} on question {question.question_id}: {e}")
            
            benchmark_run.completed_questions = i + 1
            
            # Save intermediate results
            if (i + 1) % 10 == 0:
                self.save_run(benchmark_run)
        
        benchmark_run.status = "completed"
        self.save_run(benchmark_run)
        
        logger.info(f"Benchmark completed: {run_id}")
        return benchmark_run
    
    def save_run(self, run: BenchmarkRun):
        """Save benchmark run to file."""
        output_file = self.results_path / f"benchmark_{run.run_id}.json"
        with open(output_file, 'w') as f:
            json.dump(run.model_dump(), f, indent=2, default=str)
        logger.info(f"Saved benchmark run to {output_file}")


async def main():
    """Main benchmark function."""
    parser = argparse.ArgumentParser(description="Run GraphProbe AI benchmark")
    parser.add_argument("--questions", default="evaluation/datasets/questions_visible.json",
                       help="Path to questions file")
    parser.add_argument("--pipeline", choices=["rag", "graphrag", "agentic"],
                       help="Run specific pipeline only")
    parser.add_argument("--limit", type=int, help="Limit number of questions")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--resume", action="store_true", help="Resume from previous run")
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    
    # Load questions
    questions = runner.load_questions(args.questions)
    if not questions:
        logger.error("No questions loaded")
        return False
    
    # Determine pipelines
    pipelines = None
    if args.pipeline:
        pipelines = [PipelineType(args.pipeline)]
    
    # Override output path if specified
    if args.output:
        runner.results_path = Path(args.output)
    
    # Run benchmark
    await runner.run_benchmark(
        questions=questions,
        pipelines=pipelines,
        limit=args.limit,
        resume=args.resume
    )
    
    return True


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
