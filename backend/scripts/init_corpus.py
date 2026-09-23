#!/usr/bin/env python3
"""Pre-initialize corpus for production deployment."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieval.vector_retriever import VectorRetriever
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize production corpus."""
    logger.info("Starting corpus initialization...")
    
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        stats = retriever.get_collection_stats()
        logger.info(f"Current vector DB stats: {stats}")
        
        if stats.get('document_count', 0) > 0:
            logger.info(f"Vector DB already has {stats['document_count']} chunks, skipping initialization")
            return True
        
        logger.info("Vector DB empty, initializing with fallback corpus")
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        
        if success:
            final_stats = retriever.get_collection_stats()
            logger.info(f"Corpus initialization successful: {final_stats}")
            return True
        else:
            logger.error("Corpus initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Corpus initialization error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)