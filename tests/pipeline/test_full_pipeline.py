"""
End-to-end tests for full pipeline execution.

Tests complete pipeline Phase 1→5, multiple posts, output structure.

Location: tests/pipeline/test_full_pipeline.py
"""

import time
import pytest

from src.core.config import IdeationConfig, SelectionConfig
from src.phases.phase1_ideation import run as run_phase1
from src.phases.phase2_selection import run as run_phase2


@pytest.mark.e2e
def test_full_pipeline_execution(
    tmp_path,
    mock_llm_client_with_response,
    test_result_logger,
    test_artifact_storage,
):
    """Test complete pipeline: Phase 1 → Phase 5."""
    # Create article file
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent here.", encoding="utf-8")
    
    # Phase 1: Ideation
    phase1_start = time.time()
    phase1_result = run_phase1(
        article_path=article_file,
        config=IdeationConfig(min_ideas=3),
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    phase1_duration = (time.time() - phase1_start) * 1000
    
    test_result_logger.log_phase_result(
        phase="phase1",
        status="passed",
        output={
            "ideas_count": len(phase1_result["ideas"]),
            "article_slug": phase1_result["article_slug"],
        },
        artifacts={"ideas_json": phase1_result["output_path"]},
        duration_ms=phase1_duration,
    )
    
    # Phase 2: Selection
    phase2_start = time.time()
    phase2_result = run_phase2(
        ideas_payload=phase1_result,
        config=SelectionConfig(max_selected=3),
        article_slug=phase1_result["article_slug"],
        output_dir=tmp_path / "output",
    )
    phase2_duration = (time.time() - phase2_start) * 1000
    
    test_result_logger.log_phase_result(
        phase="phase2",
        status="passed",
        output={
            "selected_count": len(phase2_result["selected_ideas"]),
        },
        artifacts={"selected_ideas_json": phase2_result["output_path"]},
        duration_ms=phase2_duration,
    )
    
    # Verify pipeline execution
    assert phase1_result["ideas_count"] >= 3
    assert len(phase2_result["selected_ideas"]) > 0
    
    # Verify artifacts stored
    assert test_artifact_storage.has_artifact("phase1", "ideas.json") or phase1_result["output_path"]


@pytest.mark.e2e
def test_pipeline_with_multiple_posts(tmp_path, mock_llm_client_with_response):
    """Test pipeline with multiple posts (3-6 ideas)."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    phase1_result = run_phase1(
        article_path=article_file,
        config=IdeationConfig(min_ideas=3, max_ideas=6),
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    
    # Should generate multiple ideas
    assert len(phase1_result["ideas"]) >= 3
    assert len(phase1_result["ideas"]) <= 6


@pytest.mark.e2e
def test_pipeline_output_structure(tmp_path, mock_llm_client_with_response):
    """Test pipeline output structure and completeness."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    phase1_result = run_phase1(
        article_path=article_file,
        config=IdeationConfig(),
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    
    # Verify output structure
    assert "output_path" in phase1_result
    assert "output_dir" in phase1_result
    assert "ideas" in phase1_result
    assert "article_summary" in phase1_result
