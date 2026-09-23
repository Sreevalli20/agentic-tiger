"""GraphRAG pipeline with real TigerGraph integration."""
import json
from app.pipelines.base import BasePipeline
from app.models.schemas import PipelineResult, PipelineMetrics, PipelineType, Evidence, EvidenceMetadata, Citation, GraphContext
from app.tigergraph.graph_service import GraphService
from app.retrieval.vector_retriever import VectorRetriever
from app.services.llm_service import LLMService
from app.core.config import settings
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


class GraphRAGPipeline(BasePipeline):
    """GraphRAG pipeline using TigerGraph for graph traversal."""
    
    def __init__(self):
        """Initialize GraphRAG pipeline."""
        self.graph_service = GraphService()
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
        """Run GraphRAG pipeline on a question."""
        start_time = time.time()
        metrics = self.create_metrics()
        
        # Lazy load corpus when pipeline is actually used
        self._ensure_corpus_loaded()
        
        logger.info(f"Running GraphRAG pipeline for: {question[:50]}...")
        
        # Step 1: Entity extraction and linking
        entity_start = time.time()
        entities = await self.graph_service.extract_entities(question)
        metrics.retrieval_time_ms = self.track_time(entity_start)
        
        # Step 2: Graph traversal
        graph_start = time.time()
        graph_context = await self.graph_service.traverse_graph(entities, max_hops=2)
        metrics.graph_nodes = graph_context.nodes_visited
        metrics.graph_edges = graph_context.edges_traversed
        graph_time = self.track_time(graph_start)
        
        # Step 3: Document retrieval based on graph context
        retrieval_start = time.time()
        
        # Use graph entities to enhance retrieval if available
        if graph_context.entities:
            # Combine question with entity names for better retrieval
            enhanced_query = question + " " + " ".join(graph_context.entities[:3])
            chunks = await self.vector_retriever.search(enhanced_query, top_k=settings.top_k_retrieval)
        else:
            chunks = await self.vector_retriever.search(question, top_k=settings.top_k_retrieval)
        
        metrics.retrieval_time_ms += self.track_time(retrieval_start)
        metrics.chunks_retrieved = len(chunks)
        metrics.retrieval_steps = 2  # Entity extraction + graph traversal
        
        if not chunks:
            logger.warning("No chunks retrieved for GraphRAG")
            return PipelineResult(
                pipeline=PipelineType.GRAPHRAG,
                question=question,
                answer="No relevant documents found in the corpus to answer this question.",
                confidence=0.0,
                evidence=[],
                citations=[],
                graph_context=graph_context,
                metrics=metrics
            )
        
        # Step 4: Generate answer with graph context
        generation_start = time.time()
        
        # Add graph context to the prompt
        enhanced_chunks = chunks.copy()
        if graph_context.relationships:
            graph_context_text = f"\n\nGraph Context:\n{json.dumps(graph_context.relationships[:5], indent=2)}"
            enhanced_chunks.append({"content": graph_context_text, "document_id": "graph_context"})
        
        answer, tokens = await self.llm_service.generate_answer(question, enhanced_chunks)
        metrics.generation_time_ms = self.track_time(generation_start)
        metrics.input_tokens = tokens["input"]
        metrics.output_tokens = tokens["output"]
        metrics.total_tokens = tokens["total"]
        
        # Step 5: Create evidence and citations
        evidence = []
        citations = []
        for i, chunk in enumerate(chunks):
            evidence.append(Evidence(
                content=chunk.get("content", ""),
                metadata=EvidenceMetadata(
                    source=chunk.get("document_id", "unknown"),
                    source_type="graph",
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
        
        # Calculate confidence based on retrieval scores and graph traversal
        if chunks:
            avg_score = sum(chunk.get("score", 0.0) for chunk in chunks) / len(chunks)
            # Boost confidence if graph traversal was successful
            graph_boost = 0.1 if graph_context.nodes_visited > 0 else 0.0
            confidence = min(1.0, avg_score + graph_boost)
        else:
            confidence = 0.0
        
        # Calculate total latency
        metrics.total_latency_ms = self.track_time(start_time)
        
        return PipelineResult(
            pipeline=PipelineType.GRAPHRAG,
            question=question,
            answer=answer,
            confidence=confidence,
            evidence=evidence,
            citations=citations,
            graph_context=graph_context,
            metrics=metrics
        )
