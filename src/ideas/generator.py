"""
Idea generation module

Generates post ideas from articles using LLM.

Location: src/ideas/generator.py
"""

from pathlib import Path
from typing import Any, Dict

from ..core.config import IdeationConfig, POST_IDEATOR_TEMPLATE
from ..core.llm_client import HttpLLMClient
from ..core.utils import render_template, parse_json_safely, validate_json_structure


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
        # Build prompt
        prompt = self.build_prompt(article_text, config)
        
        # Call LLM
        raw_response = self.llm.generate(prompt)
        
        # Parse and validate response
        payload = parse_json_safely(raw_response)
        self.validate_response(payload)
        
        return payload
    
    def build_prompt(
        self,
        article_text: str,
        config: IdeationConfig,
    ) -> str:
        """
        Build prompt from template and inputs.
        
        Args:
            article_text: Article content
            config: Ideation configuration
        
        Returns:
            Complete prompt string
        """
        context = {
            "ideation_config_json": config.to_json(),
            "article": article_text,
        }
        
        return render_template(POST_IDEATOR_TEMPLATE, context)
    
    def validate_response(self, payload: Dict[str, Any]) -> None:
        """
        Validate LLM response structure.
        
        Args:
            payload: Parsed JSON response
        
        Raises:
            ValueError: If structure is invalid
        """
        # Check top-level keys
        validate_json_structure(payload, ["article_summary", "ideas"])
        
        # Validate article_summary
        summary = payload["article_summary"]
        validate_json_structure(summary, [
            "title",
            "main_thesis",
            "key_insights",
            "themes",
            "keywords",
            "main_message",
        ])
        
        # Validate ideas
        ideas = payload["ideas"]
        if not isinstance(ideas, list):
            raise ValueError("'ideas' must be a list")
        
        if len(ideas) == 0:
            raise ValueError("No ideas generated")
        
        # Validate each idea
        required_idea_keys = [
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
        
        for idx, idea in enumerate(ideas):
            try:
                validate_json_structure(idea, required_idea_keys)
            except ValueError as exc:
                raise ValueError(f"Invalid idea at index {idx}: {exc}") from exc