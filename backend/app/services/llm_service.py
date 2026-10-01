"""LLM service for answer generation with provider abstraction."""
from typing import Dict, Any, List, Optional
from openai import OpenAI
import anthropic
from groq import Groq
import warnings
import asyncio
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
        # Prefer provider-specific API keys
        if self.provider == "groq":
            api_key = settings.groq_api_key
        else:
            api_key = settings.llm_api_key

        if not api_key:
            logger.warning(f"LLM API key not configured for provider {self.provider}")
            return

        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=api_key)
                logger.info("Initialized OpenAI client")
            elif self.provider == "anthropic":
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Initialized Anthropic client")
            elif self.provider == "groq":
                self.client = Groq(api_key=api_key)
                logger.info("Initialized Groq client")
            else:
                logger.warning(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None

    async def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> tuple[str, Dict[str, int]]:
        """Generate answer based on question and context."""
        if not self.client:
            raise ValueError(f"LLM client not initialized for provider {self.provider}. Please check API key configuration.")
        
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
            elif self.provider == "groq":
                return await self._generate_groq(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise e
    
    async def _generate_openai(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using OpenAI with timeout protection."""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                ),
                timeout=settings.operation_timeout_seconds
            )
            
            answer = response.choices[0].message.content
            tokens = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            return answer, tokens
        except asyncio.TimeoutError:
            logger.error(f"OpenAI generation timed out after {settings.operation_timeout_seconds}s")
            return f"LLM generation timed out after {settings.operation_timeout_seconds}s", {
                "input": 0,
                "output": 0,
                "total": 0
            }
    
    async def _generate_anthropic(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using Anthropic with timeout protection."""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=settings.llm_model,
                    max_tokens=500,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                ),
                timeout=settings.operation_timeout_seconds
            )

            answer = response.content[0].text
            tokens = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens
            }

            return answer, tokens
        except asyncio.TimeoutError:
            logger.error(f"Anthropic generation timed out after {settings.operation_timeout_seconds}s")
            return f"LLM generation timed out after {settings.operation_timeout_seconds}s", {
                "input": 0,
                "output": 0,
                "total": 0
            }

    async def _generate_groq(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Generate answer using Groq with timeout protection."""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always provide a complete answer in the content field."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.5
                ),
                timeout=settings.operation_timeout_seconds
            )
            
            # Extract answer from response
            message = response.choices[0].message
            answer = message.content if message.content else ""
            
            logger.info(f"Groq response answer length: {len(answer) if answer else 0}")
            logger.info(f"Groq response answer preview: {answer[:200] if answer else 'EMPTY'}")
            
            # For GPT-OSS models with reasoning, the content field might be empty
            # In this case, we need to extract the actual answer from the reasoning
            if not answer or answer.strip() == "":
                if hasattr(message, 'reasoning') and message.reasoning:
                    logger.warning(f"Content field is empty, using reasoning field (length: {len(message.reasoning)})")
                    # Extract the final answer from reasoning - look for patterns like "So the answer is:" or just use the last part
                    reasoning = message.reasoning
                    # Try to extract a concise answer from the reasoning
                    lines = reasoning.split('\n')
                    # Look for conclusion sentences
                    for line in reversed(lines):
                        if 'answer' in line.lower() or 'result' in line.lower() or 'conclusion' in line.lower():
                            answer = line.strip()
                            break
                    if not answer:
                        # Use the last non-empty line as the answer
                        for line in reversed(lines):
                            if line.strip():
                                answer = line.strip()
                                break
                    # Limit answer length
                    if answer and len(answer) > 500:
                        answer = answer[:500] + "..."
            
            if not answer or answer.strip() == "":
                logger.warning("Groq returned empty answer after all extraction attempts")
                raise ValueError("LLM returned empty answer")
            
            tokens = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            return answer, tokens
        except asyncio.TimeoutError:
            logger.error(f"Groq generation timed out after {settings.operation_timeout_seconds}s")
            raise TimeoutError(f"Groq generation timed out after {settings.operation_timeout_seconds}s")
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise e
