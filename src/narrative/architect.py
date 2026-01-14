"""
Narrative Architect module

Generates detailed slide-by-slide narrative structures from coherence briefs.

Location: src/narrative/architect.py
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..coherence.brief import CoherenceBrief
from ..core.config import MAX_SLIDES_PER_POST, MIN_SLIDES_PER_POST, DEEPSEEK_MAX_TOKENS
from ..core.llm_client import HttpLLMClient
from ..core.prompt_registry import get_latest_prompt, get_prompt_by_key_and_version
from ..core.utils import validate_llm_json_response

if TYPE_CHECKING:
    from ..core.llm_logger import LLMLogger


def build_insights_block(brief: CoherenceBrief) -> str:
    """
    Build formatted insights block for prompt injection.
    
    Formats all insights from key_insights_content that are referenced
    in key_insights_used into a single block string.
    
    Args:
        brief: CoherenceBrief with insights to format
    
    Returns:
        Formatted string block with all insights
    """
    used_ids = set(brief.key_insights_used or [])
    lines: List[str] = []
    
    for insight in brief.key_insights_content:
        if used_ids and insight.get("id") not in used_ids:
            continue
        
        insight_id = insight.get("id", "unknown")
        content = insight.get("content", "")
        insight_type = insight.get("type", "unknown")
        strength = insight.get("strength", "N/A")
        source_quote = insight.get("source_quote", "")
        
        lines.append(
            f"- ID: {insight_id}\n"
            f"  Content: {content}\n"
            f"  Type: {insight_type}\n"
            f"  Strength: {strength} (1-10 scale)\n"
            f"  Source Quote: {source_quote}"
        )
    
    return "\n".join(lines) if lines else "- (no insights provided)"


class NarrativeArchitect:
    """
    Generate narrative structures from coherence briefs.
    
    Transforms a high-level coherence brief into a detailed slide-by-slide
    narrative structure that guides copywriters and visual composers.
    """
    
    def __init__(
        self,
        llm_client: HttpLLMClient,
        logger: Optional["LLMLogger"] = None,
    ) -> None:
        """
        Initialize Narrative Architect.
        
        Args:
            llm_client: LLM client for generation
            logger: Optional LLM logger for tracking calls and steps
        """
        self.llm = llm_client
        self.logger = logger
    
    def generate_structure(
        self,
        brief: CoherenceBrief,
        context: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate narrative structure for a post based on its coherence brief.
        
        Args:
            brief: CoherenceBrief with all necessary context
            context: Optional context identifier (e.g., post_id) for organizing logs
            prompt_version: Optional prompt version to use (e.g., "v1", "v2"). 
                          If None, uses the latest version from database.
        
        Returns:
            Dict with narrative structure: pacing, transition_style, arc_refined, slides, rationale
        
        Raises:
            ValueError: If brief is invalid, response validation fails, or prompt not found in database
        """
        context = context or brief.post_id
        
        # Load prompt template from database
        prompt_key = "narrative_architect"
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
        
        # Build prompt dictionary from brief fields
        prompt_dict = self._build_prompt_dict(brief)
        
        # Build prompt from template string using simple replacement
        # (same method as render_template but for string instead of file)
        prompt = template_text
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Call LLM (logging is handled automatically by HttpLLMClient if logger is provided)
        raw_response = self.llm.generate(
            prompt,
            context=context,
            temperature=0.2,
            max_tokens=DEEPSEEK_MAX_TOKENS,
            prompt_key=prompt_key,
            template=template_text,
        )
        
        # Validate response structure
        try:
            payload = self._validate_response(raw_response, brief)
        except ValueError as e:
            # Log validation error using SQL logger if available
            if self.logger:
                try:
                    # Get trace_id from context if available
                    trace_id = getattr(self.logger, 'current_trace_id', None) or getattr(self.logger, 'session_id', None)
                    if trace_id:
                        self.logger.log_step_event(
                            trace_id=trace_id,
                            name=f"narrative_architect_validation_error_{brief.post_id}",
                            input_text=f"Validating narrative structure for {brief.post_id}",
                            output_text=None,
                            error=str(e),
                            status="error",
                            type="postprocess",
                            metadata={
                                "post_id": brief.post_id,
                                "idea_id": brief.idea_id,
                                "platform": brief.platform,
                                "format": brief.format,
                            },
                        )
                except Exception:
                    # Don't fail the main operation if logging fails
                    pass
            raise
        
        # Post-process: Select templates for each slide using Template Selector
        from ..templates.selector import TemplateSelector
        template_selector = TemplateSelector()
        
        for slide in payload["slides"]:
            try:
                template_id, template_justification, template_confidence = template_selector.select_template(
                    module_type=slide.get("module_type", ""),
                    purpose=slide.get("purpose", ""),
                    copy_direction=slide.get("copy_direction", ""),
                    key_elements=slide.get("key_elements", []),
                    persona=brief.persona,
                    tone=brief.tone,
                    platform=brief.platform,
                )
                slide["template_id"] = template_id
                slide["template_justification"] = template_justification
                slide["template_confidence"] = template_confidence
            except Exception as e:
                # If template selection fails, log warning but continue
                # This allows the pipeline to continue even if template selection fails
                if self.logger:
                    try:
                        trace_id = getattr(self.logger, 'current_trace_id', None) or getattr(self.logger, 'session_id', None)
                        if trace_id:
                            self.logger.log_step_event(
                                trace_id=trace_id,
                                name=f"template_selector_warning_{brief.post_id}",
                                input_text=f"Template selection for slide {slide.get('slide_number', 'unknown')}",
                                output_text=None,
                                error=str(e),
                                status="warning",
                                type="postprocess",
                                metadata={
                                    "post_id": brief.post_id,
                                    "slide_number": slide.get("slide_number"),
                                    "module_type": slide.get("module_type"),
                                },
                            )
                    except Exception:
                        pass
                # Continue without template_id if selection fails
                slide["template_id"] = None
                slide["template_justification"] = None
                slide["template_confidence"] = 0.0
        
        # Build normalized narrative structure
        # Include all fields from payload for brief enrichment
        narrative_structure = {
            "pacing": payload["narrative_pacing"],
            "transition_style": payload["transition_style"],
            "arc_refined": payload["arc_refined"],
            "slides": payload["slides"],
            "rationale": payload["rationale"],
        }
        
        # Enrich coherence brief
        brief.enrich_from_narrative_structure(narrative_structure)
        
        # Log success using SQL logger if available
        if self.logger:
            try:
                # Get trace_id from context if available
                trace_id = getattr(self.logger, 'current_trace_id', None) or getattr(self.logger, 'session_id', None)
                if trace_id:
                    self.logger.log_step_event(
                        trace_id=trace_id,
                        name=f"narrative_architect_success_{brief.post_id}",
                        input_text=f"Generating narrative structure for {brief.post_id}",
                        output_text=f"Narrative structure generated: {len(payload['slides'])} slides, {payload['narrative_pacing']} pacing",
                        output_obj={
                            "post_id": brief.post_id,
                            "num_slides": len(payload["slides"]),
                            "pacing": payload["narrative_pacing"],
                            "transition_style": payload["transition_style"],
                            "insights_referenced": self._count_insights_referenced(payload["slides"]),
                        },
                        status="success",
                        type="postprocess",
                        metadata={
                            "post_id": brief.post_id,
                            "idea_id": brief.idea_id,
                            "platform": brief.platform,
                            "format": brief.format,
                            "num_slides": len(payload["slides"]),
                            "pacing": payload["narrative_pacing"],
                            "transition_style": payload["transition_style"],
                        },
                    )
            except Exception:
                # Don't fail the main operation if logging fails
                pass
        
        # Return full payload (including rationale)
        return payload
    
    def _build_prompt_dict(self, brief: CoherenceBrief) -> Dict[str, Any]:
        """
        Build prompt dictionary from coherence brief fields.
        
        Maps all necessary brief attributes to template placeholders.
        
        Args:
            brief: CoherenceBrief to extract fields from
        
        Returns:
            Dictionary mapping template placeholders to values
        """
        return {
            # Narrative foundation
            "objective": brief.objective,
            "narrative_arc": brief.narrative_arc,
            "estimated_slides": str(brief.estimated_slides),
            "hook": brief.hook,
            
            # Content essence
            "angle": brief.angle,
            "main_message": brief.main_message,
            "value_proposition": brief.value_proposition,
            "keywords_to_emphasize": ", ".join(brief.keywords_to_emphasize),
            "themes": ", ".join(brief.themes),
            
            # Source material
            "article_context": brief.article_context,
            "key_insights_used": ", ".join(brief.key_insights_used),
            "key_insights_content_block": build_insights_block(brief),
            
            # Emotional journey
            "primary_emotion": brief.primary_emotion,
            "secondary_emotions": ", ".join(brief.secondary_emotions),
            "avoid_emotions": ", ".join(brief.avoid_emotions),
            "target_emotions": ", ".join(brief.target_emotions),
            
            # Audience understanding
            "persona": brief.persona,
            "pain_points": ", ".join(brief.pain_points),
            "desires": ", ".join(brief.desires),
            
            # Voice & platform
            "platform": brief.platform,
            "format": brief.format,
            "tone": brief.tone,
            "personality_traits": ", ".join(brief.personality_traits),
            "vocabulary_level": brief.vocabulary_level,
            "formality": brief.formality,
            
            # Constraints
            "avoid_topics": ", ".join(brief.avoid_topics),
        }
    
    def _validate_response(
        self,
        raw_response: str,
        brief: CoherenceBrief,
    ) -> Dict[str, Any]:
        """
        Validate LLM response structure and semantics.
        
        Args:
            raw_response: Raw JSON response from LLM
            brief: CoherenceBrief for semantic validation
        
        Returns:
            Validated and parsed payload
        
        Raises:
            ValueError: If validation fails
        """
        # Structural validation
        payload = validate_llm_json_response(
            raw_response=raw_response,
            top_level_keys=[
                "narrative_pacing",
                "transition_style",
                "arc_refined",
                "slides",
                "rationale",
            ],
            list_validations={
                "slides": [
                    "slide_number",
                    "module_type",
                    "purpose",
                    "target_emotions",
                    "copy_direction",
                    "visual_direction",
                    "key_elements",
                    "insights_referenced",
                    "transition_to_next",
                ],
            },
        )
        
        # Validate copy_direction and visual_direction are non-empty strings
        for idx, slide in enumerate(payload["slides"]):
            copy_direction = slide.get("copy_direction", "")
            visual_direction = slide.get("visual_direction", "")
            
            if not copy_direction or not isinstance(copy_direction, str):
                warnings.warn(
                    f"Slide {idx + 1}: 'copy_direction' is missing or invalid (expected non-empty string). Continuing anyway.",
                    UserWarning,
                    stacklevel=2
                )
                # Set default to avoid downstream errors
                slide["copy_direction"] = "Write engaging copy that aligns with the slide's purpose and narrative arc."
            
            if not visual_direction or not isinstance(visual_direction, str):
                warnings.warn(
                    f"Slide {idx + 1}: 'visual_direction' is missing or invalid (expected non-empty string). Continuing anyway.",
                    UserWarning,
                    stacklevel=2
                )
                # Set default to avoid downstream errors
                slide["visual_direction"] = "Create a visual composition that supports the narrative and emotional tone of this slide."
            
            # Validate minimum length (50-300 words as specified in prompt) - warn but don't fail
            copy_words = len(copy_direction.split()) if copy_direction else 0
            visual_words = len(visual_direction.split()) if visual_direction else 0
            
            if copy_words < 50:
                warnings.warn(
                    f"Slide {idx + 1}: 'copy_direction' is shorter than recommended (got {copy_words} words, recommended: 50-300). Continuing anyway.",
                    UserWarning,
                    stacklevel=2
                )
            
            if visual_words < 50:
                warnings.warn(
                    f"Slide {idx + 1}: 'visual_direction' is shorter than recommended (got {visual_words} words, recommended: 50-300). Continuing anyway.",
                    UserWarning,
                    stacklevel=2
                )
        
        # Semantic validation
        self._validate_semantics(payload, brief)
        
        return payload
    
    def _validate_semantics(
        self,
        payload: Dict[str, Any],
        brief: CoherenceBrief,
    ) -> None:
        """
        Perform semantic validation on narrative structure.
        
        Args:
            payload: Parsed JSON payload
            brief: CoherenceBrief for context
        
        Raises:
            ValueError: If semantic validation fails
        """
        # Validate pacing
        valid_pacing = {"fast", "moderate", "deliberate"}
        pacing = payload.get("narrative_pacing")
        if pacing not in valid_pacing:
            raise ValueError(
                f"Invalid narrative_pacing: '{pacing}'. Must be one of {valid_pacing}"
            )
        
        # Validate transition style
        valid_transitions = {"abrupt", "smooth", "dramatic", "conversational"}
        transition_style = payload.get("transition_style")
        if transition_style not in valid_transitions:
            raise ValueError(
                f"Invalid transition_style: '{transition_style}'. "
                f"Must be one of {valid_transitions}"
            )
        
        # Validate slide count
        slides = payload.get("slides", [])
        num_slides = len(slides)
        
        if brief.format == "single_image":
            if num_slides != 1:
                raise ValueError(
                    f"single_image format requires exactly 1 slide, got {num_slides}"
                )
        else:
            if num_slides < MIN_SLIDES_PER_POST or num_slides > MAX_SLIDES_PER_POST:
                raise ValueError(
                    f"Slide count {num_slides} must be between "
                    f"{MIN_SLIDES_PER_POST} and {MAX_SLIDES_PER_POST} for {brief.format} format"
                )
        
        # Validate first slide is hook
        if slides and slides[0].get("module_type") != "hook":
            raise ValueError("First slide must have module_type='hook'")
        
        # Validate last slide is cta if required
        if "professional_cta" in brief.required_elements:
            if not slides or slides[-1].get("module_type") != "cta":
                raise ValueError(
                    "Last slide must have module_type='cta' when professional_cta is required"
                )
        
        # Validate all insights are referenced
        insights_used = set(brief.key_insights_used or [])
        if insights_used:
            insights_referenced = set()
            for slide in slides:
                insights_referenced.update(slide.get("insights_referenced", []))
            
            missing = insights_used - insights_referenced
            if missing:
                raise ValueError(
                    f"Insights not referenced in any slide: {sorted(missing)}"
                )
        
        # Validate no avoid_emotions appear in target_emotions
        avoid_emotions = set(brief.avoid_emotions or [])
        if avoid_emotions:
            for idx, slide in enumerate(slides):
                target_emotions = slide.get("target_emotions", [])
                if not isinstance(target_emotions, list):
                    continue
                
                overlap = avoid_emotions & set(target_emotions)
                if overlap:
                    raise ValueError(
                        f"Slide {idx + 1} uses avoid_emotions: {sorted(overlap)}"
                    )
    
    def _count_insights_referenced(self, slides: List[Dict[str, Any]]) -> int:
        """
        Count unique insights referenced across all slides.
        
        Args:
            slides: List of slide dictionaries
        
        Returns:
            Number of unique insight IDs referenced
        """
        referenced = set()
        for slide in slides:
            referenced.update(slide.get("insights_referenced", []))
        return len(referenced)

