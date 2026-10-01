"""Run evaluation on all 50 hidden questions and generate artifact."""
import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
INPUT_FILE = "../hackathon-resources/questions/eval_hidden.jsonl"
OUTPUT_FILE = "../evaluation/hidden_questions_results.json"

async def evaluate_single_question(client, question_data, index):
    """Evaluate a single question."""
    qid = question_data.get("qid", f"q{index}")
    question = question_data["question"]
    qtype = question_data.get("qtype", "unknown")
    
    print(f"[{index+1}/50] Processing {qid}: {question[:60]}...")
    
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/investigate",
            json={
                "question": question,
                "pipeline": "agentic"
            },
            timeout=300.0
        )
        
        if response.status_code == 200:
            result = response.json()
            answer_data = result['result']
            
            # Build agentic trace
            agentic_trace = []
            for step in answer_data.get('agent_trace', {}).get('steps', []):
                agentic_trace.append({
                    "step": step.get('step'),
                    "agent": "agentic_orchestrator",
                    "action": step.get('tool'),
                    "details": step.get('result_summary', '')
                })
            
            return {
                "qid": qid,
                "question": question,
                "qtype": qtype,
                "answer": answer_data.get('answer', ''),
                "tokens_used": answer_data.get('metrics', {}).get('total_tokens', 0),
                "agentic_trace": agentic_trace,
                "confidence": answer_data.get('confidence', 0.0),
                "retrieval_steps": answer_data.get('metrics', {}).get('retrieval_steps', 0),
                "status": "success"
            }
        else:
            print(f"  ERROR: {response.status_code} - {response.text[:200]}")
            return {
                "qid": qid,
                "question": question,
                "qtype": qtype,
                "answer": "",
                "tokens_used": 0,
                "agentic_trace": [],
                "confidence": 0.0,
                "retrieval_steps": 0,
                "status": f"error_{response.status_code}",
                "error": response.text[:500]
            }
    except Exception as e:
        print(f"  EXCEPTION: {str(e)[:200]}")
        return {
            "qid": qid,
            "question": question,
            "qtype": qtype,
            "answer": "",
            "tokens_used": 0,
            "agentic_trace": [],
            "confidence": 0.0,
            "retrieval_steps": 0,
            "status": "exception",
            "error": str(e)[:500]
        }

async def run_evaluation():
    """Run evaluation on all hidden questions."""
    # Read questions
    questions = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    
    print(f"Loaded {len(questions)} questions from {INPUT_FILE}")
    
    # Run evaluation
    results = []
    async with httpx.AsyncClient(timeout=300.0) as client:
        for i, question_data in enumerate(questions):
            result = await evaluate_single_question(client, question_data, i)
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(0.5)
    
    # Build final artifact
    artifact = {
        "project": "GraphProbe AI",
        "pipeline": "Agentic GraphRAG",
        "total_questions": len(results),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "llm_provider": "groq",
        "llm_model": "llama-3.3-70b-versatile",
        "results": results
    }
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)
    
    print(f"\nEvaluation complete!")
    print(f"Total questions: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] != 'success')}")
    print(f"Results saved to: {OUTPUT_FILE}")
    
    return artifact

if __name__ == "__main__":
    artifact = asyncio.run(run_evaluation())
