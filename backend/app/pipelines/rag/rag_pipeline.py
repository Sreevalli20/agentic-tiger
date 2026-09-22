"""RAG pipeline with vector retrieval."""
from app.pipelines.base import BasePipeline
from app.models.schemas import PipelineResult, PipelineMetrics, PipelineType, Evidence, EvidenceMetadata, Citation
from app.retrieval.vector_retriever import VectorRetriever
from app.services.llm_service import LLMService
import time
import logging

logger = logging.getLogger(__name__)


class RAGPipeline(BasePipeline):
    """RAG pipeline using vector similarity search."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_retriever = VectorRetriever()
        self.llm_service = LLMService()
    
    async def run(self, question: str) -> PipelineResult:
        """Run RAG pipeline on a question."""
        start_time = time.time()
        metrics = self.create_metrics()
        
        logger.info(f"Running RAG pipeline for: {question[:50]}...")
        
        # Step 1: Vector retrieval
        retrieval_start = time.time()
        chunks = await self.vector_retriever.search(question, top_k=5)
        metrics.retrieval_time_ms = self.track_time(retrieval_start)
        metrics.chunks_retrieved = len(chunks)
        metrics.retrieval_steps = 1
        
        # Step 2: Generate answer
        generation_start = time.time()
        answer, tokens = await self.llm_service.generate_answer(question, chunks)
        metrics.generation_time_ms = self.track_time(generation_start)
        metrics.input_tokens = tokens["input"]
        metrics.output_tokens = tokens["output"]
        metrics.total_tokens = tokens["total"]
        
        # Step 3: Create evidence and citations
        evidence = []
        citations = []
        for i, chunk in enumerate(chunks):
            evidence.append(Evidence(
                content=chunk.get("content", ""),
                metadata=EvidenceMetadata(
                    source=chunk.get("document_id", "unknown"),
                    source_type="vector",
                    confidence=chunk.get("score", 0.0),
                    chunk_id=chunk.get("chunk_id", f"chunk_{i}")
                )
            ))
        
        # Calculate total latency
        metrics.total_latency_ms = self.track_time(start_time)
        
        return PipelineResult(
            pipeline=PipelineType.RAG,
            question=question,
            answer=answer,
            confidence=0.7,  # Placeholder - will be calculated
            evidence=evidence,
            citations=citations,
            metrics=metrics
        )
