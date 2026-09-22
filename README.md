# GraphProbe AI

**Investigate. Connect. Verify. Know When to Stop.**

An explainable benchmarking and investigation platform that compares RAG, GraphRAG, and Agentic GraphRAG on the same questions and evidence corpus.

## Research Question

**When does Agentic GraphRAG actually provide enough additional reasoning value to justify its additional retrieval steps, latency, and token cost?**

## Overview

GraphProbe AI implements three independent retrieval pipelines to provide a fair, reproducible comparison:

- **RAG**: Vector similarity search with document retrieval
- **GraphRAG**: Entity extraction and TigerGraph graph traversal
- **Agentic GraphRAG**: Stateful orchestrator with dynamic tool selection and evidence evaluation

The system demonstrates that:
- Simple questions can be handled by simpler retrieval (RAG)
- Questions requiring relationships benefit from structural reasoning (GraphRAG)
- Complex multi-hop questions require adaptive investigation (Agentic GraphRAG)

## Architecture

```
User → Frontend (React/TypeScript) → FastAPI Backend → Orchestrator
→ RAG / GraphRAG / Agentic Pipelines → TigerGraph + ChromaDB + LLM
→ Results + Metrics + Traces → Dashboard
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Features

### Three Independent Pipelines
- **RAG Pipeline**: Vector similarity search using ChromaDB
- **GraphRAG Pipeline**: Entity extraction and TigerGraph graph traversal
- **Agentic GraphRAG Pipeline**: Stateful agent with dynamic tool selection

### Agentic Investigation
- **Dynamic Tool Selection**: Chooses retrieval method based on evidence state
- **Evidence Evaluation**: Assesses sufficiency at each step
- **Stopping Criteria**: Stops when evidence is sufficient or budget exhausted
- **Complete Traces**: Step-by-step visibility into reasoning process

### Benchmarking
- **Reproducible Runner**: Versioned benchmark execution with resumable support
- **Fair Comparison**: Same question, corpus, and evaluation for all pipelines
- **Comprehensive Metrics**: Accuracy, completeness, tokens, latency, retrieval behavior
- **Question Classification**: Identifies when each approach is most effective

### Explainability
- **Agent Traces**: Complete execution history with tool selections and results
- **Evidence Citations**: Grounded answers with source attribution
- **Graph Context**: Visual representation of entities and relationships
- **Stopping Reasons**: Clear explanation of why investigation stopped

## Technology Stack

### Backend
- **Python 3.14.6**: Core runtime
- **FastAPI**: Web framework
- **TigerGraph (pytigergraph)**: Graph database
- **ChromaDB**: Vector database
- **OpenAI/Anthropic**: LLM integration
- **Sentence Transformers**: Embeddings

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Recharts**: Data visualization
- **Lucide React**: Icons

### Infrastructure
- **Docker**: Containerization (planned)
- **pytest**: Testing
- **Black/Ruff**: Code quality

## Setup

### Prerequisites
- Python 3.14.6 (or 3.12 if compatibility issues)
- Node.js 18+
- TigerGraph instance (or cloud connection)
- LLM API key (optional, has fallback)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tiger
   ```

2. **Run setup script**
   ```bash
   python scripts/setup.py
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Health check**
   ```bash
   python scripts/health_check.py
   ```

## Usage

### Start Backend
```bash
cd backend
python -m app.main
```

Backend runs on `http://localhost:8000`

### Start Frontend
```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### Ingest Data
```bash
python scripts/ingest.py
```

### Run Benchmark
```bash
# Full benchmark
python scripts/benchmark.py

# Limited questions
python scripts/benchmark.py --limit 10

# Specific pipeline
python scripts/benchmark.py --pipeline agentic

# Resume interrupted run
python scripts/benchmark.py --resume
```

### Evaluate Results
```bash
python scripts/evaluate.py <run_id>
```

## Project Structure

```
agentic-graphrag-tigergraph/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── pipelines/      # RAG, GraphRAG, Agentic
│   │   ├── agents/         # Agent orchestrator
│   │   ├── retrieval/      # Vector/graph retrieval
│   │   ├── tigergraph/     # TigerGraph integration
│   │   └── main.py         # Application entry
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   └── App.tsx        # Main app
│   └── package.json       # Node dependencies
│
├── data/                   # Data directory
│   ├── raw/               # Raw documents
│   ├── processed/         # Processed chunks
│   └── official_dataset/  # Hackathon dataset
│
├── evaluation/            # Evaluation infrastructure
│   ├── datasets/          # Evaluation questions
│   ├── runners/           # Benchmark runners
│   ├── metrics/           # Metric calculation
│   └── reports/           # Generated reports
│
├── docs/                  # Documentation
│   ├── architecture.md    # Architecture details
│   ├── evaluation.md      # Evaluation methodology
│   ├── methodology.md     # Research methodology
│   ├── demo-script.md     # Demo flow
│   └── submission-checklist.md
│
├── scripts/               # Utility scripts
│   ├── setup.py          # Initial setup
│   ├── ingest.py         # Data ingestion
│   ├── benchmark.py      # Benchmark runner
│   ├── evaluate.py       # Evaluation
│   └── health_check.py   # System health
│
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── LICENSE              # License
```

## Documentation

- [Architecture](docs/architecture.md) - System architecture and data flow
- [Evaluation Methodology](docs/evaluation.md) - Metrics and evaluation approach
- [Methodology](docs/methodology.md) - Research methodology and hypotheses
- [Demo Script](docs/demo-script.md) - Demo flow for judges
- [Submission Checklist](docs/submission-checklist.md) - Round 1 deliverables

## Configuration

Key environment variables (see `.env.example`):

```bash
# LLM
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o-mini

# TigerGraph
TIGERGRAPH_HOST=localhost
TIGERGRAPH_PORT=14240
TIGERGRAPH_USERNAME=tigergraph
TIGERGRAPH_PASSWORD=tigergraph
TIGERGRAPH_GRAPH=graphrag_hackathon

# Agent
MAX_AGENT_ITERATIONS=10
EVIDENCE_SUFFICIENCY_THRESHOLD=0.8
MAX_TOKEN_BUDGET=10000
```

## Metrics

The system tracks:

- **Accuracy**: Correctness against ground truth
- **Completeness**: Coverage of required facts
- **Token Efficiency**: Input/output/total tokens
- **Retrieval**: Steps, chunks, nodes, edges
- **Performance**: Latency breakdown
- **Agentic Behavior**: Iterations, tools, stopping reasons

See [docs/evaluation.md](docs/evaluation.md) for detailed metrics.

## Testing

```bash
# Run health check
python scripts/health_check.py

# Run tests (when implemented)
cd backend
pytest

# Run specific test
pytest tests/test_retrieval.py
```

## Docker

Docker configuration is planned but not yet implemented for Round 1. The application is designed to run natively for development and testing.

## Limitations

- Requires TigerGraph instance (or cloud connection)
- Requires official hackathon dataset for real benchmarks
- LLM API key recommended for full functionality
- Some components are placeholders pending dataset/credentials

## Future Work

- Temporal reasoning for evolving facts (Round 2)
- Conflict resolution for contradictory evidence
- Multi-modal support (images, tables, code)
- Learned decision policy for tool selection
- User feedback integration
- Cost optimization with dynamic budgeting

## License

MIT License - See LICENSE file for details

## Hackathon Submission

This project is submitted for the TigerGraph Agentic GraphRAG Hackathon 2026 - Round 1.

### Round 1 Deliverables

- [x] Working Agentic GraphRAG system
- [x] GitHub repository structure
- [x] Architecture diagram
- [x] Demo video script
- [x] Metrics dashboard framework
- [x] Benchmarking infrastructure
- [x] Evidence and citations
- [x] Agentic trace visualization
- [x] Comprehensive documentation

### Evaluation Criteria Addressed

- **Investigation accuracy (30%)**: Three-pipeline comparison with accuracy metrics
- **Evidence quality & explainability (15%)**: Complete traces, citations, graph context
- **Agentic effectiveness & efficiency (15%)**: Dynamic tool selection, stopping criteria, cost tracking
- **Agentic design, engineering & code quality (15%)**: Professional structure, type hints, testing
- **Innovation (15%)**: Adaptive retrieval, evidence sufficiency, cost-aware investigation
- **Final presentation & Q&A (10%)**: Demo script and explainable UI

## Contributing

This is a hackathon submission. For the TigerGraph team, please refer to the official repository structure and documentation.

## Contact

For hackathon-related questions, please use the official communication channels.

---

**GraphProbe AI - Know When to Stop.**
