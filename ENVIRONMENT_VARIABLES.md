# Environment Variables Documentation

## Backend Environment Variables

### LLM Configuration
- `LLM_PROVIDER`: LLM provider to use (google, openai, anthropic) - Default: google
- `LLM_API_KEY`: API key for LLM provider (fallback if GOOGLE_API_KEY not set)
- `GOOGLE_API_KEY`: Google Gemini API key (preferred for Google provider)
- `LLM_MODEL`: Model name to use - Default: gemini-1.5-flash
- `LLM_BASE_URL`: Base URL for LLM API - Default: https://api.openai.com/v1

### TigerGraph Configuration
- `TG_HOST`: TigerGraph host address (include protocol http:// or https://)
- `TG_PORT`: TigerGraph REST++ port - Default: 14240
- `TG_SECRET`: TigerGraph secret key for authentication
- `TG_GRAPHNAME`: TigerGraph graph name - Default: Transaction_Fraud

### Vector Database Configuration
- `VECTOR_DB_PATH`: Path to ChromaDB vector database - Default: ./data/vector_db
- `EMBEDDING_MODEL`: Embedding model to use - Default: openai/text-embedding-3-small

### Storage Configuration
- `STORAGE_DB_PATH`: Path to SQLite storage database - Default: ./data/graphprobe.db

### Application Configuration
- `APP_HOST`: Application host - Default: 0.0.0.0
- `APP_PORT`: Application port - Default: 8000
- `PORT`: Server port (overrides APP_PORT in production) - Set by Render
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins

### Data Configuration
- `DATA_PATH`: Path to data directory - Default: ./data
- `CHUNK_SIZE`: Text chunk size for processing - Default: 500
- `CHUNK_OVERLAP`: Text chunk overlap - Default: 50
- `TOP_K_RETRIEVAL`: Number of top results to retrieve - Default: 5

### Agent Configuration
- `MAX_AGENT_ITERATIONS`: Maximum agent iterations - Default: 10
- `EVIDENCE_SUFFICIENCY_THRESHOLD`: Evidence sufficiency threshold - Default: 0.8
- `MAX_TOKEN_BUDGET`: Maximum token budget - Default: 10000

### Benchmark Configuration
- `BENCHMARK_OUTPUT_PATH`: Path to benchmark results - Default: ./evaluation/results
- `MAX_CONCURRENT_BENCHMARKS`: Maximum concurrent benchmarks - Default: 3

## Frontend Environment Variables

### API Configuration
- `VITE_API_BASE_URL`: Backend API URL
  - Development: http://localhost:8000
  - Production: https://graphprobe-ai-backend.onrender.com

## Required Variables for Production

### Backend (Render)
- `GOOGLE_API_KEY`: Required for LLM functionality
- `TG_HOST`: Required for TigerGraph functionality
- `TG_SECRET`: Required for TigerGraph authentication
- `PORT`: Set by Render automatically

### Frontend (Vercel)
- `VITE_API_BASE_URL`: Required to point to production backend

## Security Notes

### Never Commit to Git
- `GOOGLE_API_KEY`
- `LLM_API_KEY`
- `TG_SECRET`
- Any other API keys or secrets

### Frontend Variables
- Only public configuration should be in VITE_* variables
- Never expose secrets in frontend environment variables

### Backend Variables
- Secrets should be set in Render dashboard
- Use `sync: false` for sensitive variables in render.yaml
- Secrets are injected at runtime, not committed to code

## Development Setup

### Backend (.env)
```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-1.5-flash

TG_HOST=http://localhost
TG_PORT=14240
TG_SECRET=your_tigergraph_secret_here
TG_GRAPHNAME=Transaction_Fraud

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Production Setup

### Render Environment Variables
Set these in the Render dashboard:
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `TG_HOST`: Your TigerGraph host (including protocol)
- `TG_SECRET`: Your TigerGraph secret
- `PORT`: Set automatically by Render

### Vercel Environment Variables
Set these in Vercel project settings:
- `VITE_API_BASE_URL`: https://graphprobe-ai-backend.onrender.com

## Variable Sources

### Backend Configuration
- Defined in: `backend/app/core/config.py`
- Loaded from: Environment variables or .env file
- Defaults provided in: Settings class

### Frontend Configuration
- Defined in: `frontend/src/services/api.ts`
- Loaded from: VITE_* environment variables
- Fallback logic for localhost vs production

## Storage Architecture

### Vector Database (ChromaDB)
- Location: `./data/vector_db`
- Persistence: Local filesystem (ephemeral on Render)
- Contains: Document embeddings and search index
- Note: Will be lost on Render restart/redeploy

### Storage Database (SQLite)
- Location: `./data/graphprobe.db`
- Persistence: Local filesystem (ephemeral on Render)
- Contains: Investigations, benchmark results, agent traces, file uploads
- Note: Will be lost on Render restart/redeploy

### Corpus Data
- Location: `hackathon-resources/corpus/corpus.jsonl`
- Persistence: Git repository (persistent)
- Contains: Source documents for ingestion
- Note: Lazy-loaded on first query

## Important Notes

1. **Render Filesystem**: Render Free tier has ephemeral filesystem storage. Data in `./data/` will be lost on restart/redeploy.

2. **Corpus Ingestion**: The corpus is lazy-loaded from the git repository on first query, not during startup, to maintain lightweight backend startup.

3. **Storage Strategy**: Currently uses local SQLite for persistence. For production persistence, consider:
   - Render Disk (paid tier)
   - External database (PostgreSQL, etc.)
   - Cloud storage (S3, etc.)

4. **API Keys**: Never commit API keys to git. Use environment variables and secret management.

5. **CORS**: Ensure CORS origins match your deployment domains exactly.
