"""Benchmark runner for evaluation questions."""
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from app.data.dataset_parser import DatasetParser
from app.services.orchestrator import Orchestrator
from app.models.schemas import PipelineType, BenchmarkRun, BenchmarkResult
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Runner for benchmarking pipelines on evaluation questions."""
    
    def __init__(self):
        """Initialize benchmark runner."""
        self.orchestrator = Orchestrator()
        self.parser = None
        self.results_dir = Path(settings.benchmark_output_path)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_evaluation_questions(self, questions_path: str) -> List[Dict[str, Any]]:
        """Load public evaluation questions.
        
        Args:
            questions_path: Path to questions directory
            
        Returns:
            List of evaluation questions
        """
        try:
            public_path = Path(questions_path) / "eval_public.jsonl"
            
            if not public_path.exists():
                logger.error(f"Public questions file not found: {public_path}")
                return []
            
            questions = []
            with open(public_path, 'r', encoding='utf-8') as f:
                for line in f:
                    q = json.loads(line.strip())
                    questions.append(q)
            
            logger.info(f"Loaded {len(questions)} public evaluation questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to load evaluation questions: {e}")
            return []
    
    async def run_benchmark(
        self,
        pipelines: List[PipelineType] = None,
        limit: Optional[int] = None,
        resume_from: Optional[str] = None
    ) -> BenchmarkRun:
        """Run benchmark on evaluation questions.
        
        Args:
            pipelines: List of pipelines to test
            limit: Maximum number of questions to test
            resume_from: Run ID to resume from
            
        Returns:
            Benchmark run with results
        """
        if pipelines is None:
            pipelines = [PipelineType.RAG, PipelineType.GRAPHRAG, PipelineType.AGENTIC]
        
        run_id = resume_from or str(uuid.uuid4())
        
        # Load questions
        project_root = Path(__file__).parent.parent.parent.parent
        questions_path = project_root / "hackathon-resources" / "questions"
        questions = self.load_evaluation_questions(str(questions_path))
        
        if not questions:
            logger.error("No evaluation questions loaded")
            return BenchmarkRun(
                run_id=run_id,
                status="failed",
                configuration={"pipelines": [p.value for p in pipelines]}
            )
        
        # Apply limit if specified
        if limit:
            questions = questions[:limit]
        
        logger.info(f"Starting benchmark run {run_id} with {len(questions)} questions")
        
        # Initialize benchmark run
        benchmark_run = BenchmarkRun(
            run_id=run_id,
            total_questions=len(questions),
            completed_questions=0,
            status="in_progress",
            configuration={
                "pipelines": [p.value for p in pipelines],
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Run each question through each pipeline
        results = []
        
        for q_idx, question in enumerate(questions):
            logger.info(f"Processing question {q_idx + 1}/{len(questions)}: {question['qid']}")
            
            for pipeline in pipelines:
                try:
                    logger.info(f"  Running {pipeline.value} pipeline...")
                    
                    # Run pipeline
                    result = await self.orchestrator.run_pipeline(
                        question=question['question'],
                        pipeline=pipeline
                    )
                    
                    # Evaluate against gold answer if available
                    evaluation = None
                    if 'answer' in question:
                        evaluation = self._evaluate_answer(
                            result.answer,
                            question['answer'],
                            question.get('qtype', 'unknown')
                        )
                    
                    # Create benchmark result
                    benchmark_result = BenchmarkResult(
                        run_id=run_id,
                        question_id=question['qid'],
                        question=question['question'],
                        pipeline=pipeline,
                        result=result,
                        evaluation=evaluation
                    )
                    
                    results.append(benchmark_result)
                    
                except Exception as e:
                    logger.error(f"  Failed to run {pipeline.value}: {e}")
            
            # Update progress
            benchmark_run.completed_questions = q_idx + 1
            
            # Save intermediate results
            if (q_idx + 1) % 10 == 0:
                self._save_results(run_id, results)
        
        # Finalize benchmark run
        benchmark_run.results = results
        benchmark_run.status = "completed"
        
        # Save final results
        self._save_results(run_id, results)
        
        logger.info(f"Benchmark run {run_id} completed")
        
        return benchmark_run
    
    def _evaluate_answer(
        self,
        predicted: str,
        gold: List[str],
        qtype: str
    ) -> Dict[str, Any]:
        """Evaluate predicted answer against gold answer.
        
        Args:
            predicted: Predicted answer
            gold: Gold answer(s)
            qtype: Question type
            
        Returns:
            Evaluation metrics
        """
        from rapidfuzz import fuzz
        
        # Normalize answers for comparison
        predicted_normalized = predicted.lower().strip()
        gold_normalized = [g.lower().strip() for g in gold]
        
        # Calculate similarity scores
        similarities = [fuzz.ratio(predicted_normalized, g) for g in gold_normalized]
        max_similarity = max(similarities) if similarities else 0
        
        # Determine if correct (similarity > 80%)
        is_correct = max_similarity >= 80
        
        return {
            "is_correct": is_correct,
            "similarity": max_similarity,
            "predicted": predicted,
            "gold": gold,
            "qtype": qtype
        }
    
    def _save_results(self, run_id: str, results: List[BenchmarkResult]):
        """Save benchmark results to file.
        
        Args:
            run_id: Benchmark run ID
            results: List of benchmark results
        """
        try:
            results_file = self.results_dir / f"{run_id}.json"
            
            # Convert to serializable format
            serializable_results = []
            for r in results:
                serializable_results.append({
                    "run_id": r.run_id,
                    "question_id": r.question_id,
                    "question": r.question,
                    "pipeline": r.pipeline.value,
                    "answer": r.result.answer,
                    "confidence": r.result.confidence,
                    "metrics": r.result.metrics.dict(),
                    "evaluation": r.evaluation,
                    "timestamp": r.timestamp.isoformat()
                })
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"Saved results to {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def get_results(self, run_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load benchmark results from file.
        
        Args:
            run_id: Benchmark run ID
            
        Returns:
            List of benchmark results or None if not found
        """
        try:
            results_file = self.results_dir / f"{run_id}.json"
            
            if not results_file.exists():
                logger.warning(f"Results file not found: {results_file}")
                return None
            
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            logger.info(f"Loaded results from {results_file}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return None
    
    def get_all_runs(self) -> List[Dict[str, Any]]:
        """Get all benchmark runs.
        
        Returns:
            List of benchmark run summaries
        """
        try:
            runs = []
            
            for results_file in self.results_dir.glob("*.json"):
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    
                    if results:
                        run_id = results_file.stem
                        runs.append({
                            "run_id": run_id,
                            "total_results": len(results),
                            "file_path": str(results_file),
                            "timestamp": results[0].get("timestamp") if results else None
                        })
                except Exception as e:
                    logger.error(f"Failed to read {results_file}: {e}")
            
            return sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get runs: {e}")
            return []
    
    def calculate_metrics(self, run_id: str) -> Dict[str, Any]:
        """Calculate aggregate metrics for a benchmark run.
        
        Args:
            run_id: Benchmark run ID
            
        Returns:
            Aggregate metrics
        """
        results = self.get_results(run_id)
        
        if not results:
            return {}
        
        # Group by pipeline
        pipeline_metrics = {}
        
        for result in results:
            pipeline = result.get("pipeline")
            
            if pipeline not in pipeline_metrics:
                pipeline_metrics[pipeline] = {
                    "total": 0,
                    "correct": 0,
                    "total_tokens": 0,
                    "total_latency": 0,
                    "total_retrieval_steps": 0,
                    "question_types": {}
                }
            
            metrics = pipeline_metrics[pipeline]
            metrics["total"] += 1
            
            # Accuracy
            if result.get("evaluation", {}).get("is_correct"):
                metrics["correct"] += 1
            
            # Tokens
            metrics["total_tokens"] += result.get("metrics", {}).get("total_tokens", 0)
            
            # Latency
            metrics["total_latency"] += result.get("metrics", {}).get("total_latency_ms", 0)
            
            # Retrieval steps
            metrics["total_retrieval_steps"] += result.get("metrics", {}).get("retrieval_steps", 0)
            
            # Question type
            qtype = result.get("evaluation", {}).get("qtype", "unknown")
            if qtype not in metrics["question_types"]:
                metrics["question_types"][qtype] = {"total": 0, "correct": 0}
            metrics["question_types"][qtype]["total"] += 1
            if result.get("evaluation", {}).get("is_correct"):
                metrics["question_types"][qtype]["correct"] += 1
        
        # Calculate averages
        for pipeline, metrics in pipeline_metrics.items():
            metrics["accuracy"] = metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
            metrics["avg_tokens"] = metrics["total_tokens"] / metrics["total"] if metrics["total"] > 0 else 0
            metrics["avg_latency"] = metrics["total_latency"] / metrics["total"] if metrics["total"] > 0 else 0
            metrics["avg_retrieval_steps"] = metrics["total_retrieval_steps"] / metrics["total"] if metrics["total"] > 0 else 0
            
            # Calculate per-question-type accuracy
            for qtype, qtype_metrics in metrics["question_types"].items():
                qtype_metrics["accuracy"] = qtype_metrics["correct"] / qtype_metrics["total"] if qtype_metrics["total"] > 0 else 0
        
        return pipeline_metrics


# Global benchmark runner instance
benchmark_runner = BenchmarkRunner()
