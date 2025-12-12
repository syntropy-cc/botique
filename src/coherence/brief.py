"""
Coherence brief data model

Complete coherence brief structure that travels through all pipeline phases.

Location: src/coherence/brief.py
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CoherenceBrief:
    """
    Complete coherence brief for a post.
    
    This document ensures consistency across all generation phases:
    - Voice (tone, personality, vocabulary)
    - Visual (palette, typography, style)
    - Emotions (primary, secondary, avoid)
    - Content (keywords, themes, message)
    - Audience (persona, pain points, desires)
    - Structure (objective, arc, slides)
    
    The brief travels through:
    - Phase 3: Narrative Architecture
    - Phase 4: Slide Generation
    - Phase 5: Caption Writing
    """
    
    # =========================================================================
    # METADATA
    # =========================================================================
    
    post_id: str                    # Unique post identifier
    idea_id: str                    # Reference to source idea
    platform: str                   # Target platform
    format: str                     # Content format
    
    # =========================================================================
    # VOICE
    # =========================================================================
    
    tone: str                       # Overall tone
    personality_traits: List[str]   # Voice personality
    vocabulary_level: str           # simple/moderate/sophisticated
    formality: str                  # casual/neutral/formal
    
    # =========================================================================
    # VISUAL (Brand-aligned)
    # =========================================================================
    
    palette_id: str                 # Color palette ID
    palette: Dict[str, str]         # Actual color values
    typography_id: str              # Typography config ID
    typography: Dict[str, str]      # Font configurations
    visual_style: str               # Style description
    visual_mood: str                # Mood keyword
    canvas: Dict[str, Any]          # Canvas dimensions
    
    # =========================================================================
    # EMOTIONS
    # =========================================================================
    
    primary_emotion: str            # Main emotional target
    secondary_emotions: List[str]   # Supporting emotions
    avoid_emotions: List[str]       # Emotions to avoid
    target_emotions: List[str]      # All target emotions
    
    # =========================================================================
    # CONTENT
    # =========================================================================
    
    keywords_to_emphasize: List[str]  # Key terms to highlight
    themes: List[str]                  # Content themes
    main_message: str                  # Core message
    value_proposition: str             # Value to audience
    angle: str                         # Unique angle
    hook: str                          # Opening hook
    
    # =========================================================================
    # AUDIENCE
    # =========================================================================
    
    persona: str                    # Target persona description
    pain_points: List[str]          # Audience challenges
    desires: List[str]              # Audience goals
    
    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    
    avoid_topics: List[str]         # Topics to avoid
    required_elements: List[str]    # Must-include elements
    
    # =========================================================================
    # STRUCTURE
    # =========================================================================
    
    objective: str                  # Post objective
    narrative_arc: str              # Story structure
    estimated_slides: int           # Number of slides
    
    # =========================================================================
    # CONTEXT
    # =========================================================================
    
    article_context: str            # Article summary for this post
    key_insights_used: List[str]    # Insight IDs used
    key_insights_content: List[Dict[str, Any]] = field(default_factory=list)  # Full insight content
    
    # =========================================================================
    # BRAND ALIGNMENT
    # =========================================================================
    
    brand_values: List[str] = field(default_factory=list)  # Aligned brand values
    brand_assets: Dict[str, str] = field(default_factory=dict)  # Brand handle and assets
    
    # =========================================================================
    # EVOLUTIVE FIELDS (Added by subsequent phases)
    # =========================================================================
    
    # Phase 3: Narrative Architect
    narrative_structure: Optional[Dict[str, Any]] = None  # Detailed slide-by-slide structure
    narrative_pacing: Optional[str] = None  # "fast", "moderate", "deliberate"
    transition_style: Optional[str] = None  # "abrupt", "smooth", "dramatic"
    
    # Phase 4: Copywriter
    copy_guidelines: Optional[Dict[str, Any]] = None  # Writing patterns and guidelines
    cta_guidelines: Optional[Dict[str, Any]] = None  # CTA details and suggestions
    
    # Phase 4: Visual Composer
    visual_preferences: Optional[Dict[str, Any]] = None  # Layout and composition preferences
    
    # Phase 5: Caption Writer
    platform_constraints: Optional[Dict[str, Any]] = None  # Platform-specific constraints
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the brief
        """
        return {
            "metadata": {
                "post_id": self.post_id,
                "idea_id": self.idea_id,
                "platform": self.platform,
                "format": self.format,
            },
            "voice": {
                "tone": self.tone,
                "personality_traits": self.personality_traits,
                "vocabulary_level": self.vocabulary_level,
                "formality": self.formality,
            },
            "visual": {
                "palette_id": self.palette_id,
                "palette": self.palette,
                "typography_id": self.typography_id,
                "typography": self.typography,
                "style": self.visual_style,
                "mood": self.visual_mood,
                "canvas": self.canvas,
            },
            "emotions": {
                "primary": self.primary_emotion,
                "secondary": self.secondary_emotions,
                "avoid": self.avoid_emotions,
                "target": self.target_emotions,
            },
            "content": {
                "keywords_to_emphasize": self.keywords_to_emphasize,
                "themes": self.themes,
                "main_message": self.main_message,
                "value_proposition": self.value_proposition,
                "angle": self.angle,
                "hook": self.hook,
            },
            "audience": {
                "persona": self.persona,
                "pain_points": self.pain_points,
                "desires": self.desires,
            },
            "constraints": {
                "avoid_topics": self.avoid_topics,
                "required_elements": self.required_elements,
            },
            "structure": {
                "objective": self.objective,
                "narrative_arc": self.narrative_arc,
                "estimated_slides": self.estimated_slides,
            },
            "context": {
                "article_context": self.article_context,
                "key_insights_used": self.key_insights_used,
                "key_insights_content": self.key_insights_content,
            },
            "brand": {
                "values": self.brand_values,
                "assets": self.brand_assets,
            },
            "evolution": {
                "narrative_structure": self.narrative_structure,
                "narrative_pacing": self.narrative_pacing,
                "transition_style": self.transition_style,
                "copy_guidelines": self.copy_guidelines,
                "cta_guidelines": self.cta_guidelines,
                "visual_preferences": self.visual_preferences,
                "platform_constraints": self.platform_constraints,
            }
        }
    
    def to_prompt_context(self) -> str:
        """
        Format as readable context block for LLM prompts.
        
        This string is injected into prompts for:
        - Narrative Architect
        - Copywriter
        - Visual Composer
        - Caption Writer
        
        Returns:
            Formatted context string
        """
        return f"""
=== COHERENCE BRIEF ===

BRAND IDENTITY:
- Values: {', '.join(self.brand_values)}
- Color Palette: {self.palette_id}
- Typography: {self.typography_id}

VOICE:
- Tone: {self.tone}
- Personality: {', '.join(self.personality_traits)}
- Vocabulary: {self.vocabulary_level}
- Formality: {self.formality}

VISUAL:
- Theme: {self.palette.get('theme', 'N/A')}
- Primary: {self.palette['primary']}
- Accent: {self.palette['accent']}
- CTA: {self.palette['cta']}
- Typography: {self.typography['heading_font']} / {self.typography['body_font']}
- Canvas: {self.canvas['width']}x{self.canvas['height']} ({self.canvas['aspect_ratio']})
- Style: {self.visual_style}
- Mood: {self.visual_mood}

EMOTIONS:
- Primary: {self.primary_emotion}
- Secondary: {', '.join(self.secondary_emotions)}
- Avoid: {', '.join(self.avoid_emotions)}

CONTENT:
- Main Message: {self.main_message}
- Value Prop: {self.value_proposition}
- Keywords: {', '.join(self.keywords_to_emphasize[:5])}
- Angle: {self.angle}
- Hook: {self.hook}

AUDIENCE:
- Persona: {self.persona}
- Pain Points: {', '.join(self.pain_points[:3])}
- Desires: {', '.join(self.desires[:3])}

STRUCTURE:
- Objective: {self.objective}
- Arc: {self.narrative_arc}
- Slides: {self.estimated_slides}

CONSTRAINTS:
- Avoid: {', '.join(self.avoid_topics)}
- Required: {', '.join(self.required_elements)}

======================
""".strip()
    
    def get_summary(self) -> str:
        """
        Get a one-line summary of the brief.
        
        Returns:
            Brief summary string
        """
        return (
            f"{self.post_id}: {self.platform}/{self.format} | "
            f"{self.tone} tone | {self.palette_id} | "
            f"{self.estimated_slides} slides"
        )
    
    def validate(self) -> List[str]:
        """
        Validate brief completeness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        if not self.post_id:
            errors.append("post_id is required")
        
        if not self.platform:
            errors.append("platform is required")
        
        if not self.tone:
            errors.append("tone is required")
        
        if not self.palette_id:
            errors.append("palette_id is required")
        
        if not self.typography_id:
            errors.append("typography_id is required")
        
        # Constraints
        if self.estimated_slides < 5 or self.estimated_slides > 12:
            errors.append(f"estimated_slides must be 5-12, got {self.estimated_slides}")
        
        if not self.personality_traits:
            errors.append("personality_traits cannot be empty")
        
        if not self.keywords_to_emphasize:
            errors.append("keywords_to_emphasize cannot be empty")
        
        return errors
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"CoherenceBrief({self.get_summary()})"
    
    # =========================================================================
    # ENRICHMENT METHODS (Called by subsequent phases)
    # =========================================================================
    
    def enrich_from_narrative_structure(
        self,
        narrative_structure: Dict[str, Any]
    ) -> None:
        """
        Enrich brief with detailed narrative structure from Narrative Architect.
        
        Args:
            narrative_structure: Complete narrative structure with slides, pacing, etc.
        """
        self.narrative_structure = narrative_structure
        self.narrative_pacing = narrative_structure.get("pacing", "moderate")
        self.transition_style = narrative_structure.get("transition_style", "smooth")
    
    def enrich_from_copywriting(
        self,
        copy_guidelines: Dict[str, Any]
    ) -> None:
        """
        Enrich brief with copywriting guidelines from Copywriter.
        
        Args:
            copy_guidelines: Writing patterns, CTA details, etc.
        """
        self.copy_guidelines = copy_guidelines
        self.cta_guidelines = copy_guidelines.get("cta_details", {})
    
    def enrich_from_visual_composition(
        self,
        visual_preferences: Dict[str, Any]
    ) -> None:
        """
        Enrich brief with visual preferences from Visual Composer.
        
        Args:
            visual_preferences: Layout style, composition rules, etc.
        """
        self.visual_preferences = visual_preferences
    
    def enrich_from_caption_writing(
        self,
        platform_constraints: Dict[str, Any]
    ) -> None:
        """
        Enrich brief with platform constraints from Caption Writer.
        
        Args:
            platform_constraints: Platform-specific limits, formats, etc.
        """
        self.platform_constraints = platform_constraints
    
    # =========================================================================
    # PHASE-SPECIFIC CONTEXT METHODS
    # =========================================================================
    
    def to_narrative_architect_context(self) -> str:
        """
        Context optimized for Narrative Architect (Phase 3).
        
        Focuses on: voice, emotions, content, structure (high-level).
        
        Returns:
            Formatted context string for Narrative Architect
        """
        return f"""
=== COHERENCE BRIEF (Narrative Architect) ===

VOICE:
- Tone: {self.tone}
- Personality: {', '.join(self.personality_traits)}
- Vocabulary: {self.vocabulary_level}
- Formality: {self.formality}

EMOTIONS:
- Primary: {self.primary_emotion}
- Secondary: {', '.join(self.secondary_emotions)}
- Avoid: {', '.join(self.avoid_emotions)}

CONTENT:
- Main Message: {self.main_message}
- Value Prop: {self.value_proposition}
- Keywords: {', '.join(self.keywords_to_emphasize[:5])}
- Angle: {self.angle}
- Hook: {self.hook}

STRUCTURE (High-level):
- Objective: {self.objective}
- Arc: {self.narrative_arc}
- Estimated Slides: {self.estimated_slides}

KEY INSIGHTS:
{self._format_insights_for_context()}

AUDIENCE:
- Persona: {self.persona}
- Pain Points: {', '.join(self.pain_points[:3])}
- Desires: {', '.join(self.desires[:3])}

CONSTRAINTS:
- Avoid Topics: {', '.join(self.avoid_topics)}
- Required Elements: {', '.join(self.required_elements)}

==========================================
""".strip()
    
    def to_copywriter_context(self) -> str:
        """
        Context optimized for Copywriter (Phase 4).
        
        Focuses on: voice, content, audience, narrative structure (if available).
        
        Returns:
            Formatted context string for Copywriter
        """
        narrative_info = ""
        if self.narrative_structure:
            narrative_info = f"""
NARRATIVE STRUCTURE:
- Pacing: {self.narrative_pacing or 'N/A'}
- Transition Style: {self.transition_style or 'N/A'}
- Slides: {len(self.narrative_structure.get('slides', []))} slides defined
"""
        
        return f"""
=== COHERENCE BRIEF (Copywriter) ===

VOICE:
- Tone: {self.tone}
- Personality: {', '.join(self.personality_traits)}
- Vocabulary: {self.vocabulary_level}
- Formality: {self.formality}

CONTENT:
- Main Message: {self.main_message}
- Value Prop: {self.value_proposition}
- Keywords: {', '.join(self.keywords_to_emphasize)}
- Angle: {self.angle}
- Hook: {self.hook}

AUDIENCE:
- Persona: {self.persona}
- Pain Points: {', '.join(self.pain_points)}
- Desires: {', '.join(self.desires)}

{narrative_info}
KEY INSIGHTS:
{self._format_insights_for_context()}

CONSTRAINTS:
- Avoid Topics: {', '.join(self.avoid_topics)}
- Required Elements: {', '.join(self.required_elements)}

=====================================
""".strip()
    
    def to_visual_composer_context(self) -> str:
        """
        Context optimized for Visual Composer (Phase 4).
        
        Focuses on: visual, emotions, narrative structure (if available).
        
        Returns:
            Formatted context string for Visual Composer
        """
        narrative_info = ""
        if self.narrative_structure:
            narrative_info = f"""
NARRATIVE STRUCTURE:
- Pacing: {self.narrative_pacing or 'N/A'}
- Transition Style: {self.transition_style or 'N/A'}
"""
        
        return f"""
=== COHERENCE BRIEF (Visual Composer) ===

VISUAL:
- Palette: {self.palette_id}
- Theme: {self.palette.get('theme', 'N/A')}
- Primary: {self.palette['primary']}
- Accent: {self.palette['accent']}
- CTA: {self.palette['cta']}
- Typography: {self.typography['heading_font']} / {self.typography['body_font']}
- Canvas: {self.canvas['width']}x{self.canvas['height']} ({self.canvas['aspect_ratio']})
- Style: {self.visual_style}
- Mood: {self.visual_mood}

EMOTIONS:
- Primary: {self.primary_emotion}
- Secondary: {', '.join(self.secondary_emotions)}
- Avoid: {', '.join(self.avoid_emotions)}

{narrative_info}
BRAND:
- Values: {', '.join(self.brand_values)}
- Assets: {self.brand_assets.get('handle', 'N/A')}

=========================================
""".strip()
    
    def to_caption_writer_context(self) -> str:
        """
        Context optimized for Caption Writer (Phase 5).
        
        Focuses on: voice, platform, CTA guidelines, platform constraints.
        
        Returns:
            Formatted context string for Caption Writer
        """
        cta_info = ""
        if self.cta_guidelines:
            cta_info = f"""
CTA GUIDELINES:
- Type: {self.cta_guidelines.get('type', 'N/A')}
- Tone: {self.cta_guidelines.get('tone', 'N/A')}
- Suggested Text: {self.cta_guidelines.get('suggested_text', 'N/A')}
"""
        
        platform_info = ""
        if self.platform_constraints:
            platform_info = f"""
PLATFORM CONSTRAINTS:
- Max Caption Length: {self.platform_constraints.get('max_caption_length', 'N/A')}
- Hashtag Count: {self.platform_constraints.get('hashtag_count', 'N/A')}
- CTA Format: {self.platform_constraints.get('cta_format', 'N/A')}
"""
        
        return f"""
=== COHERENCE BRIEF (Caption Writer) ===

PLATFORM: {self.platform}
FORMAT: {self.format}

VOICE:
- Tone: {self.tone}
- Formality: {self.formality}
- Vocabulary: {self.vocabulary_level}

{cta_info}
{platform_info}
BRAND:
- Handle: {self.brand_assets.get('handle', 'N/A')}
- Values: {', '.join(self.brand_values)}

CONTENT:
- Main Message: {self.main_message}
- Keywords: {', '.join(self.keywords_to_emphasize[:5])}

========================================
""".strip()
    
    def _format_insights_for_context(self) -> str:
        """Format key insights for context display."""
        if not self.key_insights_content:
            return "  (No insights available)"
        
        lines = []
        for insight in self.key_insights_content[:5]:  # Top 5
            insight_id = insight.get("id", "unknown")
            content = insight.get("content", "")[:100]  # Truncate long content
            insight_type = insight.get("type", "unknown")
            lines.append(f"  - [{insight_id}] ({insight_type}): {content}")
        
        return "\n".join(lines) if lines else "  (No insights available)"