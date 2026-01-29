"""
Unit tests for Phase 2: Selection.

Tests idea filtering by confidence, diverse selection strategy, top-N selection,
manual selection by IDs, and edge cases.

Location: tests/pipeline/test_phase2_selection.py
"""

import json
import pytest
from pathlib import Path

from src.core.config import SelectionConfig
from src.phases.phase2_selection import run


@pytest.fixture
def sample_ideas_payload(sample_ideas):
    """Create sample ideas payload for Phase 2."""
    return {
        "ideas": sample_ideas,
        "article_summary": {
            "title": "Test Article",
            "main_message": "Test message",
        },
    }


def test_phase2_filters_by_confidence(tmp_path, sample_ideas_payload):
    """Test Phase 2 filters ideas by confidence threshold."""
    # Add confidence scores
    sample_ideas_payload["ideas"][0]["confidence"] = 0.90
    sample_ideas_payload["ideas"][1]["confidence"] = 0.60  # Below threshold
    sample_ideas_payload["ideas"][2]["confidence"] = 0.80
    
    config = SelectionConfig(
        min_confidence=0.70,
        max_selected=5,
        strategy="top",
    )
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify filtering
    assert len(result["selected_ideas"]) <= 2  # Only ideas with confidence >= 0.70
    assert all(idea["confidence"] >= 0.70 for idea in result["selected_ideas"])


def test_phase2_diverse_selection(tmp_path, sample_ideas_payload):
    """Test Phase 2 diverse selection strategy."""
    # Add confidence scores
    for i, idea in enumerate(sample_ideas_payload["ideas"]):
        idea["confidence"] = 0.80 - (i * 0.05)
    
    config = SelectionConfig(
        min_confidence=0.70,
        max_selected=2,
        strategy="diverse",
    )
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify diverse selection (should have different platforms/tones)
    assert len(result["selected_ideas"]) <= 2
    if len(result["selected_ideas"]) > 1:
        platforms = [idea["platform"] for idea in result["selected_ideas"]]
        tones = [idea["tone"] for idea in result["selected_ideas"]]
        # Should have some diversity
        assert len(set(platforms)) > 1 or len(set(tones)) > 1


def test_phase2_top_n_selection(tmp_path, sample_ideas_payload):
    """Test Phase 2 top-N selection strategy."""
    # Add confidence scores
    sample_ideas_payload["ideas"][0]["confidence"] = 0.90
    sample_ideas_payload["ideas"][1]["confidence"] = 0.85
    sample_ideas_payload["ideas"][2]["confidence"] = 0.80
    
    config = SelectionConfig(
        min_confidence=0.70,
        max_selected=2,
        strategy="top",
    )
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify top-N selection
    assert len(result["selected_ideas"]) == 2
    # Should be sorted by confidence (highest first)
    confidences = [idea["confidence"] for idea in result["selected_ideas"]]
    assert confidences == sorted(confidences, reverse=True)


def test_phase2_manual_selection_by_ids(tmp_path, sample_ideas_payload):
    """Test Phase 2 manual selection by IDs."""
    config = SelectionConfig(
        selected_ids=["idea_001", "idea_003"],
    )
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify manual selection
    assert len(result["selected_ideas"]) == 2
    selected_ids = [idea["id"] for idea in result["selected_ideas"]]
    assert "idea_001" in selected_ids
    assert "idea_003" in selected_ids
    assert "idea_002" not in selected_ids


def test_phase2_handles_no_ideas(tmp_path):
    """Test Phase 2 handles empty ideas list."""
    empty_payload = {"ideas": []}
    config = SelectionConfig()
    
    with pytest.raises(ValueError) as exc_info:
        run(
            ideas_payload=empty_payload,
            config=config,
            article_slug="test_article",
            output_dir=tmp_path / "output",
        )
    
    assert "No ideas provided" in str(exc_info.value)


def test_phase2_handles_all_below_threshold(tmp_path, sample_ideas_payload):
    """Test Phase 2 handles case where all ideas are below confidence threshold."""
    # Set all confidences below threshold
    for idea in sample_ideas_payload["ideas"]:
        idea["confidence"] = 0.50
    
    config = SelectionConfig(
        min_confidence=0.70,
        max_selected=3,
        strategy="top",
    )
    
    # Should use all ideas (fallback behavior)
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Should still return ideas (fallback to all)
    assert len(result["selected_ideas"]) > 0


def test_phase2_saves_output_file(tmp_path, sample_ideas_payload):
    """Test Phase 2 saves selected_ideas.json file."""
    for idea in sample_ideas_payload["ideas"]:
        idea["confidence"] = 0.80
    
    config = SelectionConfig(max_selected=3)
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify output file exists
    output_path = Path(result["output_path"])
    assert output_path.exists()
    
    # Verify file content
    output_data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "selected_ideas" in output_data
    assert "stats" in output_data
    assert "config" in output_data


def test_phase2_returns_statistics(tmp_path, sample_ideas_payload):
    """Test Phase 2 returns selection statistics."""
    for idea in sample_ideas_payload["ideas"]:
        idea["confidence"] = 0.80
    
    config = SelectionConfig(max_selected=3)
    
    result = run(
        ideas_payload=sample_ideas_payload,
        config=config,
        article_slug="test_article",
        output_dir=tmp_path / "output",
    )
    
    # Verify statistics
    assert "stats" in result
    assert "selection_count" in result
    assert result["selection_count"] == len(result["selected_ideas"])
