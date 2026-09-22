"""LLM service for answer generation."""
from typing import Dict, Any, List
from openai import OpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for generating answers."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.client = None
        if settings.llm_api_key:
            self.client = OpenAI(api_key=settings.llm_api_key)
        else:
            logger.warning("LLM API key not configured")
    
    async def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> tuple[str, Dict[str, int]]:
        """Generate answer based on question and context."""
        if not self.client:
            # Return placeholder if no API key
            return f"Based on the retrieved documents, here is an answer to: {question}", {
                "input": 100,
                "output": 50,
                "total": 150
            }
        
        try:
            # Prepare context from retrieved chunks
            context_text = "\n\n".join([
                f"Document {i+1}: {chunk.get('content', '')}"
                for i, chunk in enumerate(context)
            ])
            
            prompt = f"""Answer the following question based on the provided context.

Context:
{context_text}

Question: {question}

Provide a clear, well-supported answer with citations to the relevant documents."""
            
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            tokens = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            return answer, tokens
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error generating answer: {str(e)}", {
                "input": 0,
                "output": 0,
                "total": 0
            }
