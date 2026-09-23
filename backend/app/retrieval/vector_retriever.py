"""Lightweight retrieval service using TF-IDF with real corpus."""
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Module-level shared data - all instances share this
_documents = []
_metadatas = []
_ids = []
_tfidf_vectorizer = None
_tfidf_matrix = None
_initialized = False

class VectorRetriever:
    """Lightweight retrieval service using TF-IDF with real corpus data."""
    
    def __init__(self, corpus_path: Optional[str] = None):
        """Initialize lightweight retriever.
        
        Args:
            corpus_path: Path to corpus.jsonl file
        """
        # All instances reference the same module-level data (mutable references)
        self.documents = _documents
        self.metadatas = _metadatas
        self.ids = _ids
        self.tfidf_vectorizer = _tfidf_vectorizer
        self.tfidf_matrix = _tfidf_matrix
        self._initialized = _initialized
        self.corpus_path = corpus_path
    
    def _ensure_initialized(self):
        """Ensure TF-IDF index is initialized."""
        if self._initialized:
            return  # Already initialized
        
        logger.info("TF-IDF retriever initialized successfully")
        self._initialized = True
    
    def _ensure_embedding_model(self):
        """No-op for TF-IDF - no embedding model needed."""
        pass
    
    def load_corpus(self, corpus_path: str, max_docs: int = None) -> bool:
        """Load and index the corpus using TF-IDF.
        
        Args:
            corpus_path: Path to corpus.jsonl file
            max_docs: Maximum number of documents to load (None for all)
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_initialized()
        
        try:
            logger.info(f"Loading corpus from {corpus_path}")
            corpus_file = Path(corpus_path)
            
            # If relative path doesn't work, try to find it from project root
            if not corpus_file.exists():
                project_root = Path(__file__).parent.parent.parent.parent
                alternative_path = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
                if alternative_path.exists():
                    corpus_file = alternative_path
                    logger.info(f"Using alternative corpus path: {corpus_file}")
            
            if not corpus_file.exists():
                logger.error(f"Corpus file not found: {corpus_path}")
                return False
            
            self.documents = []
            self.metadatas = []
            self.ids = []
            doc_count = 0
            
            with open(corpus_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if max_docs and doc_count >= max_docs:
                        logger.info(f"Reached max documents limit: {max_docs}")
                        break
                    try:
                        doc = json.loads(line.strip())
                        doc_id = doc.get('doc_id', f'doc_{line_num}')
                        text = doc.get('text', '')
                        
                        # Chunk the document if it's too long
                        chunks = self._chunk_text(text, chunk_size=500, overlap=50)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            self.documents.append(chunk)
                            self.metadatas.append({
                                'doc_id': doc_id,
                                'title': doc.get('title', ''),
                                'url': doc.get('url', ''),
                                'chunk_index': chunk_idx,
                                'total_chunks': len(chunks)
                            })
                            self.ids.append(f"{doc_id}_chunk_{chunk_idx}")
                        doc_count += 1
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse line {line_num}: {e}")
            
            logger.info(f"Processing {len(self.documents)} chunks from {doc_count} documents for TF-IDF indexing...")
            
            # Build TF-IDF index
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.documents)
            
            # Update module-level shared data
            global _documents, _metadatas, _ids
            global _tfidf_vectorizer, _tfidf_matrix, _initialized
            _documents.clear()
            _documents.extend(self.documents)
            _metadatas.clear()
            _metadatas.extend(self.metadatas)
            _ids.clear()
            _ids.extend(self.ids)
            _tfidf_vectorizer = self.tfidf_vectorizer
            _tfidf_matrix = self.tfidf_matrix
            _initialized = True
            
            logger.info(f"Successfully indexed {len(self.documents)} chunks from {doc_count} documents using TF-IDF")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load corpus: {e}")
            return False
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Chunk text into smaller pieces.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at word boundary
            if end < len(text) and not text[end].isspace():
                last_space = chunk.rfind(' ')
                if last_space > 0:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using TF-IDF.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of retrieved chunks with metadata
        """
        self._ensure_initialized()
        
        if not self.tfidf_vectorizer or self.tfidf_matrix is None:
            logger.warning("TF-IDF index not available, returning empty results")
            return []
        
        try:
            # Transform query using the same TF-IDF vectorizer
            query_tfidf = self.tfidf_vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_tfidf, self.tfidf_matrix).flatten()
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Format results
            formatted_results = []
            for idx in top_indices:
                formatted_results.append({
                    'content': self.documents[idx],
                    'document_id': self.metadatas[idx].get('doc_id', 'unknown'),
                    'chunk_id': self.ids[idx],
                    'score': float(similarities[idx]),
                    'metadata': self.metadatas[idx]
                })
            
            logger.info(f"Retrieved {len(formatted_results)} chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"TF-IDF search failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the TF-IDF collection.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self._initialized:
            return {'status': 'not_initialized'}
        
        try:
            return {
                'status': 'initialized',
                'document_count': len(self.documents),
                'embedding_model': 'tf-idf'
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def initialize_production_corpus(self, max_docs: int = 40) -> bool:
        """Initialize production corpus (always reloads in production mode).
        
        This loads a small subset of documents for production demo.
        In production mode, always reloads to ensure fresh data in in-memory DB.
        
        Args:
            max_docs: Maximum number of documents to load
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self._ensure_initialized()
            
            # Check if already loaded in shared data
            global _initialized
            if _initialized and len(_documents) > 0:
                logger.info(f"TF-IDF index already has {len(_documents)} chunks - using existing index")
                return True
            
            logger.info("Initializing production corpus")
            
            # Clear existing data for fresh load
            global _documents, _metadatas, _ids
            global _tfidf_vectorizer, _tfidf_matrix
            _documents.clear()
            _metadatas.clear()
            _ids.clear()
            _tfidf_vectorizer = None
            _tfidf_matrix = None
            _initialized = False
            
            # Determine corpus path - try multiple locations in order
            backend_dir = Path(__file__).parent.parent.parent
            project_root = Path(__file__).parent.parent.parent.parent
            
            # In Docker/Render, the working directory is /app (backend root)
            # Try current working directory first
            cwd = Path.cwd()
            corpus_file = cwd / "corpus_production.jsonl"
            logger.info(f"Trying corpus path (cwd): {corpus_file}, exists: {corpus_file.exists()}")
            
            if not corpus_file.exists():
                # Try backend directory (for Render deployment)
                corpus_file = backend_dir / "corpus_production.jsonl"
                logger.info(f"Trying corpus path (backend_dir): {corpus_file}, exists: {corpus_file.exists()}")
            
            if not corpus_file.exists():
                # Try hackathon-resources in backend directory
                corpus_file = backend_dir / "hackathon-resources" / "corpus" / "corpus_production.jsonl"
                logger.info(f"Trying corpus path (backend/hackathon): {corpus_file}, exists: {corpus_file.exists()}")
            
            if not corpus_file.exists():
                # Try project root (for local development)
                corpus_file = project_root / "hackathon-resources" / "corpus" / "corpus_production.jsonl"
                logger.info(f"Trying corpus path (project_root): {corpus_file}, exists: {corpus_file.exists()}")
            
            if not corpus_file.exists():
                # Fallback to full corpus if production corpus doesn't exist
                corpus_file = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
                logger.warning(f"Production corpus not found, using full corpus: {corpus_file}, exists: {corpus_file.exists()}")
            
            if not corpus_file.exists():
                logger.error(f"Corpus file not found at any location")
                return False
            
            logger.info(f"Found corpus file at: {corpus_file}")
            
            # Load the production corpus
            success = self.load_corpus(str(corpus_file), max_docs=max_docs)
            
            if success:
                final_stats = self.get_collection_stats()
                logger.info(f"Production corpus initialized with {final_stats.get('document_count', 0)} chunks")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize production corpus: {e}")
            return False
