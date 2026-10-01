"""Direct TigerGraph data check without backend."""
import os
import sys
from pathlib import Path

# Set environment variables
os.environ['TG_SECRET'] = 'test_secret'
os.environ['TG_HOST'] = 'https://tg-b9e4f040-4261-4150-8392-8fad5e33df28.tg-2635877100.i.tgcloud.io'
os.environ['TG_PORT'] = '14240'

try:
    from pyTigerGraph import TigerGraphConnection
    
    print("=== Direct TigerGraph Connection Test ===")
    
    # Connect to TigerGraph
    conn = TigerGraphConnection(
        host='https://tg-b9e4f040-4261-4150-8392-8fad5e33df28.tg-2635877100.i.tgcloud.io',
        restppPort=14240,
        gsqlSecret='test_secret',
        graphname='Transaction_Fraud'
    )
    
    print("Connection initialized")
    
    # Get schema
    print("\n=== Schema Check ===")
    try:
        schema = conn.getSchema()
        vertex_types = [vt['Name'] for vt in schema.get("VertexTypes", [])]
        edge_types = [et['Name'] for et in schema.get("EdgeTypes", [])]
        print(f"Vertex types: {vertex_types}")
        print(f"Edge types: {edge_types}")
    except Exception as e:
        print(f"Schema check failed: {e}")
        # Try alternative method
        try:
            print("Trying alternative schema check...")
            vertex_types = conn.getVertexTypes()
            edge_types = conn.getEdgeTypes()
            print(f"Vertex types (alt): {vertex_types}")
            print(f"Edge types (alt): {edge_types}")
        except Exception as e2:
            print(f"Alternative schema check also failed: {e2}")
    
    # Get vertex counts
    print("\n=== Vertex Counts ===")
    try:
        vertex_counts = conn.getVertexCount('*')
        print(f"Vertex counts: {vertex_counts}")
        total_vertices = sum(vertex_counts.values()) if vertex_counts else 0
        print(f"Total vertices: {total_vertices}")
    except Exception as e:
        print(f"Vertex count check failed: {e}")
    
    # Get edge counts
    print("\n=== Edge Counts ===")
    try:
        edge_counts = conn.getEdgeCount('*')
        print(f"Edge counts: {edge_counts}")
        total_edges = sum(edge_counts.values()) if edge_counts else 0
        print(f"Total edges: {total_edges}")
    except Exception as e:
        print(f"Edge count check failed: {e}")
    
    # Try critical traversal
    print("\n=== Critical Traversal Test ===")
    print("Query: 2012 Summer Games -> 20 kilometres walk -> Chen Ding")
    
    try:
        # Query for 2012 Summer Games
        query = 'SELECT * FROM Games WHERE year == 2012 AND season == "Summer"'
        result = conn.runInterpretedQuery(query)
        print(f"2012 Summer Games query: {len(result) if result else 0} results")
        if result:
            for r in result[:3]:
                print(f"  {r}")
    except Exception as e:
        print(f"2012 Summer Games query failed: {e}")
    
    try:
        # Query for 20km walk events
        query = '''
        SELECT t1.name, t3.name, e.medal_type
        FROM Event:t1 - (ATHLETE_WON_MEDAL_IN_EVENT:e) <- Athlete:t3
        WHERE t1.name CONTAINS "20 kilometre" OR t1.name CONTAINS "20km"
        LIMIT 10
        '''
        result = conn.runInterpretedQuery(query)
        print(f"20km walk events: {len(result) if result else 0} results")
        if result:
            for r in result:
                print(f"  {r}")
    except Exception as e:
        print(f"20km walk query failed: {e}")
    
    # Try simple vertex query
    print("\n=== Simple Vertex Query ===")
    try:
        # Try to get a few vertices
        if 'Document' in vertex_types:
            docs = conn.getVertices('Document', limit=5)
            print(f"Document vertices (sample): {len(docs) if docs else 0}")
            if docs:
                for doc in docs[:2]:
                    print(f"  {doc}")
    except Exception as e:
        print(f"Document query failed: {e}")
    
    try:
        if 'Event' in vertex_types:
            events = conn.getVertices('Event', limit=5)
            print(f"Event vertices (sample): {len(events) if events else 0}")
            if events:
                for event in events[:2]:
                    print(f"  {event}")
    except Exception as e:
        print(f"Event query failed: {e}")
    
    print("\n=== Test Complete ===")

except ImportError:
    print("pyTigerGraph not installed")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
