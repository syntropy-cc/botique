"""
Unit tests for CoherenceBrief data model.

Tests brief creation, serialization, validation, and enrichment methods.

Location: tests/tools/coherence/test_brief.py
"""

import unittest

from src.coherence.brief import CoherenceBrief
from tests.tools.utils import (
    create_sample_idea,
    create_sample_article_summary,
    assert_brief_valid,
)


class TestBriefCreation(unittest.TestCase):
    """Test cases for brief creation."""
    
    def test_brief_creation(self):
        """Test basic brief creation."""
        brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative", "strategic"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={
                "primary": "#FFFFFF",
                "secondary": "#F5F5F5",
                "accent": "#0060FF",
                "background": "#FFFFFF",
                "text": "#222831",
                "text_secondary": "#666666",
                "cta": "#FF6B00",
                "details_1": "#0060FF",
                "details_2": "#FF6B00",
                "theme": "light",
            },
            typography_id="brand_professional",
            typography={
                "heading_font": "Inter Bold",
                "body_font": "Inter Regular",
                "heading_weight": "700",
                "body_weight": "400",
            },
            visual_style="clean_professional_data_focused",
            visual_mood="calm_authoritative",
            canvas={"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
            primary_emotion="trust",
            secondary_emotions=["curiosity"],
            avoid_emotions=["fear"],
            target_emotions=["trust", "curiosity"],
            keywords_to_emphasize=["automation", "efficiency"],
            themes=["business", "automation"],
            main_message="Workflow automation is essential",
            value_proposition="Increase efficiency by 40%",
            angle="Modern businesses need smarter automation",
            hook="Did you know that 73% of companies struggle?",
            persona="C-Level executives",
            pain_points=["operational_inefficiency"],
            desires=["efficiency"],
            avoid_topics=["layoffs"],
            required_elements=["brand_handle"],
            objective="engagement",
            narrative_arc="problem-solution",
            estimated_slides=7,
            article_context="Article about workflow automation",
            key_insights_used=["insight_1"],
            key_insights_content=[
                {"id": "insight_1", "content": "Automation reduces work by 60%"}
            ],
            brand_values=["go_deep_or_go_home"],
            brand_assets={"handle": "@syntropy"},
        )
        
        assert_brief_valid(brief)
        self.assertEqual(brief.post_id, "post_001")
        self.assertEqual(brief.platform, "linkedin")
    
    def test_brief_creation_minimal(self):
        """Test brief creation with minimal required fields."""
        brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={
                "primary": "#FFFFFF",
                "secondary": "#F5F5F5",
                "accent": "#0060FF",
                "background": "#FFFFFF",
                "text": "#222831",
                "text_secondary": "#666666",
                "cta": "#FF6B00",
                "details_1": "#0060FF",
                "details_2": "#FF6B00",
                "theme": "light",
            },
            typography_id="brand_professional",
            typography={
                "heading_font": "Inter Bold",
                "body_font": "Inter Regular",
                "heading_weight": "700",
                "body_weight": "400",
            },
            visual_style="clean",
            visual_mood="calm",
            canvas={"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
            themes=[],
            main_message="Test message",
            value_proposition="Test value",
            angle="Test angle",
            hook="Test hook",
            persona="Test persona",
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
        
        assert_brief_valid(brief)


class TestBriefSerialization(unittest.TestCase):
    """Test cases for brief serialization."""
    
    def setUp(self):
        """Set up brief for testing."""
        self.brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={"primary": "#FFFFFF", "accent": "#0060FF", "theme": "light"},
            typography_id="brand_professional",
            typography={"heading_font": "Inter Bold", "body_font": "Inter Regular"},
            visual_style="clean",
            visual_mood="calm",
            canvas={"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
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
    
    def test_brief_to_dict(self):
        """Test brief serialization to dictionary."""
        brief_dict = self.brief.to_dict()
        
        self.assertIsInstance(brief_dict, dict)
        self.assertIn("metadata", brief_dict)
        self.assertIn("voice", brief_dict)
        self.assertIn("visual", brief_dict)
        self.assertIn("content", brief_dict)
        
        # Check metadata
        self.assertEqual(brief_dict["metadata"]["post_id"], "post_001")
        self.assertEqual(brief_dict["metadata"]["platform"], "linkedin")
        
        # Check voice
        self.assertEqual(brief_dict["voice"]["tone"], "professional")
    
    def test_brief_to_dict_structure(self):
        """Test that to_dict produces correct nested structure."""
        brief_dict = self.brief.to_dict()
        
        # Verify nested structure
        self.assertIn("metadata", brief_dict)
        self.assertIn("voice", brief_dict)
        self.assertIn("visual", brief_dict)
        self.assertIn("content", brief_dict)
        self.assertIn("audience", brief_dict)
        self.assertIn("constraints", brief_dict)
        self.assertIn("structure", brief_dict)
        self.assertIn("context", brief_dict)
        self.assertIn("brand", brief_dict)
        self.assertIn("evolution", brief_dict)
        
        # Verify metadata fields
        self.assertEqual(brief_dict["metadata"]["post_id"], self.brief.post_id)
        self.assertEqual(brief_dict["metadata"]["platform"], self.brief.platform)
        
        # Verify voice fields
        self.assertEqual(brief_dict["voice"]["tone"], self.brief.tone)
        self.assertEqual(brief_dict["voice"]["personality_traits"], self.brief.personality_traits)
    
    def test_brief_serialization_preserves_data(self):
        """Test that serialization preserves all data correctly."""
        original_brief = self.brief
        
        # Serialize
        brief_dict = original_brief.to_dict()
        
        # Verify all key fields are in the dict
        self.assertEqual(brief_dict["metadata"]["post_id"], original_brief.post_id)
        self.assertEqual(brief_dict["metadata"]["idea_id"], original_brief.idea_id)
        self.assertEqual(brief_dict["metadata"]["platform"], original_brief.platform)
        self.assertEqual(brief_dict["voice"]["tone"], original_brief.tone)
        self.assertEqual(brief_dict["visual"]["palette_id"], original_brief.palette_id)
        self.assertEqual(brief_dict["visual"]["typography_id"], original_brief.typography_id)


class TestBriefValidation(unittest.TestCase):
    """Test cases for brief validation."""
    
    def test_brief_validate_complete(self):
        """Test validation of complete brief."""
        brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={"primary": "#FFFFFF", "theme": "light"},
            typography_id="brand_professional",
            typography={"heading_font": "Inter Bold"},
            visual_style="clean",
            visual_mood="calm",
            canvas={"width": 1080, "height": 1080},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
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
        
        errors = brief.validate()
        self.assertEqual(len(errors), 0)
    
    def test_brief_validate_missing_required(self):
        """Test validation with missing required fields."""
        brief = CoherenceBrief(
            post_id="",  # Missing
            idea_id="idea_001",
            platform="",  # Missing
            format="carousel",
            tone="",  # Missing
            personality_traits=[],
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
        
        errors = brief.validate()
        self.assertGreater(len(errors), 0)
        self.assertIn("post_id is required", errors)
        self.assertIn("platform is required", errors)
        self.assertIn("tone is required", errors)
        self.assertIn("palette_id is required", errors)
        self.assertIn("typography_id is required", errors)
        self.assertIn("personality_traits cannot be empty", errors)
        self.assertIn("keywords_to_emphasize cannot be empty", errors)
    
    def test_brief_validate_slide_count(self):
        """Test validation of slide count constraints."""
        # Carousel with too few slides
        brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={"primary": "#FFFFFF"},
            typography_id="brand_professional",
            typography={"heading_font": "Inter Bold"},
            visual_style="clean",
            visual_mood="calm",
            canvas={},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
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
            estimated_slides=3,  # Too few for carousel
            article_context="",
            key_insights_used=[],
            key_insights_content=[],
            brand_values=[],
            brand_assets={},
        )
        
        errors = brief.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("estimated_slides" in err for err in errors))
        
        # Single image with 1 slide (valid)
        brief2 = CoherenceBrief(
            post_id="post_002",
            idea_id="idea_002",
            platform="instagram",
            format="single_image",
            tone="casual",
            personality_traits=["friendly"],
            vocabulary_level="moderate",
            formality="casual",
            palette_id="brand_light_community",
            palette={"primary": "#FFFFFF"},
            typography_id="brand_primary",
            typography={"heading_font": "Poppins Bold"},
            visual_style="vibrant",
            visual_mood="energetic",
            canvas={},
            primary_emotion="excitement",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
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
            estimated_slides=1,  # Valid for single_image
            article_context="",
            key_insights_used=[],
            key_insights_content=[],
            brand_values=[],
            brand_assets={},
        )
        
        errors2 = brief2.validate()
        # Should not have slide count error
        self.assertFalse(any("estimated_slides" in err for err in errors2))


class TestBriefEnrichment(unittest.TestCase):
    """Test cases for brief enrichment methods."""
    
    def setUp(self):
        """Set up brief for testing."""
        self.brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={"primary": "#FFFFFF"},
            typography_id="brand_professional",
            typography={"heading_font": "Inter Bold"},
            visual_style="clean",
            visual_mood="calm",
            canvas={},
            primary_emotion="trust",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=[],
            keywords_to_emphasize=["keyword1"],
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
    
    def test_brief_evolution_fields(self):
        """Test evolution fields handling."""
        # Initially None
        self.assertIsNone(self.brief.narrative_structure)
        self.assertIsNone(self.brief.copy_guidelines)
        
        # Enrich with narrative structure
        narrative_structure = {
            "pacing": "moderate",
            "transition_style": "smooth",
            "arc_refined": "Refined arc description",
            "slides": [],
        }
        self.brief.enrich_from_narrative_structure(narrative_structure)
        
        self.assertIsNotNone(self.brief.narrative_structure)
        self.assertEqual(self.brief.narrative_pacing, "moderate")
        self.assertEqual(self.brief.transition_style, "smooth")
        
        # Enrich with copywriting
        copy_guidelines = {
            "headline_style": "bold",
            "body_style": "concise",
            "cta_details": {"type": "button", "text": "Learn More"},
        }
        self.brief.enrich_from_copywriting(copy_guidelines)
        
        self.assertIsNotNone(self.brief.copy_guidelines)
        self.assertIsNotNone(self.brief.cta_guidelines)
    
    def test_brief_default_values(self):
        """Test default value application."""
        # Evolution fields should default to None
        self.assertIsNone(self.brief.narrative_structure)
        self.assertIsNone(self.brief.narrative_pacing)
        self.assertIsNone(self.brief.transition_style)
        self.assertIsNone(self.brief.copy_guidelines)
        self.assertIsNone(self.brief.cta_guidelines)


class TestBriefContextMethods(unittest.TestCase):
    """Test cases for context formatting methods."""
    
    def setUp(self):
        """Set up brief for testing."""
        self.brief = CoherenceBrief(
            post_id="post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative", "strategic"],
            vocabulary_level="sophisticated",
            formality="formal",
            palette_id="brand_light_professional",
            palette={"primary": "#FFFFFF", "theme": "light"},
            typography_id="brand_professional",
            typography={"heading_font": "Inter Bold"},
            visual_style="clean",
            visual_mood="calm",
            canvas={},
            primary_emotion="trust",
            secondary_emotions=["curiosity"],
            avoid_emotions=["fear"],
            target_emotions=["trust"],
            keywords_to_emphasize=["automation"],
            themes=["business"],
            main_message="Test message",
            value_proposition="Test value",
            angle="Test angle",
            hook="Test hook",
            persona="C-Level",
            pain_points=["inefficiency"],
            desires=["efficiency"],
            avoid_topics=["layoffs"],
            required_elements=["brand_handle"],
            objective="engagement",
            narrative_arc="problem-solution",
            estimated_slides=7,
            article_context="Test context",
            key_insights_used=["insight_1"],
            key_insights_content=[{"id": "insight_1", "content": "Test insight"}],
            brand_values=["go_deep"],
            brand_assets={"handle": "@syntropy"},
        )
    
    def test_to_narrative_architect_context(self):
        """Test narrative architect context formatting."""
        context = self.brief.to_narrative_architect_context()
        
        self.assertIsInstance(context, str)
        self.assertIn("Narrative Architect", context)
        self.assertIn("professional", context)
        self.assertIn("trust", context)
        self.assertIn("automation", context)
    
    def test_to_copywriter_context(self):
        """Test copywriter context formatting."""
        context = self.brief.to_copywriter_context()
        
        self.assertIsInstance(context, str)
        self.assertIn("Copywriter", context)
        self.assertIn("professional", context)
    
    def test_to_copywriter_context_with_narrative(self):
        """Test copywriter context with narrative structure."""
        self.brief.enrich_from_narrative_structure({
            "pacing": "moderate",
            "transition_style": "smooth",
            "slides": [],
        })
        
        context = self.brief.to_copywriter_context()
        
        self.assertIn("NARRATIVE STRUCTURE", context)
        self.assertIn("moderate", context)


if __name__ == "__main__":
    unittest.main()
