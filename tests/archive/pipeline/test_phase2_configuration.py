"""
Unit tests for Phase 2: Configuration.

Tests Coherence Brief building from ideas, Parameter Resolver (palette, typography),
brief validation, brief enrichment with article summary, and different platform/tone combinations.

Location: tests/pipeline/test_phase2_configuration.py
"""

import pytest

from src.coherence.builder import CoherenceBriefBuilder
from tests.pipeline.conftest import assert_brief_valid, sample_idea, sample_article_summary


def test_build_brief_from_idea(sample_idea, sample_article_summary):
    """Test building coherence brief from idea."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Verify brief is valid
    assert_brief_valid(brief)
    
    # Verify brief has correct post_id
    assert brief.post_id == "test_post_001"
    assert brief.idea_id == sample_idea["id"]
    
    # Verify platform and tone match idea
    assert brief.platform == sample_idea["platform"]
    assert brief.tone == sample_idea["tone"]
    
    # Verify palette and typography are set
    assert brief.palette_id is not None
    assert brief.typography_id is not None
    assert brief.palette is not None
    assert brief.typography is not None


def test_brief_validation(sample_idea, sample_article_summary):
    """Test brief validation."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Validate brief
    CoherenceBriefBuilder.validate_brief(brief)
    
    # Should not raise exception if valid


def test_different_platform_tone_combinations(sample_article_summary):
    """Test brief building with different platform/tone combinations."""
    platforms = ["linkedin", "twitter", "instagram"]
    tones = ["professional", "casual", "conversational"]
    
    for platform in platforms:
        for tone in tones:
            idea = {
                "id": f"idea_{platform}_{tone}",
                "platform": platform,
                "format": "carousel" if platform != "twitter" else "single_image",
                "tone": tone,
                "persona": "Test persona",
                "objective": "engagement",
                "narrative_arc": "problem-solution",
                "estimated_slides": 5,
                "hook": "Test hook",
                "angle": "Test angle",
                "value_proposition": "Test value",
                "key_insights_used": [],
                "keywords_to_emphasize": [],
                "primary_emotion": "curiosity",
                "secondary_emotions": [],
                "avoid_emotions": [],
                "personality_traits": [],
                "pain_points": [],
                "desires": [],
                "vocabulary_level": "moderate",
                "formality": "neutral",
            }
            
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=sample_article_summary,
                post_id=f"post_{platform}_{tone}",
            )
            
            # Verify brief is valid for each combination
            assert_brief_valid(brief)
            assert brief.platform == platform
            assert brief.tone == tone


def test_brief_enrichment_with_article_summary(sample_idea, sample_article_summary):
    """Test brief enrichment with article summary."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Verify article summary data is incorporated
    assert brief.themes is not None
    assert brief.keywords_to_emphasize is not None
    assert brief.main_message is not None
    
    # Verify key insights are included if present
    if sample_article_summary.get("key_insights"):
        assert brief.key_insights_content is not None


def test_parameter_resolver_palette_selection(sample_idea, sample_article_summary):
    """Test Parameter Resolver selects appropriate palette."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Verify palette is selected based on platform + tone
    assert brief.palette_id is not None
    assert brief.palette is not None
    
    # Verify palette has required fields
    assert "primary" in brief.palette or "theme" in brief.palette


def test_parameter_resolver_typography_selection(sample_idea, sample_article_summary):
    """Test Parameter Resolver selects appropriate typography."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Verify typography is selected based on platform + tone
    assert brief.typography_id is not None
    assert brief.typography is not None
    
    # Verify typography has required fields
    assert "heading_font" in brief.typography or "body_font" in brief.typography


def test_brief_canvas_configuration(sample_idea, sample_article_summary):
    """Test brief canvas configuration based on platform."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Verify canvas is configured
    assert brief.canvas is not None
    assert "width" in brief.canvas
    assert "height" in brief.canvas
    
    # Verify dimensions are appropriate for platform
    if brief.platform == "linkedin":
        # LinkedIn carousel is typically square
        assert brief.canvas["width"] == brief.canvas["height"]


def test_brief_serialization(sample_idea, sample_article_summary):
    """Test brief serialization to dict."""
    brief = CoherenceBriefBuilder.build_from_idea(
        idea=sample_idea,
        article_summary=sample_article_summary,
        post_id="test_post_001",
    )
    
    # Serialize to dict
    brief_dict = brief.to_dict()
    
    # Verify dict has required fields
    assert "post_id" in brief_dict
    assert "platform" in brief_dict
    assert "tone" in brief_dict
    assert "palette_id" in brief_dict
    assert "typography_id" in brief_dict
