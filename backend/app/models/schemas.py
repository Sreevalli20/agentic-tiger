"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class PipelineType(str, Enum):
    """Pipeline types."""
    RAG = "rag"
    GRAPHRAG = "graphrag"
    AGENTIC = "agentic"
    COMPARE_ALL = "compare_all"


class ToolType(str, Enum):
    """Agent tool types."""
    ENTITY_LINK = "entity_link"
    GRAPH_TRAVERSE = "graph_traverse"
    VECTOR_SEARCH = "vector_search"
    DOCUMENT_RETRIEVE = "document_retrieve"
    EVALUATE_EVIDENCE = "evaluate_evidence"
    AGGREGATE = "aggregate"
    VERIFY = "verify"
    STOP = "stop"


class EvidenceMetadata(BaseModel):
    """Metadata for evidence items."""
    source: str
    source_type: str  # "document", "graph", "vector"
    confidence: float = 0.0
    timestamp: Optional[datetime] = None
    authority: Optional[str] = None
    version: Optional[str] = None
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    entity_id: Optional[str] = None
    relationship_id: Optional[str] = None


class Evidence(BaseModel):
    """Evidence item supporting an answer."""
    content: str
    metadata: EvidenceMetadata
    relevance_score: float = 0.0


class Citation(BaseModel):
    """Citation linking answer claims to evidence."""
    claim: str
    evidence_ids: List[str]
    confidence: float = 0.0


class AgentStep(BaseModel):
    """Single step in agent execution trace."""
    step: int
    tool: ToolType
    input: str
    result_summary: str
    tokens: int = 0
    latency_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentTrace(BaseModel):
    """Complete agent execution trace."""
    question: str
    run_id: str
    steps: List[AgentStep] = []
    strategy_changes: List[str] = []
    evidence_count: int = 0
    citation_count: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    stopping_reason: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GraphContext(BaseModel):
    """Graph context for GraphRAG and Agentic pipelines."""
    entities: List[str] = []
    relationships: List[Dict[str, Any]] = []
    traversal_depth: int = 0
    nodes_visited: int = 0
    edges_traversed: int = 0


class PipelineMetrics(BaseModel):
    """Metrics for a pipeline execution."""
    retrieval_time_ms: float = 0.0
    generation_time_ms: float = 0.0
    total_latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    retrieval_steps: int = 0
    chunks_retrieved: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    tools_used: List[str] = []
    iterations: int = 0
    strategy_changes: int = 0


class PipelineResult(BaseModel):
    """Result from a pipeline execution."""
    pipeline: PipelineType
    question: str
    answer: str
    confidence: float = 0.0
    evidence: List[Evidence] = []
    citations: List[Citation] = []
    graph_context: Optional[GraphContext] = None
    agent_trace: Optional[AgentTrace] = None
    metrics: PipelineMetrics
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CompareRequest(BaseModel):
    """Request to compare pipelines."""
    question: str
    pipelines: List[PipelineType] = [PipelineType.RAG, PipelineType.GRAPHRAG, PipelineType.AGENTIC]


class CompareResponse(BaseModel):
    """Response from pipeline comparison."""
    question: str
    results: Dict[PipelineType, PipelineResult]
    comparison: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InvestigateRequest(BaseModel):
    """Request to investigate a question."""
    question: str
    pipeline: PipelineType = PipelineType.AGENTIC


class InvestigateResponse(BaseModel):
    """Response from investigation."""
    result: PipelineResult
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BenchmarkQuestion(BaseModel):
    """Question for benchmarking."""
    question_id: str
    question: str
    expected_answer: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None


class BenchmarkResult(BaseModel):
    """Result from benchmark execution."""
    run_id: str
    question_id: str
    question: str
    pipeline: PipelineType
    result: PipelineResult
    evaluation: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BenchmarkRun(BaseModel):
    """Complete benchmark run."""
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_questions: int = 0
    completed_questions: int = 0
    results: List[BenchmarkResult] = []
    status: str = "in_progress"
    configuration: Dict[str, Any] = {}


class MetricsSummary(BaseModel):
    """Summary metrics for dashboard."""
    accuracy: Dict[str, float] = {}
    completeness: Dict[str, float] = {}
    token_efficiency: Dict[str, float] = {}
    retrieval: Dict[str, float] = {}
    agentic_behavior: Dict[str, float] = {}
    performance: Dict[str, float] = {}
    classification: Dict[str, int] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    tigergraph_connected: bool = False
    vector_db_connected: bool = False
    llm_configured: bool = False
    vector_db_stats: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
