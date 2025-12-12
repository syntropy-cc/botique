"""
Idea generation module

Generates post ideas from articles using LLM.

Location: src/ideas/generator.py
"""

from pathlib import Path
from typing import Any, Dict

from ..core.config import IdeationConfig, POST_IDEATOR_TEMPLATE
from ..core.llm_client import HttpLLMClient
from ..core.utils import build_prompt_from_template, validate_llm_json_response


class IdeaGenerator:
    """
    Generate post ideas from articles.
    
    Uses the post_ideator prompt template to analyze articles and
    generate diverse, platform-specific post ideas.
    """
    
    def __init__(self, llm_client: HttpLLMClient):
        """
        Initialize idea generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    def generate_ideas(
        self,
        article_text: str,
        config: IdeationConfig,
    ) -> Dict[str, Any]:
        """
        Generate post ideas from article text.
        
        Args:
            article_text: Full article content
            config: Ideation configuration
        
        Returns:
            Dict with "article_summary" and "ideas" keys
        
        Raises:
            ValueError: If response structure is invalid
        """
        # Build prompt using to_prompt_dict() to get all template variables
        prompt_dict = config.to_prompt_dict()
        prompt_dict["article"] = article_text
        prompt = build_prompt_from_template(POST_IDEATOR_TEMPLATE, prompt_dict)
        
        # Call LLM
        raw_response = self.llm.generate(prompt)
        
        # Parse and validate response
        payload = validate_llm_json_response(
            raw_response=raw_response,
            top_level_keys=["article_summary", "ideas"],
            nested_validations={
                "article_summary": [
                    "title",
                    "main_thesis",
                    "key_insights",
                    "themes",
                    "keywords",
                    "main_message",
                ]
            },
            list_validations={
                "ideas": [
                    "id",
                    "platform",
                    "format",
                    "tone",
                    "persona",
                    "objective",
                    "angle",
                    "hook",
                    "narrative_arc",
                    "key_insights_used",
                    "estimated_slides",
                    "confidence",
                ]
            },
        )
        
        return payload