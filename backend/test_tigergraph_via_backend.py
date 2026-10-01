"""Test TigerGraph data via backend endpoints."""
import requests
import json

BASE_URL = "https://graphprobe-ai-backend.onrender.com"

def test_tigergraph_via_backend():
    """Test TigerGraph data via backend endpoints."""
    
    # Test 1: Health check
    print("=== Test 1: Health Check ===")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Config check
    print("\n=== Test 2: Config Check ===")
    response = requests.get(f"{BASE_URL}/api/config")
    print(f"Status: {response.status_code}")
    config = response.json()
    print(f"TigerGraph Host: {config.get('tigergraph_host')}")
    print(f"TigerGraph Port: {config.get('tigergraph_port')}")
    print(f"TigerGraph Graph: {config.get('tigergraph_graph')}")
    print(f"TigerGraph Configured: {config.get('tigergraph_configured')}")
    
    # Test 3: Metrics check
    print("\n=== Test 3: Metrics Check ===")
    response = requests.get(f"{BASE_URL}/api/metrics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Investigate with Olympic question
    print("\n=== Test 4: Investigate Olympic Question ===")
    question = "Who won the gold medal in the men's 20 kilometres walk athletics event at the Summer Olympics held immediately before 2016?"
    response = requests.post(
        f"{BASE_URL}/api/investigate",
        json={"question": question},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"Pipeline: {result.get('result', {}).get('pipeline')}")
        print(f"Answer: {result.get('result', {}).get('answer')}")
        print(f"Confidence: {result.get('result', {}).get('confidence')}")
        
        # Check agent trace
        agent_trace = result.get('result', {}).get('agent_trace', {})
        print(f"\nAgent Trace:")
        print(f"Run ID: {agent_trace.get('run_id')}")
        print(f"Tools Used: {agent_trace.get('tools_used')}")
        
        # Check graph traverse step
        steps = agent_trace.get('steps', [])
        for step in steps:
            if step.get('tool') == 'graph_traverse':
                print(f"\nGraph Traverse Step:")
                print(f"  Input: {step.get('input')}")
                print(f"  Result Summary: {step.get('result_summary')}")
                print(f"  Latency: {step.get('latency_ms')}ms")
        
        # Check graph context
        graph_context = result.get('result', {}).get('graph_context', {})
        print(f"\nGraph Context:")
        print(f"  Entities: {graph_context.get('entities')}")
        print(f"  Relationships: {graph_context.get('relationships')}")
        print(f"  Nodes Visited: {graph_context.get('nodes_visited')}")
        print(f"  Edges Traversed: {graph_context.get('edges_traversed')}")
        
        # Check metrics
        metrics = result.get('result', {}).get('metrics', {})
        print(f"\nMetrics:")
        print(f"  Graph Nodes: {metrics.get('graph_nodes')}")
        print(f"  Graph Edges: {metrics.get('graph_edges')}")
        print(f"  Chunks Retrieved: {metrics.get('chunks_retrieved')}")
        
        # Get trace if available
        run_id = result.get('result', {}).get('run_id')
        if run_id:
            print(f"\n=== Test 5: Get Trace ===")
            trace_response = requests.get(f"{BASE_URL}/api/trace/{run_id}")
            print(f"Status: {trace_response.status_code}")
            trace = trace_response.json()
            print(f"Trace ID: {trace.get('trace_id')}")
            print(f"Tools Used: {trace.get('tools_used')}")
            print(f"Steps: {len(trace.get('steps', []))}")
            
            print(f"\n=== Test 6: Get Evidence ===")
            evidence_response = requests.get(f"{BASE_URL}/api/evidence/{run_id}")
            print(f"Status: {evidence_response.status_code}")
            evidence = evidence_response.json()
            print(f"Evidence Count: {len(evidence) if isinstance(evidence, list) else 0}")
            if isinstance(evidence, list) and len(evidence) > 0:
                print(f"First Evidence Source: {evidence[0].get('metadata', {}).get('source_type')}")

if __name__ == "__main__":
    test_tigergraph_via_backend()
