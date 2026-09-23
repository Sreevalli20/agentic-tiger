# Architecture

## System Overview

GraphProbe AI is a multi-pipeline investigation platform that compares RAG, GraphRAG, and Agentic GraphRAG approaches on the same corpus and questions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Investigate│  │ Compare  │  │ Metrics  │  │  Trace   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                               │
                        ┌──────▼──────┐
                        │   FastAPI   │
                        │   Backend   │
                        └──────┬──────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
         │  Orchestrator│ │Benchmark│ │   API      │
         └──────┬──────┘ └────┬────┘ └──────┬──────┘
                │              │              │
         ┌──────┴──────────────┴──────────────┐
         │                                      │
    ┌────▼────┐  ┌─────────┐  ┌────────────┐  │
    │   RAG   │  │GraphRAG │  │  Agentic   │  │
    └────┬────┘  └────┬────┘  └─────┬──────┘  │
         │            │              │         │
         └────────────┴──────────────┘         │
                       │                        │
            ┌──────────┴──────────┐            │
            │                     │            │
      ┌─────▼─────┐        ┌─────▼─────┐      │
      │ Vector DB │        │TigerGraph │      │
      │ (ChromaDB)│        │  Graph    │      │
      └───────────┘        └───────────┘      │
                                          │
                                    ┌─────▼─────┐
                                    │    LLM    │
                                    │ (Google   │
                                    │  Gemini)  │
                                    └───────────┘
```

## Components

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom glassmorphism theme
- **Routing**: React Router
- **HTTP Client**: Axios via custom API service
- **Charts**: Recharts for metrics visualization

### Backend
- **Framework**: FastAPI with Python 3.12
- **Server**: Gunicorn (production) / Uvicorn (development)
- **API**: RESTful endpoints with OpenAPI documentation

### Data Layer

#### Vector Database (ChromaDB)
- **Purpose**: Semantic document retrieval
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Storage**: Persistent local storage
- **Indexing**: HNSW with cosine similarity

#### Graph Database (TigerGraph)
- **Purpose**: Multi-hop reasoning and relationship traversal
- **Schema**: 7 vertex types, 8 edge types
- **Connection**: pyTigerGraph client
- **Querying**: GSQL for graph traversal

### Pipelines

#### RAG Pipeline
1. **Vector Retrieval**: Semantic search over document chunks
2. **Answer Generation**: LLM synthesis with retrieved context
3. **Citation**: Source attribution to documents

#### GraphRAG Pipeline
1. **Entity Extraction**: Identify entities from question
2. **Graph Traversal**: Navigate relationships in TigerGraph
3. **Enhanced Retrieval**: Combine graph context with vector search
4. **Answer Generation**: LLM synthesis with graph-augmented context

#### Agentic GraphRAG Pipeline
1. **State Management**: Track evidence, confidence, and investigation state
2. **Dynamic Tool Selection**: Choose tools based on current state
3. **Iterative Investigation**: Retrieve, evaluate, and verify evidence
4. **Stopping Criteria**: Stop when evidence is sufficient or budget exhausted
5. **Trace Generation**: Complete execution history

### Benchmark System
- **Dataset**: 100 public evaluation questions with gold answers
- **Pipelines**: All three pipelines tested on same questions
- **Evaluation**: Accuracy, completeness, latency, token usage
- **Persistence**: JSON storage with run metadata
- **Metrics**: Per-pipeline and per-question-type analysis

## Data Flow

### Investigation Flow
```
User Question
    ↓
Frontend (Investigate Page)
    ↓
POST /api/investigate
    ↓
Orchestrator.run_pipeline()
    ↓
Pipeline.run() (RAG/GraphRAG/Agentic)
    ↓
Retrieval (Vector/Graph/Agent)
    ↓
Evidence Collection
    ↓
LLM Generation
    ↓
Answer + Citations + Metrics
    ↓
Frontend Display
```

### Benchmark Flow
```
Load Evaluation Questions
    ↓
For Each Question:
    For Each Pipeline:
        Run Pipeline
        Evaluate Answer
        Record Metrics
    ↓
Aggregate Results
    ↓
Save to JSON
    ↓
Dashboard Display
```

### Ingestion Flow
```
hackathon-resources/corpus.jsonl
    ↓
Dataset Parser
    ↓
Event Extraction
    ↓
Entity Extraction (Athletes, Nations, Venues)
    ↓
TigerGraph Schema Creation
    ↓
Vertex Loading
    ↓
Edge Loading
    ↓
Validation
    ↓
Vector Database Indexing
```

## Technology Stack

### Backend
- **Language**: Python 3.12
- **Web Framework**: FastAPI
- **Graph Database**: TigerGraph (pyTigerGraph)
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers
- **LLM**: Google Gemini (with OpenAI/Anthropic support)
- **Data Processing**: Pandas, NumPy
- **Evaluation**: RapidFuzz, NLTK

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP**: Axios

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (frontend)
- **Application Server**: Gunicorn (backend)

## Security

### Environment Variables
- All secrets stored in `.env` (not committed)
- `.env.example` provides template
- Docker Compose mounts `.env` from host

### Data Protection
- Hidden evaluation questions never exposed
- Benchmark results stored locally
- No secrets in logs or error messages
- CORS configured for trusted origins

### API Security
- Health endpoint for monitoring
- Input validation via Pydantic
- Error handling without information leakage

## Performance Considerations

### Vector Retrieval
- Document chunking: 500 characters with 50 overlap
- Top-K retrieval: 5 chunks (configurable)
- Embedding caching: ChromaDB persistence

### Graph Traversal
- Max hops: 2 (configurable)
- Vertex deduplication: Primary key indexing
- Edge traversal: Directional for performance

### Agentic Investigation
- Max iterations: 10 (configurable)
- Token budget: 10,000 (configurable)
- Evidence threshold: 0.8 (configurable)

### Scalability
- Vector DB: Handles 2,951 documents easily
- Graph DB: < 10K vertices, < 20K edges
- Benchmark: Async execution with background tasks
- Frontend: Static files served by Nginx

## Deployment

### Development
```bash
# Backend
cd backend
python -m app.main

# Frontend
cd frontend
npm run dev
```

### Production (Docker)
```bash
docker-compose up -d
```

### Cloud Deployment
- **Frontend**: Vercel (static build)
- **Backend**: Render (Docker container)
- **TigerGraph**: TigerGraph Cloud or self-hosted

## Monitoring

### Health Checks
- `/api/health`: Service status and connections
- Docker health checks for containers
- Uptime monitoring via restart policy

### Logging
- Python logging to stdout/stderr
- Structured logging with levels
- Error tracking with context

### Metrics
- Pipeline execution metrics
- Benchmark aggregation
- Per-question-type analysis
- Dashboard visualization

## Extension Points

### Adding New Pipelines
1. Create pipeline class inheriting from `BasePipeline`
2. Implement `run()` method
3. Add to `PipelineType` enum
4. Register in orchestrator

### Adding New Tools
1. Add to `ToolType` enum
2. Implement in `AgentOrchestrator`
3. Add action execution method
4. Update decision logic

### Adding New Evaluation Metrics
1. Extend evaluation function in `BenchmarkRunner`
2. Add to metrics calculation
3. Update dashboard display

## Known Limitations

1. **TigerGraph Dependency**: Requires TigerGraph instance for graph features
2. **LLM Rate Limits**: Free tier may have rate limits
3. **Vector DB Performance**: Local ChromaDB not optimized for production scale
4. **Corpus Scope**: Limited to Olympic events dataset
5. **Single Language**: English only (corpus language)

## Future Enhancements

1. **Temporal Reasoning**: Time-based entity relationships
2. **Multi-modal**: Image and table support
3. **Learned Policies**: ML-based tool selection
4. **Distributed Processing**: Parallel benchmark execution
5. **Real-time Updates**: Streaming investigation results
6. **Advanced Visualization**: Interactive graph exploration
