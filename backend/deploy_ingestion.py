"""Direct TigerGraph ingestion script for production deployment."""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Explicitly load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from {env_path}")

from app.tigergraph.ingestion import TigerGraphIngestion
from app.core.config import settings
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Execute TigerGraph ingestion."""
    print("=" * 70)
    print("TIGERGRAPH INGESTION - PRODUCTION DEPLOYMENT")
    print("=" * 70)
    print()
    
    # Print configuration (without secrets)
    print("Configuration:")
    print(f"  TG_HOST: {settings.tg_host}")
    print(f"  TG_PORT: {settings.tg_port}")
    print(f"  TG_GRAPHNAME: {settings.tg_graphname}")
    print(f"  TG_SECRET configured: {bool(settings.tg_secret)}")
    print()
    
    if not settings.tg_secret:
        print("ERROR: TG_SECRET not configured")
        print("This script requires TigerGraph credentials to run.")
        return False
    
    # Paths to hackathon resources
    project_root = Path(__file__).parent.parent
    corpus_path = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
    questions_path = project_root / "hackathon-resources" / "questions"
    
    print("Data paths:")
    print(f"  Corpus: {corpus_path}")
    print(f"  Corpus exists: {corpus_path.exists()}")
    print(f"  Questions: {questions_path}")
    print(f"  Questions exists: {questions_path.exists()}")
    print()
    
    if not corpus_path.exists():
        print("ERROR: Corpus file not found")
        return False
    
    try:
        # Initialize ingestion pipeline
        print("Step 1: Initializing TigerGraph connection...")
        ingestion = TigerGraphIngestion()
        
        if not ingestion.conn:
            print("ERROR: Failed to connect to TigerGraph")
            print("Please check TG_HOST and TG_SECRET configuration")
            return False
        
        print("[OK] TigerGraph connection established")
        print()
        
        # Run full ingestion
        print("Step 2: Running full ingestion pipeline...")
        print("  - Loading dataset")
        print("  - Creating schema")
        print("  - Ingesting vertices")
        print("  - Ingesting edges")
        print()
        
        results = ingestion.run_full_ingestion(str(corpus_path), str(questions_path))
        
        print()
        print("=" * 70)
        print("INGESTION RESULTS")
        print("=" * 70)
        print(f"Status: {results['status']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
        print()
        
        if results['status'] == 'completed':
            print("Steps completed:")
            for step, status in results.get('steps', {}).items():
                status_str = "[OK]" if status == 'completed' or isinstance(status, dict) and status.get('success', 0) > 0 else "[X]"
                print(f"  {status_str} {step}: {status}")
            print()
            
            if 'vertex_counts' in results:
                print("Vertex counts:")
                total_vertices = 0
                for vertex_type, count in results['vertex_counts'].items():
                    print(f"  - {vertex_type}: {count}")
                    total_vertices += count
                print(f"  Total: {total_vertices}")
            print()
            
            if 'edge_counts' in results:
                print("Edge counts:")
                total_edges = 0
                for edge_type, count in results['edge_counts'].items():
                    print(f"  - {edge_type}: {count}")
                    total_edges += count
                print(f"  Total: {total_edges}")
            print()
            
            print("=" * 70)
            print("SUCCESS: Ingestion completed successfully")
            print("=" * 70)
            return True
        else:
            print("ERROR: Ingestion failed")
            print("Errors:")
            for error in results.get('errors', []):
                print(f"  - {error}")
            print()
            print("=" * 70)
            print("FAILED: Ingestion did not complete")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"ERROR: Unexpected error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
