"""
Copywriter module

Generates text content for slides with positioning and emphasis specifications.

Location: src/copywriting/writer.py
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..core.utils import validate_llm_json_response
# Try new locations first, fallback to old locations
try:
    from boutique.state_management.models.coherence_brief import CoherenceBrief
    from framework.llm.http_client import HttpLLMClient
    from framework.llm.prompt_helpers import get_or_register_prompt as get_latest_prompt
    from framework.llm.prompt_helpers import get_prompt_by_key_and_version
except ImportError:
    from ..coherence.brief import CoherenceBrief
    from ..core.llm_client import HttpLLMClient
    from ..core.prompt_registry import get_latest_prompt, get_prompt_by_key_and_version

if TYPE_CHECKING:
    try:
        from framework.llm.logger import LLMLogger
    except ImportError:
        from ..core.llm_logger import LLMLogger


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
    Generate text content for slides with positioning and emphasis.
    
    Creates text content (title, subtitle, body) with low-level positioning
    (x, y coordinates) and emphasis styles (bold, italic, underline, etc.)
    for each slide based on narrative structure and coherence brief.
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
    
    def generate_slide_copy(
        self,
        brief: CoherenceBrief,
        slide_info: Dict[str, Any],
        article_text: str,
        context: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate text content for a specific slide with positioning and emphasis.
        
        Args:
            brief: CoherenceBrief with all necessary context
            slide_info: Specific slide from narrative_structure with content_slots, copy_direction, etc.
            article_text: Full article content for reference
            context: Optional context identifier (e.g., post_id_slide_1) for organizing logs
            prompt_version: Optional prompt version to use. If None, uses the latest version.
        
        Returns:
            Dict with slide_content: title, subtitle, body (each can be null or object),
            copy_guidelines, and cta_guidelines
        
        Raises:
            ValueError: If brief is invalid, response validation fails, or prompt not found
        """
        context = context or f"{brief.post_id}_slide_{slide_info.get('slide_number', 'unknown')}"
        
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
        
        # Build prompt dictionary from brief and slide fields
        prompt_dict = self._build_prompt_dict(brief, slide_info, article_text)
        
        # Build prompt from template string using simple replacement
        prompt = template_text
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Call LLM (logging is handled automatically by HttpLLMClient if logger is provided)
        raw_response = self.llm.generate(
            prompt,
            context=context,
            temperature=0.3,
            max_tokens=8000,
            prompt_key=prompt_key,
            template=template_text,
        )
        
        # Validate response structure
        try:
            payload = self._validate_response(raw_response, slide_info, brief)
        except ValueError as e:
            # Log validation error using SQL logger if available
            if self.logger:
                try:
                    trace_id = self.logger.current_trace_id or self.logger.session_id
                    if trace_id:
                        self.logger.log_step_event(
                            trace_id=trace_id,
                            name=f"copywriter_validation_error_{brief.post_id}_slide_{slide_info.get('slide_number', 'unknown')}",
                            input_text=f"Validating slide copy for {brief.post_id} slide {slide_info.get('slide_number', 'unknown')}",
                            output_text=None,
                            error=str(e),
                            status="error",
                            type="postprocess",
                            metadata={
                                "post_id": brief.post_id,
                                "slide_number": slide_info.get("slide_number"),
                                "module_type": slide_info.get("module_type"),
                            },
                        )
                except Exception:
                    pass
            raise
        
        # Enrich coherence brief
        copy_guidelines_dict = payload.get("copy_guidelines", {})
        cta_guidelines_dict = payload.get("cta_guidelines")
        
        # Build copy_guidelines with cta_details nested
        copy_guidelines = {
            "headline_style": copy_guidelines_dict.get("headline_style"),
            "body_style": copy_guidelines_dict.get("body_style"),
            "cta_details": cta_guidelines_dict if cta_guidelines_dict else {},
        }
        brief.enrich_from_copywriting(copy_guidelines)
        
        # Log success using SQL logger if available
        if self.logger:
            try:
                trace_id = self.logger.current_trace_id or self.logger.session_id
                if trace_id:
                    text_elements_count = sum(1 for key in ["title", "subtitle", "body"] if payload.get(key) is not None)
                    self.logger.log_step_event(
                        trace_id=trace_id,
                        name=f"copywriter_success_{brief.post_id}_slide_{slide_info.get('slide_number', 'unknown')}",
                        input_text=f"Generating slide copy for {brief.post_id} slide {slide_info.get('slide_number', 'unknown')}",
                        output_text=f"Slide copy generated: {text_elements_count} text elements",
                        output_obj={
                            "post_id": brief.post_id,
                            "slide_number": slide_info.get("slide_number"),
                            "text_elements_count": text_elements_count,
                            "has_title": payload.get("title") is not None,
                            "has_subtitle": payload.get("subtitle") is not None,
                            "has_body": payload.get("body") is not None,
                        },
                        status="success",
                        type="postprocess",
                        metadata={
                            "post_id": brief.post_id,
                            "slide_number": slide_info.get("slide_number"),
                            "module_type": slide_info.get("module_type"),
                            "text_elements_count": text_elements_count,
                        },
                    )
            except Exception:
                pass
        
        return payload
    
    def _build_prompt_dict(self, brief: CoherenceBrief, slide_info: Dict[str, Any], article_text: str) -> Dict[str, Any]:
        """
        Build prompt dictionary from coherence brief and slide info fields.
        
        Maps all necessary attributes to template placeholders.
        Only includes attributes relevant to copywriting.
        
        Args:
            brief: CoherenceBrief to extract fields from
            slide_info: Specific slide dict from narrative_structure
            article_text: Full article content
        
        Returns:
            Dictionary mapping template placeholders to values
        """
        # Extract content slots info
        content_slots = slide_info.get("content_slots", {})
        content_slots_str = ""
        for slot_name, slot_info in content_slots.items():
            required = slot_info.get("required", False)
            max_chars = slot_info.get("max_chars", "N/A")
            content_slots_str += f"  - {slot_name}: required={required}, max_chars={max_chars}\n"
        
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
            "slide_insights_content_block": _build_slide_insights_block(brief, slide_info),
            
            # Slide Context
            "slide_number": str(slide_info.get("slide_number", "unknown")),
            "module_type": slide_info.get("module_type", "unknown"),
            "purpose": slide_info.get("purpose", ""),
            "copy_direction": slide_info.get("copy_direction", ""),
            "content_slots": content_slots_str.strip() or "No specific content slots defined",
            "slide_target_emotions": ", ".join(slide_info.get("target_emotions", [])),
            "key_elements": ", ".join(slide_info.get("key_elements", [])),
            "insights_referenced": ", ".join(slide_info.get("insights_referenced", [])),
            "transition_to_next": slide_info.get("transition_to_next") or "N/A (last slide)",
            
            # Branding (Reference only - for positioning calculations)
            "canvas_width": str(brief.canvas.get("width", 1080)),
            "canvas_height": str(brief.canvas.get("height", 1350)),
            "canvas_aspect_ratio": brief.canvas.get("aspect_ratio", "4:5"),
            
            # Constraints
            "avoid_topics": ", ".join(brief.avoid_topics),
            "required_elements": ", ".join(brief.required_elements),
        }
    
    def _validate_response(
        self,
        raw_response: str,
        slide_info: Dict[str, Any],
        brief: CoherenceBrief,
    ) -> Dict[str, Any]:
        """
        Validate LLM response structure and semantics.
        
        Args:
            raw_response: Raw JSON response from LLM
            slide_info: Slide dict for validation context
            brief: CoherenceBrief for semantic validation
        
        Returns:
            Validated and parsed payload
        
        Raises:
            ValueError: If validation fails
        """
        # Structural validation - basic JSON structure
        payload = validate_llm_json_response(
            raw_response=raw_response,
            top_level_keys=[
                "slide_number",
                "title",
                "subtitle",
                "body",
                "copy_guidelines",
                "cta_guidelines",
            ],
        )
        
        # Validate slide_number matches
        slide_number = payload.get("slide_number")
        expected_slide_number = slide_info.get("slide_number")
        if slide_number != expected_slide_number:
            raise ValueError(
                f"Slide number mismatch: expected {expected_slide_number}, got {slide_number}"
            )
        
        # Validate text elements structure
        canvas_width = brief.canvas.get("width", 1080)
        canvas_height = brief.canvas.get("height", 1350)
        
        text_elements = ["title", "subtitle", "body"]
        at_least_one = False
        
        for element_name in text_elements:
            element = payload.get(element_name)
            
            if element is None:
                continue  # Null is valid
            
            at_least_one = True
            
            # Must have content, position, emphasis
            if not isinstance(element, dict):
                raise ValueError(f"{element_name} must be an object or null, got {type(element).__name__}")
            
            if "content" not in element:
                raise ValueError(f"{element_name} missing 'content' field")
            
            if "position" not in element:
                raise ValueError(f"{element_name} missing 'position' field")
            
            if "emphasis" not in element:
                raise ValueError(f"{element_name} missing 'emphasis' field")
            
            # Validate content
            content = element.get("content")
            if not isinstance(content, str) or len(content) == 0:
                raise ValueError(f"{element_name}.content must be a non-empty string")
            
            # Validate position
            position = element.get("position")
            if not isinstance(position, dict):
                raise ValueError(f"{element_name}.position must be an object")
            
            x = position.get("x")
            y = position.get("y")
            
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError(f"{element_name}.position.x and .y must be integers")
            
            if x < 0 or x > canvas_width:
                raise ValueError(
                    f"{element_name}.position.x ({x}) out of bounds (0-{canvas_width})"
                )
            
            if y < 0 or y > canvas_height:
                raise ValueError(
                    f"{element_name}.position.y ({y}) out of bounds (0-{canvas_height})"
                )
            
            # Validate emphasis
            emphasis = element.get("emphasis")
            if not isinstance(emphasis, list):
                raise ValueError(f"{element_name}.emphasis must be an array")
            
            for idx, emph in enumerate(emphasis):
                if not isinstance(emph, dict):
                    raise ValueError(f"{element_name}.emphasis[{idx}] must be an object")
                
                required_keys = ["text", "start_index", "end_index", "styles"]
                missing = [k for k in required_keys if k not in emph]
                if missing:
                    raise ValueError(f"{element_name}.emphasis[{idx}] missing keys: {missing}")
                
                # Validate indices
                start_idx = emph.get("start_index")
                end_idx = emph.get("end_index")
                
                if not isinstance(start_idx, int) or not isinstance(end_idx, int):
                    raise ValueError(f"{element_name}.emphasis[{idx}].start_index and .end_index must be integers")
                
                # Auto-correct indices that are slightly out of bounds
                # This handles cases where the LLM miscalculates indices due to Unicode or other issues
                content_len = len(content)
                original_start_idx = start_idx
                original_end_idx = end_idx
                actual_text = emph.get("text", "")
                
                # First, check if indices are valid and text matches
                indices_valid = (0 <= start_idx < end_idx <= content_len)
                text_matches = False
                if indices_valid:
                    expected_text = content[start_idx:end_idx]
                    text_matches = (actual_text == expected_text)
                
                # If indices are invalid or text doesn't match, try to auto-correct
                if not indices_valid or not text_matches:
                    if actual_text:
                        # Try to find the text in the content
                        # First, try near the original start_idx (within 10 characters)
                        found_pos = -1
                        search_start = max(0, start_idx - 10)
                        search_end = min(content_len, start_idx + 50)
                        candidate = content[search_start:search_end]
                        pos_in_candidate = candidate.find(actual_text)
                        if pos_in_candidate != -1:
                            found_pos = search_start + pos_in_candidate
                        
                        # If not found nearby, search the entire content
                        if found_pos == -1:
                            found_pos = content.find(actual_text)
                        
                        if found_pos != -1:
                            # Found the text - use these indices
                            start_idx = found_pos
                            end_idx = found_pos + len(actual_text)
                            # Update the emphasis dict with corrected indices
                            emph["start_index"] = start_idx
                            emph["end_index"] = end_idx
                        else:
                            # Text not found - check if it's a small index error
                            if end_idx > content_len and end_idx <= content_len + 5:
                                # Small overrun - try clamping end_idx and checking if text matches
                                clamped_end = content_len
                                if start_idx < clamped_end:
                                    expected_text = content[start_idx:clamped_end]
                                    # Check if actual_text is a prefix of expected_text
                                    if actual_text and expected_text.startswith(actual_text):
                                        # Text matches as prefix - use clamped end
                                        end_idx = start_idx + len(actual_text)
                                        emph["start_index"] = start_idx
                                        emph["end_index"] = end_idx
                                    else:
                                        raise ValueError(
                                            f"{element_name}.emphasis[{idx}] invalid indices: "
                                            f"start_index={original_start_idx}, end_index={original_end_idx}, "
                                            f"content_length={content_len}, and text '{actual_text}' not found in content"
                                        )
                                else:
                                    raise ValueError(
                                        f"{element_name}.emphasis[{idx}] invalid indices: "
                                        f"start_index={original_start_idx}, end_index={original_end_idx}, "
                                        f"content_length={content_len}"
                                    )
                            else:
                                raise ValueError(
                                    f"{element_name}.emphasis[{idx}] invalid indices: "
                                    f"start_index={original_start_idx}, end_index={original_end_idx}, "
                                    f"content_length={content_len}, and text '{actual_text}' not found in content"
                                )
                    else:
                        # No text provided - can't auto-correct
                        if end_idx > content_len:
                            raise ValueError(
                                f"{element_name}.emphasis[{idx}] invalid indices: "
                                f"start_index={start_idx}, end_index={original_end_idx}, content_length={content_len}"
                            )
                        elif end_idx <= start_idx:
                            raise ValueError(
                                f"{element_name}.emphasis[{idx}] invalid indices: "
                                f"start_index={original_start_idx}, end_index={original_end_idx}, "
                                f"content_length={content_len}"
                            )
                
                # Final validation: ensure text matches content substring
                expected_text = content[start_idx:end_idx]
                if actual_text != expected_text:
                    raise ValueError(
                        f"{element_name}.emphasis[{idx}].text ('{actual_text}') doesn't match "
                        f"content substring at indices {start_idx}-{end_idx} ('{expected_text}')"
                    )
                
                # Validate styles
                styles = emph.get("styles")
                if not isinstance(styles, list):
                    raise ValueError(f"{element_name}.emphasis[{idx}].styles must be an array")
                
                valid_styles = {"bold", "italic", "underline", "stylized"}
                for style in styles:
                    if not isinstance(style, str) or style not in valid_styles:
                        raise ValueError(
                            f"{element_name}.emphasis[{idx}].styles contains invalid style '{style}'. "
                            f"Valid styles: {valid_styles}"
                        )
        
        if not at_least_one:
            raise ValueError("At least one of title, subtitle, or body must be non-null")
        
        # Semantic validation
        self._validate_semantics(payload, slide_info, brief)
        
        return payload
    
    def _validate_semantics(
        self,
        payload: Dict[str, Any],
        slide_info: Dict[str, Any],
        brief: CoherenceBrief,
    ) -> None:
        """
        Perform semantic validation on slide content.
        
        Args:
            payload: Parsed JSON payload
            slide_info: Slide dict for context
            brief: CoherenceBrief for context
        
        Raises:
            ValueError: If semantic validation fails
        """
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
                if element_name and payload.get(element_name) is None:
                    raise ValueError(
                        f"Required content slot '{slot_name}' (maps to '{element_name}') is missing from output"
                    )
        
        # Validate no avoid_emotions appear (implicit check - copywriter should avoid them)
        # This is more of a content check, but we can't validate text content semantically
        # without NLP, so we skip this for now
        
        # Validate CTA guidelines are present for CTA slides
        module_type = slide_info.get("module_type")
        if module_type == "cta":
            cta_guidelines = payload.get("cta_guidelines")
            if not cta_guidelines:
                # This is a warning, not an error - CTA guidelines are helpful but not strictly required
                pass

