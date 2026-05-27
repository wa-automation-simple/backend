"""OpenAI Integration for Chatbot Service"""
import asyncio
from typing import Optional, Dict, Any, List, AsyncGenerator
from openai import AsyncOpenAI
from ..core.config import settings


class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = "gpt-4"
        self.default_max_tokens = 1024
        self.default_temperature = 0.7
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Create a chat completion"""
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=max_tokens or self.default_max_tokens,
            temperature=temperature or self.default_temperature,
            stream=stream
        )
        
        if stream:
            return response
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Create a streaming chat completion"""
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=max_tokens or self.default_max_tokens,
            temperature=temperature or self.default_temperature,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embeddings(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Generate embeddings for text"""
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Moderate content for safety"""
        response = await self.client.moderations.create(input=text)
        return response.results[0]
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in text (approximate)"""
        import tiktoken
        
        model_name = model or self.default_model
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))


# Singleton instance
openai_client = OpenAIClient()
