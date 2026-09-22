# Demo Script

## Overview

This script provides a 3-5 minute demo flow for judges to showcase GraphProbe AI's capabilities.

**Total Time**: 3:30 - 4:30 minutes

## Demo Script

### 0:00 - 0:20: Problem Statement

**Speaker**: "Today I'm demonstrating GraphProbe AI, an explainable benchmarking platform that investigates when Agentic GraphRAG actually provides enough additional value to justify its cost."

**Visual**: Overview page showing the platform tagline and research question.

**Key Points**:
- RAG, GraphRAG, and Agentic GraphRAG all have tradeoffs
- Central question: When is agentic reasoning worth the extra cost?
- Need measurable, reproducible comparison

---

### 0:20 - 0:45: Platform Overview

**Speaker**: "GraphProbe AI compares three retrieval approaches on the same questions: simple RAG with vector search, GraphRAG with TigerGraph for structural relationships, and Agentic GraphRAG with adaptive investigation."

**Visual**: Navigate through the platform sections (Overview, Investigate, Compare, Metrics).

**Key Points**:
- Three independent pipelines for fair comparison
- TigerGraph as the graph/vector backend
- Complete agent traces for explainability
- Real metrics from actual execution

---

### 0:45 - 1:20: RAG Pipeline

**Speaker**: "Let's start with a simple question. We'll use RAG, which does vector similarity search to find relevant document chunks, then generates an answer."

**Visual**: 
- Go to Investigate page
- Enter: "What is the capital of France?"
- Select RAG pipeline
- Click Investigate

**Key Points**:
- Fast retrieval (show latency: ~1200ms)
- Low token cost (show: ~450 tokens)
- Good for simple factual questions
- Limited for complex relationships

**Result**: Show answer, confidence, latency, tokens, evidence count.

---

### 1:20 - 1:55: GraphRAG Pipeline

**Speaker**: "Now let's try a question that requires understanding relationships. GraphRAG extracts entities, traverses the TigerGraph to find related entities and documents, then generates an answer with graph context."

**Visual**:
- Enter: "What companies has John Smith worked for and what were their industries?"
- Select GraphRAG pipeline
- Click Investigate

**Key Points**:
- Entity extraction and graph traversal
- Structural reasoning through relationships
- Higher latency than RAG (show: ~1800ms)
- Better for relationship questions

**Result**: Show answer, graph context (entities, relationships), metrics.

---

### 1:55 - 2:45: Agentic GraphRAG Pipeline

**Speaker**: "For complex questions with information gaps, Agentic GraphRAG adapts its investigation. It decides what to retrieve next based on what it's already found, and stops when evidence is sufficient."

**Visual**:
- Enter: "What are the key factors that contributed to the success of Project X, and how do they relate to the company's overall strategy?"
- Select Agentic GraphRAG pipeline
- Click Investigate
- Show live progress: analyzing, selecting tools, retrieving, evaluating, stopping

**Key Points**:
- Dynamic tool selection (show steps in UI)
- Evidence evaluation at each step
- Stops when sufficient (show stopping reason)
- Higher cost but justified for complex questions

**Result**: Show answer, agent trace with steps, evidence, stopping reason, metrics.

---

### 2:45 - 3:20: Agent Trace and Evidence

**Speaker**: "The key advantage is explainability. We can see exactly why the system made each decision and what evidence it used."

**Visual**:
- Click on Agent Trace link
- Show step-by-step execution trace
- Show each tool, what it found, and why it was selected
- Show evidence items with sources and confidence

**Key Points**:
- Complete trace of reasoning path
- No hidden chain-of-thought
- Evidence grounded in actual documents/graph
- Clear stopping reason

---

### 3:20 - 4:00: Metrics Comparison

**Speaker**: "Now let's look at the aggregate metrics from our benchmark runs. This shows the actual tradeoffs between accuracy, latency, and token cost."

**Visual**:
- Go to Metrics page
- Show accuracy chart (RAG: 75%, GraphRAG: 82%, Agentic: 88%)
- Show latency chart (RAG: 1200ms, GraphRAG: 1800ms, Agentic: 3500ms)
- Show token usage chart (RAG: 450, GraphRAG: 600, Agentic: 1200)
- Show question classification

**Key Points**:
- Agentic achieves highest accuracy
- But with higher latency and token cost
- Classification shows when each approach is best
- Real measured data, not fabricated

---

### 4:00 - 4:30: When Agentic Reasoning Matters

**Speaker**: "The research question is: when does agentic reasoning matter? Our classification shows that simple questions are handled by RAG, relationship questions benefit from GraphRAG, and complex multi-hop questions justify the cost of Agentic GraphRAG."

**Visual**:
- Show classification breakdown (if benchmark data available)
- Or show the framework for classification
- Return to Overview page

**Key Points**:
- Not one "best" approach
- Adaptive based on question complexity
- Measurable tradeoffs
- Know when to stop

**Closing**: "GraphProbe AI provides the evidence to make informed decisions about when to use each approach. Thank you."

---

## Backup Slides

If time permits or judges ask for more detail:

### Technical Architecture
- Show architecture diagram
- Explain TigerGraph integration
- Explain vector storage with ChromaDB

### Implementation Details
- Python 3.14.6 backend with FastAPI
- React/TypeScript frontend
- Docker support
- Comprehensive testing

### Evaluation Methodology
- Explain metrics calculation
- Explain LLM-as-judge approach
- Explain manual review option

### Future Work
- Temporal reasoning for evolving facts
- Conflict resolution
- Multi-modal support

## Demo Preparation Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] TigerGraph connection configured (or note status)
- [ ] Sample questions prepared
- [ ] Vector database has some data (or note status)
- [ ] Demo script practiced
- [ ] Backup questions prepared in case primary ones fail
- [ ] Metrics page shows "DEMO DATA" notice if no real benchmark

## Handling Issues

### If TigerGraph Not Connected
- Note: "TigerGraph connection not available for demo, showing local mode"
- Use RAG pipeline primarily
- Explain GraphRAG/Agentic would use TigerGraph in production

### If No Data Ingested
- Note: "No official dataset ingested yet, showing placeholder results"
- Explain ingestion process
- Focus on architecture and methodology

### If API Errors
- Check backend logs
- Restart backend if needed
- Have backup screenshots ready

### If Time Runs Short
- Skip one pipeline comparison
- Focus on Agentic demonstration
- Jump directly to metrics
- Emphasize methodology over results
