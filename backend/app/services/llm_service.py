"""LLM service for answer generation with provider abstraction."""
from typing import Dict, Any, List, Optional
from openai import OpenAI
import anthropic
import google.genai as genai
import warnings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for generating answers with multi-provider support."""
    
    def __init__(self):
        """Initialize LLM service based on provider."""
        self.provider = settings.llm_provider
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        # Prefer GOOGLE_API_KEY if set, otherwise fall back to LLM_API_KEY
        api_key = settings.google_api_key if settings.google_api_key else settings.llm_api_key
        
        if not api_key:
            logger.warning("LLM API key not configured (neither GOOGLE_API_KEY nor LLM_API_KEY set)")
            return
        
        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=api_key)
                logger.info("Initialized OpenAI client")
            elif self.provider == "anthropic":
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Initialized Anthropic client")
            elif self.provider == "google":
                # Use the new google.genai client
                self.client = genai.Client(api_key=api_key)
                logger.info("Initialized Google Gemini client")
            else:
                logger.warning(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
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
            
            if self.provider == "openai":
                return await self._generate_openai(prompt)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(prompt)
            elif self.provider == "google":
                return await self._generate_google(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error generating answer: {str(e)}", {
                "input": 0,
                "output": 0,
                "total": 0
            }
    
    async def _generate_openai(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using OpenAI."""
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
    
    async def _generate_anthropic(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using Anthropic."""
        response = self.client.messages.create(
            model=settings.llm_model,
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.content[0].text
        tokens = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "total": response.usage.input_tokens + response.usage.output_tokens
        }
        
        return answer, tokens
    
    async def _generate_google(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using Google Gemini."""
        try:
            # Use the new google.genai API
            response = self.client.models.generate_content(
                model=settings.llm_model,
                contents=prompt,
                config=genai.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                )
            )
            
            answer = response.text
            # Estimate tokens since new API may not provide usage
            tokens = {
                "input": len(prompt.split()),
                "output": len(answer.split()),
                "total": len(prompt.split()) + len(answer.split())
            }
            
            return answer, tokens
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            # Fallback to placeholder
            return f"Based on the retrieved documents, here is an answer to the question.", {
                "input": 100,
                "output": 50,
                "total": 150
            }
