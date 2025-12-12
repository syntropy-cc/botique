"""
LLM client module

HTTP client for OpenAI-compatible chat APIs (DeepSeek, OpenAI, Anthropic, etc.).

Location: src/core/llm_client.py
"""

import json
import os
import time
from typing import Optional, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .llm_logger import LLMLogger


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
        logger: Optional["LLMLogger"] = None,
    ) -> None:
        """
        Initialize LLM client.
        
        Args:
            api_key: API key (if None, reads from LLM_API_KEY env var)
            base_url: API base URL (default: DeepSeek)
            model: Model identifier
            timeout: Request timeout in seconds
            logger: Optional LLM logger for tracking calls
        
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
        self.logger = logger
    
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
        Automatically logs the call if logger is configured.
        
        Args:
            prompt: The full prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
        
        Returns:
            Assistant's response text
        
        Raises:
            RuntimeError: If API request fails or response format is invalid
        """
        # Start timing
        start_time = time.time()
        status = "success"
        error_msg = None
        content = None
        tokens_input = None
        tokens_output = None
        tokens_total = None
        
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
            try:
                response = requests.post(
                    self.chat_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )
            except requests.exceptions.Timeout:
                status = "timeout"
                error_msg = f"LLM API request timed out after {self.timeout} seconds"
                raise RuntimeError(error_msg)
            except requests.exceptions.RequestException as exc:
                status = "error"
                error_msg = f"LLM API request failed: {exc}"
                raise RuntimeError(error_msg) from exc
            
            # Check HTTP status
            if response.status_code != 200:
                status = "error"
                error_msg = f"LLM API error {response.status_code}: {response.text}"
                raise RuntimeError(error_msg)
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                status = "error"
                error_msg = f"Invalid JSON response from LLM API: {response.text}"
                raise RuntimeError(error_msg) from exc
            
            # Extract usage information if available
            usage = data.get("usage", {})
            if usage:
                tokens_input = usage.get("prompt_tokens")
                tokens_output = usage.get("completion_tokens")
                tokens_total = usage.get("total_tokens")
            
            # Extract content
            try:
                content = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as exc:
                status = "error"
                error_msg = f"Unexpected LLM response format. Response: {json.dumps(data, indent=2)}"
                raise RuntimeError(error_msg) from exc
            
            if not isinstance(content, str):
                status = "error"
                error_msg = f"Expected string content from LLM, got {type(content)}"
                raise RuntimeError(error_msg)
            
            content = content.strip()
            
        finally:
            # Always log the call, even if there was an error
            duration_ms = (time.time() - start_time) * 1000
            
            if self.logger:
                self.logger.log_call(
                    prompt=prompt,
                    response=content,
                    model=self.model,
                    base_url=self.base_url,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    duration_ms=duration_ms,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    tokens_total=tokens_total,
                    status=status,
                    error=error_msg,
                )
        
        return content
    
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
    def create_deepseek(
        api_key: Optional[str] = None,
        logger: Optional["LLMLogger"] = None,
    ) -> HttpLLMClient:
        """Create client configured for DeepSeek"""
        return HttpLLMClient(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            logger=logger,
        )
    
    @staticmethod
    def create_openai(
        api_key: Optional[str] = None,
        logger: Optional["LLMLogger"] = None,
    ) -> HttpLLMClient:
        """Create client configured for OpenAI"""
        return HttpLLMClient(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            model="gpt-4o",
            logger=logger,
        )
    
    @staticmethod
    def create_from_config(
        config: dict,
        logger: Optional["LLMLogger"] = None,
    ) -> HttpLLMClient:
        """Create client from configuration dictionary"""
        return HttpLLMClient(
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.deepseek.com/v1"),
            model=config.get("model", "deepseek-chat"),
            timeout=config.get("timeout", 60),
            logger=logger,
        )