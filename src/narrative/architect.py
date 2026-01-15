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
        # Save raw response path for debugging (initialize outside try to access in except)
        raw_response_path = None
        raw_response = None
        
        try:
            raw_response = self.llm.generate(
                prompt,
                context=context,
                temperature=0.2,
                max_tokens=DEEPSEEK_MAX_TOKENS,
                prompt_key=prompt_key,
                template=template_text,
            )
            
            # Log raw response for debugging (truncated if too long)
            import logging
            logger_debug = logging.getLogger(__name__)
            response_preview = raw_response[:500] if len(raw_response) > 500 else raw_response
            logger_debug.info(f"Narrative Architect raw response preview (first 500 chars): {response_preview}")
            
            # Also save to file explicitly for easier debugging (in addition to HttpLLMClient auto-save)
            try:
                from pathlib import Path
                from ..core.config import OUTPUT_DIR
                debug_dir = OUTPUT_DIR / context / "debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                raw_response_path = debug_dir / f"narrative_architect_response_{timestamp}.json"
                raw_response_path.write_text(raw_response, encoding="utf-8")
                logger_debug.info(f"Raw response saved to: {raw_response_path}")
            except Exception as save_error:
                logger_debug.warning(f"Could not save raw response to file: {save_error}")
            
            # Try to parse JSON to see structure before validation
            try:
                import json
                parsed_preview = json.loads(raw_response)
                logger_debug.info(f"Parsed JSON has keys: {list(parsed_preview.keys())}")
                if "slides" in parsed_preview and len(parsed_preview["slides"]) > 0:
                    first_slide_keys = list(parsed_preview["slides"][0].keys())
                    logger_debug.info(f"First slide has keys: {first_slide_keys}")
                    logger_debug.info(f"First slide content: {json.dumps(parsed_preview['slides'][0], indent=2)[:1000]}")
                else:
                    logger_debug.warning(f"No slides found in response or slides array is empty")
                    if "slides" in parsed_preview:
                        logger_debug.warning(f"Slides array length: {len(parsed_preview['slides'])}")
            except Exception as parse_error:
                logger_debug.warning(f"Could not parse JSON preview: {parse_error}")
        except Exception as llm_error:
            # If LLM call itself fails, propagate but include context
            import logging
            logger_debug = logging.getLogger(__name__)
            logger_debug.error(f"LLM call failed for {brief.post_id}: {llm_error}")
            raise
        
        # Validate response structure
        try:
            payload = self._validate_response(raw_response, brief)
        except ValueError as e:
            # Log detailed validation error including raw response snippet
            import logging
            logger_debug = logging.getLogger(__name__)
            error_msg = str(e)
            logger_debug.error(f"Narrative Architect validation failed for {brief.post_id}: {error_msg}")
            
            # Show saved file path if available
            if 'raw_response_path' in locals() and raw_response_path and raw_response_path.exists():
                logger_debug.error(f"Full raw response saved to: {raw_response_path}")
            
            # Try to show what we got instead of what we expected
            if 'raw_response' in locals():
                try:
                    import json
                    parsed_error = json.loads(raw_response)
                    logger_debug.error(f"Parsed response top-level keys: {list(parsed_error.keys())}")
                    
                    if "slides" in parsed_error:
                        if len(parsed_error["slides"]) > 0:
                            first_slide = parsed_error["slides"][0]
                            first_slide_keys = list(first_slide.keys())
                            logger_debug.error(f"First slide received keys: {first_slide_keys}")
                            logger_debug.error(f"Expected keys: template_type, value_subtype, purpose, target_emotions, copy_direction, visual_direction, key_elements, insights_referenced, transition_to_next")
                            logger_debug.error(f"First slide content: {json.dumps(first_slide, indent=2, ensure_ascii=False)}")
                            
                            # Show what's missing
                            expected_keys = ["template_type", "value_subtype", "purpose", "target_emotions", "copy_direction", "visual_direction", "key_elements", "insights_referenced", "transition_to_next"]
                            missing_keys = [key for key in expected_keys if key not in first_slide_keys]
                            if missing_keys:
                                logger_debug.error(f"Missing keys in first slide: {missing_keys}")
                        else:
                            logger_debug.error(f"Slides array is empty!")
                    else:
                        logger_debug.error(f"No 'slides' key found in response. Available keys: {list(parsed_error.keys())}")
                    
                    # Show raw response snippet for debugging
                    logger_debug.error(f"Raw response snippet (first 1500 chars): {raw_response[:1500]}")
                except Exception as parse_exc:
                    logger_debug.error(f"Could not parse response for error details: {parse_exc}")
                    logger_debug.error(f"Raw response (first 1000 chars): {raw_response[:1000]}")
            
            # Log validation error using SQL logger if available
            if self.logger:
                try:
                    # Get trace_id from context if available
                    trace_id = getattr(self.logger, 'current_trace_id', None) or getattr(self.logger, 'session_id', None)
                    if trace_id:
                        # Include raw response snippet in metadata
                        response_snippet = raw_response[:1000] if len(raw_response) > 1000 else raw_response
                        self.logger.log_step_event(
                            trace_id=trace_id,
                            name=f"narrative_architect_validation_error_{brief.post_id}",
                            input_text=f"Validating narrative structure for {brief.post_id}",
                            output_text=response_snippet,
                            error=error_msg,
                            status="error",
                            type="postprocess",
                            metadata={
                                "post_id": brief.post_id,
                                "idea_id": brief.idea_id,
                                "platform": brief.platform,
                                "format": brief.format,
                                "error_detail": error_msg,
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
                    template_type=slide.get("template_type", ""),
                    value_subtype=slide.get("value_subtype"),
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
                                    "template_type": slide.get("template_type"),
                                    "value_subtype": slide.get("value_subtype"),
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
        # Structural validation - strict validation requiring template_type and value_subtype
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
                    "template_type",
                    "value_subtype",
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
        
        # Ensure optional fields have defaults if missing (but structure validation should catch required fields)
        slides = payload.get("slides", [])
        for idx, slide in enumerate(slides):
            # Ensure lists are properly initialized
            if "key_elements" not in slide:
                slide["key_elements"] = []
            if "insights_referenced" not in slide:
                slide["insights_referenced"] = []
            if "target_emotions" not in slide:
                slide["target_emotions"] = []
            # transition_to_next is optional (can be null for last slide)
            if "transition_to_next" not in slide:
                slide["transition_to_next"] = None
        
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
        if slides and slides[0].get("template_type") != "hook":
            raise ValueError("First slide must have template_type='hook'")
        
        # Validate last slide is cta if required
        if "professional_cta" in brief.required_elements or "cta" in brief.required_elements:
            if not slides or slides[-1].get("template_type") != "cta":
                raise ValueError(
                    "Last slide must have template_type='cta' when professional_cta or cta is required"
                )
        
        # Validate template_type and value_subtype for each slide
        for idx, slide in enumerate(slides):
            template_type = slide.get("template_type")
            value_subtype = slide.get("value_subtype")
            
            # Validate template_type is one of the valid types
            valid_template_types = {"hook", "transition", "value", "cta"}
            if template_type not in valid_template_types:
                raise ValueError(
                    f"Slide {idx + 1}: Invalid template_type '{template_type}'. "
                    f"Must be one of {valid_template_types}"
                )
            
            # Validate value_subtype rules
            if template_type == "value":
                # Value slides must have value_subtype specified
                valid_value_subtypes = {"data", "insight", "solution", "example"}
                if not value_subtype:
                    raise ValueError(
                        f"Slide {idx + 1}: template_type='value' requires value_subtype "
                        f"(must be one of {valid_value_subtypes})"
                    )
                if value_subtype not in valid_value_subtypes:
                    raise ValueError(
                        f"Slide {idx + 1}: Invalid value_subtype '{value_subtype}' for template_type='value'. "
                        f"Must be one of {valid_value_subtypes}"
                    )
            else:
                # Hook, transition, and cta slides must have value_subtype = null
                if value_subtype is not None:
                    raise ValueError(
                        f"Slide {idx + 1}: template_type='{template_type}' must have value_subtype=null, "
                        f"got '{value_subtype}'"
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

