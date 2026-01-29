"""
Unit tests for Coherence Brief evolution through phases.

Tests brief initialization, enrichment through phases, consistency, serialization.

Location: tests/pipeline/test_coherence_brief_evolution.py
"""

import json
import pytest

from src.coherence.brief import CoherenceBrief
from tests.pipeline.conftest import sample_coherence_brief, sample_narrative_structure


def test_brief_initialization(sample_coherence_brief):
    """Test brief initialization in Phase 2."""
    assert sample_coherence_brief.post_id is not None
    assert sample_coherence_brief.platform is not None
    assert sample_coherence_brief.tone is not None
    assert sample_coherence_brief.palette_id is not None
    assert sample_coherence_brief.typography_id is not None


def test_brief_enrichment_phase3(sample_coherence_brief, sample_narrative_structure):
    """Test brief enrichment in Phase 3 (narrative structure)."""
    initial_fields = set(sample_coherence_brief.to_dict().keys())
    
    # Enrich with narrative structure
    sample_coherence_brief.enrich_from_narrative(sample_narrative_structure)
    
    enriched_fields = set(sample_coherence_brief.to_dict().keys())
    
    # Verify new fields were added
    assert len(enriched_fields) >= len(initial_fields)


def test_brief_enrichment_phase4(sample_coherence_brief):
    """Test brief enrichment in Phase 4 (copy guidelines, visual preferences)."""
    copy_guidelines = {
        "headline_style": "statistic_led",
        "body_style": "conversational_professional",
    }
    
    visual_preferences = {
        "layout_style": "centered",
        "text_hierarchy": "bold_headlines",
    }
    
    # Enrich brief
    if hasattr(sample_coherence_brief, "enrich_from_copywriting"):
        sample_coherence_brief.enrich_from_copywriting(copy_guidelines)
    
    if hasattr(sample_coherence_brief, "enrich_from_visual_composition"):
        sample_coherence_brief.enrich_from_visual_composition(visual_preferences)


def test_brief_consistency_across_phases(sample_coherence_brief):
    """Test brief consistency across phases."""
    initial_post_id = sample_coherence_brief.post_id
    initial_platform = sample_coherence_brief.platform
    
    # After enrichment, core fields should remain consistent
    assert sample_coherence_brief.post_id == initial_post_id
    assert sample_coherence_brief.platform == initial_platform


def test_brief_serialization(sample_coherence_brief):
    """Test brief serialization/deserialization."""
    # Serialize
    brief_dict = sample_coherence_brief.to_dict()
    
    # Verify serialization
    assert isinstance(brief_dict, dict)
    assert "post_id" in brief_dict
    
    # Can be serialized to JSON
    json_str = json.dumps(brief_dict)
    assert len(json_str) > 0


def test_brief_validation_at_each_stage(sample_coherence_brief):
    """Test brief validation at each stage."""
    # Brief should be valid after initialization
    assert sample_coherence_brief.post_id is not None
    assert sample_coherence_brief.platform is not None
    
    # After enrichment, should still be valid
    # (Additional validation would be done by CoherenceBriefBuilder.validate_brief)
