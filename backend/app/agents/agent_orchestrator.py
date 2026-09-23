"""Agent orchestrator for Agentic GraphRAG."""
from typing import List, Dict, Any, Optional
from app.agents.agent_state import AgentState
from app.models.schemas import ToolType, Evidence, EvidenceMetadata, AgentStep, AgentTrace
from app.retrieval.vector_retriever import VectorRetriever
from app.tigergraph.graph_service import GraphService
from app.services.llm_service import LLMService
from app.core.config import settings
from app.storage.storage_manager import storage_manager
from pathlib import Path
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrator for Agentic GraphRAG with dynamic tool selection."""
    
    def __init__(self):
        """Initialize agent orchestrator."""
        self.vector_retriever = VectorRetriever()
        self.graph_service = GraphService()
        self.llm_service = LLMService()
        # Remove corpus loading from __init__ - will load lazily
    
    def _ensure_corpus_loaded(self):
        """Ensure the corpus is loaded into the vector database (lazy load)."""
        try:
            self.vector_retriever._ensure_initialized()
            stats = self.vector_retriever.get_collection_stats()
            
            # Only load if completely empty (0 documents)
            if stats.get('document_count', 0) == 0:
                logger.warning("Vector database is empty - attempting production initialization")
                from app.core.config import settings
                self.vector_retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
            else:
                logger.info(f"Vector database already contains {stats['document_count']} chunks - using existing index")
        except Exception as e:
            logger.error(f"Failed to check corpus status: {e}")

    async def run(self, question: str) -> tuple[str, AgentTrace, List[Evidence], Dict[str, Any]]:
        """Run agentic investigation on a question."""
        # Lazy load corpus when pipeline is actually used
        self._ensure_corpus_loaded()
        
        # Initialize state
        state = AgentState(
            question=question,
            run_id=str(uuid.uuid4())
        )
        
        trace = AgentTrace(
            question=question,
            run_id=state.run_id
        )
        
        logger.info(f"Starting agentic investigation for: {question[:50]}...")
        
        # Main agent loop
        while state.iteration < settings.max_agent_iterations:
            state.iteration += 1
            step_start = time.time()
            
            # Decide next action
            action = await self._decide_action(state)
            
            # Execute action
            step_result = await self._execute_action(state, action)
            
            # Update state
            await self._update_state(state, step_result)
            
            # Record step in trace
            trace.steps.append(AgentStep(
                step=state.iteration,
                tool=action,
                input=f"Action: {action}",
                result_summary=step_result.get("summary", ""),
                tokens=step_result.get("tokens", 0),
                latency_ms=self.track_time(step_start)
            ))
            
            # Check stopping conditions
            should_stop, reason = await self._should_stop(state)
            if should_stop:
                state.stopping_reason = reason
                logger.info(f"Stopping investigation: {reason}")
                break
        
        # Generate final answer
        final_answer, answer_tokens = await self.llm_service.generate_answer(
            question, 
            [{"content": e.content} for e in state.evidence]
        )
        state.final_answer = final_answer
        state.tokens_used += answer_tokens["total"]
        
        # Finalize trace
        trace.evidence_count = len(state.evidence)
        trace.citation_count = len(state.citations)
        trace.total_tokens = state.tokens_used
        trace.total_latency_ms = self.track_time(state.started_at.timestamp())
        trace.stopping_reason = state.stopping_reason
        
        from datetime import datetime, timezone
        state.completed_at = datetime.now(timezone.utc)
        
        # Save agent trace to persistent storage
        storage_manager.save_agent_trace({
            'trace_id': state.run_id,
            'run_id': state.run_id,
            'question': question,
            'steps': [step.model_dump() for step in trace.steps],
            'tools_used': [tool.value for tool in state.tools_used],
            'evidence_collected': [ev.model_dump() for ev in state.evidence],
            'strategy_changes': trace.strategy_changes,
            'stop_reason': state.stopping_reason,
            'timing': {
                'total_latency_ms': trace.total_latency_ms,
                'total_tokens': trace.total_tokens
            }
        })
        
        return final_answer, trace, state.evidence, state.to_dict()
    
    async def _decide_action(self, state: AgentState) -> ToolType:
        """Decide next action based on current state."""
        # Simple decision policy - can be enhanced with LLM-based decision making
        if state.iteration == 1:
            # First step: extract entities
            return ToolType.ENTITY_LINK
        elif not state.graph_entities:
            # No entities yet: extract them
            return ToolType.ENTITY_LINK
        elif len(state.evidence) < 3:
            # Need more evidence: vector search
            return ToolType.VECTOR_SEARCH
        elif not state.graph_relationships and state.iteration <= 3:
            # Have entities but no relationships: try graph traversal (limited attempts)
            return ToolType.GRAPH_TRAVERSE
        else:
            # Have evidence and graph (or max graph attempts): evaluate if sufficient
            return ToolType.EVALUATE_EVIDENCE
    
    async def _execute_action(self, state: AgentState, action: ToolType) -> Dict[str, Any]:
        """Execute the selected action."""
        if action == ToolType.ENTITY_LINK:
            return await self._action_entity_link(state)
        elif action == ToolType.GRAPH_TRAVERSE:
            return await self._action_graph_traverse(state)
        elif action == ToolType.VECTOR_SEARCH:
            return await self._action_vector_search(state)
        elif action == ToolType.EVALUATE_EVIDENCE:
            return await self._action_evaluate_evidence(state)
        else:
            return {"summary": f"Action {action} not implemented yet", "tokens": 0}
    
    async def _action_entity_link(self, state: AgentState) -> Dict[str, Any]:
        """Extract and link entities."""
        entities = await self.graph_service.extract_entities(state.question)
        state.graph_entities = entities
        state.tools_used.append(ToolType.ENTITY_LINK)
        return {
            "summary": f"Extracted {len(entities)} entities: {entities[:3]}",
            "tokens": 0
        }
    
    async def _action_graph_traverse(self, state: AgentState) -> Dict[str, Any]:
        """Traverse graph from entities."""
        graph_context = await self.graph_service.traverse_graph(state.graph_entities)
        state.graph_relationships = graph_context.relationships
        state.tools_used.append(ToolType.GRAPH_TRAVERSE)
        return {
            "summary": f"Traversed graph: {graph_context.nodes_visited} nodes, {graph_context.edges_traversed} edges",
            "tokens": 0
        }
    
    async def _action_vector_search(self, state: AgentState) -> Dict[str, Any]:
        """Perform vector similarity search."""
        chunks = await self.vector_retriever.search(state.question, top_k=5)
        state.retrieved_chunks.extend(chunks)
        
        # Convert chunks to evidence
        for chunk in chunks:
            evidence = Evidence(
                content=chunk.get("content", ""),
                metadata=EvidenceMetadata(
                    source=chunk.get("document_id", "unknown"),
                    source_type="vector",
                    confidence=chunk.get("score", 0.0),
                    chunk_id=chunk.get("chunk_id", "")
                )
            )
            state.evidence.append(evidence)
        
        state.tools_used.append(ToolType.VECTOR_SEARCH)
        return {
            "summary": f"Retrieved {len(chunks)} chunks via vector search",
            "tokens": 0
        }
    
    async def _action_evaluate_evidence(self, state: AgentState) -> Dict[str, Any]:
        """Evaluate evidence sufficiency."""
        # Calculate evidence sufficiency score
        evidence_score = min(1.0, len(state.evidence) / 5.0)
        state.confidence = evidence_score
        state.tools_used.append(ToolType.EVALUATE_EVIDENCE)
        
        # Identify missing information
        if evidence_score < settings.evidence_sufficiency_threshold:
            state.missing_information.append("Need more supporting evidence")
        
        return {
            "summary": f"Evidence sufficiency: {evidence_score:.2f}",
            "tokens": 0
        }
    
    async def _update_state(self, state: AgentState, result: Dict[str, Any]):
        """Update state based on action result."""
        state.actions.append({
            "iteration": state.iteration,
            "result": result
        })
    
    async def _should_stop(self, state: AgentState) -> tuple[bool, str]:
        """Determine if agent should stop."""
        # Stop if evidence is sufficient
        if state.confidence >= settings.evidence_sufficiency_threshold:
            return True, f"Evidence sufficiency ({state.confidence:.2f}) meets threshold ({settings.evidence_sufficiency_threshold})"
        
        # Stop if max iterations reached
        if state.iteration >= settings.max_agent_iterations:
            return True, f"Maximum iterations ({settings.max_agent_iterations}) reached"
        
        # Stop if token budget exceeded
        if state.tokens_used >= settings.max_token_budget:
            return True, f"Token budget ({settings.max_token_budget}) exceeded"
        
        # Continue investigation
        return False, ""
    
    def track_time(self, start_time: float) -> float:
        """Calculate elapsed time in milliseconds."""
        return (time.time() - start_time) * 1000
