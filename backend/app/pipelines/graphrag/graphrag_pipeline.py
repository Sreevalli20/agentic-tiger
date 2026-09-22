"""GraphRAG pipeline with TigerGraph integration."""
from app.pipelines.base import BasePipeline
from app.models.schemas import PipelineResult, PipelineMetrics, PipelineType, Evidence, EvidenceMetadata, Citation, GraphContext
from app.tigergraph.graph_service import GraphService
from app.retrieval.vector_retriever import VectorRetriever
from app.services.llm_service import LLMService
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
    
    async def run(self, question: str) -> PipelineResult:
        """Run GraphRAG pipeline on a question."""
        start_time = time.time()
        metrics = self.create_metrics()
        
        logger.info(f"Running GraphRAG pipeline for: {question[:50]}...")
        
        # Step 1: Entity extraction and linking
        entity_start = time.time()
        entities = await self.graph_service.extract_entities(question)
        entity_time = self.track_time(entity_start)
        
        # Step 2: Graph traversal
        graph_start = time.time()
        graph_context = await self.graph_service.traverse_graph(entities, max_hops=2)
        metrics.graph_nodes = graph_context.nodes_visited
        metrics.graph_edges = graph_context.edges_traversed
        graph_time = self.track_time(graph_start)
        
        # Step 3: Document retrieval based on graph
        retrieval_start = time.time()
        chunks = await self.vector_retriever.search(question, top_k=5)
        metrics.retrieval_time_ms = self.track_time(retrieval_start)
        metrics.chunks_retrieved = len(chunks)
        metrics.retrieval_steps = 2  # Entity extraction + graph traversal
        
        # Step 4: Generate answer with graph context
        generation_start = time.time()
        answer, tokens = await self.llm_service.generate_answer(question, chunks)
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
        
        # Calculate total latency
        metrics.total_latency_ms = self.track_time(start_time)
        
        return PipelineResult(
            pipeline=PipelineType.GRAPHRAG,
            question=question,
            answer=answer,
            confidence=0.75,  # Placeholder - will be calculated
            evidence=evidence,
            citations=citations,
            graph_context=graph_context,
            metrics=metrics
        )
