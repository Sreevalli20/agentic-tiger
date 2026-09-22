# Data Directory

This directory contains the corpus and evaluation datasets for GraphProbe AI.

## Structure

- `raw/` - Raw documents (PDF, text, JSON, etc.)
- `processed/` - Processed and chunked documents
- `official_dataset/` - Official hackathon dataset (do not commit ground truth)
- `vector_db/` - ChromaDB vector database (auto-generated)

## Official Hackathon Dataset

Place the official hackathon dataset in the `official_dataset/` directory:

- `corpus/` - Document corpus
- `questions_visible.json` - 100 visible evaluation questions
- `questions_hidden.json` - 50 hidden evaluation questions (DO NOT COMMIT)

**IMPORTANT:** Never commit private/hidden evaluation answers or ground truth to the repository.

## Ingestion

Run the ingestion pipeline to process documents:

```bash
python scripts/ingest.py
```

This will:
1. Load documents from the corpus
2. Normalize and chunk documents
3. Create embeddings
4. Ingest into TigerGraph (graph entities/relationships)
5. Ingest into ChromaDB (vector representations)
6. Validate ingestion
