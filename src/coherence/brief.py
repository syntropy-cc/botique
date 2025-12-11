"""
Coherence brief data model

Complete coherence brief structure for per-post consistency.

Location: src/coherence/brief.py
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CoherenceBrief:
    """
    Complete coherence brief for a post.
    
    This document travels through all generation phases, ensuring consistency
    in voice, visuals, emotions, and content across all slides.
    """
    
    # Metadata
    post_id: str
    idea_id: str
    platform: str
    format: str
    
    # Voice
    tone: str
    personality_traits: List[str] = field(default_factory=list)
    vocabulary_level: str = "moderate"
    formality: str = "neutral"
    
    # Visual
    palette_id: str = ""
    palette: Dict[str, str] = field(default_factory=dict)
    typography_id: str = ""
    typography: Dict[str, str] = field(default_factory=dict)
    visual_style: str = ""
    visual_mood: str = ""
    canvas: Dict[str, Any] = field(default_factory=dict)
    
    # Emotions
    primary_emotion: str = ""
    secondary_emotions: List[str] = field(default_factory=list)
    avoid_emotions: List[str] = field(default_factory=list)
    target_emotions: List[str] = field(default_factory=list)
    
    # Content
    keywords_to_emphasize: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    main_message: str = ""
    value_proposition: str = ""
    angle: str = ""
    hook: str = ""
    
    # Audience
    persona: str = ""
    pain_points: List[str] = field(default_factory=list)
    desires: List[str] = field(default_factory=list)
    
    # Constraints
    avoid_topics: List[str] = field(default_factory=list)
    required_elements: List[str] = field(default_factory=list)
    
    # Structure
    objective: str = "engagement"
    narrative_arc: str = ""
    estimated_slides: int = 7
    
    # Context (for reference)
    article_context: str = ""
    key_insights_used: List[str] = field(default_factory=list)
    
    # Brand
    brand_values: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
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
                "brand_values": self.brand_values,
            },
        }
    
    def validate(self) -> List[str]:
        """
        Validate coherence brief completeness.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        if not self.post_id:
            errors.append("post_id is required")
        if not self.idea_id:
            errors.append("idea_id is required")
        if not self.platform:
            errors.append("platform is required")
        if not self.format:
            errors.append("format is required")
        if not self.tone:
            errors.append("tone is required")
        
        # Visual requirements
        if not self.palette_id:
            errors.append("palette_id is required")
        if not self.palette:
            errors.append("palette is required")
        if not self.typography_id:
            errors.append("typography_id is required")
        if not self.canvas:
            errors.append("canvas is required")
        
        # Content requirements
        if not self.main_message and not self.hook:
            errors.append("main_message or hook is required")
        
        # Structure requirements
        if self.estimated_slides < 1:
            errors.append("estimated_slides must be at least 1")
        
        return errors
    
    def to_prompt_context(self) -> str:
        """
        Format as a readable context block for LLM prompts.
        
        This is what gets injected into narrative architect, copywriter, etc.
        """
        palette_preview = ""
        if self.palette:
            primary = self.palette.get("primary", "")
            accent = self.palette.get("accent", "")
            palette_preview = f" ({primary}, {accent})" if primary and accent else ""
        
        typography_preview = ""
        if self.typography:
            heading_font = self.typography.get("heading_font", "")
            typography_preview = f" ({heading_font})" if heading_font else ""
        
        return f"""
=== COHERENCE BRIEF ===

VOICE:
- Tone: {self.tone}
- Personality: {', '.join(self.personality_traits[:5]) if self.personality_traits else 'N/A'}
- Vocabulary: {self.vocabulary_level}
- Formality: {self.formality}

VISUAL:
- Palette: {self.palette_id}{palette_preview}
- Typography: {self.typography_id}{typography_preview}
- Style: {self.visual_style}
- Mood: {self.visual_mood}

EMOTIONS:
- Primary: {self.primary_emotion}
- Secondary: {', '.join(self.secondary_emotions[:3]) if self.secondary_emotions else 'N/A'}
- Avoid: {', '.join(self.avoid_emotions[:3]) if self.avoid_emotions else 'N/A'}

CONTENT:
- Main Message: {self.main_message}
- Value Prop: {self.value_proposition}
- Keywords: {', '.join(self.keywords_to_emphasize[:5]) if self.keywords_to_emphasize else 'N/A'}
- Angle: {self.angle}
- Hook: {self.hook}

AUDIENCE:
- Persona: {self.persona}
- Pain Points: {', '.join(self.pain_points[:3]) if self.pain_points else 'N/A'}
- Desires: {', '.join(self.desires[:3]) if self.desires else 'N/A'}

STRUCTURE:
- Objective: {self.objective}
- Arc: {self.narrative_arc}
- Slides: {self.estimated_slides}

CONSTRAINTS:
- Avoid: {', '.join(self.avoid_topics[:3]) if self.avoid_topics else 'N/A'}
- Required: {', '.join(self.required_elements) if self.required_elements else 'N/A'}

BRAND:
- Values: {', '.join(self.brand_values) if self.brand_values else 'N/A'}

======================
"""

