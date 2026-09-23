#!/usr/bin/env python3
"""Ingest demo-sized subset of corpus for production demo."""
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.retrieval.vector_retriever import VectorRetriever

def main():
    """Ingest demo-sized subset."""
    print("Starting demo corpus ingestion...")
    
    # Initialize vector retriever
    vr = VectorRetriever()
    vr._ensure_initialized()
    
    # Clear existing collection to start fresh
    if vr.collection.count() > 0:
        print(f"Clearing existing {vr.collection.count()} documents...")
        vr.client.delete_collection('documents')
        vr.collection = vr.client.get_or_create_collection(
            name='documents',
            metadata={'hnsw:space': 'cosine'}
        )
        print("Collection cleared")
    
    # Load demo-sized subset (first 150 documents)
    corpus_path = Path(__file__).parent.parent / 'hackathon-resources' / 'corpus' / 'corpus.jsonl'
    print(f"Loading corpus from {corpus_path}")
    
    if not corpus_path.exists():
        print(f"ERROR: Corpus file not found: {corpus_path}")
        return False
    
    documents = []
    metadatas = []
    ids = []
    doc_count = 0
    max_docs = 450  # Include documents needed for eval questions (up to line 423)
    
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if doc_count >= max_docs:
                break
            try:
                doc = json.loads(line.strip())
                doc_id = doc.get('doc_id', f'doc_{line_num}')
                text = doc.get('text', '')
                
                # Chunk the document
                chunks = vr._chunk_text(text, chunk_size=500, overlap=50)
                
                for chunk_idx, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        'doc_id': doc_id,
                        'title': doc.get('title', ''),
                        'url': doc.get('url', ''),
                        'chunk_index': chunk_idx,
                        'total_chunks': len(chunks)
                    })
                    ids.append(f'{doc_id}_chunk_{chunk_idx}')
                doc_count += 1
                if doc_count % 50 == 0:
                    print(f"Processed {doc_count} documents...")
            except json.JSONDecodeError as e:
                print(f"Failed to parse line {line_num}: {e}")
    
    print(f"Total chunks to index: {len(documents)}")
    print(f"From {doc_count} documents")
    
    # Generate embeddings
    print("Generating embeddings...")
    vr._ensure_embedding_model()
    embeddings = vr.embedding_model.encode(documents, show_progress_bar=True)
    # Convert numpy array to list if needed
    if hasattr(embeddings, 'tolist'):
        embeddings = embeddings.tolist()
    
    # Add to collection in batches
    print("Adding to vector database...")
    batch_size = 5000  # ChromaDB max batch size is around 5461
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        print(f"Adding batch {i//batch_size + 1} ({i} to {batch_end})...")
        vr.collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end],
            embeddings=embeddings[i:batch_end]
        )
    
    print(f"Successfully indexed {len(documents)} chunks from {doc_count} documents")
    print(f"Collection count: {vr.collection.count()}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
