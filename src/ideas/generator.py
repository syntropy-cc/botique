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
        save_raw_response: bool = True,
        raw_response_path: Path = None,
    ) -> Dict[str, Any]:
        """
        Generate post ideas from article text.
        
        Args:
            article_text: Full article content
            config: Ideation configuration
            save_raw_response: Whether to save raw LLM response even on validation errors
            raw_response_path: Optional path to save raw response (auto-generated if None)
        
        Returns:
            Dict with "article_summary" and "ideas" keys
        
        Raises:
            ValueError: If response structure is invalid
        """
        # Build prompt using to_prompt_dict() to get all template variables
        prompt_dict = config.to_prompt_dict()
        prompt_dict["article"] = article_text
        prompt = build_prompt_from_template(POST_IDEATOR_TEMPLATE, prompt_dict)
        
        # Call LLM - this will always log the call via HttpLLMClient
        raw_response = self.llm.generate(prompt)
        
        # Save raw response before validation (so it's saved even if validation fails)
        if save_raw_response and raw_response_path:
            raw_response_path.parent.mkdir(parents=True, exist_ok=True)
            raw_response_path.write_text(raw_response, encoding="utf-8")
        
        try:
            # Parse and validate response according to post_ideator.md template structure
            payload = validate_llm_json_response(
                raw_response=raw_response,
                top_level_keys=["article_summary", "ideas"],
                nested_validations={
                    "article_summary": [
                        "title",
                        "main_thesis",
                        "detected_tone",
                        "key_insights",
                        "themes",
                        "keywords",
                        "main_message",
                        "avoid_topics",
                    ]
                },
                list_validations={
                    "ideas": [
                        "id",
                        "platform",
                        "format",
                        "tone",
                        "persona",
                        "personality_traits",
                        "objective",
                        "angle",
                        "hook",
                        "narrative_arc",
                        "vocabulary_level",
                        "formality",
                        "key_insights_used",
                        "target_emotions",
                        "primary_emotion",
                        "secondary_emotions",
                        "avoid_emotions",
                        "value_proposition",
                        "article_context_for_idea",
                        "idea_explanation",
                        "estimated_slides",
                        "confidence",
                        "rationale",
                        "risks",
                        "keywords_to_emphasize",
                        "pain_points",
                        "desires",
                    ],
                    "article_summary.key_insights": [
                        "id",
                        "content",
                        "type",
                        "strength",
                        "source_quote",
                    ],
                },
            )
        except ValueError as e:
            # Re-raise but raw response is already saved and logged
            raise ValueError(
                f"Failed to validate LLM response: {e}. "
                f"Raw response saved to: {raw_response_path if save_raw_response and raw_response_path else 'N/A'}"
            ) from e
        
        # Validate minimum counts (template requirements)
        ideas = payload["ideas"]
        if len(ideas) == 0:
            raise ValueError("At least one idea must be generated")
        
        if len(ideas) < config.num_ideas_min:
            raise ValueError(
                f"Generated {len(ideas)} ideas, but minimum is {config.num_ideas_min}"
            )
        
        key_insights = payload["article_summary"]["key_insights"]
        if len(key_insights) == 0:
            raise ValueError("At least one key insight must be generated")
        
        if len(key_insights) < config.num_insights_min:
            raise ValueError(
                f"Generated {len(key_insights)} insights, but minimum is {config.num_insights_min}"
            )
        
        return payload