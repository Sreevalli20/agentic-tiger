"""Manual corpus initialization script."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.retrieval.vector_retriever import VectorRetriever

def main():
    print("Initializing production corpus...")
    
    retriever = VectorRetriever()
    retriever._ensure_initialized()
    retriever._ensure_embedding_model()
    
    # Check if already initialized
    stats = retriever.get_collection_stats()
    if stats.get('document_count', 0) > 0:
        print(f"Vector DB already has {stats['document_count']} chunks, skipping initialization")
        return True
    
    # Initialize with production corpus
    success = retriever.initialize_production_corpus(max_docs=40)
    stats = retriever.get_collection_stats()
    
    print(f"Initialization result: {success}")
    print(f"Final stats: {stats}")
    
    doc_count = stats.get('document_count', 0)
    if doc_count > 0:
        print(f"SUCCESS: Vector DB has {doc_count} chunks")
        return True
    else:
        print("FAILED: Vector DB is empty")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
