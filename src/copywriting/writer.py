"""
Copywriter module

Generates text content for slides with emphasis guidance.

Location: src/copywriting/writer.py
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..coherence.brief import CoherenceBrief
from ..core.llm_client import HttpLLMClient
from ..core.prompt_registry import get_latest_prompt, get_prompt_by_key_and_version
from ..core.utils import validate_llm_json_response

if TYPE_CHECKING:
    from ..core.llm_logger import LLMLogger


def _build_template_context_block(template) -> str:
    """
    Build detailed template context block for a specific slide.
    
    Formats all template attributes for display in the copywriter prompt.
    
    Args:
        template: TextualTemplate instance
    
    Returns:
        Formatted string block with template details
    """
    lines = []
    lines.append("    Template Context:")
    
    # Detailed description
    if template.detailed_description:
        lines.append(f"      - Detailed Description: {template.detailed_description}")
    
    # Structure (emphasize it's conceptual)
    if template.structure:
        lines.append(f"      - Structure: `{template.structure}` (conceptual guide, not literal text)")
    
    # Length range
    if template.length_range:
        lines.append(f"      - Length: {template.length_range[0]}-{template.length_range[1]} characters")
    
    # Tone
    if template.tone:
        lines.append(f"      - Tone: {template.tone}")
    
    # Creative guidance
    if template.creative_guidance:
        lines.append(f"      - Creative Guidance: {template.creative_guidance}")
    
    # Interpretation notes
    if template.interpretation_notes:
        lines.append(f"      - Interpretation Notes: {template.interpretation_notes}")
    
    # Usage examples
    if template.usage_examples:
        lines.append("      - Usage Examples (creative variations for inspiration):")
        for idx, example in enumerate(template.usage_examples, 1):
            lines.append(f"        {idx}. \"{example}\"")
    
    # What to avoid
    if template.what_to_avoid:
        lines.append(f"      - What to Avoid: {template.what_to_avoid}")
    
    # Basic example (legacy)
    if template.example:
        lines.append(f"      - Basic Example: \"{template.example}\"")
    
    return "\n".join(lines) + "\n" if lines else ""


def _build_slide_insights_block(brief: CoherenceBrief, slide_info: Dict[str, Any]) -> str:
    """
    Build formatted insights block for a specific slide.
    
    Only includes insights that are in slide_info["insights_referenced"].
    
    Args:
        brief: CoherenceBrief with insights to format
        slide_info: Specific slide dict with insights_referenced field
    
    Returns:
        Formatted string block with slide-referenced insights only
    """
    referenced_ids = set(slide_info.get("insights_referenced", []))
    lines: List[str] = []
    
    for insight in brief.key_insights_content:
        if insight.get("id") not in referenced_ids:
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
    
    return "\n".join(lines) if lines else "- (no insights referenced for this slide)"


class Copywriter:
    """
    Generate text content for slides with emphasis guidance.
    
    Creates text content (title, subtitle, body) with emphasis guidance
    (list of strings to emphasize) for each slide based on narrative structure
    and coherence brief. Positioning and visual styling are handled by the Visual Composer.
    """
    
    def __init__(
        self,
        llm_client: HttpLLMClient,
        logger: Optional["LLMLogger"] = None,
    ) -> None:
        """
        Initialize Copywriter.
        
        Args:
            llm_client: LLM client for generation
            logger: Optional LLM logger for tracking calls and steps
        """
        self.llm = llm_client
        self.logger = logger
    
    def generate_post_copy(
        self,
        brief: CoherenceBrief,
        slides_info: List[Dict[str, Any]],
        article_text: str,
        context: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate text content for all slides of a post in a single LLM call.
        
        This ensures coherence and flow across all slides while reducing context redundancy.
        
        Args:
            brief: CoherenceBrief with all necessary context
            slides_info: List of all slides from narrative_structure with content_slots, copy_direction, etc.
            article_text: Full article content for reference
            context: Optional context identifier (e.g., post_id) for organizing logs
            prompt_version: Optional prompt version to use. If None, uses the latest version.
        
        Returns:
            Dict with "slides" array containing copy for each slide, and "post_guidelines"
            Each slide dict has: title, subtitle, body (each can be null or object),
            copy_guidelines, and cta_guidelines
        
        Raises:
            ValueError: If brief is invalid, response validation fails, or prompt not found
        """
        context = context or f"{brief.post_id}_post_copy"
        
        # Load prompt template from database
        prompt_key = "copywriter"
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
        
        # Build prompt dictionary from brief and all slides
        prompt_dict = self._build_prompt_dict(brief, slides_info, article_text)
        
        # Build prompt from template string using simple replacement
        prompt = template_text
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Calculate max_tokens dynamically based on number of slides
        # Formula: min(8192, 1000 + (num_slides * 500))
        # This ensures:
        # - Posts pequenos (1-3 slides): ~2500 tokens
        # - Posts médios (4-8 slides): ~4000-5000 tokens
        # - Posts grandes (9+ slides): 8192 tokens (máximo)
        from ..core.config import DEEPSEEK_MAX_TOKENS
        num_slides = len(slides_info)
        calculated_max_tokens = min(DEEPSEEK_MAX_TOKENS, 1000 + (num_slides * 500))
        
        # Call LLM (logging is handled automatically by HttpLLMClient if logger is provided)
        raw_response = self.llm.generate(
            prompt,
            context=context,
            temperature=0.3,
            max_tokens=calculated_max_tokens,
            prompt_key=prompt_key,
            template=template_text,
        )
        
        # Check for potential truncation (simple heuristic: incomplete JSON structure)
        response_stripped = raw_response.strip()
        potential_truncation = False
        if response_stripped:
            # Check if response ends abruptly (not with closing braces)
            # This is a simple heuristic - complete JSON should end with } or ]}
            if not (response_stripped.endswith("}") or response_stripped.endswith("]}")):
                potential_truncation = True
        
        # Validate response structure
        try:
            payload = self._validate_response(raw_response, slides_info, brief)
        except ValueError as e:
            # If we suspect truncation, log a specific warning
            if potential_truncation:
                import warnings
                warnings.warn(
                    f"Response may be truncated for post {brief.post_id}. "
                    f"Consider increasing max_tokens or reducing number of slides.",
                    UserWarning,
                )
                # Log truncation warning to logger if available
                if self.logger:
                    try:
                        trace_id = self.logger.current_trace_id or self.logger.session_id
                        if trace_id:
                            self.logger.log_step_event(
                                trace_id=trace_id,
                                name=f"copywriter_truncation_warning_{brief.post_id}",
                                input_text=f"Post copy generation for {brief.post_id}",
                                output_text=None,
                                error=f"Potential truncation detected: {str(e)}",
                                status="error",
                                type="postprocess",
                                metadata={
                                    "post_id": brief.post_id,
                                    "total_slides": len(slides_info),
                                    "max_tokens_used": calculated_max_tokens,
                                    "potential_truncation": True,
                                },
                            )
                    except Exception:
                        pass
            # Log validation error using SQL logger if available
            if self.logger:
                try:
                    trace_id = self.logger.current_trace_id or self.logger.session_id
                    if trace_id:
                        self.logger.log_step_event(
                            trace_id=trace_id,
                            name=f"copywriter_validation_error_{brief.post_id}",
                            input_text=f"Validating post copy for {brief.post_id}",
                            output_text=None,
                            error=str(e),
                            status="error",
                            type="postprocess",
                            metadata={
                                "post_id": brief.post_id,
                                "total_slides": len(slides_info),
                            },
                        )
                except Exception:
                    pass
            raise
        
        # Extract and enrich coherence brief with guidelines from the post
        # Use guidelines from the first slide or aggregate if needed
        slides_copy = payload.get("slides", [])
        if slides_copy:
            first_slide = slides_copy[0]
            copy_guidelines_dict = first_slide.get("copy_guidelines", {})
            # Enrich brief (will be updated with each slide's guidelines if needed)
            copy_guidelines = {
                "headline_style": copy_guidelines_dict.get("headline_style"),
                "body_style": copy_guidelines_dict.get("body_style"),
                "cta_details": {},
            }
            brief.enrich_from_copywriting(copy_guidelines)
        
        # Log success using SQL logger if available
        if self.logger:
            try:
                trace_id = self.logger.current_trace_id or self.logger.session_id
                if trace_id:
                    total_elements = sum(
                        sum(1 for key in ["title", "subtitle", "body"] if slide.get(key) is not None)
                        for slide in slides_copy
                    )
                    self.logger.log_step_event(
                        trace_id=trace_id,
                        name=f"copywriter_success_{brief.post_id}",
                        input_text=f"Generating post copy for {brief.post_id}",
                        output_text=f"Post copy generated: {len(slides_copy)} slides, {total_elements} total text elements",
                        output_obj={
                            "post_id": brief.post_id,
                            "total_slides": len(slides_copy),
                            "total_text_elements": total_elements,
                        },
                        status="success",
                        type="postprocess",
                        metadata={
                            "post_id": brief.post_id,
                            "total_slides": len(slides_copy),
                        },
                    )
            except Exception:
                pass
        
        return payload
    
    def generate_slide_copy(
        self,
        brief: CoherenceBrief,
        slide_info: Dict[str, Any],
        article_text: str,
        context: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        DEPRECATED: Use generate_post_copy instead.
        
        This method is kept for backwards compatibility but is deprecated.
        Generate copy for a single slide by wrapping it in generate_post_copy.
        """
        result = self.generate_post_copy(
            brief=brief,
            slides_info=[slide_info],
            article_text=article_text,
            context=context or f"{brief.post_id}_slide_{slide_info.get('slide_number', 'unknown')}",
            prompt_version=prompt_version,
        )
        # Return the first (and only) slide from the result
        slides = result.get("slides", [])
        if slides:
            return slides[0]
        raise ValueError("No slide copy returned from generate_post_copy")
    
    def _build_prompt_dict(self, brief: CoherenceBrief, slides_info: List[Dict[str, Any]], article_text: str) -> Dict[str, Any]:
        """
        Build prompt dictionary from coherence brief and all slides info.
        
        Maps all necessary attributes to template placeholders.
        Only includes attributes relevant to copywriting.
        
        Args:
            brief: CoherenceBrief to extract fields from
            slides_info: List of all slide dicts from narrative_structure
            article_text: Full article content
        
        Returns:
            Dictionary mapping template placeholders to values
        """
        # Build slides context block with all slides
        slides_context_lines = []
        all_referenced_insights = set()
        
        # Extract template_ids from slides
        template_ids = []
        for slide in slides_info:
            template_id = slide.get("template_id")
            if template_id:
                template_ids.append(template_id)
        
        # Load templates library and get detailed reference for selected templates
        from ..templates.library import TemplateLibrary
        template_library = TemplateLibrary()
        templates_reference = template_library.to_detailed_reference(template_ids) if template_ids else "- (no templates selected)"
        
        for slide in slides_info:
            slide_num = slide.get("slide_number", "?")
            template_type = slide.get("template_type", "unknown")
            value_subtype = slide.get("value_subtype")
            template_id = slide.get("template_id", "N/A")
            purpose = slide.get("purpose", "")
            copy_direction = slide.get("copy_direction", "")
            visual_direction = slide.get("visual_direction", "")
            
            # Get template details for this slide
            template_details = ""
            if template_id and template_id != "N/A":
                template = template_library.get_template(template_id)
                if template:
                    template_details = _build_template_context_block(template)
            
            # Content slots
            content_slots = slide.get("content_slots", {})
            content_slots_str = ""
            for slot_name, slot_info in content_slots.items():
                required = slot_info.get("required", False)
                max_chars = slot_info.get("max_chars", "N/A")
                content_slots_str += f"    - {slot_name}: required={required}, max_chars={max_chars}\n"
            
            # Collect referenced insights
            referenced_ids = set(slide.get("insights_referenced", []))
            all_referenced_insights.update(referenced_ids)
            
            # Build template type display
            template_type_display = template_type
            if template_type == "value" and value_subtype:
                template_type_display = f"{template_type}/{value_subtype}"
            
            slides_context_lines.append(
                f"  SLIDE {slide_num} ({template_type_display}, template: {template_id}):\n"
                f"    Purpose: {purpose}\n"
                f"    Copy Direction: {copy_direction[:200]}{'...' if len(copy_direction) > 200 else ''}\n"
                f"    Visual Direction: {visual_direction[:200]}{'...' if len(visual_direction) > 200 else ''}\n"
                f"    Content Slots:\n{content_slots_str}"
                f"    Target Emotions: {', '.join(slide.get('target_emotions', []))}\n"
                f"    Key Elements: {', '.join(slide.get('key_elements', []))}\n"
                f"    Insights Referenced: {', '.join(slide.get('insights_referenced', []))}\n"
                f"    Transition: {slide.get('transition_to_next', 'N/A (last slide)' if slide_num == len(slides_info) else 'N/A')}\n"
                f"{template_details}"
            )
        
        slides_context_block = "\n".join(slides_context_lines)
        
        # Build insights block with all referenced insights
        insights_lines = []
        for insight in brief.key_insights_content:
            if insight.get("id") not in all_referenced_insights:
                continue
            
            insight_id = insight.get("id", "unknown")
            content = insight.get("content", "")
            insight_type = insight.get("type", "unknown")
            strength = insight.get("strength", "N/A")
            source_quote = insight.get("source_quote", "")
            
            insights_lines.append(
                f"- ID: {insight_id}\n"
                f"  Content: {content}\n"
                f"  Type: {insight_type}\n"
                f"  Strength: {strength} (1-10 scale)\n"
                f"  Source Quote: {source_quote}"
            )
        
        insights_block = "\n".join(insights_lines) if insights_lines else "- (no insights referenced)"
        
        return {
            # Voice & Platform
            "platform": brief.platform,
            "format": brief.format,
            "tone": brief.tone,
            "personality_traits": ", ".join(brief.personality_traits),
            "vocabulary_level": brief.vocabulary_level,
            "formality": brief.formality,
            
            # Content Essence (Post-level)
            "main_message": brief.main_message,
            "value_proposition": brief.value_proposition,
            "keywords_to_emphasize": ", ".join(brief.keywords_to_emphasize),
            "angle": brief.angle,
            "hook": brief.hook,
            "idea_explanation": brief.idea_explanation or "N/A",
            "rationale": brief.rationale or "N/A",
            
            # Audience Understanding (Post-level)
            "persona": brief.persona,
            "pain_points": ", ".join(brief.pain_points),
            "desires": ", ".join(brief.desires),
            
            # Emotional Journey
            "primary_emotion": brief.primary_emotion,
            "secondary_emotions": ", ".join(brief.secondary_emotions),
            "avoid_emotions": ", ".join(brief.avoid_emotions),
            "target_emotions": ", ".join(brief.target_emotions),
            
            # Source Material
            "article_context": brief.article_context,
            "article_text": article_text[:5000],  # Truncate if too long (first 5000 chars)
            "slide_insights_content_block": insights_block,
            
            # All Slides Context
            "total_slides": str(len(slides_info)),
            "slides_context": slides_context_block,
            
            # Templates Reference
            "templates_reference": templates_reference,
            
            # Constraints
            "avoid_topics": ", ".join(brief.avoid_topics),
            "required_elements": ", ".join(brief.required_elements),
        }
    
    def _validate_response(
        self,
        raw_response: str,
        slides_info: List[Dict[str, Any]],
        brief: CoherenceBrief,
    ) -> Dict[str, Any]:
        """
        Validate LLM response structure and semantics for all slides.
        
        Args:
            raw_response: Raw JSON response from LLM
            slides_info: List of slide dicts for validation context
            brief: CoherenceBrief for semantic validation
        
        Returns:
            Validated and parsed payload with "slides" array
        
        Raises:
            ValueError: If validation fails
        """
        # Structural validation - basic JSON structure
        payload = validate_llm_json_response(
            raw_response=raw_response,
            top_level_keys=[
                "slides",
            ],
        )
        
        # Validate slides array exists and has correct length
        slides = payload.get("slides", [])
        if not isinstance(slides, list):
            raise ValueError(f"'slides' must be an array, got {type(slides).__name__}")
        
        if len(slides) != len(slides_info):
            raise ValueError(
                f"Expected {len(slides_info)} slides in response, got {len(slides)}"
            )
        
        # Create a map of expected slide numbers
        expected_slide_numbers = {slide.get("slide_number") for slide in slides_info}
        
            # Validate each slide
        for slide_idx, slide_payload in enumerate(slides):
            # Find corresponding slide_info
            slide_number = slide_payload.get("slide_number")
            if slide_number not in expected_slide_numbers:
                raise ValueError(
                    f"Slide {slide_idx + 1}: unexpected slide_number {slide_number}"
                )
            
            # Find matching slide_info
            slide_info = None
            for info in slides_info:
                if info.get("slide_number") == slide_number:
                    slide_info = info
                    break
            
            if not slide_info:
                raise ValueError(f"Slide {slide_idx + 1}: no matching slide_info for slide_number {slide_number}")
            
            # Validate slide_number matches
            if slide_number != slide_info.get("slide_number"):
                raise ValueError(
                    f"Slide {slide_idx + 1}: slide_number mismatch: expected {slide_info.get('slide_number')}, got {slide_number}"
                )
            
            # Validate text elements structure for this slide
            text_elements = ["title", "subtitle", "body"]
            at_least_one = False
            
            for element_name in text_elements:
                element = slide_payload.get(element_name)
                
                if element is None:
                    continue  # Null is valid
                
                at_least_one = True
                
                # Must have content and emphasis
                if not isinstance(element, dict):
                    raise ValueError(f"Slide {slide_number}: {element_name} must be an object or null, got {type(element).__name__}")
                
                if "content" not in element:
                    raise ValueError(f"Slide {slide_number}: {element_name} missing 'content' field")
                
                if "emphasis" not in element:
                    raise ValueError(f"Slide {slide_number}: {element_name} missing 'emphasis' field")
                
                # Validate content
                content = element.get("content")
                if not isinstance(content, str) or len(content) == 0:
                    raise ValueError(f"Slide {slide_number}: {element_name}.content must be a non-empty string")
                
                # Validate emphasis (simplified - list of strings)
                # Emphasis is a simple list of strings (words/phrases to emphasize)
                # The Visual Composer will determine how to visually emphasize them
                emphasis = element.get("emphasis")
                if not isinstance(emphasis, list):
                    raise ValueError(f"Slide {slide_number}: {element_name}.emphasis must be an array")
                
                for emph_idx, emph_item in enumerate(emphasis):
                    if not isinstance(emph_item, str):
                        raise ValueError(
                            f"Slide {slide_number}: {element_name}.emphasis[{emph_idx}] must be a string, "
                            f"got {type(emph_item).__name__}"
                        )
                    # Optional: validate that emphasis string appears in content (case-insensitive)
                    # This helps catch typos but is lenient
                    if emph_item and emph_item.lower() not in content.lower():
                        # Warn but don't fail - the string might be a partial match or variation
                        pass
            
            if not at_least_one:
                raise ValueError(f"Slide {slide_number}: At least one of title, subtitle, or body must be non-null")
            
            # Semantic validation for this slide
            self._validate_semantics_slide(slide_payload, slide_info, brief)
        
        return payload
    
    def _validate_semantics_slide(
        self,
        slide_payload: Dict[str, Any],
        slide_info: Dict[str, Any],
        brief: CoherenceBrief,
    ) -> None:
        """
        Perform semantic validation on a single slide's content.
        
        Args:
            slide_payload: Parsed JSON payload for one slide
            slide_info: Slide dict for context
            brief: CoherenceBrief for context
        
        Raises:
            ValueError: If semantic validation fails
        """
        slide_number = slide_payload.get("slide_number", "?")
        
        # Validate content_slots requirements are met
        content_slots = slide_info.get("content_slots", {})
        
        # Map content_slots to text elements
        slot_to_element = {
            "headline": "title",
            "subheadline": "subtitle",
            "body": "body",
        }
        
        for slot_name, slot_info in content_slots.items():
            if slot_info.get("required", False):
                element_name = slot_to_element.get(slot_name)
                if element_name and slide_payload.get(element_name) is None:
                    raise ValueError(
                        f"Slide {slide_number}: Required content slot '{slot_name}' (maps to '{element_name}') is missing from output"
                    )
        
        # Validate no avoid_emotions appear (implicit check - copywriter should avoid them)
        # This is more of a content check, but we can't validate text content semantically
        # without NLP, so we skip this for now
        
        # Validate CTA guidelines are present for CTA slides
        template_type = slide_info.get("template_type")
        if template_type == "cta":
            cta_guidelines = slide_payload.get("cta_guidelines")
            if not cta_guidelines:
                # This is a warning, not an error - CTA guidelines are helpful but not strictly required
                pass

