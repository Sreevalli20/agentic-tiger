# Methodology

## Research Question

**When does Agentic GraphRAG actually provide enough additional reasoning value to justify its additional retrieval steps, latency, and token cost?**

## Hypothesis

We hypothesize that:
1. Simple questions can be handled effectively by basic RAG
2. Questions requiring structural relationships benefit from GraphRAG
3. Complex multi-hop questions with evidence gaps require Agentic GraphRAG
4. The tradeoff between accuracy/complexity and cost/latency can be quantified

## Approach

### Multi-Pipeline Comparison

We implement three independent pipelines to ensure fair comparison:

#### Pipeline A: RAG
- **Purpose**: Baseline retrieval
- **Method**: Vector similarity search → LLM generation
- **Expected Use Case**: Simple factual questions with direct document matches

#### Pipeline B: GraphRAG
- **Purpose**: Structural reasoning
- **Method**: Entity extraction → Graph traversal → Document retrieval → LLM generation
- **Expected Use Case**: Questions requiring entity relationships and multi-hop connections

#### Pipeline C: Agentic GraphRAG
- **Purpose**: Adaptive investigation
- **Method**: Stateful orchestrator → Dynamic tool selection → Evidence evaluation → Stopping criteria
- **Expected Use Case**: Complex questions with information gaps requiring adaptive retrieval depth

### Adaptive Retrieval

The Agentic GraphRAG pipeline uses a decision policy to select tools:

```
State (question, evidence, confidence, gaps) → Decision Policy → Tool Selection
→ Action Execution → State Update → Stopping Check → (Continue/Stop)
```

#### Decision Policy Inputs
- Question complexity
- Identified entities
- Available graph connections
- Vector search confidence
- Evidence completeness
- Contradictions
- Previous retrieval results
- Token budget

#### Available Tools
- **ENTITY_LINK**: Extract and link entities from text
- **GRAPH_TRAVERSE**: Traverse TigerGraph from entities
- **VECTOR_SEARCH**: Perform vector similarity search
- **DOCUMENT_RETRIEVE**: Retrieve full documents
- **EVALUATE_EVIDENCE**: Assess evidence sufficiency
- **AGGREGATE**: Combine evidence from multiple sources
- **VERIFY**: Cross-check claims against evidence
- **STOP**: Halt investigation

#### Stopping Criteria
The agent stops when:
- Evidence sufficiency threshold is met (default: 0.8)
- Required entities/relationships are supported
- Answer can be grounded in evidence
- Confidence reaches configured threshold
- No meaningful information gap remains

Or when:
- Maximum iterations reached (default: 10)
- Retrieval repeatedly returns redundant evidence
- Additional investigation has diminishing value
- Token budget exceeded (default: 10,000)

### Evidence Sufficiency Score

We calculate a transparent evidence score using observable signals:

```
Evidence Sufficiency = (
    source_relevance * 0.3 +
    evidence_coverage * 0.3 +
    citation_coverage * 0.2 +
    entity_coverage * 0.1 +
    relationship_coverage * 0.1
) * (1 - contradiction_penalty)
```

Where:
- **source_relevance**: Average relevance score of retrieved evidence
- **evidence_coverage**: Percentage of answer claims supported by evidence
- **citation_coverage**: Percentage of claims with valid citations
- **entity_coverage**: Percentage of key entities found in evidence
- **relationship_coverage**: Percentage of key relationships found in graph
- **contradiction_penalty**: Penalty for conflicting evidence (0-1)

This is explicitly labeled as an estimated score, not ground-truth probability.

### Cost-Aware Investigation

We track resource usage alongside accuracy:

#### Token Cost
- Input tokens per pipeline
- Output tokens per pipeline
- Total tokens per pipeline
- Tokens per successful answer

#### Latency Cost
- Retrieval latency
- Generation latency
- Total latency
- Per-step latency (agentic)

#### Retrieval Cost
- Number of retrieval steps
- Chunks retrieved
- Graph nodes visited
- Graph edges traversed
- Tools used (agentic)

This enables analysis of the accuracy-cost tradeoff.

### Explainable Retrieval Path

Every investigation produces a complete trace:

```json
{
  "question": "...",
  "run_id": "...",
  "steps": [
    {
      "step": 1,
      "tool": "entity_linking",
      "input": "...",
      "result_summary": "...",
      "tokens": 0,
      "latency_ms": 0
    },
    ...
  ],
  "stopping_reason": "Evidence sufficiency (0.85) meets threshold (0.8)"
}
```

The UI visualizes this trace to show:
- Why each tool was selected
- What each tool found
- How evidence accumulated
- Why the system stopped

### Investigation Profiles

After execution, questions are classified based on measured behavior:

#### Simple Retrieval
- RAG achieves high accuracy
- Minimal retrieval steps
- Low latency and token cost
- **Interpretation**: Agentic not justified

#### Structural Reasoning
- GraphRAG significantly outperforms RAG
- Graph traversal provides key information
- Moderate latency increase
- **Interpretation**: Graph structure valuable

#### Multi-Hop Investigation
- Agentic significantly outperforms both
- Multiple tool types used
- Evidence gaps resolved through adaptive retrieval
- Higher cost but justified by accuracy gain
- **Interpretation**: Agentic investigation valuable

## Reproducibility

### Benchmark Execution
```bash
# Run full benchmark
python scripts/benchmark.py --questions evaluation/datasets/questions_visible.json

# Run limited benchmark
python scripts/benchmark.py --limit 10

# Run specific pipeline
python scripts/benchmark.py --pipeline agentic

# Resume interrupted benchmark
python scripts/benchmark.py --resume
```

### Versioned Results
- Each benchmark run has unique ID
- Results never overwritten without explicit instruction
- JSON/JSONL format for easy analysis
- Includes configuration metadata

### Configuration Tracking
All runs include:
- Pipeline configurations
- Model settings
- Retrieval parameters
- Agent limits (iterations, budget)
- Timestamp

## Validation

### Component Testing
- Unit tests for retrieval
- Unit tests for agent state
- Unit tests for stopping logic
- Unit tests for metrics
- Integration tests for TigerGraph
- API tests

### End-to-End Testing
- Health check script validates all components
- Sample questions test each pipeline
- Benchmark runner validates data flow

### Manual Review
- Option for manual evaluation of subset
- LLM-as-judge outputs saved for inspection
- Citation verification interface

## Limitations

1. **Dataset Bias**: Evaluation dataset may not represent all question types
2. **Ground Truth Quality**: Accuracy depends on ground truth quality
3. **Heuristic Metrics**: Some metrics (evidence sufficiency) are estimates
4. **LLM Variability**: LLM outputs may vary between runs
5. **Graph Schema**: Graph schema affects GraphRAG performance
6. **Cost Model**: Token costs are approximations

## Future Work

1. **Temporal Reasoning**: Support for evolving facts (Round 2)
2. **Conflict Resolution**: Explicit handling of conflicting evidence
3. **Learned Decision Policy**: ML-based tool selection
4. **Multi-Modal**: Support for images, tables, code
5. **User Feedback**: Interactive investigation refinement
6. **Cost Optimization**: Dynamic budget allocation
