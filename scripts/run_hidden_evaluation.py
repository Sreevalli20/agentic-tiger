#!/usr/bin/env python3
"""Script to run 50 hidden evaluation questions through Agentic GraphRAG pipeline."""
import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.pipelines.agentic.agentic_pipeline import AgenticPipeline
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HiddenEvaluationRunner:
    """Runner for hidden evaluation questions."""
    
    def __init__(self):
        """Initialize evaluation runner."""
        self.pipeline = AgenticPipeline()
        self.questions_path = Path(__file__).parent.parent / "hackathon-resources" / "questions" / "eval_hidden.jsonl"
        self.output_path = Path(__file__).parent.parent / "evaluation" / "hidden_questions_results.json"
    
    def load_hidden_questions(self) -> List[Dict[str, Any]]:
        """Load hidden evaluation questions."""
        try:
            if not self.questions_path.exists():
                logger.error(f"Hidden questions file not found: {self.questions_path}")
                return []
            
            questions = []
            with open(self.questions_path, 'r', encoding='utf-8') as f:
                for line in f:
                    q = json.loads(line.strip())
                    questions.append(q)
            
            logger.info(f"Loaded {len(questions)} hidden evaluation questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to load hidden questions: {e}")
            return []
    
    def format_agentic_trace(self, trace) -> List[Dict[str, Any]]:
        """Format agent trace for JSON output."""
        formatted_trace = []
        
        for step in trace.steps:
            formatted_trace.append({
                "step": step.step,
                "agent": "AgenticGraphRAG",
                "action": step.tool.value,
                "details": step.result_summary
            })
        
        return formatted_trace
    
    async def run_question(self, question: str, qid: str) -> Dict[str, Any]:
        """Run a single question through the Agentic pipeline."""
        logger.info(f"Running question {qid}: {question[:50]}...")
        
        try:
            result = await self.pipeline.run(question)
            
            # Format the result
            formatted_result = {
                "question": question,
                "answer": result.answer,
                "tokens_used": result.metrics.total_tokens,
                "agentic_trace": self.format_agentic_trace(result.agent_trace)
            }
            
            logger.info(f"Completed {qid}: tokens={result.metrics.total_tokens}, steps={len(result.agent_trace.steps)}")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Failed to run question {qid}: {e}")
            return {
                "question": question,
                "answer": f"ERROR: {str(e)}",
                "tokens_used": 0,
                "agentic_trace": [{"step": 1, "agent": "ERROR", "action": "failed", "details": str(e)}]
            }
    
    async def run_all_questions(self) -> Dict[str, Any]:
        """Run all hidden evaluation questions."""
        questions = self.load_hidden_questions()
        
        if not questions:
            logger.error("No questions loaded")
            return None
        
        logger.info(f"Starting evaluation of {len(questions)} hidden questions")
        
        results = []
        
        for idx, q in enumerate(questions):
            logger.info(f"Processing question {idx + 1}/{len(questions)}: {q['qid']}")
            
            result = await self.run_question(q['question'], q['qid'])
            results.append(result)
            
            # Small delay between questions to avoid rate limiting
            if idx < len(questions) - 1:
                await asyncio.sleep(0.5)
        
        # Create final output
        output = {
            "project": "GraphProbe AI",
            "pipeline": "Agentic GraphRAG",
            "total_questions": len(results),
            "results": results
        }
        
        # Save to file
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Saved results to {self.output_path}")
        
        return output
    
    def validate_output(self) -> bool:
        """Validate the output JSON file."""
        try:
            if not self.output_path.exists():
                logger.error(f"Output file not found: {self.output_path}")
                return False
            
            with open(self.output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structure
            if data.get("project") != "GraphProbe AI":
                logger.error("Invalid project name")
                return False
            
            if data.get("pipeline") != "Agentic GraphRAG":
                logger.error("Invalid pipeline name")
                return False
            
            if data.get("total_questions") != 50:
                logger.error(f"Invalid total_questions: {data.get('total_questions')}")
                return False
            
            results = data.get("results", [])
            if len(results) != 50:
                logger.error(f"Invalid number of results: {len(results)}")
                return False
            
            # Check each result
            for idx, result in enumerate(results):
                if "question" not in result:
                    logger.error(f"Result {idx} missing question")
                    return False
                
                if "answer" not in result:
                    logger.error(f"Result {idx} missing answer")
                    return False
                
                if "tokens_used" not in result:
                    logger.error(f"Result {idx} missing tokens_used")
                    return False
                
                if "agentic_trace" not in result:
                    logger.error(f"Result {idx} missing agentic_trace")
                    return False
                
                # Check for placeholder values
                answer = result.get("answer", "")
                if any(placeholder in answer.lower() for placeholder in ["todo", "example", "mock", "dummy", "placeholder"]):
                    logger.error(f"Result {idx} contains placeholder value in answer")
                    return False
            
            logger.info("Validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


async def main():
    """Main function."""
    runner = HiddenEvaluationRunner()
    
    # Run all questions
    output = await runner.run_all_questions()
    
    if not output:
        logger.error("Evaluation failed")
        return False
    
    # Validate output
    if runner.validate_output():
        logger.info("Evaluation completed successfully")
        logger.info(f"Total questions processed: {output['total_questions']}")
        logger.info(f"Output file: {runner.output_path}")
        return True
    else:
        logger.error("Validation failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
