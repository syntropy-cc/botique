"""
Abstract LLM client interface.

Defines the interface that all LLM clients must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    All LLM client implementations must inherit from this class
    and implement the generate() method.
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        context: Optional[str] = None,
        prompt_key: Optional[str] = None,
        template: Optional[str] = None,
        prompt_id: Optional[str] = None,
    ) -> str:
        """
        Generate completion from prompt.
        
        Args:
            prompt: The full prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            context: Optional context identifier
            prompt_key: Optional prompt key identifier
            template: Optional raw template text
            prompt_id: Optional prompt ID for version tracking
            
        Returns:
            Assistant's response text
        """
        pass
