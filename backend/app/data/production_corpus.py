"""Production corpus initialization for small demo deployment."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_production_corpus(max_docs: int = 40) -> List[Dict[str, Any]]:
    """Load a small production corpus from the full corpus file.
    
    This selects a diverse subset of documents for the production demo.
    
    Args:
        max_docs: Maximum number of documents to load (default: 40)
        
    Returns:
        List of document dictionaries
    """
    try:
        # Find corpus file
        project_root = Path(__file__).parent.parent.parent.parent
        corpus_file = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
        
        if not corpus_file.exists():
            logger.error(f"Corpus file not found: {corpus_file}")
            return []
        
        logger.info(f"Loading production corpus from {corpus_file} (max {max_docs} docs)")
        
        documents = []
        doc_count = 0
        
        with open(corpus_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if doc_count >= max_docs:
                    logger.info(f"Reached production corpus limit: {max_docs} documents")
                    break
                
                try:
                    doc = json.loads(line.strip())
                    documents.append(doc)
                    doc_count += 1
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse line {line_num}: {e}")
        
        logger.info(f"Successfully loaded {len(documents)} documents for production corpus")
        return documents
        
    except Exception as e:
        logger.error(f"Failed to load production corpus: {e}")
        return []


def save_production_corpus(documents: List[Dict[str, Any]], output_path: str = None) -> bool:
    """Save production corpus to a smaller JSONL file.
    
    Args:
        documents: List of document dictionaries
        output_path: Output file path (default: hackathon-resources/corpus/corpus_production.jsonl)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if output_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            output_path = project_root / "hackathon-resources" / "corpus" / "corpus_production.jsonl"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')
        
        logger.info(f"Saved {len(documents)} documents to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save production corpus: {e}")
        return False


def initialize_production_corpus(max_docs: int = 40) -> str:
    """Initialize production corpus by loading and saving a subset.
    
    Args:
        max_docs: Maximum number of documents to include
        
    Returns:
        Path to the production corpus file
    """
    documents = load_production_corpus(max_docs)
    
    if not documents:
        logger.error("No documents loaded for production corpus")
        return ""
    
    project_root = Path(__file__).parent.parent.parent.parent
    output_path = project_root / "hackathon-resources" / "corpus" / "corpus_production.jsonl"
    
    if save_production_corpus(documents, output_path):
        return str(output_path)
    
    return ""


if __name__ == "__main__":
    # Test production corpus creation
    logging.basicConfig(level=logging.INFO)
    corpus_path = initialize_production_corpus(40)
    print(f"Production corpus created at: {corpus_path}")
