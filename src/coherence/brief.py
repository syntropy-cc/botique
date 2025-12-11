"""
Coherence brief data model

Complete coherence brief structure that travels through all pipeline phases.

Location: src/coherence/brief.py
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


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
    
    # =========================================================================
    # BRAND ALIGNMENT
    # =========================================================================
    
    brand_values: List[str] = field(default_factory=list)  # Aligned brand values
    
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
            },
            "brand": {
                "values": self.brand_values,
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