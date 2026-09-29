"""TigerGraph ingestion endpoint for production deployment."""
from fastapi import APIRouter, HTTPException
from app.tigergraph.ingestion import TigerGraphIngestion
from app.core.config import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tigergraph/ingest")
async def run_tigergraph_ingestion(force: bool = False):
    """Execute TigerGraph schema creation and data ingestion.
    
    This endpoint is for one-time production deployment to:
    1. Create the Transaction_Fraud graph schema
    2. Ingest Olympic corpus data into TigerGraph
    
    Requires TG_SECRET to be configured in environment variables.
    
    Args:
        force: If True, force re-ingestion even if graph has data
    """
    try:
        # Check if TigerGraph credentials are available
        if not settings.tg_secret:
            raise HTTPException(
                status_code=503,
                detail="TigerGraph credentials not configured. TG_SECRET environment variable is required."
            )
        
        # Paths to corpus - use production corpus in backend directory
        # In Render, the working directory is /app (Docker WORKDIR)
        # The Dockerfile copies corpus to /app/corpus_production.jsonl (backend root)
        # Try multiple possible locations for the corpus file
        backend_dir = Path(__file__).parent.parent
        
        logger.info(f"Current working directory: {Path.cwd()}")
        logger.info(f"Backend directory: {backend_dir}")
        logger.info(f"Files in backend_dir: {list(backend_dir.iterdir())}")
        
        # Try corpus in backend directory first (Dockerfile copies it here)
        corpus_path = backend_dir / "corpus_production.jsonl"
        logger.info(f"Checking path 1: {corpus_path}, exists: {corpus_path.exists()}")
        
        # If not found, try in backend/app directory (Git location)
        if not corpus_path.exists():
            corpus_path = backend_dir / "app" / "corpus_production.jsonl"
            logger.info(f"Checking path 2: {corpus_path}, exists: {corpus_path.exists()}")
        
        # If not found, try in parent directory (for development)
        if not corpus_path.exists():
            corpus_path = backend_dir.parent / "corpus_production.jsonl"
            logger.info(f"Checking path 3: {corpus_path}, exists: {corpus_path.exists()}")
        
        # If still not found, try in project root
        if not corpus_path.exists():
            corpus_path = backend_dir.parent.parent / "corpus_production.jsonl"
            logger.info(f"Checking path 4: {corpus_path}, exists: {corpus_path.exists()}")
        
        questions_path = backend_dir.parent / "hackathon-resources" / "questions"
        
        # Verify corpus exists
        if not corpus_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Corpus file not found: {corpus_path}"
            )
        
        logger.info(f"Starting TigerGraph ingestion from {corpus_path} (force={force})")
        
        # Initialize ingestion pipeline
        ingestion = TigerGraphIngestion()
        ingestion.force_reingestion = force
        
        # Check connection
        if not ingestion.conn:
            raise HTTPException(
                status_code=503,
                detail="Failed to connect to TigerGraph. Check TG_HOST and TG_SECRET configuration."
            )
        
        # Run full ingestion
        results = ingestion.run_full_ingestion(str(corpus_path), str(questions_path))
        
        logger.info(f"TigerGraph ingestion completed: {results['status']}")
        
        return {
            "status": results['status'],
            "steps": results.get('steps', {}),
            "vertex_counts": results.get('vertex_counts', {}),
            "edge_counts": results.get('edge_counts', {}),
            "duration_seconds": results.get('duration_seconds'),
            "errors": results.get('errors', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TigerGraph ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/tigergraph/status")
async def get_tigergraph_status():
    """Get TigerGraph connection and graph status."""
    try:
        if not settings.tg_secret:
            return {
                "configured": False,
                "message": "TigerGraph credentials not configured"
            }
        
        ingestion = TigerGraphIngestion()
        
        if not ingestion.conn:
            return {
                "configured": True,
                "connected": False,
                "message": "Failed to connect to TigerGraph"
            }
        
        # Try to get schema to verify connection
        try:
            schema = ingestion.conn.getSchema()
            vertex_counts = ingestion.conn.getVertexCount('*')
            edge_counts = ingestion.conn.getEdgeCount('*')
            
            return {
                "configured": True,
                "connected": True,
                "graph_name": settings.tg_graphname,
                "schema": schema,
                "vertex_counts": vertex_counts,
                "edge_counts": edge_counts
            }
        except Exception as e:
            return {
                "configured": True,
                "connected": True,
                "query_failed": True,
                "error": str(e)
            }
        
    except Exception as e:
        logger.error(f"Failed to get TigerGraph status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
