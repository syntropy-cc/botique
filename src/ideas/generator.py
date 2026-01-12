"""
Idea generation module

Generates post ideas from articles using LLM.

Location: src/ideas/generator.py
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import IdeationConfig
# Try new location first, fallback to old location
try:
    from framework.llm.http_client import HttpLLMClient
    from framework.llm.prompt_helpers import get_or_register_prompt as get_latest_prompt
    from framework.llm.prompt_helpers import get_prompt_by_key_and_version
except ImportError:
    from ..core.llm_client import HttpLLMClient
    from ..core.prompt_registry import get_latest_prompt, get_prompt_by_key_and_version
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
        context: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate post ideas from article text.
        
        Args:
            article_text: Full article content
            config: Ideation configuration
            context: Optional context identifier (e.g., article_slug) for organizing saved responses
            prompt_version: Optional prompt version to use (e.g., "v1", "v2"). 
                          If None, uses the latest version from database.
        
        Returns:
            Dict with "article_summary" and "ideas" keys
        
        Raises:
            ValueError: If response structure is invalid or prompt not found in database
        """
        # Load prompt template from database
        prompt_key = "post_ideator"
        if prompt_version:
            prompt_data = get_prompt_by_key_and_version(prompt_key, prompt_version)
            if not prompt_data:
                raise ValueError(
                    f"Prompt '{prompt_key}' version '{prompt_version}' not found in database. "
                    f"Use a valid version or register the prompt first."
                )
        else:
            prompt_data = get_latest_prompt(prompt_key)
            if not prompt_data:
                raise ValueError(
                    f"Prompt '{prompt_key}' not found in database. "
                    f"Please register the prompt in the database first."
                )
        
        template_text = prompt_data["template"]
        
        # Build prompt using to_prompt_dict() to get all template variables
        prompt_dict = config.to_prompt_dict()
        prompt_dict["article"] = article_text
        
        # Build prompt from template string using simple replacement
        # (same method as render_template but for string instead of file)
        prompt = template_text
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Call LLM - raw response will be automatically saved by HttpLLMClient.generate()
        # if save_raw_responses is enabled (default: True)
        # Pass prompt_key and template for automatic prompt_id registration
        raw_response = self.llm.generate(
            prompt,
            context=context,
            prompt_key=prompt_key,
            template=template_text,
        )
        
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