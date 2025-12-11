"""
LLM client module

HTTP client for OpenAI-compatible chat APIs (DeepSeek, OpenAI, Anthropic, etc.).

Location: src/core/llm_client.py
"""

import json
import os
from typing import Optional

import requests


class HttpLLMClient:
    """
    HTTP client for OpenAI-compatible chat completion APIs.
    
    Supports any API that implements the OpenAI /v1/chat/completions format,
    including DeepSeek, OpenAI, and others.
    
    Features:
    - Single message prompts (user → assistant)
    - Configurable temperature and max tokens
    - Error handling with detailed messages
    - Timeout support
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        timeout: int = 60,
    ) -> None:
        """
        Initialize LLM client.
        
        Args:
            api_key: API key (if None, reads from LLM_API_KEY env var)
            base_url: API base URL (default: DeepSeek)
            model: Model identifier
            timeout: Request timeout in seconds
        
        Raises:
            RuntimeError: If API key is not provided or found in environment
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError(
                "API key not found. Set LLM_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
    
    @property
    def chat_url(self) -> str:
        """Get the chat completions endpoint URL"""
        return f"{self.base_url}/chat/completions"
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate completion from prompt.
        
        Sends a single user message and returns the assistant's response.
        
        Args:
            prompt: The full prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
        
        Returns:
            Assistant's response text
        
        Raises:
            RuntimeError: If API request fails or response format is invalid
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        try:
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"LLM API request timed out after {self.timeout} seconds"
            )
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"LLM API request failed: {exc}") from exc
        
        # Check HTTP status
        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error {response.status_code}: {response.text}"
            )
        
        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid JSON response from LLM API: {response.text}"
            ) from exc
        
        # Extract content
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected LLM response format. Response: {json.dumps(data, indent=2)}"
            ) from exc
        
        if not isinstance(content, str):
            raise RuntimeError(
                f"Expected string content from LLM, got {type(content)}"
            )
        
        return content.strip()
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"HttpLLMClient(model='{self.model}', "
            f"base_url='{self.base_url}', "
            f"timeout={self.timeout})"
        )


class LLMClientFactory:
    """
    Factory for creating LLM clients with different configurations.
    
    Useful for testing and switching between providers.
    """
    
    @staticmethod
    def create_deepseek(api_key: Optional[str] = None) -> HttpLLMClient:
        """Create client configured for DeepSeek"""
        return HttpLLMClient(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )
    
    @staticmethod
    def create_openai(api_key: Optional[str] = None) -> HttpLLMClient:
        """Create client configured for OpenAI"""
        return HttpLLMClient(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            model="gpt-4o",
        )
    
    @staticmethod
    def create_from_config(config: dict) -> HttpLLMClient:
        """Create client from configuration dictionary"""
        return HttpLLMClient(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.deepseek.com/v1"),
            model=config.get("model", "deepseek-chat"),
            timeout=config.get("timeout", 60),
        )