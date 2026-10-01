"""Test Groq integration with a single hidden evaluation question."""
import asyncio
import httpx
import json

async def test_single_question():
    """Test a single hidden evaluation question."""
    question = "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://localhost:8000/api/investigate",
            json={
                "question": question,
                "pipeline": "agentic"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("=== SUCCESS ===")
            print(f"Question: {result['result']['question']}")
            answer = result['result']['answer']
            print(f"Answer length: {len(answer)}")
            print(f"Answer preview: {answer[:100]}")
            print(f"Confidence: {result['result']['confidence']}")
            print(f"Total Tokens: {result['result']['metrics']['total_tokens']}")
            print(f"Retrieval Steps: {result['result']['metrics']['retrieval_steps']}")
            print(f"\nAgent Trace:")
            for step in result['result']['agent_trace']['steps']:
                print(f"  Step {step['step']}: {step['tool']} - {step['result_summary']}")
            
            # Check for placeholder text
            if "Based on the retrieved documents, here is an answer to the question" in answer:
                print("\n[X] ERROR: Placeholder answer detected!")
                return False
            elif not answer or answer.strip() == "":
                print("\n[X] ERROR: Empty answer detected!")
                return False
            else:
                print("\n[OK] Genuine answer generated!")
                return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False

if __name__ == "__main__":
    result = asyncio.run(test_single_question())
    if result:
        print("\n[OK] Test PASSED")
    else:
        print("\n[X] Test FAILED")
