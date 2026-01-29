"""
Unit tests for CoherenceBriefBuilder.

Tests brief construction, validation, and derivation logic.

Location: tests/tools/coherence/test_builder.py
"""

import unittest
from unittest.mock import patch, MagicMock

from src.coherence.builder import CoherenceBriefBuilder
from src.coherence.brief import CoherenceBrief
from tests.tools.utils import (
    create_sample_idea,
    create_sample_article_summary,
    assert_brief_valid,
)


class TestBuildFromIdea(unittest.TestCase):
    """Test cases for build_from_idea method."""
    
    def test_build_from_idea_basic(self):
        """Test basic brief construction from idea."""
        idea = create_sample_idea()
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        assert_brief_valid(brief)
        self.assertEqual(brief.post_id, "post_001")
        self.assertEqual(brief.idea_id, idea["id"])
        self.assertEqual(brief.platform, idea["platform"])
        self.assertEqual(brief.format, idea["format"])
        self.assertEqual(brief.tone, idea["tone"])
    
    def test_build_from_idea_audience_enrichment(self):
        """Test that brief includes audience enrichment."""
        idea = create_sample_idea(persona="C-Level executives")
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        # Should have enriched personality traits
        self.assertIsNotNone(brief.personality_traits)
        self.assertGreater(len(brief.personality_traits), 0)
    
    def test_build_from_idea_brand_selection(self):
        """Test that brand assets are selected correctly."""
        idea = create_sample_idea(
            platform="linkedin",
            tone="professional",
            persona="C-Level executives",
        )
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        # Should have palette and typography
        self.assertIsNotNone(brief.palette_id)
        self.assertIsNotNone(brief.palette)
        self.assertIsNotNone(brief.typography_id)
        self.assertIsNotNone(brief.typography)
        self.assertIsNotNone(brief.canvas)
        
        # Palette should match brand selection
        self.assertIn("professional", brief.palette_id.lower())
    
    def test_build_from_idea_visual_attributes(self):
        """Test that visual style and mood are derived."""
        idea = create_sample_idea(
            tone="professional",
            persona="C-Level executives",
        )
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        self.assertIsNotNone(brief.visual_style)
        self.assertIsNotNone(brief.visual_mood)
    
    def test_build_from_idea_brand_values(self):
        """Test that brand values are detected."""
        idea = create_sample_idea()
        article_summary = create_sample_article_summary(
            main_message="Deep dive into automation with open source community"
        )
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        self.assertIsNotNone(brief.brand_values)
        self.assertIsInstance(brief.brand_values, list)
        # Should detect values from content
        self.assertGreater(len(brief.brand_values), 0)
    
    def test_build_from_idea_key_insights(self):
        """Test that key insights are filtered correctly."""
        idea = create_sample_idea(key_insights_used=["insight_1", "insight_2"])
        article_summary = create_sample_article_summary()
        article_summary["key_insights"] = [
            {"id": "insight_1", "content": "First insight"},
            {"id": "insight_2", "content": "Second insight"},
            {"id": "insight_3", "content": "Third insight"},
        ]
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        # Should only include used insights
        self.assertEqual(len(brief.key_insights_content), 2)
        insight_ids = [insight["id"] for insight in brief.key_insights_content]
        self.assertIn("insight_1", insight_ids)
        self.assertIn("insight_2", insight_ids)
        self.assertNotIn("insight_3", insight_ids)
    
    def test_build_from_idea_required_elements(self):
        """Test that required elements are set correctly."""
        # Conversion objective should require CTA
        idea = create_sample_idea(objective="conversion")
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        self.assertIn("brand_handle", brief.required_elements)
        self.assertIn("cta", brief.required_elements)
        
        # LinkedIn should require professional CTA
        idea2 = create_sample_idea(platform="linkedin")
        brief2 = CoherenceBriefBuilder.build_from_idea(
            idea=idea2,
            article_summary=article_summary,
            post_id="post_002",
        )
        
        self.assertIn("professional_cta", brief2.required_elements)


class TestValidateBrief(unittest.TestCase):
    """Test cases for validate_brief method."""
    
    def test_validate_brief_success(self):
        """Test successful brief validation."""
        idea = create_sample_idea()
        article_summary = create_sample_article_summary()
        
        brief = CoherenceBriefBuilder.build_from_idea(
            idea=idea,
            article_summary=article_summary,
            post_id="post_001",
        )
        
        # Should not raise exception
        CoherenceBriefBuilder.validate_brief(brief)
    
    def test_validate_brief_failure(self):
        """Test validation failure handling."""
        # Create invalid brief (missing required fields)
        brief = CoherenceBrief(
            post_id="",  # Missing
            idea_id="idea_001",
            platform="",  # Missing
            format="carousel",
            tone="",  # Missing
            personality_traits=[],  # Empty
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="",  # Missing
            palette={},
            typography_id="",  # Missing
            typography={},
            visual_style="clean",
            visual_mood="calm",
            canvas={},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=[],  # Empty
            themes=[],
            main_message="Test",
            value_proposition="Test",
            angle="Test",
            hook="Test",
            persona="Test",
            pain_points=[],
            desires=[],
            avoid_topics=[],
            required_elements=[],
            objective="engagement",
            narrative_arc="linear",
            estimated_slides=7,
            article_context="",
            key_insights_used=[],
            key_insights_content=[],
            brand_values=[],
            brand_assets={},
        )
        
        # Should raise ValueError with validation errors
        with self.assertRaises(ValueError) as context:
            CoherenceBriefBuilder.validate_brief(brief)
        
        error_msg = str(context.exception)
        self.assertIn("validation failed", error_msg.lower())


class TestDeriveVisualStyle(unittest.TestCase):
    """Test cases for visual style derivation."""
    
    def test_derive_visual_style(self):
        """Test visual style derivation logic."""
        # C-Level
        style = CoherenceBriefBuilder._derive_visual_style(
            tone="professional",
            persona="C-Level executives",
        )
        self.assertIn("professional", style.lower())
        
        # Founder
        style2 = CoherenceBriefBuilder._derive_visual_style(
            tone="empowering",
            persona="Founders and entrepreneurs",
        )
        self.assertIn("visionary", style2.lower() or "bold" in style2.lower())
        
        # Developer
        style3 = CoherenceBriefBuilder._derive_visual_style(
            tone="technical",
            persona="Developers and programmers",
        )
        self.assertIn("technical", style3.lower() or "code" in style3.lower())
    
    def test_derive_visual_style_tone_fallback(self):
        """Test tone-based fallback for visual style."""
        # Professional tone
        style = CoherenceBriefBuilder._derive_visual_style(
            tone="professional",
            persona="Unknown",
        )
        self.assertIsNotNone(style)
        
        # Urgent tone
        style2 = CoherenceBriefBuilder._derive_visual_style(
            tone="urgent",
            persona="Unknown",
        )
        self.assertIsNotNone(style2)


class TestDeriveVisualMood(unittest.TestCase):
    """Test cases for visual mood derivation."""
    
    def test_derive_visual_mood(self):
        """Test visual mood derivation logic."""
        mood_map = {
            "urgency": "dramatic_focused",
            "excitement": "energetic_vibrant",
            "curiosity": "intriguing_exploratory",
            "motivation": "uplifting_inspiring",
            "trust": "calm_authoritative",
        }
        
        for emotion, expected_mood in mood_map.items():
            mood = CoherenceBriefBuilder._derive_visual_mood(
                primary_emotion=emotion,
                tone="test",
            )
            self.assertEqual(mood, expected_mood)
    
    def test_derive_visual_mood_unknown(self):
        """Test visual mood derivation for unknown emotion."""
        mood = CoherenceBriefBuilder._derive_visual_mood(
            primary_emotion="unknown_emotion",
            tone="test",
        )
        
        # Should return default
        self.assertIsNotNone(mood)
        self.assertEqual(mood, "balanced_professional")


class TestDetectBrandValues(unittest.TestCase):
    """Test cases for brand value detection."""
    
    def test_detect_brand_values(self):
        """Test brand value detection logic."""
        article_summary = {
            "themes": ["deep learning", "comprehensive analysis"],
            "keywords": ["deep", "mastery"],
            "main_message": "Go deep or go home",
        }
        idea = {
            "keywords_to_emphasize": ["deep", "comprehensive"],
            "angle": "Master deep understanding",
            "value_proposition": "Achieve mastery",
        }
        
        values = CoherenceBriefBuilder._detect_brand_values(
            article_summary=article_summary,
            idea=idea,
        )
        
        self.assertIsInstance(values, list)
        self.assertGreater(len(values), 0)
        # Should detect "go_deep_or_go_home"
        self.assertIn("go_deep_or_go_home", values)
    
    def test_detect_brand_values_keywords(self):
        """Test brand value detection by keywords."""
        # Test open source keywords
        article_summary = {
            "themes": ["open source", "community"],
            "keywords": ["open source", "transparent"],
            "main_message": "Open source collaboration",
        }
        idea = {
            "keywords_to_emphasize": ["open source"],
            "angle": "",
            "value_proposition": "",
        }
        
        values = CoherenceBriefBuilder._detect_brand_values(
            article_summary=article_summary,
            idea=idea,
        )
        
        self.assertIn("open_source", values)
        
        # Test community keywords
        article_summary2 = {
            "themes": ["community", "collaboration"],
            "keywords": ["community", "together"],
            "main_message": "Community collaboration",
        }
        
        values2 = CoherenceBriefBuilder._detect_brand_values(
            article_summary=article_summary2,
            idea=idea,
        )
        
        self.assertIn("community_collaboration", values2)
    
    def test_detect_brand_values_default(self):
        """Test default brand value when none detected."""
        article_summary = {
            "themes": ["generic"],
            "keywords": ["generic"],
            "main_message": "Generic message",
        }
        idea = {
            "keywords_to_emphasize": ["generic"],
            "angle": "",
            "value_proposition": "",
        }
        
        values = CoherenceBriefBuilder._detect_brand_values(
            article_summary=article_summary,
            idea=idea,
        )
        
        # Should have at least default value
        self.assertGreater(len(values), 0)
        self.assertIn("community_collaboration", values)


if __name__ == "__main__":
    unittest.main()
