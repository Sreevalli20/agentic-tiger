"""Standalone script to run TigerGraph ingestion locally without HTTP timeout."""
import sys
import logging
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.tigergraph.ingestion import TigerGraphIngestion
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run ingestion locally."""
    logger.info("Starting local TigerGraph ingestion...")
    
    # Check configuration
    logger.info(f"TigerGraph Host: {settings.tg_host}")
    logger.info(f"TigerGraph Port: {settings.tg_port}")
    logger.info(f"TigerGraph Graph: {settings.tg_graphname}")
    logger.info(f"TigerGraph Secret configured: {bool(settings.tg_secret)}")
    
    if not settings.tg_secret:
        logger.error("TG_SECRET not configured. Please set it in .env file")
        return False
    
    # Find corpus file
    backend_dir = Path(__file__).parent
    corpus_path = backend_dir / "corpus_production.jsonl"
    
    if not corpus_path.exists():
        corpus_path = backend_dir / "app" / "corpus_production.jsonl"
    
    if not corpus_path.exists():
        logger.error(f"Corpus file not found at {corpus_path}")
        return False
    
    logger.info(f"Using corpus: {corpus_path}")
    
    # Initialize ingestion
    ingestion = TigerGraphIngestion()
    
    if not ingestion.conn:
        logger.error("Failed to connect to TigerGraph")
        return False
    
    # Check schema first
    logger.info("Checking schema...")
    if not ingestion.create_schema():
        logger.error("Schema check failed")
        return False
    
    # Run full ingestion
    logger.info("Starting full ingestion...")
    results = ingestion.run_full_ingestion(str(corpus_path), "")
    
    logger.info("=" * 50)
    logger.info("INGESTION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Status: {results['status']}")
    logger.info(f"Duration: {results.get('duration_seconds', 0):.2f}s")
    
    if 'steps' in results:
        logger.info("\nSteps:")
        for step, result in results['steps'].items():
            logger.info(f"  {step}: {result}")
    
    if 'vertex_counts' in results:
        logger.info(f"\nVertex counts: {results['vertex_counts']}")
    
    if 'edge_counts' in results:
        logger.info(f"Edge counts: {results['edge_counts']}")
    
    if results.get('errors'):
        logger.error(f"\nErrors: {results['errors']}")
    
    return results['status'] in ['completed', 'skipped']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
