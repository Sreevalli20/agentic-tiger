"""Agentic GraphRAG pipeline with dynamic orchestration."""
from app.pipelines.base import BasePipeline
from app.models.schemas import PipelineResult, PipelineMetrics, PipelineType, Evidence, Citation, GraphContext
from app.agents.agent_orchestrator import AgentOrchestrator
import time
import logging

logger = logging.getLogger(__name__)


class AgenticPipeline(BasePipeline):
    """Agentic GraphRAG pipeline with dynamic tool selection."""
    
    def __init__(self):
        """Initialize Agentic pipeline."""
        self.agent_orchestrator = AgentOrchestrator()
    
    async def run(self, question: str) -> PipelineResult:
        """Run Agentic GraphRAG pipeline on a question."""
        start_time = time.time()
        metrics = self.create_metrics()
        
        logger.info(f"Running Agentic GraphRAG pipeline for: {question[:50]}...")
        
        # Run agent orchestrator
        answer, trace, evidence, state_dict = await self.agent_orchestrator.run(question)
        
        # Update metrics from state
        metrics.total_latency_ms = self.track_time(start_time)
        metrics.chunks_retrieved = len(evidence)
        metrics.retrieval_steps = len(trace.steps)
        metrics.iterations = trace.steps[-1].step if trace.steps else 0
        metrics.tools_used = [step.tool.value for step in trace.steps]
        metrics.strategy_changes = len(trace.strategy_changes)
        metrics.total_tokens = trace.total_tokens
        
        # Create graph context from state
        graph_context = GraphContext(
            entities=state_dict.get("graph_entities", []),
            relationships=state_dict.get("graph_relationships", []),
            traversal_depth=0,
            nodes_visited=len(state_dict.get("graph_entities", [])),
            edges_traversed=len(state_dict.get("graph_relationships", []))
        )
        
        # Create citations from evidence
        citations = []
        for i, ev in enumerate(evidence):
            citations.append(Citation(
                claim=f"Claim {i+1}",
                evidence_ids=[ev.metadata.chunk_id or f"ev_{i}"],
                confidence=ev.metadata.confidence
            ))
        
        return PipelineResult(
            pipeline=PipelineType.AGENTIC,
            question=question,
            answer=answer,
            confidence=state_dict.get("confidence", 0.0),
            evidence=evidence,
            citations=citations,
            graph_context=graph_context,
            agent_trace=trace,
            metrics=metrics
        )
