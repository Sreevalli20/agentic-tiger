"""RAG pipeline with real vector retrieval from corpus."""
from app.pipelines.base import BasePipeline
from app.models.schemas import PipelineResult, PipelineMetrics, PipelineType, Evidence, EvidenceMetadata, Citation
from app.retrieval.vector_retriever import VectorRetriever
from app.services.llm_service import LLMService
from app.core.config import settings
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


class RAGPipeline(BasePipeline):
    """RAG pipeline using vector similarity search with real corpus."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.vector_retriever = VectorRetriever()
        self.llm_service = LLMService()
        # Remove corpus loading from __init__ - will load lazily
    
    def _ensure_corpus_loaded(self):
        """Ensure the corpus is loaded into the vector database (lazy load)."""
        try:
            self.vector_retriever._ensure_initialized()
            self.vector_retriever._ensure_embedding_model()
            stats = self.vector_retriever.get_collection_stats()
            
            # Only load if completely empty (0 documents)
            if stats.get('document_count', 0) == 0:
                logger.warning("Vector database is empty - initializing with production corpus")
                self.vector_retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
                stats = self.vector_retriever.get_collection_stats()
                logger.info(f"After production corpus initialization: {stats}")
            else:
                logger.info(f"Vector database already contains {stats['document_count']} chunks - using existing index")
        except Exception as e:
            logger.error(f"Failed to check corpus status: {e}")
    
    async def run(self, question: str) -> PipelineResult:
        """Run RAG pipeline on a question."""
        start_time = time.time()
        metrics = self.create_metrics()
        
        # Lazy load corpus when pipeline is actually used
        self._ensure_corpus_loaded()
        
        logger.info(f"Running RAG pipeline for: {question[:50]}...")
        
        # Step 1: Vector retrieval
        retrieval_start = time.time()
        chunks = await self.vector_retriever.search(question, top_k=settings.top_k_retrieval)
        metrics.retrieval_time_ms = self.track_time(retrieval_start)
        metrics.chunks_retrieved = len(chunks)
        metrics.retrieval_steps = 1
        
        if not chunks:
            logger.warning("No chunks retrieved from vector search")
            return PipelineResult(
                pipeline=PipelineType.RAG,
                question=question,
                answer="No relevant documents found in the corpus to answer this question.",
                confidence=0.0,
                evidence=[],
                citations=[],
                metrics=metrics
            )
        
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
            
            # Create citation for each evidence item
            citations.append(Citation(
                claim=f"Evidence {i+1}",
                evidence_ids=[chunk.get("chunk_id", f"chunk_{i}")],
                confidence=chunk.get("score", 0.0)
            ))
        
        # Calculate confidence based on retrieval scores
        if chunks:
            avg_score = sum(chunk.get("score", 0.0) for chunk in chunks) / len(chunks)
            confidence = min(1.0, avg_score + 0.1)  # Boost slightly
        else:
            confidence = 0.0
        
        # Calculate total latency
        metrics.total_latency_ms = self.track_time(start_time)
        
        return PipelineResult(
            pipeline=PipelineType.RAG,
            question=question,
            answer=answer,
            confidence=confidence,
            evidence=evidence,
            citations=citations,
            metrics=metrics
        )
