"""
Coherence brief builder module

Constructs brand-aligned coherence briefs from ideas and platform configs.

Location: src/coherence/builder.py
"""

from typing import Any, Dict, List

from .brief import CoherenceBrief
from ..brand.library import BrandLibrary
from ..brand.audience import get_audience_profile, enrich_idea_with_audience


class CoherenceBriefBuilder:
    """
    Builds brand-aligned coherence briefs from ideas.
    
    Responsibilities:
    1. Extract idea attributes from LLM response
    2. Select appropriate platform-specific configs (palette, typography, canvas)
    3. Enrich with audience profile data
    4. Derive visual attributes (style, mood)
    5. Detect brand value alignment
    6. Validate completeness
    """
    
    @staticmethod
    def build_from_idea(
        idea: Dict[str, Any],
        article_summary: Dict[str, Any],
        post_id: str,
    ) -> CoherenceBrief:
        """
        Build complete coherence brief from idea.
        
        Args:
            idea: Idea dict from post_ideator output
            article_summary: Article summary for context
            post_id: Unique identifier for this post
        
        Returns:
            Complete CoherenceBrief object
        """
        platform = idea["platform"]
        format_type = idea["format"]
        tone = idea["tone"]
        persona = idea.get("persona", "")
        
        # =====================================================================
        # SELECT BRAND-ALIGNED CONFIGURATIONS
        # =====================================================================
        
        palette = BrandLibrary.select_palette(platform, tone, persona)
        typography = BrandLibrary.select_typography(platform, persona)
        canvas = BrandLibrary.get_canvas_config(platform, format_type)
        
        # =====================================================================
        # ENRICH WITH AUDIENCE PROFILE
        # =====================================================================
        
        audience_profile = get_audience_profile(persona)
        if audience_profile:
            idea = enrich_idea_with_audience(idea, audience_profile)
        
        # Extract enriched attributes
        personality_traits = idea.get("personality_traits", [])
        pain_points = idea.get("pain_points", [])
        desires = idea.get("desires", [])
        vocabulary_level = idea.get("vocabulary_level", "moderate")
        formality = idea.get("formality", "neutral")
        
        # =====================================================================
        # DERIVE VISUAL ATTRIBUTES
        # =====================================================================
        
        visual_style = CoherenceBriefBuilder._derive_visual_style(tone, persona)
        visual_mood = CoherenceBriefBuilder._derive_visual_mood(
            idea.get("primary_emotion", ""), tone
        )
        
        # =====================================================================
        # DETECT BRAND VALUES
        # =====================================================================
        
        brand_values = CoherenceBriefBuilder._detect_brand_values(
            article_summary, idea
        )
        
        # =====================================================================
        # BUILD REQUIRED ELEMENTS
        # =====================================================================
        
        required_elements = ["brand_handle"]
        
        if idea.get("objective") == "conversion":
            required_elements.append("cta")
        
        if platform == "linkedin":
            required_elements.append("professional_cta")
        
        # =====================================================================
        # EXTRACT KEY INSIGHTS CONTENT
        # =====================================================================
        
        key_insights_used = idea.get("key_insights_used", [])
        all_insights = article_summary.get("key_insights", [])
        key_insights_content = [
            insight for insight in all_insights
            if insight.get("id") in key_insights_used
        ]
        
        # =====================================================================
        # BUILD BRAND ASSETS
        # =====================================================================
        
        brand_assets = {
            "handle": "@syntropy",  # Default, can be configured
            "tagline": "Go deep or go home",
        }
        
        # =====================================================================
        # CONSTRUCT COHERENCE BRIEF
        # =====================================================================
        
        return CoherenceBrief(
            # Metadata
            post_id=post_id,
            idea_id=idea["id"],
            platform=platform,
            format=format_type,
            
            # Voice
            tone=tone,
            personality_traits=personality_traits[:5],  # Top 5
            vocabulary_level=vocabulary_level,
            formality=formality,
            
            # Visual (Brand-aligned)
            palette_id=palette.id,
            palette={
                "primary": palette.primary,
                "secondary": palette.secondary,
                "accent": palette.accent,
                "background": palette.background,
                "text": palette.text,
                "text_secondary": palette.text_secondary,
                "cta": palette.cta,
                "details_1": palette.details_1,
                "details_2": palette.details_2,
                "theme": palette.theme,
            },
            typography_id=typography.id,
            typography={
                "heading_font": typography.heading_font,
                "body_font": typography.body_font,
                "heading_weight": typography.weights.get("heading", "700"),
                "body_weight": typography.weights.get("body", "400"),
            },
            visual_style=visual_style,
            visual_mood=visual_mood,
            canvas={
                "width": canvas.width,
                "height": canvas.height,
                "aspect_ratio": canvas.aspect_ratio,
            },
            
            # Emotions
            primary_emotion=idea.get("primary_emotion", ""),
            secondary_emotions=idea.get("secondary_emotions", []),
            avoid_emotions=idea.get("avoid_emotions", []),
            target_emotions=idea.get("target_emotions", []),
            
            # Content
            keywords_to_emphasize=idea.get("keywords_to_emphasize", []),
            themes=article_summary.get("themes", []),
            main_message=article_summary.get("main_message", ""),
            value_proposition=idea.get("value_proposition", ""),
            angle=idea.get("angle", ""),
            hook=idea.get("hook", ""),
            
            # Audience
            persona=persona,
            pain_points=pain_points[:5],  # Top 5
            desires=desires[:5],  # Top 5
            
            # Constraints
            avoid_topics=article_summary.get("avoid_topics", []),
            required_elements=required_elements,
            
            # Structure
            objective=idea.get("objective", "engagement"),
            narrative_arc=idea.get("narrative_arc", ""),
            estimated_slides=idea.get("estimated_slides", 7),
            
            # Context
            article_context=idea.get("article_context_for_idea", ""),
            key_insights_used=idea.get("key_insights_used", []),
            key_insights_content=key_insights_content,
            idea_explanation=idea.get("idea_explanation"),
            rationale=idea.get("rationale"),
            
            # Brand
            brand_values=brand_values,
            brand_assets=brand_assets,
        )
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    @staticmethod
    def _derive_visual_style(tone: str, persona: str) -> str:
        """
        Derive visual style aligned with brand identity.
        
        Maps tone and persona to visual style categories:
        - C-Level: Clean, professional, data-driven
        - Founders: Bold, visionary, action-oriented
        - Developers: Technical, code-focused, minimalist
        
        Args:
            tone: Content tone
            persona: Target persona
        
        Returns:
            Visual style identifier
        """
        tone_lower = tone.lower()
        persona_lower = persona.lower()
        
        # C-Level: Clean, professional, data-driven
        if any(x in persona_lower for x in ["c-level", "executive", "decisor"]):
            return "clean_professional_data_focused"
        
        # Founders: Bold, visionary, action-oriented
        elif any(x in persona_lower for x in ["founder", "visionário", "startup"]):
            return "bold_visionary_action_driven"
        
        # Developers: Technical, code-focused, minimalist
        elif any(x in persona_lower for x in ["developer", "dev", "forjador"]):
            return "technical_code_focused_minimal"
        
        # Tone-based fallbacks
        elif "professional" in tone_lower:
            return "clean_corporate"
        elif any(x in tone_lower for x in ["urgent", "critical"]):
            return "bold_dramatic"
        elif "empowering" in tone_lower:
            return "vibrant_energetic"
        else:
            return "modern_balanced"
    
    @staticmethod
    def _derive_visual_mood(primary_emotion: str, tone: str) -> str:
        """
        Derive visual mood from emotions.
        
        Maps emotional targets to visual mood keywords.
        
        Args:
            primary_emotion: Primary emotional target
            tone: Content tone
        
        Returns:
            Visual mood identifier
        """
        emotion_lower = primary_emotion.lower()
        
        mood_map = {
            "urgency": "dramatic_focused",
            "excitement": "energetic_vibrant",
            "curiosity": "intriguing_exploratory",
            "motivation": "uplifting_inspiring",
            "trust": "calm_authoritative",
            "inspiration": "aspirational_bold",
            "determination": "strong_confident",
            "empowerment": "bold_empowering",
        }
        
        return mood_map.get(emotion_lower, "balanced_professional")
    
    @staticmethod
    def _detect_brand_values(
        article_summary: Dict[str, Any],
        idea: Dict[str, Any]
    ) -> List[str]:
        """
        Detect which brand values align with this content.
        
        Analyzes article themes, keywords, and idea attributes to identify
        alignment with brand values:
        - go_deep_or_go_home
        - open_source
        - community_collaboration
        - pioneer_new_world
        
        Args:
            article_summary: Article summary dict
            idea: Idea dict
        
        Returns:
            List of aligned brand value identifiers
        """
        detected_values = []
        
        # Collect all text for analysis
        themes = article_summary.get("themes", [])
        keywords = article_summary.get("keywords", [])
        idea_keywords = idea.get("keywords_to_emphasize", [])
        
        all_text = " ".join([
            " ".join(themes),
            " ".join(keywords),
            " ".join(idea_keywords),
            article_summary.get("main_message", ""),
            idea.get("angle", ""),
            idea.get("value_proposition", ""),
        ]).lower()
        
        # Brand value keyword mappings
        value_keywords = {
            "go_deep_or_go_home": [
                "deep", "depth", "comprehensive", "detailed", "mastery",
                "expert", "advanced", "profundo", "maestria"
            ],
            "open_source": [
                "open source", "oss", "transparent", "collaborative",
                "community-driven", "código aberto", "transparente"
            ],
            "community_collaboration": [
                "community", "collaboration", "together", "shared",
                "collective", "comunidade", "colaboração", "juntos"
            ],
            "pioneer_new_world": [
                "pioneer", "first", "innovative", "revolutionary",
                "explore", "new", "pioneiro", "inovador", "explorar"
            ]
        }
        
        # Check for keyword matches
        for value_id, keywords_list in value_keywords.items():
            if any(kw in all_text for kw in keywords_list):
                detected_values.append(value_id)
        
        # If none detected, add default community value
        if not detected_values:
            detected_values.append("community_collaboration")
        
        return detected_values
    
    @staticmethod
    def validate_brief(brief: CoherenceBrief) -> None:
        """
        Validate coherence brief completeness.
        
        Args:
            brief: CoherenceBrief to validate
        
        Raises:
            ValueError: If validation fails
        """
        errors = brief.validate()
        
        if errors:
            error_msg = "\n".join([f"  - {err}" for err in errors])
            raise ValueError(
                f"Coherence brief validation failed:\n{error_msg}"
            )