#!/usr/bin/env python3
"""Initialize production corpus for deployment."""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.retrieval.vector_retriever import VectorRetriever
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize production corpus."""
    logger.info("Initializing production corpus...")
    
    retriever = VectorRetriever()
    retriever._ensure_initialized()
    retriever._ensure_embedding_model()
    
    stats = retriever.get_collection_stats()
    logger.info(f"Current vector DB stats: {stats}")
    
    if stats.get('document_count', 0) == 0:
        logger.info("Vector DB is empty, initializing corpus...")
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        final_stats = retriever.get_collection_stats()
        logger.info(f"Initialization: {success}, Final stats: {final_stats}")
    else:
        logger.info(f"Vector DB already has {stats.get('document_count', 0)} chunks")

if __name__ == "__main__":
    main()
