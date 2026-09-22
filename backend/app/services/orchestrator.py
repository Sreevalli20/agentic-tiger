"""Orchestrator for running different RAG pipelines."""
from app.models.schemas import PipelineType, PipelineResult, PipelineMetrics, GraphContext
from app.pipelines.rag.rag_pipeline import RAGPipeline
from app.pipelines.graphrag.graphrag_pipeline import GraphRAGPipeline
from app.pipelines.agentic.agentic_pipeline import AgenticPipeline
import logging

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrator for running different RAG pipelines."""
    
    def __init__(self):
        """Initialize orchestrator with pipeline instances."""
        self.rag_pipeline = RAGPipeline()
        self.graphrag_pipeline = GraphRAGPipeline()
        self.agentic_pipeline = AgenticPipeline()
    
    async def run_pipeline(self, question: str, pipeline: PipelineType) -> PipelineResult:
        """Run the specified pipeline on a question."""
        logger.info(f"Running {pipeline} pipeline for question: {question[:50]}...")
        
        if pipeline == PipelineType.RAG:
            return await self.rag_pipeline.run(question)
        elif pipeline == PipelineType.GRAPHRAG:
            return await self.graphrag_pipeline.run(question)
        elif pipeline == PipelineType.AGENTIC:
            return await self.agentic_pipeline.run(question)
        else:
            raise ValueError(f"Unknown pipeline type: {pipeline}")
