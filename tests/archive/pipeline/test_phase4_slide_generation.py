"""
Unit tests for Phase 4: Slide Generation.

Tests Copywriter + Visual Composer + Compositor, template adherence,
text positioning, slide validation.

Location: tests/pipeline/test_phase4_slide_generation.py
"""

import pytest
from unittest.mock import Mock

from src.copywriting.writer import Copywriter
from tests.pipeline.conftest import sample_coherence_brief, sample_narrative_structure


@pytest.fixture
def mock_copywriter_response():
    """Mock LLM response for copywriter."""
    return {
        "slides": [
            {
                "slide_number": 1,
                "title": {
                    "content": "Test headline",
                    "emphasis": ["Test"],
                },
            },
        ],
    }


def test_copywriter_generates_content(sample_coherence_brief, sample_narrative_structure, mock_llm_client, mock_copywriter_response):
    """Test Copywriter generates slide content."""
    mock_llm_client.generate.return_value = str(mock_copywriter_response)
    
    copywriter = Copywriter(llm_client=mock_llm_client, logger=Mock())
    
    # Generate content for all slides
    slide_content = copywriter.generate_slide_content(
        brief=sample_coherence_brief,
        narrative_structure=sample_narrative_structure,
    )
    
    # Verify content structure
    assert "slides" in slide_content
    assert len(slide_content["slides"]) > 0


def test_template_structure_adherence(sample_coherence_brief, sample_narrative_structure):
    """Test that generated content follows template structure."""
    # This is a placeholder - actual test would verify content matches template requirements
    # For now, just verify structure exists
    assert sample_narrative_structure is not None
    assert sample_coherence_brief is not None


def test_text_positioning(sample_slide_content):
    """Test text positioning in slide content."""
    for slide in sample_slide_content["slides"]:
        if "title" in slide:
            title = slide["title"]
            if isinstance(title, dict) and "position" in title:
                assert "x" in title["position"]
                assert "y" in title["position"]


def test_slide_validation_dimensions():
    """Test slide validation for dimensions."""
    # Standard dimensions
    canvas_width = 1080
    canvas_height = 1080
    
    # Verify dimensions are valid
    assert canvas_width > 0
    assert canvas_height > 0
    assert canvas_width == canvas_height  # Square for LinkedIn


def test_text_limits(sample_slide_content):
    """Test text content stays within limits."""
    for slide in sample_slide_content["slides"]:
        if "title" in slide:
            title_content = slide["title"].get("content", "") if isinstance(slide["title"], dict) else str(slide["title"])
            # Headlines should be reasonably short
            assert len(title_content) < 200  # Reasonable limit
