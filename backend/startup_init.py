"""Startup initialization script for production corpus."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.retrieval.vector_retriever import VectorRetriever
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Running startup initialization...")
    
    try:
        retriever = VectorRetriever()
        retriever._ensure_initialized()
        retriever._ensure_embedding_model()
        
        # Check current stats
        stats = retriever.get_collection_stats()
        print(f"Current vector DB stats: {stats}")
        
        # Clear existing data
        if retriever.collection:
            try:
                retriever.collection.delete()
                logger.info("Cleared existing vector collection")
            except Exception as clear_error:
                logger.warning(f"Failed to clear collection: {clear_error}")
        
        # Initialize with production corpus (use fallback if corpus file not found)
        print(f"Initializing production corpus with max_docs={settings.production_max_docs}")
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        final_stats = retriever.get_collection_stats()
        
        print(f"Initialization result: {success}")
        print(f"Final stats: {final_stats}")
        print(f"Document count: {final_stats.get('document_count', 0)}")
        
        if final_stats.get('document_count', 0) > 0:
            print("SUCCESS: Vector DB initialized with chunks")
            return 0
        else:
            print("FAILED: Vector DB is still empty")
            return 1
            
    except Exception as e:
        print(f"ERROR: Startup initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
