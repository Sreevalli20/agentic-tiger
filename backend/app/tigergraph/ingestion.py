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
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize TigerGraph connection."""
        try:
            # Try to import pytigergraph with fallback handling
            try:
                from pytigergraph import TigerGraphConnection
            except ImportError:
                logger.warning("pytigergraph not available - TigerGraph features will be disabled")
                self.conn = None
                return
            
            self.conn = TigerGraphConnection(
                host=settings.tg_host,
                port=settings.tg_port,
                password=settings.tg_secret,
                graphname=settings.tg_graphname
            )
            logger.info("TigerGraph connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TigerGraph connection: {e}")
            self.conn = None
    
    def create_schema(self) -> bool:
        """Create the TigerGraph schema."""
        if not self.conn:
            logger.error("No TigerGraph connection available")
            return False
        
        try:
            logger.info("Creating TigerGraph schema...")
            
            # Drop existing graph if it exists
            try:
                self.conn.gsql(f'DROP GRAPH {settings.tg_graphname}')
                logger.info(f"Dropped existing graph {settings.tg_graphname}")
            except:
                logger.info("No existing graph to drop")
            
            # Create schema GSQL
            schema_gsql = """
            CREATE VERTEX Document(PRIMARY_ID doc_id STRING, title STRING, url STRING, wikidata_qid STRING, wikipedia_pageid INT, approx_tokens INT, text_snippet STRING)
            CREATE VERTEX Event(PRIMARY_ID event_id STRING, name STRING, sport STRING, games STRING, year INT, season STRING, date STRING, venue STRING, competitors INT, nations INT, event_type STRING)
            CREATE VERTEX Athlete(PRIMARY_ID athlete_id STRING, name STRING, noc STRING, sport STRING)
            CREATE VERTEX Nation(PRIMARY_ID noc STRING, country_name STRING)
            CREATE VERTEX Venue(PRIMARY_ID venue_id STRING, name STRING, location STRING, type STRING)
            CREATE VERTEX Games(PRIMARY_ID games_id STRING, year INT, season STRING, host_city STRING, host_country STRING)
            CREATE VERTEX Sport(PRIMARY_ID sport_id STRING, name STRING, category STRING)
            
            CREATE DIRECTED EDGE DOCUMENT_ABOUT_EVENT(FROM Document, TO Event, relevance_score FLOAT)
            CREATE DIRECTED EDGE EVENT_PART_OF_GAMES(FROM Event, TO Games)
            CREATE DIRECTED EDGE EVENT_IN_SPORT(FROM Event, TO Sport)
            CREATE DIRECTED EDGE EVENT_HELD_AT_VENUE(FROM Event, TO Venue, date STRING)
            CREATE DIRECTED EDGE ATHLETE_WON_MEDAL_IN_EVENT(FROM Athlete, TO Event, medal_type STRING, result STRING)
            CREATE DIRECTED EDGE ATHLETE_REPRESENTS_NATION(FROM Athlete, TO Nation)
            CREATE DIRECTED EDGE NATION_PARTICIPATED_IN_GAMES(FROM Nation, TO Games, athlete_count INT)
            CREATE DIRECTED EDGE VENUE_LOCATED_IN_CITY(FROM Venue, TO Games)
            
            CREATE GRAPH """ + settings.tg_graphname + """(Document, Event, Athlete, Nation, Venue, Games, Sport, DOCUMENT_ABOUT_EVENT, EVENT_PART_OF_GAMES, EVENT_IN_SPORT, EVENT_HELD_AT_VENUE, ATHLETE_WON_MEDAL_IN_EVENT, ATHLETE_REPRESENTS_NATION, NATION_PARTICIPATED_IN_GAMES, VENUE_LOCATED_IN_CITY)
            """
            
            self.conn.gsql(schema_gsql)
            logger.info("Schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    def load_dataset(self, corpus_path: str, questions_path: str) -> bool:
        """Load and parse the dataset."""
        try:
            logger.info("Loading dataset...")
            self.parser = DatasetParser(corpus_path, questions_path)
            data = self.parser.load_all()
            logger.info(f"Loaded {len(data['documents'])} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return False
    
    def ingest_documents(self) -> Dict[str, int]:
        """Ingest documents as Document vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting documents...")
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                text_snippet = doc.get('text', '')[:500] if doc.get('text') else ''
                
                self.conn.upsertVertex(
                    'Document',
                    doc['doc_id'],
                    {
                        'title': doc.get('title', ''),
                        'url': doc.get('url', ''),
                        'wikidata_qid': doc.get('wikidata_qid', ''),
                        'wikipedia_pageid': doc.get('wikipedia_pageid', 0),
                        'approx_tokens': doc.get('approx_tokens', 0),
                        'text_snippet': text_snippet
                    }
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest document {doc.get('doc_id')}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} documents, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_events(self) -> Dict[str, int]:
        """Ingest events as Event vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting events...")
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                self.conn.upsertVertex(
                    'Event',
                    event_info['event_id'],
                    {
                        'name': event_info.get('name', ''),
                        'sport': event_info.get('sport', ''),
                        'games': event_info.get('games', ''),
                        'year': event_info.get('year', 0),
                        'season': event_info.get('season', ''),
                        'date': event_info.get('date', ''),
                        'venue': event_info.get('venue', ''),
                        'competitors': int(event_info.get('competitors', 0)) if event_info.get('competitors', '').isdigit() else 0,
                        'nations': int(event_info.get('nations', 0)) if event_info.get('nations', '').isdigit() else 0,
                        'event_type': event_info.get('event_type', '')
                    }
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest event for doc {doc.get('doc_id')}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} events, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_athletes(self) -> Dict[str, int]:
        """Ingest athletes as Athlete vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting athletes...")
        athletes = {}  # Deduplicate by athlete_id
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                for medalist in event_info.get('medalists', []):
                    athlete_id = self._normalize_name(medalist['name'])
                    
                    if athlete_id not in athletes:
                        athletes[athlete_id] = {
                            'name': medalist['name'],
                            'noc': medalist.get('noc', ''),
                            'sport': event_info.get('sport', '')
                        }
            except Exception as e:
                logger.error(f"Failed to extract athletes from doc {doc.get('doc_id')}: {e}")
        
        # Load athletes
        for athlete_id, athlete_data in athletes.items():
            try:
                self.conn.upsertVertex(
                    'Athlete',
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
        """Ingest nations as Nation vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting nations...")
        nations = {}  # Deduplicate by NOC
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                
                for medalist in event_info.get('medalists', []):
                    noc = medalist.get('noc', '').upper()
                    if noc and noc not in nations:
                        # Map NOC to country name (simplified)
                        country_name = self._noc_to_country_name(noc)
                        nations[noc] = country_name
            except Exception as e:
                logger.error(f"Failed to extract nations from doc {doc.get('doc_id')}: {e}")
        
        # Load nations
        for noc, country_name in nations.items():
            try:
                self.conn.upsertVertex(
                    'Nation',
                    noc,
                    {'country_name': country_name}
                )
                success += 1
            except Exception as e:
                logger.error(f"Failed to ingest nation {noc}: {e}")
                failed += 1
        
        logger.info(f"Ingested {success} nations, {failed} failed")
        return {'success': success, 'failed': failed}
    
    def ingest_venues(self) -> Dict[str, int]:
        """Ingest venues as Venue vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting venues...")
        venues = {}  # Deduplicate by venue_id
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                venue_name = event_info.get('venue', '')
                
                if venue_name:
                    venue_id = self._normalize_name(venue_name)
                    if venue_id not in venues:
                        venues[venue_id] = {
                            'name': venue_name,
                            'location': event_info.get('games', '').split()[-1] if event_info.get('games') else '',
                            'type': 'unknown'
                        }
            except Exception as e:
                logger.error(f"Failed to extract venues from doc {doc.get('doc_id')}: {e}")
        
        # Load venues
        for venue_id, venue_data in venues.items():
            try:
                self.conn.upsertVertex(
                    'Venue',
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
        """Ingest Olympic Games as Games vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting games...")
        games = {}  # Deduplicate by games_id
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                games_str = event_info.get('games', '')
                year = event_info.get('year', 0)
                season = event_info.get('season', '')
                
                if year and season:
                    games_id = f"{year}_{season}"
                    if games_id not in games:
                        games[games_id] = {
                            'year': year,
                            'season': season,
                            'host_city': 'unknown',  # Would need additional parsing
                            'host_country': 'unknown'
                        }
            except Exception as e:
                logger.error(f"Failed to extract games from doc {doc.get('doc_id')}: {e}")
        
        # Load games
        for games_id, games_data in games.items():
            try:
                self.conn.upsertVertex(
                    'Games',
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
        """Ingest sports as Sport vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting sports...")
        sports = {}  # Deduplicate by sport_id
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                sport_name = event_info.get('sport', '')
                
                if sport_name and sport_name != 'Unknown':
                    sport_id = self._normalize_name(sport_name)
                    if sport_id not in sports:
                        sports[sport_id] = {
                            'name': sport_name,
                            'category': 'Olympic'
                        }
            except Exception as e:
                logger.error(f"Failed to extract sports from doc {doc.get('doc_id')}: {e}")
        
        # Load sports
        for sport_id, sport_data in sports.items():
            try:
                self.conn.upsertVertex(
                    'Sport',
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
        """Ingest edges between vertices."""
        if not self.conn or not self.parser:
            logger.error("Connection or parser not initialized")
            return {'success': 0, 'failed': 0}
        
        logger.info("Ingesting edges...")
        success = 0
        failed = 0
        
        for doc in self.parser.documents:
            try:
                event_info = self.parser.extract_event_info(doc)
                doc_id = doc['doc_id']
                event_id = event_info['event_id']
                
                # DOCUMENT_ABOUT_EVENT
                self.conn.upsertEdge('Document', doc_id, 'DOCUMENT_ABOUT_EVENT', 'Event', event_id, {'relevance_score': 1.0})
                success += 1
                
                # EVENT_PART_OF_GAMES
                games_id = f"{event_info.get('year', 0)}_{event_info.get('season', '')}"
                if event_info.get('year'):
                    self.conn.upsertEdge('Event', event_id, 'EVENT_PART_OF_GAMES', 'Games', games_id)
                    success += 1
                
                # EVENT_IN_SPORT
                sport_id = self._normalize_name(event_info.get('sport', ''))
                if sport_id and sport_id != 'unknown':
                    self.conn.upsertEdge('Event', event_id, 'EVENT_IN_SPORT', 'Sport', sport_id)
                    success += 1
                
                # EVENT_HELD_AT_VENUE
                venue_id = self._normalize_name(event_info.get('venue', ''))
                if venue_id and venue_id != 'unknown':
                    self.conn.upsertEdge('Event', event_id, 'EVENT_HELD_AT_VENUE', 'Venue', venue_id, {'date': event_info.get('date', '')})
                    success += 1
                
                # ATHLETE_WON_MEDAL_IN_EVENT and ATHLETE_REPRESENTS_NATION
                for medalist in event_info.get('medalists', []):
                    athlete_id = self._normalize_name(medalist['name'])
                    noc = medalist.get('noc', '').upper()
                    
                    self.conn.upsertEdge('Athlete', athlete_id, 'ATHLETE_WON_MEDAL_IN_EVENT', 'Event', event_id, {'medal_type': medalist['medal_type'], 'result': ''})
                    success += 1
                    
                    if noc:
                        self.conn.upsertEdge('Athlete', athlete_id, 'ATHLETE_REPRESENTS_NATION', 'Nation', noc)
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
        """Run the complete ingestion pipeline."""
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
            
            # Step 2: Create schema
            if not self.create_schema():
                results['status'] = 'failed'
                results['errors'].append('Failed to create schema')
                return results
            
            results['steps']['create_schema'] = 'completed'
            
            # Step 3: Ingest vertices
            results['steps']['ingest_documents'] = self.ingest_documents()
            results['steps']['ingest_events'] = self.ingest_events()
            results['steps']['ingest_athletes'] = self.ingest_athletes()
            results['steps']['ingest_nations'] = self.ingest_nations()
            results['steps']['ingest_venues'] = self.ingest_venues()
            results['steps']['ingest_games'] = self.ingest_games()
            results['steps']['ingest_sports'] = self.ingest_sports()
            
            # Step 4: Ingest edges
            results['steps']['ingest_edges'] = self.ingest_edges()
            
            # Step 5: Get vertex/edge counts
            try:
                vertex_counts = self.conn.getVertexCount('*')
                edge_counts = self.conn.getEdgeCount('*')
                results['vertex_counts'] = vertex_counts
                results['edge_counts'] = edge_counts
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
