"""Script to verify TigerGraph data ingestion."""
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


def verify_ingestion():
    """Verify TigerGraph data ingestion."""
    logger.info("Verifying TigerGraph data ingestion...")
    
    # Check configuration
    if not settings.tg_secret:
        logger.error("TG_SECRET not configured")
        return False
    
    # Initialize ingestion
    ingestion = TigerGraphIngestion()
    
    if not ingestion.conn:
        logger.error("Failed to connect to TigerGraph")
        return False
    
    try:
        # Get schema
        schema = ingestion.conn.getSchema()
        vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
        edge_types = [et['Name'] for et in schema.get("EdgeTypes", [])]
        
        logger.info(f"Vertex types: {vertex_types}")
        logger.info(f"Edge types: {edge_types}")
        
        # Get vertex counts
        vertex_counts = ingestion.conn.getVertexCount('*')
        logger.info(f"Vertex counts: {vertex_counts}")
        
        # Get edge counts
        edge_counts = ingestion.conn.getEdgeCount('*')
        logger.info(f"Edge counts: {edge_counts}")
        
        # Check for critical data
        critical_checks = {
            'Document': vertex_counts.get('Document', 0) > 0,
            'Event': vertex_counts.get('Event', 0) > 0,
            'Athlete': vertex_counts.get('Athlete', 0) > 0,
            'Games': vertex_counts.get('Games', 0) > 0,
            'DOCUMENT_ABOUT_EVENT': edge_counts.get('DOCUMENT_ABOUT_EVENT', 0) > 0,
            'EVENT_PART_OF_GAMES': edge_counts.get('EVENT_PART_OF_GAMES', 0) > 0,
            'ATHLETE_WON_MEDAL_IN_EVENT': edge_counts.get('ATHLETE_WON_MEDAL_IN_EVENT', 0) > 0,
        }
        
        logger.info("\nCritical data checks:")
        for check, passed in critical_checks.items():
            status = "✓" if passed else "✗"
            logger.info(f"  {status} {check}: {passed}")
        
        # Try the critical traversal: 2012 Summer Games -> 20 kilometres walk -> Chen Ding
        logger.info("\nAttempting critical traversal: 2012 Summer Games -> 20 kilometres walk -> Chen Ding")
        
        try:
            # Query for 2012 Summer Games
            query = 'SELECT * FROM Games WHERE year == 2012 AND season == "Summer"'
            result = ingestion.conn.runInterpretedQuery(query)
            logger.info(f"2012 Summer Games query: {len(result) if result else 0} results")
            
            if result and len(result) > 0:
                games_id = f"2012_Summer"
                logger.info(f"Games ID: {games_id}")
                
                # Query for events in 2012 Summer Games
                query = f'''
                SELECT t1.name, t1.year, t1.sport
                FROM Games:t - (EVENT_PART_OF_GAMES) <- Event:t1
                WHERE t.year == 2012
                LIMIT 10
                '''
                result = ingestion.conn.runInterpretedQuery(query)
                logger.info(f"Events in 2012: {len(result) if result else 0} results")
                
                if result:
                    for event in result[:3]:
                        logger.info(f"  Event: {event}")
                
                # Query for Chen Ding
                query = '''
                SELECT t1.name, t3.name, e.medal_type
                FROM Event:t1 - (ATHLETE_WON_MEDAL_IN_EVENT:e) <- Athlete:t3
                WHERE t1.name CONTAINS "20 kilometre" OR t1.name CONTAINS "20km"
                LIMIT 10
                '''
                result = ingestion.conn.runInterpretedQuery(query)
                logger.info(f"20km walk events: {len(result) if result else 0} results")
                
                if result:
                    for event in result:
                        logger.info(f"  {event}")
            
        except Exception as traversal_error:
            logger.error(f"Critical traversal failed: {traversal_error}")
        
        # Summary
        total_vertices = sum(vertex_counts.values()) if vertex_counts else 0
        total_edges = sum(edge_counts.values()) if edge_counts else 0
        
        logger.info(f"\n=== SUMMARY ===")
        logger.info(f"Total vertices: {total_vertices}")
        logger.info(f"Total edges: {total_edges}")
        logger.info(f"All critical checks passed: {all(critical_checks.values())}")
        
        return all(critical_checks.values())
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_ingestion()
    sys.exit(0 if success else 1)
