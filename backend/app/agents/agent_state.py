"""Agent state management for Agentic GraphRAG."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from app.models.schemas import ToolType, Evidence, GraphContext


@dataclass
class AgentState:
    """State object for Agentic GraphRAG orchestrator."""
    
    # Core
    question: str
    iteration: int = 0
    run_id: str = ""
    
    # Planning
    plan: List[str] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Evidence
    evidence: List[Evidence] = field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Graph
    graph_entities: List[str] = field(default_factory=list)
    graph_relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics
    confidence: float = 0.0
    tokens_used: int = 0
    latency_ms: float = 0.0
    
    # Agent behavior
    tools_used: List[ToolType] = field(default_factory=list)
    strategy_changes: List[str] = field(default_factory=list)
    
    # Stopping conditions
    missing_information: List[str] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    stopping_reason: str = ""
    
    # Final output
    final_answer: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "question": self.question,
            "iteration": self.iteration,
            "run_id": self.run_id,
            "plan": self.plan,
            "actions": self.actions,
            "evidence_count": len(self.evidence),
            "graph_entities": self.graph_entities,
            "graph_relationships": self.graph_relationships,
            "confidence": self.confidence,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "tools_used": [t.value for t in self.tools_used],
            "strategy_changes": self.strategy_changes,
            "missing_information": self.missing_information,
            "contradictions": self.contradictions,
            "stopping_reason": self.stopping_reason,
            "final_answer": self.final_answer,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else None
        }
