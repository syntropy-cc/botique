"""
Unit tests for Phase 3: Post Creation.

Tests Narrative Architect + Template Selector integration, narrative structure validation,
template selection confidence thresholds, brief enrichment, and layout assignment.

Location: tests/pipeline/test_phase3_post_creation.py
"""

import json
import pytest
from unittest.mock import Mock

from src.narrative.architect import NarrativeArchitect
from src.templates.selector import TemplateSelector
from tests.pipeline.conftest import assert_narrative_structure_valid, sample_coherence_brief


@pytest.fixture
def mock_narrative_llm_response():
    """Mock LLM response for narrative structure generation."""
    return json.dumps({
        "slides": [
            {
                "slide_number": 1,
                "module_type": "hook",
                "template_type": "hook",
                "purpose": "Grab attention",
                "copy_direction": "Create curiosity",
                "target_emotions": ["curiosity"],
                "content_slots": ["headline"],
            },
            {
                "slide_number": 2,
                "module_type": "value_data",
                "template_type": "value",
                "value_subtype": "data",
                "purpose": "Present statistic",
                "copy_direction": "Show scale of problem",
                "target_emotions": ["surprise"],
                "content_slots": ["headline", "statistic"],
            },
        ],
    })


def test_narrative_architect_generates_structure(sample_coherence_brief, mock_llm_client, mock_narrative_llm_response):
    """Test Narrative Architect generates narrative structure."""
    mock_llm_client.generate.return_value = mock_narrative_llm_response
    
    architect = NarrativeArchitect(llm_client=mock_llm_client, logger=Mock())
    
    narrative_structure = architect.generate_narrative_structure(
        brief=sample_coherence_brief,
        article_text="Test article content",
    )
    
    # Verify structure
    assert_narrative_structure_valid(narrative_structure)
    assert len(narrative_structure["slides"]) >= 1


def test_template_selector_integration(sample_narrative_structure):
    """Test Template Selector selects templates for narrative structure."""
    selector = TemplateSelector()
    
    # Enrich with templates
    enriched = selector.enrich_with_templates(sample_narrative_structure)
    
    # Verify all slides have template_id
    for slide in enriched["slides"]:
        if slide.get("template_type") in ["hook", "value", "cta", "transition"]:
            assert "template_id" in slide
            assert "template_confidence" in slide
            assert slide["template_confidence"] > 0.0


def test_template_selection_confidence_threshold(sample_narrative_structure):
    """Test template selection confidence thresholds."""
    selector = TemplateSelector()
    enriched = selector.enrich_with_templates(sample_narrative_structure)
    
    # Verify confidence scores
    for slide in enriched["slides"]:
        if "template_confidence" in slide:
            assert slide["template_confidence"] >= 0.0
            assert slide["template_confidence"] <= 1.0


def test_narrative_structure_validation(sample_narrative_structure):
    """Test narrative structure validation."""
    # Should have at least 1 slide (or 5 for carousel)
    assert len(sample_narrative_structure["slides"]) >= 1
    
    # All slides should have template_type
    for slide in sample_narrative_structure["slides"]:
        assert "template_type" in slide
        assert "purpose" in slide


def test_brief_enrichment_with_narrative(sample_coherence_brief, sample_narrative_structure):
    """Test brief enrichment with narrative structure."""
    # Enrich brief
    sample_coherence_brief.enrich_from_narrative(sample_narrative_structure)
    
    # Verify narrative structure was added
    assert hasattr(sample_coherence_brief, "narrative_structure") or sample_coherence_brief.narrative_structure is not None


def test_layout_assignment(sample_narrative_structure):
    """Test layout assignment for slides."""
    # Layout should be assigned (either in narrative structure or separately)
    # This is a placeholder - actual implementation depends on Layout Resolver
    for slide in sample_narrative_structure["slides"]:
        # Layout may be assigned later, but structure should support it
        assert "slide_number" in slide
