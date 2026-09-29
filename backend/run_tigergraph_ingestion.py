"""Execute TigerGraph schema creation and ingestion pipeline."""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from app.tigergraph.ingestion import TigerGraphIngestion
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Execute TigerGraph ingestion."""
    print("=" * 60)
    print("TigerGraph Ingestion Pipeline")
    print("=" * 60)
    print(f"TG_HOST: {settings.tg_host}")
    print(f"TG_PORT: {settings.tg_port}")
    print(f"TG_GRAPHNAME: {settings.tg_graphname}")
    print(f"TG_SECRET configured: {bool(settings.tg_secret)}")
    print()
    
    if not settings.tg_secret:
        print("ERROR: TG_SECRET not configured in .env")
        print("Please set TG_SECRET in the .env file to connect to TigerGraph")
        return False
    
    # Paths to hackathon resources
    project_root = Path(__file__).parent.parent
    corpus_path = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
    questions_path = project_root / "hackathon-resources" / "questions"
    
    print(f"Corpus path: {corpus_path}")
    print(f"Corpus exists: {corpus_path.exists()}")
    print(f"Questions path: {questions_path}")
    print(f"Questions exists: {questions_path.exists()}")
    print()
    
    if not corpus_path.exists():
        print("ERROR: Corpus file not found")
        return False
    
    # Initialize ingestion pipeline
    print("Initializing TigerGraph ingestion pipeline...")
    ingestion = TigerGraphIngestion()
    
    # Check connection
    if not ingestion.conn:
        print("ERROR: Failed to connect to TigerGraph")
        print("Check TG_HOST and TG_SECRET configuration")
        return False
    
    print("TigerGraph connection established")
    print()
    
    # Run full ingestion
    print("Running full ingestion pipeline...")
    results = ingestion.run_full_ingestion(str(corpus_path), str(questions_path))
    
    print()
    print("=" * 60)
    print("INGESTION RESULTS")
    print("=" * 60)
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    print()
    
    if results['status'] == 'completed':
        print("Steps completed:")
        for step, status in results.get('steps', {}).items():
            print(f"  - {step}: {status}")
        print()
        
        if 'vertex_counts' in results:
            print("Vertex counts:")
            for vertex_type, count in results['vertex_counts'].items():
                print(f"  - {vertex_type}: {count}")
        print()
        
        if 'edge_counts' in results:
            print("Edge counts:")
            for edge_type, count in results['edge_counts'].items():
                print(f"  - {edge_type}: {count}")
        print()
        
        print("SUCCESS: Ingestion completed successfully")
        return True
    else:
        print("ERROR: Ingestion failed")
        print("Errors:")
        for error in results.get('errors', []):
            print(f"  - {error}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
