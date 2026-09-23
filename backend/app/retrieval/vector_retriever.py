"""Vector retrieval service using ChromaDB with real corpus."""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Vector retrieval service using ChromaDB with real corpus data."""
    
    def __init__(self, corpus_path: Optional[str] = None):
        """Initialize vector retriever.
        
        Args:
            corpus_path: Path to corpus.jsonl file
        """
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.embedding_type = None
        self.corpus_path = corpus_path
        self._initialized = False
        # Lazy initialization - don't load at startup
    
    def _ensure_initialized(self):
        """Ensure ChromaDB client and embedding model are initialized (lazy load)."""
        if self._initialized:
            return  # Already initialized
        
        try:
            # Initialize ChromaDB - use absolute path from backend directory
            from pathlib import Path
            db_path = Path(__file__).parent.parent.parent / "data" / "vector_db"
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            self._initialized = True
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
            self._initialized = False
    
    def _ensure_embedding_model(self):
        """Ensure embedding model is loaded (lazy load)."""
        if self.embedding_model is not None:
            return  # Already loaded
        
        try:
            # Try sentence-transformers first (CPU-only, no API key required)
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_type = 'sentence_transformers'
                logger.info("SentenceTransformer embedding model initialized successfully")
                return
            except ImportError:
                logger.warning("sentence-transformers not available, trying OpenAI embeddings")
            
            # Fallback to OpenAI embeddings API
            from app.core.config import settings
            api_key = settings.google_api_key if settings.google_api_key else settings.llm_api_key
            
            if not api_key:
                logger.warning("No API key configured for embeddings")
                self.embedding_model = None
                self.embedding_type = None
                return
            
            self.embedding_model = OpenAI(api_key=api_key)
            self.embedding_type = 'openai'
            logger.info("OpenAI embedding client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding client: {e}")
            self.embedding_model = None
            self.embedding_type = None
    
    def load_corpus(self, corpus_path: str, max_docs: int = None) -> bool:
        """Load and index the corpus into ChromaDB.
        
        Args:
            corpus_path: Path to corpus.jsonl file
            max_docs: Maximum number of documents to load (None for all)
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_initialized()
        self._ensure_embedding_model()
        
        if not self.embedding_model:
            logger.error("Embedding model not available")
            return False
        
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
            
            documents = []
            metadatas = []
            ids = []
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
                            documents.append(chunk)
                            metadatas.append({
                                'doc_id': doc_id,
                                'title': doc.get('title', ''),
                                'url': doc.get('url', ''),
                                'chunk_index': chunk_idx,
                                'total_chunks': len(chunks)
                            })
                            ids.append(f"{doc_id}_chunk_{chunk_idx}")
                        doc_count += 1
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse line {line_num}: {e}")
            
            logger.info(f"Processing {len(documents)} chunks from {doc_count} documents for embedding...")
            
            # Generate embeddings based on model type
            embeddings = []
            if self.embedding_type == 'sentence_transformers':
                # Use sentence-transformers (CPU-only, batch processing)
                logger.info("Using sentence-transformers for embeddings")
                embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
                # Convert numpy array to list if needed
                if hasattr(embeddings, 'tolist'):
                    embeddings = embeddings.tolist()
            elif self.embedding_type == 'openai':
                # Use OpenAI API
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i+batch_size]
                    try:
                        response = self.embedding_model.embeddings.create(
                            model="text-embedding-3-small",
                            input=batch
                        )
                        batch_embeddings = [item.embedding for item in response.data]
                        embeddings.extend(batch_embeddings)
                        logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
                    except Exception as e:
                        logger.error(f"Failed to generate embeddings for batch {i//batch_size + 1}: {e}")
                        raise
            else:
                logger.error("No embedding model available")
                return False
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Successfully indexed {len(documents)} chunks from {doc_count} documents")
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
        """Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of retrieved chunks with metadata
        """
        self._ensure_initialized()
        self._ensure_embedding_model()
        
        if not self.collection:
            logger.warning("Vector collection not available, returning empty results")
            return []
        
        if not self.embedding_model:
            logger.warning("Embedding model not available, returning empty results")
            return []
        
        try:
            # Generate query embedding based on model type
            if self.embedding_type == 'sentence_transformers':
                query_embedding = self.embedding_model.encode([query])
                # sentence-transformers returns numpy array, convert to list
                if hasattr(query_embedding, 'tolist'):
                    query_embedding = query_embedding.tolist()
                # Ensure it's a list of lists (ChromaDB format)
                if not isinstance(query_embedding, list):
                    query_embedding = [query_embedding]
            elif self.embedding_type == 'openai':
                response = self.embedding_model.embeddings.create(
                    model="text-embedding-3-small",
                    input=[query]
                )
                query_embedding = [item.embedding for item in response.data]
            else:
                logger.warning("No embedding model available")
                return []
            
            # Search collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'document_id': results['metadatas'][0][i].get('doc_id', 'unknown'),
                        'chunk_id': results['ids'][0][i],
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i]
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} chunks for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection.
        
        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            return {'status': 'not_initialized'}
        
        try:
            count = self.collection.count()
            model_name = 'none'
            if self.embedding_type == 'sentence_transformers':
                model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            elif self.embedding_type == 'openai':
                model_name = 'openai/text-embedding-3-small'
            
            return {
                'status': 'initialized',
                'document_count': count,
                'embedding_model': model_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def initialize_production_corpus(self, max_docs: int = 40) -> bool:
        """Initialize production corpus if vector database is empty.
        
        This loads a small subset of documents for production demo.
        
        Args:
            max_docs: Maximum number of documents to load
            
        Returns:
            True if initialization was needed and successful, False otherwise
        """
        try:
            self._ensure_initialized()
            stats = self.get_collection_stats()
            
            # Only initialize if completely empty
            if stats.get('document_count', 0) > 0:
                logger.info(f"Vector DB already has {stats['document_count']} chunks - skipping initialization")
                return False
            
            logger.info("Vector DB is empty - initializing production corpus")
            
            # Determine corpus path
            from app.core.config import settings
            corpus_path = settings.production_corpus_path
            
            # Try relative path first (from backend directory)
            corpus_file = Path(corpus_path)
            if not corpus_file.exists():
                # Try absolute path from backend directory
                backend_dir = Path(__file__).parent.parent.parent
                corpus_file = backend_dir / "corpus_production.jsonl"
            
            if not corpus_file.exists():
                # Try absolute path from project root
                project_root = Path(__file__).parent.parent.parent.parent
                corpus_file = project_root / "hackathon-resources" / "corpus" / "corpus_production.jsonl"
            
            if not corpus_file.exists():
                logger.error(f"Production corpus file not found: {corpus_file}")
                return False
            
            # Load the production corpus
            success = self.load_corpus(str(corpus_file), max_docs=max_docs)
            
            if success:
                final_stats = self.get_collection_stats()
                logger.info(f"Production corpus initialized with {final_stats.get('document_count', 0)} chunks")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize production corpus: {e}")
            return False
