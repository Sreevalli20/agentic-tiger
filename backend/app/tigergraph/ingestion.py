"""TigerGraph ingestion pipeline for the hackathon dataset."""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.data.dataset_parser import DatasetParser
from app.core.config import settings
import time

logger = logging.getLogger(__name__)


class TigerGraphIngestion:
    """Ingestion pipeline for loading dataset into TigerGraph."""
    
    def __init__(self):
        """Initialize ingestion pipeline."""
        self.conn = None
        self.parser = None
        self.force_reingestion = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize TigerGraph connection."""
        try:
            try:
                from pyTigerGraph import TigerGraphConnection
            except ImportError:
                logger.warning("pyTigerGraph not available - TigerGraph features will be disabled")
                self.conn = None
                return
            
            # Ensure host includes protocol
            host = settings.tg_host
            if not host.startswith(('http://', 'https://')):
                host = f'http://{host}'
            
            self.conn = TigerGraphConnection(
                host=host,
                restppPort=settings.tg_port,
                gsqlSecret=settings.tg_secret,
                graphname=settings.tg_graphname
            )
            logger.info("TigerGraph connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TigerGraph connection: {e}")
            self.conn = None
    
    def _reconnect(self):
        """Reconnect to TigerGraph after schema creation."""
        try:
            from pyTigerGraph import TigerGraphConnection
            
            host = settings.tg_host
            if not host.startswith(('http://', 'https://')):
                host = f'http://{host}'
            
            self.conn = TigerGraphConnection(
                host=host,
                restppPort=settings.tg_port,
                gsqlSecret=settings.tg_secret,
                graphname=settings.tg_graphname
            )
            logger.info("TigerGraph reconnected successfully")
        except Exception as e:
            logger.error(f"Failed to reconnect to TigerGraph: {e}")
            self.conn = None
    
    def create_schema(self) -> bool:
        """Check if the manually created TigerGraph schema exists and is compatible."""
        if not self.conn:
            logger.error("No TigerGraph connection available")
            return False
        
        try:
            logger.info("Checking TigerGraph schema...")
            
            # Check if graph already exists (schema was manually created)
            try:
                schema = self.conn.getSchema()
                if schema and len(schema.get("VertexTypes", [])) > 0:
                    vertex_types = {vt['Name'] for vt in schema.get("VertexTypes", [])}
                    edge_types = {et['Name'] for et in schema.get("EdgeTypes", [])}
                    logger.info(f"Graph {settings.tg_graphname} exists with vertex types: {vertex_types}")
                    logger.info(f"Graph {settings.tg_graphname} exists with edge types: {edge_types}")
                    
                    # Check if we have the expected Olympic schema
                    expected_vertices = {'Document', 'Event', 'Athlete', 'Nation', 'Venue', 'Games', 'Sport'}
                    expected_edges = {'DOCUMENT_ABOUT_EVENT', 'EVENT_PART_OF_GAMES', 'EVENT_IN_SPORT', 
                                    'EVENT_HELD_AT_VENUE', 'ATHLETE_WON_MEDAL_IN_EVENT', 
                                    'ATHLETE_REPRESENTS_NATION', 'NATION_PARTICIPATED_IN_GAMES', 
                                    'VENUE_LOCATED_IN_CITY'}
                    
                    if expected_vertices.issubset(vertex_types):
                        logger.info(f"Graph has Olympic schema - ready for data ingestion")
                        if expected_edges.issubset(edge_types):
                            logger.info(f"Graph has all expected edges - ready for data ingestion")
                        else:
                            logger.warning(f"Graph missing some edges. Expected: {expected_edges - edge_types}")
                        return True
                    else:
                        logger.error(f"Graph exists with different schema. Expected: {expected_vertices}, Found: {vertex_types}")
                        return False
                else:
                    logger.error(f"Graph {settings.tg_graphname} exists but has no vertex types")
                    return False
            except Exception as check_error:
                logger.error(f"Graph existence check failed: {check_error}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to check schema: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_dataset(self, corpus_path: str, questions_path: str) -> bool:
        """Load and parse the dataset."""
        try:
            logger.info(f"Loading dataset from {corpus_path}...")
            
            # For production corpus, load directly without DatasetParser
            # since we only need the corpus file
            import json
            from pathlib import Path
            
            corpus_file = Path(corpus_path)
            if not corpus_file.exists():
                logger.error(f"Corpus file not found: {corpus_path}")
                return False
            
            documents = []
            with open(corpus_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        doc = json.loads(line.strip())
                        documents.append(doc)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse line {line_num}: {e}")
            
            # Create a simple parser-like object for extraction
            class SimpleParser:
                def __init__(self, documents):
                    self.documents = documents
                
                def extract_event_info(self, document):
                    # Import DatasetParser to use its extraction logic
                    from app.data.dataset_parser import DatasetParser
                    # Create a temporary parser just for extraction
                    temp_parser = DatasetParser("", "")
                    return temp_parser.extract_event_info(document)
            
            self.parser = SimpleParser(documents)
            logger.info(f"Loaded {len(documents)} documents from production corpus")
            return True
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ingest_documents(self) -> Dict[str, int]:
        """Ingest documents as Document vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting documents...")
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            logger.info(f"Available vertex types: {vertex_types}")
            
            # Use the first available vertex type if Document doesn't exist
            vertex_type = 'Document' if 'Document' in vertex_types else (vertex_types[0] if vertex_types else 'Document')
            logger.info(f"Using vertex type: {vertex_type}")
        except:
            vertex_type = 'Document'
            logger.info("Could not get schema, defaulting to Document vertex type")
        
        for doc in self.parser.documents:
            try:
                # Match manually created schema: Document(doc_id, title, text)
                text_snippet = doc.get('text', '')[:1000] if doc.get('text') else ''
                
                self.conn.upsertVertex(
                    vertex_type,
                    doc['doc_id'],
                    {
                        'title': doc.get('title', ''),
                        'text': text_snippet
                    }
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest document {doc.get('doc_id')}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} documents, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_events(self) -> Dict[str, int]:
        """Ingest events as Event vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting events...")
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Event' if 'Event' in vertex_types else (vertex_types[0] if vertex_types else 'Event')
            logger.info(f"Using vertex type for events: {vertex_type}")
        except:
            vertex_type = 'Event'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                # Match manually created schema: Event(event_id, name, year, season)
                self.conn.upsertVertex(
                    vertex_type,
                    event_info['event_id'],
                    {
                        'name': event_info.get('name', ''),
                        'year': event_info.get('year', 0),
                        'season': event_info.get('season', '')
                    }
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest event for doc {doc.get('doc_id')}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} events, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_athletes(self) -> Dict[str, int]:
        """Ingest athletes as Athlete vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting athletes...")
        athletes = {}  # Deduplicate by athlete_id
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Athlete' if 'Athlete' in vertex_types else (vertex_types[0] if vertex_types else 'Athlete')
            logger.info(f"Using vertex type for athletes: {vertex_type}")
        except:
            vertex_type = 'Athlete'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                for medalist in event_info.get('medalists', []):
                    athlete_id = self._normalize_name(medalist['name'])
                    
                    if athlete_id not in athletes:
                        # Match manually created schema: Athlete(athlete_id, name)
                        athletes[athlete_id] = {
                            'name': medalist['name']
                        }
            except Exception as e:
                logger.error(f"Failed to extract athletes from doc {doc.get('doc_id')}: {e}")
        
        # Load athletes
        for athlete_id, athlete_data in athletes.items():
            try:
                self.conn.upsertVertex(
                    vertex_type,
                    athlete_id,
                    athlete_data
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest athlete {athlete_id}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} athletes, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_nations(self) -> Dict[str, int]:
        """Ingest nations as Nation vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting nations...")
        nations = {}  # Deduplicate by NOC
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Nation' if 'Nation' in vertex_types else (vertex_types[0] if vertex_types else 'Nation')
            logger.info(f"Using vertex type for nations: {vertex_type}")
        except:
            vertex_type = 'Nation'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                for medalist in event_info.get('medalists', []):
                    noc = medalist.get('noc', '').upper()
                    if noc and noc not in nations:
                        # Match manually created schema: Nation(noc, name)
                        country_name = self._noc_to_country_name(noc)
                        nations[noc] = country_name
            except Exception as e:
                logger.error(f"Failed to extract nations from doc {doc.get('doc_id')}: {e}")
        
        # Load nations
        for noc, country_name in nations.items():
            try:
                self.conn.upsertVertex(
                    vertex_type,
                    noc,
                    {'name': country_name}
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest nation {noc}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} nations, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_venues(self) -> Dict[str, int]:
        """Ingest venues as Venue vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting venues...")
        venues = {}  # Deduplicate by venue_id
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Venue' if 'Venue' in vertex_types else (vertex_types[0] if vertex_types else 'Venue')
            logger.info(f"Using vertex type for venues: {vertex_type}")
        except:
            vertex_type = 'Venue'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                venue_name = event_info.get('venue', '')
                
                if venue_name:
                    venue_id = self._normalize_name(venue_name)
                    if venue_id not in venues:
                        # Match manually created schema: Venue(venue_id, name, city)
                        venues[venue_id] = {
                            'name': venue_name,
                            'city': event_info.get('games', '').split()[-1] if event_info.get('games') else ''
                        }
            except Exception as e:
                logger.error(f"Failed to extract venues from doc {doc.get('doc_id')}: {e}")
        
        # Load venues
        for venue_id, venue_data in venues.items():
            try:
                self.conn.upsertVertex(
                    vertex_type,
                    venue_id,
                    venue_data
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest venue {venue_id}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} venues, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_games(self) -> Dict[str, int]:
        """Ingest Olympic Games as Games vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting games...")
        games = {}  # Deduplicate by games_id
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Games' if 'Games' in vertex_types else (vertex_types[0] if vertex_types else 'Games')
            logger.info(f"Using vertex type for games: {vertex_type}")
        except:
            vertex_type = 'Games'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                games_str = event_info.get('games', '')
                year = event_info.get('year', 0)
                season = event_info.get('season', '')
                
                if year and season:
                    games_id = f"{year}_{season}"
                    if games_id not in games:
                        # Match manually created schema: Games(games_id, year, season, name)
                        games[games_id] = {
                            'year': year,
                            'season': season,
                            'name': f"{year} {season}"
                        }
            except Exception as e:
                logger.error(f"Failed to extract games from doc {doc.get('doc_id')}: {e}")
        
        # Load games
        for games_id, games_data in games.items():
            try:
                self.conn.upsertVertex(
                    vertex_type,
                    games_id,
                    games_data
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest games {games_id}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} games, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_sports(self) -> Dict[str, int]:
        """Ingest sports as Sport vertices using manually created schema."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting sports...")
        sports = {}  # Deduplicate by sport_id
        success = 0
        failed = 0
        
        # Get available vertex types
        try:
            schema = self.conn.getSchema()
            vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
            vertex_type = 'Sport' if 'Sport' in vertex_types else (vertex_types[0] if vertex_types else 'Sport')
            logger.info(f"Using vertex type for sports: {vertex_type}")
        except:
            vertex_type = 'Sport'
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                sport_name = event_info.get('sport', '')
                
                if sport_name and sport_name != 'Unknown':
                    sport_id = self._normalize_name(sport_name)
                    if sport_id not in sports:
                        # Match manually created schema: Sport(sport_id, name)
                        sports[sport_id] = {
                            'name': sport_name
                        }
            except Exception as e:
                logger.error(f"Failed to extract sports from doc {doc.get('doc_id')}: {e}")
        
        # Load sports
        for sport_id, sport_data in sports.items():
            try:
                self.conn.upsertVertex(
                    vertex_type,
                    sport_id,
                    sport_data
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest sport {sport_id}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} sports, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_edges(self) -> Dict[str, int]:
        """Ingest edges between vertices using manually created schema (no edge attributes)."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting edges...")
        success = 0
        failed = 0
        
        # Get available edge types
        try:
            schema = self.conn.getSchema()
            edge_types = [et['Name'] for et in schema.get("EdgeTypes", [])]
            logger.info(f"Available edge types: {edge_types}")
        except:
            edge_types = []
            logger.info("Could not get edge types from schema")
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                doc_id = doc['doc_id']
                event_id = event_info['event_id']
                
                # Try to create edges if the types exist (using manually created schema without attributes)
                if 'DOCUMENT_ABOUT_EVENT' in edge_types:
                    self.conn.upsertEdge('Document', doc_id, 'DOCUMENT_ABOUT_EVENT', 'Event', event_id)
                    success += 1
                
                if 'EVENT_PART_OF_GAMES' in edge_types:
                    games_id = f"{event_info.get('year', 0)}_{event_info.get('season', '')}"
                    if event_info.get('year'):
                        self.conn.upsertEdge('Event', event_id, 'EVENT_PART_OF_GAMES', 'Games', games_id)
                        success += 1
                
                if 'EVENT_IN_SPORT' in edge_types:
                    sport_id = self._normalize_name(event_info.get('sport', ''))
                    if sport_id and sport_id != 'unknown':
                        self.conn.upsertEdge('Event', event_id, 'EVENT_IN_SPORT', 'Sport', sport_id)
                        success += 1
                
                if 'EVENT_HELD_AT_VENUE' in edge_types:
                    venue_id = self._normalize_name(event_info.get('venue', ''))
                    if venue_id and venue_id != 'unknown':
                        self.conn.upsertEdge('Event', event_id, 'EVENT_HELD_AT_VENUE', 'Venue', venue_id)
                        success += 1
                
                if 'ATHLETE_WON_MEDAL_IN_EVENT' in edge_types:
                    for medalist in event_info.get('medalists', []):
                        athlete_id = self._normalize_name(medalist['name'])
                        self.conn.upsertEdge('Athlete', athlete_id, 'ATHLETE_WON_MEDAL_IN_EVENT', 'Event', event_id)
                        success += 1
                
                if 'ATHLETE_REPRESENTS_NATION' in edge_types:
                    for medalist in event_info.get('medalists', []):
                        athlete_id = self._normalize_name(medalist['name'])
                        noc = medalist.get('noc', '').upper()
                        if noc:
                            self.conn.upsertEdge('Athlete', athlete_id, 'ATHLETE_REPRESENTS_NATION', 'Nation', noc)
                            success += 1
                
                if 'NATION_PARTICIPATED_IN_GAMES' in edge_types:
                    for medalist in event_info.get('medalists', []):
                        noc = medalist.get('noc', '').upper()
                        games_id = f"{event_info.get('year', 0)}_{event_info.get('season', '')}"
                        if noc and event_info.get('year'):
                            self.conn.upsertEdge('Nation', noc, 'NATION_PARTICIPATED_IN_GAMES', 'Games', games_id)
                            success += 1
                
                if 'VENUE_LOCATED_IN_CITY' in edge_types:
                    venue_id = self._normalize_name(event_info.get('venue', ''))
                    games_id = f"{event_info.get('year', 0)}_{event_info.get('season', '')}"
                    if venue_id and venue_id != 'unknown' and event_info.get('year'):
                        self.conn.upsertEdge('Venue', venue_id, 'VENUE_LOCATED_IN_CITY', 'Games', games_id)
                        success += 1
                
            except Exception as e:
                logger.error(f"Failed to ingest edges for doc {doc.get('doc_id')}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} edges, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a name for use as vertex ID."""
        # Remove special characters, convert to lowercase, replace spaces with underscores
        normalized = name.lower().replace(' ', '_').replace('-', '_').replace("'", '')
        # Remove any remaining non-alphanumeric characters
        normalized = ''.join(c for c in normalized if c.isalnum() or c == '_')
        return normalized
    
    def _noc_to_country_name(self, noc: str) -> str:
        """Convert NOC code to country name (simplified)."""
        # This is a simplified mapping - in production, use a complete NOC mapping
        noc_map = {
            'USA': 'United States',
            'GBR': 'Great Britain',
            'GER': 'Germany',
            'FRA': 'France',
            'CHN': 'China',
            'RUS': 'Russia',
            'JPN': 'Japan',
            'AUS': 'Australia',
            'CAN': 'Canada',
            'BRA': 'Brazil',
            'HUN': 'Hungary',
            'POR': 'Portugal',
            'NED': 'Netherlands',
            'KOR': 'South Korea',
            'NOR': 'Norway',
            'SWE': 'Sweden',
            'ITA': 'Italy',
            'ESP': 'Spain'
        }
        return noc_map.get(noc, noc)
    
    def run_full_ingestion(self, corpus_path: str, questions_path: str) -> Dict[str, Any]:
        """Run the complete ingestion pipeline idempotently."""
        start_time = time.time()
        results = {
            'status': 'started',
            'steps': {},
            'errors': []
        }
        
        try:
            # Step 1: Load dataset
            if not self.load_dataset(corpus_path, questions_path):
                results['status'] = 'failed'
                results['errors'].append('Failed to load dataset')
                return results
            
            results['steps']['load_dataset'] = 'completed'
            
            # Step 2: Create schema (idempotent)
            if not self.create_schema():
                results['status'] = 'failed'
                results['errors'].append('Failed to create schema')
                return results
            
            results['steps']['create_schema'] = 'completed'
            
            # Step 3: Check if graph already has data (unless force reingestion)
            if not self.force_reingestion:
                try:
                    vertex_counts = self.conn.getVertexCount('*')
                    total_vertices = sum(vertex_counts.values()) if vertex_counts else 0
                    logger.info(f"Current vertex counts: {vertex_counts}, Total: {total_vertices}")
                    
                    # If graph already has substantial data, skip re-ingestion
                    # Use a higher threshold to ensure we have enough data for meaningful queries
                    if total_vertices > 500:
                        logger.info(f"Graph already has {total_vertices} vertices - skipping data ingestion")
                        results['status'] = 'skipped'
                        results['message'] = 'Graph already contains data'
                        results['vertex_counts'] = vertex_counts
                        try:
                            edge_counts = self.conn.getEdgeCount('*')
                            results['edge_counts'] = edge_counts
                        except:
                            pass
                        results['duration_seconds'] = time.time() - start_time
                        return results
                    else:
                        logger.info(f"Graph has only {total_vertices} vertices - proceeding with data ingestion")
                except Exception as count_error:
                    logger.warning(f"Failed to check existing vertex counts: {count_error}")
                    logger.info("Proceeding with data ingestion due to count check failure")
            else:
                logger.info("Force reingestion enabled - skipping data check")
            
            # Step 4: Ingest vertices
            results['steps']['ingest_documents'] = self.ingest_documents()
            results['steps']['ingest_events'] = self.ingest_events()
            results['steps']['ingest_athletes'] = self.ingest_athletes()
            results['steps']['ingest_nations'] = self.ingest_nations()
            results['steps']['ingest_venues'] = self.ingest_venues()
            results['steps']['ingest_games'] = self.ingest_games()
            results['steps']['ingest_sports'] = self.ingest_sports()
            
            # Step 5: Ingest edges
            results['steps']['ingest_edges'] = self.ingest_edges()
            
            # Step 6: Get vertex/edge counts
            try:
                vertex_counts = self.conn.getVertexCount('*')
                edge_counts = self.conn.getEdgeCount('*')
                results['vertex_counts'] = vertex_counts
                results['edge_counts'] = edge_counts
                logger.info(f"Final vertex counts: {vertex_counts}")
                logger.info(f"Final edge counts: {edge_counts}")
            except Exception as e:
                logger.error(f"Failed to get counts: {e}")
                results['errors'].append(f"Failed to get counts: {e}")
            
            results['status'] = 'completed'
            results['duration_seconds'] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            results['status'] = 'failed'
            results['errors'].append(str(e))
        
        return results


def main():
    """Test the ingestion pipeline."""
    import sys
    from pathlib import Path
    
    # Paths to hackathon resources
    project_root = Path(__file__).parent.parent.parent.parent
    corpus_path = project_root / "hackathon-resources" / "corpus" / "corpus.jsonl"
    questions_path = project_root / "hackathon-resources" / "questions"
    
    ingestion = TigerGraphIngestion()
    
    # Note: This will fail without actual TigerGraph credentials
    # It's designed to work when credentials are provided
    print("TigerGraph Ingestion Pipeline")
    print("=" * 50)
    print("Note: This requires valid TigerGraph credentials in .env")
    print("Current TG_HOST:", settings.tg_host)
    print("Current TG_PORT:", settings.tg_port)
    print("Current TG_GRAPHNAME:", settings.tg_graphname)
    print()
    
    if not settings.tg_secret:
        print("TG_SECRET not configured. Skipping actual ingestion.")
        print("To run ingestion, set TG_SECRET in .env")
        return
    
    results = ingestion.run_full_ingestion(str(corpus_path), str(questions_path))
    
    print("\n=== Ingestion Results ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
