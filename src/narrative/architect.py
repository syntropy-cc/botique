"""
Narrative Architect module

Generates detailed slide-by-slide narrative structures from coherence briefs.

Location: src/narrative/architect.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from typing import TYPE_CHECKING

from ..coherence.brief import CoherenceBrief
from ..core.config import NARRATIVE_ARCHITECT_TEMPLATE, MAX_SLIDES_PER_POST, MIN_SLIDES_PER_POST
from ..core.llm_client import HttpLLMClient
from ..core.utils import build_prompt_from_template, validate_llm_json_response

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
    
    def _log_step(
        self,
        step: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        post_id: Optional[str] = None,
    ) -> None:
        """
        Log an application-level step.
        
        Args:
            step: Step identifier (e.g., "start", "build_prompt")
            message: Human-readable message
            data: Optional additional data to log
            post_id: Optional post ID for correlation
        """
        if not self.logger:
            return
        
        # Write step log as JSON line to debug directory
        # This is a simple approach; could be extended to use a structured logger
        try:
            from ..core.config import OUTPUT_DIR
            
            context = post_id or "narrative_architect"
            debug_dir = OUTPUT_DIR / context / "debug"
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = debug_dir / "narrative_architect_steps.jsonl"
            
            log_entry = {
                "step": step,
                "message": message,
                "post_id": post_id,
                "data": data or {},
            }
            
            with log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            # Don't fail the main operation if logging fails
            pass
    
    def generate_structure(
        self,
        brief: CoherenceBrief,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate narrative structure for a post based on its coherence brief.
        
        Args:
            brief: CoherenceBrief with all necessary context
            context: Optional context identifier (e.g., post_id) for organizing logs
        
        Returns:
            Dict with narrative structure: pacing, transition_style, arc_refined, slides, rationale
        
        Raises:
            ValueError: If brief is invalid or response validation fails
        """
        context = context or brief.post_id
        
        # Log start
        self._log_step(
            "start",
            f"Starting narrative structure generation for post {brief.post_id}",
            {"idea_id": brief.idea_id, "platform": brief.platform, "format": brief.format},
            post_id=brief.post_id,
        )
        
        # Build prompt dictionary from brief fields
        prompt_dict = self._build_prompt_dict(brief)
        
        # Log prompt build
        self._log_step(
            "build_prompt",
            "Prompt built successfully",
            {
                "num_insights": len(brief.key_insights_content),
                "insights_used": len(brief.key_insights_used),
                "estimated_slides": brief.estimated_slides,
            },
            post_id=brief.post_id,
        )
        
        # Read template and build prompt
        template_text = NARRATIVE_ARCHITECT_TEMPLATE.read_text(encoding="utf-8")
        prompt = build_prompt_from_template(NARRATIVE_ARCHITECT_TEMPLATE, prompt_dict)
        
        # Log LLM call initiation
        self._log_step(
            "llm_call",
            "Initiating LLM call",
            {
                "prompt_key": "narrative_architect",
                "temperature": 0.2,
                "max_tokens": 2048,
            },
            post_id=brief.post_id,
        )
        
        # Call LLM
        raw_response = self.llm.generate(
            prompt,
            context=context,
            temperature=0.2,
            max_tokens=2048,
            prompt_key="narrative_architect",
            template=template_text,
        )
        
        # Log response received
        self._log_step(
            "llm_response",
            "LLM response received",
            {
                "response_length": len(raw_response),
                "status": "success",
            },
            post_id=brief.post_id,
        )
        
        # Validate response structure
        try:
            payload = self._validate_response(raw_response, brief)
        except ValueError as e:
            self._log_step(
                "validation_error",
                f"Validation failed: {str(e)}",
                {"error": str(e)},
                post_id=brief.post_id,
            )
            raise
        
        # Log validation success
        self._log_step(
            "validation_success",
            "Response validated successfully",
            {
                "num_slides": len(payload["slides"]),
                "pacing": payload["narrative_pacing"],
                "transition_style": payload["transition_style"],
            },
            post_id=brief.post_id,
        )
        
        # Build normalized narrative structure
        # Map "narrative_pacing" from payload to "pacing" for brief enrichment
        narrative_structure = {
            "pacing": payload["narrative_pacing"],
            "transition_style": payload["transition_style"],
            "arc_refined": payload["arc_refined"],
            "slides": payload["slides"],
        }
        
        # Enrich coherence brief
        brief.enrich_from_narrative_structure(narrative_structure)
        
        # Log brief enrichment
        self._log_step(
            "brief_enriched",
            "Coherence brief enriched with narrative structure",
            {
                "num_slides": len(payload["slides"]),
                "pacing": payload["narrative_pacing"],
                "transition_style": payload["transition_style"],
                "insights_referenced": self._count_insights_referenced(payload["slides"]),
            },
            post_id=brief.post_id,
        )
        
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
                    "content_slots",
                    "visual_mood",
                    "insights_referenced",
                    "transition_to_next",
                ],
            },
        )
        
        # Validate content_slots structure for each slide
        for idx, slide in enumerate(payload["slides"]):
            if "content_slots" not in slide:
                raise ValueError(f"Slide {idx + 1} missing 'content_slots'")
            
            content_slots = slide["content_slots"]
            if not isinstance(content_slots, dict):
                raise ValueError(f"Slide {idx + 1}: 'content_slots' must be a dictionary")
            
            # Validate each slot type
            for slot_name in ["headline", "subheadline", "body", "cta"]:
                if slot_name in content_slots:
                    slot = content_slots[slot_name]
                    if not isinstance(slot, dict):
                        raise ValueError(
                            f"Slide {idx + 1}: 'content_slots.{slot_name}' must be a dictionary"
                        )
                    
                    required_keys = ["required", "max_chars"]
                    missing = [k for k in required_keys if k not in slot]
                    if missing:
                        raise ValueError(
                            f"Slide {idx + 1}: 'content_slots.{slot_name}' missing keys: {missing}"
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

