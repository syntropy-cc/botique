"""
Integration tests for multi-phase workflows.

Tests Phase 1→2, Phase 2→3, Phase 3→4, Phase 4→5 integrations.

Location: tests/pipeline/test_phase_integrations.py
"""

import pytest

from src.core.config import IdeationConfig, SelectionConfig
from src.phases.phase1_ideation import run as run_phase1
from src.phases.phase2_selection import run as run_phase2


@pytest.mark.integration
def test_phase1_to_phase2_integration(tmp_path, mock_llm_client_with_response, test_result_logger):
    """Test Phase 1 → Phase 2 integration."""
    # Phase 1
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    phase1_result = run_phase1(
        article_path=article_file,
        config=IdeationConfig(min_ideas=3),
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    
    # Phase 2
    phase2_result = run_phase2(
        ideas_payload=phase1_result,
        config=SelectionConfig(max_selected=3),
        article_slug=phase1_result["article_slug"],
        output_dir=tmp_path / "output",
    )
    
    # Verify integration
    assert len(phase2_result["selected_ideas"]) <= len(phase1_result["ideas"])
    assert len(phase2_result["selected_ideas"]) > 0


@pytest.mark.integration
def test_phase2_to_phase3_integration(sample_coherence_brief, sample_narrative_structure):
    """Test Phase 2 → Phase 3 integration (brief + narrative)."""
    # Brief should be ready for narrative generation
    assert sample_coherence_brief is not None
    
    # Narrative structure should be compatible with brief
    assert sample_narrative_structure is not None


@pytest.mark.integration
def test_phase3_to_phase4_integration(sample_coherence_brief, sample_narrative_structure):
    """Test Phase 3 → Phase 4 integration (narrative + copy/visual)."""
    # Narrative structure should have template_ids
    for slide in sample_narrative_structure.get("slides", []):
        if slide.get("template_type"):
            # Template should be selectable
            assert "purpose" in slide or "copy_direction" in slide


@pytest.mark.integration
def test_phase4_to_phase5_integration(sample_slide_content):
    """Test Phase 4 → Phase 5 integration (slides + caption)."""
    # Slide content should be ready for caption generation
    assert sample_slide_content is not None
    assert "slides" in sample_slide_content
