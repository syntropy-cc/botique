"""
LLM client module

HTTP client for OpenAI-compatible chat APIs (DeepSeek, OpenAI, Anthropic, etc.).

Location: src/core/llm_client.py
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
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
        save_raw_responses: bool = True,
        raw_responses_dir: Optional[Path] = None,
    ) -> None:
        """
        Initialize LLM client.
        
        Args:
            api_key: API key (if None, reads from LLM_API_KEY env var)
            base_url: API base URL (default: DeepSeek)
            model: Model identifier
            timeout: Request timeout in seconds
            logger: Optional LLM logger for tracking calls
            save_raw_responses: Whether to automatically save raw responses (default: True)
            raw_responses_dir: Directory to save raw responses (default: output/{context}/debug/)
        
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
        self.save_raw_responses = save_raw_responses
        self.raw_responses_dir = raw_responses_dir
    
    @property
    def chat_url(self) -> str:
        """Get the chat completions endpoint URL"""
        return f"{self.base_url}/chat/completions"
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 8048,
        temperature: float = 0.2,
        context: Optional[str] = None,
        save_raw: Optional[bool] = None,
        prompt_key: Optional[str] = None,
        template: Optional[str] = None,
        prompt_id: Optional[str] = None,
    ) -> str:
        """
        Generate completion from prompt.
        
        Sends a single user message and returns the assistant's response.
        Automatically logs the call if logger is configured.
        Optionally saves raw response to file for debugging.
        
        If prompt_key and template are provided, automatically registers/retrieves
        the prompt_id for version tracking. If prompt_id is provided directly,
        it will be used instead.
        
        Args:
            prompt: The full prompt text (after variable substitution)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            context: Optional context identifier (e.g., article_slug) for organizing saved responses
            save_raw: Whether to save raw response (overrides instance default if provided)
            prompt_key: Optional prompt key identifier (e.g., "post_ideator")
            template: Optional raw template text (before variable substitution)
            prompt_id: Optional prompt ID (if provided, prompt_key and template are ignored)
        
        Returns:
            Assistant's response text
        
        Raises:
            RuntimeError: If API request fails or response format is invalid
        """
        # Resolve prompt_id if prompt_key and template are provided
        resolved_prompt_id = prompt_id
        if not resolved_prompt_id and prompt_key and template:
            try:
                from .prompt_helpers import get_or_register_prompt
                resolved_prompt_id, _ = get_or_register_prompt(
                    prompt_key=prompt_key,
                    template=template,
                )
            except Exception as e:
                # Don't fail the call if prompt registration fails
                # Just log a warning (could be logged to logger if available)
                pass
        
        # Start timing
        start_time = time.time()
        status = "success"
        error_msg = None
        content = None
        raw_response_text = None  # Capture raw response for logging
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
            
            # Capture raw response text BEFORE checking status (for logging/debugging)
            raw_response_text = response.text
            
            # Check HTTP status
            if response.status_code != 200:
                status = "error"
                error_msg = f"LLM API error {response.status_code}: {raw_response_text[:500]}"
                raise RuntimeError(error_msg)
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                status = "error"
                error_msg = f"Invalid JSON response from LLM API: {raw_response_text[:500]}"
                # Even if JSON parsing fails, try to extract content from raw text
                # This might be the actual LLM response wrapped in markdown or other format
                content = raw_response_text
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
                error_msg = f"Unexpected LLM response format. Response: {json.dumps(data, indent=2)[:500]}"
                # Fallback to raw response text if structure is unexpected
                content = raw_response_text
                raise RuntimeError(error_msg) from exc
            
            if not isinstance(content, str):
                status = "error"
                error_msg = f"Expected string content from LLM, got {type(content)}"
                content = str(content) if content else raw_response_text
            
            content = content.strip()
            
        finally:
            # Always log the call, even if there was an error
            # Use raw_response_text if content extraction failed
            duration_ms = (time.time() - start_time) * 1000
            log_response = content if content else (raw_response_text if 'raw_response_text' in locals() else None)
            
            # Save raw response if enabled (even on errors)
            should_save_raw = save_raw if save_raw is not None else self.save_raw_responses
            if should_save_raw and 'raw_response_text' in locals() and raw_response_text:
                self._save_raw_response(
                    raw_response_text,
                    context=context,
                    status=status,
                    error=error_msg,
                )
            
            if self.logger:
                self.logger.log_call(
                    prompt=prompt,
                    response=log_response,
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
                    prompt_id=resolved_prompt_id,
                )
        
        return content
    
    def _save_raw_response(
        self,
        raw_response: str,
        context: Optional[str] = None,
        status: str = "success",
        error: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Save raw LLM response to file for debugging.
        
        Args:
            raw_response: Raw response text to save
            context: Optional context identifier (e.g., article_slug)
            status: Call status (success/error/timeout)
            error: Error message if any
        
        Returns:
            Path to saved file, or None if saving was disabled/failed
        """
        try:
            # Determine save directory
            if self.raw_responses_dir:
                save_dir = self.raw_responses_dir
            elif context:
                from .config import OUTPUT_DIR
                save_dir = OUTPUT_DIR / context / "debug"
            else:
                from .config import OUTPUT_DIR
                save_dir = OUTPUT_DIR / "debug"
            
            # Create directory
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
            filename = f"raw_response_{timestamp}.txt"
            if status != "success":
                filename = f"raw_response_{status}_{timestamp}.txt"
            
            # Save file
            file_path = save_dir / filename
            file_path.write_text(raw_response, encoding="utf-8")
            
            return file_path
        except Exception as e:
            # Don't fail the main operation if saving fails
            # Could log this to a separate error log if needed
            return None
    
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