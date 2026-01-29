"""
Unit tests for Phase 1: Ideation.

Tests Phase 1 with mocked LLM client, verifies idea generation output structure,
validation gates, article reading, output file generation, and error handling.

Location: tests/pipeline/test_phase1_ideation.py
"""

import json
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.core.config import IdeationConfig
from src.phases.phase1_ideation import run
from tests.pipeline.conftest import assert_brief_valid


@pytest.fixture
def mock_llm_client_with_response():
    """Create mock LLM client with sample response."""
    mock_client = Mock()
    mock_client.raw_responses_dir = None
    mock_client.save_raw_responses = True
    
    # Sample LLM response
    sample_response = json.dumps({
        "article_summary": {
            "title": "The Future of Workflow Automation",
            "main_thesis": "Workflow automation is essential for modern businesses",
            "detected_tone": "professional",
            "key_insights": [
                {
                    "id": "insight_1",
                    "content": "Automation can reduce manual work by 60%",
                    "type": "statistic",
                    "strength": 8,
                    "source_quote": "According to recent studies...",
                },
                {
                    "id": "insight_2",
                    "content": "Early adopters see ROI within 3 months",
                    "type": "roi",
                    "strength": 7,
                    "source_quote": "Experts recommend...",
                },
            ],
            "themes": ["automation", "efficiency", "business"],
            "keywords": ["workflow", "automation", "efficiency"],
            "main_message": "Workflow automation is essential for modern businesses",
            "avoid_topics": ["layoffs", "job_loss"],
        },
        "ideas": [
            {
                "id": "idea_001",
                "platform": "linkedin",
                "format": "carousel",
                "tone": "professional",
                "persona": "C-Level executives",
                "personality_traits": ["authoritative", "strategic"],
                "objective": "engagement",
                "angle": "Modern businesses need smarter automation",
                "hook": "Did you know that 73% of companies struggle with inefficient workflows?",
                "narrative_arc": "problem-solution",
                "vocabulary_level": "sophisticated",
                "formality": "formal",
                "key_insights_used": ["insight_1", "insight_2"],
                "target_emotions": ["urgency", "curiosity"],
                "primary_emotion": "urgency",
                "secondary_emotions": ["curiosity", "motivation"],
                "avoid_emotions": ["fear", "confusion"],
                "value_proposition": "Increase efficiency by 40% with intelligent automation",
                "article_context_for_idea": "This idea focuses on workflow automation",
                "idea_explanation": "A detailed explanation of the idea",
                "estimated_slides": 7,
                "confidence": 0.85,
                "rationale": "This approach resonates with C-Level decision makers",
                "risks": ["may be too technical"],
                "keywords_to_emphasize": ["automation", "efficiency", "workflow"],
                "pain_points": ["operational_inefficiency"],
                "desires": ["efficiency", "cost_reduction"],
            },
            {
                "id": "idea_002",
                "platform": "linkedin",
                "format": "carousel",
                "tone": "conversational",
                "persona": "Mid-level managers",
                "personality_traits": ["helpful", "practical"],
                "objective": "education",
                "angle": "Practical guide to getting started",
                "hook": "Want to automate your workflows but don't know where to start?",
                "narrative_arc": "how-to",
                "vocabulary_level": "moderate",
                "formality": "casual",
                "key_insights_used": ["insight_1"],
                "target_emotions": ["curiosity", "confidence"],
                "primary_emotion": "curiosity",
                "secondary_emotions": ["confidence", "motivation"],
                "avoid_emotions": ["overwhelm", "confusion"],
                "value_proposition": "Step-by-step automation guide",
                "article_context_for_idea": "This idea focuses on practical implementation",
                "idea_explanation": "A guide for beginners",
                "estimated_slides": 5,
                "confidence": 0.75,
                "rationale": "Addresses common barriers to adoption",
                "risks": ["may be too basic"],
                "keywords_to_emphasize": ["automation", "guide", "steps"],
                "pain_points": ["lack_of_knowledge", "where_to_start"],
                "desires": ["clear_guidance", "practical_tips"],
            },
            {
                "id": "idea_003",
                "platform": "twitter",
                "format": "single_image",
                "tone": "casual",
                "persona": "Tech enthusiasts",
                "personality_traits": ["bold", "data-driven"],
                "objective": "awareness",
                "angle": "Quick stat with visual impact",
                "hook": "60% efficiency gain? Here's how.",
                "narrative_arc": "statistic-led",
                "vocabulary_level": "simple",
                "formality": "casual",
                "key_insights_used": ["insight_1"],
                "target_emotions": ["surprise", "curiosity"],
                "primary_emotion": "surprise",
                "secondary_emotions": ["curiosity"],
                "avoid_emotions": ["skepticism"],
                "value_proposition": "Immediate visual impact",
                "article_context_for_idea": "This idea focuses on quick visual impact",
                "idea_explanation": "A single powerful statistic",
                "estimated_slides": 1,
                "confidence": 0.70,
                "rationale": "Works well for Twitter's fast-paced environment",
                "risks": ["may lack depth"],
                "keywords_to_emphasize": ["60%", "efficiency"],
                "pain_points": ["information_overload"],
                "desires": ["quick_insights", "visual_data"],
            },
        ],
    }, ensure_ascii=False)
    
    mock_client.generate = Mock(return_value=sample_response)
    return mock_client
        
        # Sample LLM response
        self.sample_llm_response = json.dumps({
            "article_summary": {
                "title": "The Future of Workflow Automation",
                "main_thesis": "Workflow automation is essential for modern businesses",
                "detected_tone": "professional",
                "key_insights": [
                    {
                        "id": "insight_1",
                        "content": "Automation can reduce manual work by 60%",
                        "type": "statistic",
                        "strength": 8,
                        "source_quote": "According to recent studies...",
                    },
                    {
                        "id": "insight_2",
                        "content": "Early adopters see ROI within 3 months",
                        "type": "roi",
                        "strength": 7,
                        "source_quote": "Experts recommend...",
                    },
                ],
                "themes": ["automation", "efficiency", "business"],
                "keywords": ["workflow", "automation", "efficiency"],
                "main_message": "Workflow automation is essential for modern businesses",
                "avoid_topics": ["layoffs", "job_loss"],
            },
            "ideas": [
                {
                    "id": "idea_001",
                    "platform": "linkedin",
                    "format": "carousel",
                    "tone": "professional",
                    "persona": "C-Level executives",
                    "personality_traits": ["authoritative", "strategic"],
                    "objective": "engagement",
                    "angle": "Modern businesses need smarter automation",
                    "hook": "Did you know that 73% of companies struggle with inefficient workflows?",
                    "narrative_arc": "problem-solution",
                    "vocabulary_level": "sophisticated",
                    "formality": "formal",
                    "key_insights_used": ["insight_1", "insight_2"],
                    "target_emotions": ["urgency", "curiosity"],
                    "primary_emotion": "urgency",
                    "secondary_emotions": ["curiosity", "motivation"],
                    "avoid_emotions": ["fear", "confusion"],
                    "value_proposition": "Increase efficiency by 40% with intelligent automation",
                    "article_context_for_idea": "This idea focuses on workflow automation",
                    "idea_explanation": "A detailed explanation of the idea",
                    "estimated_slides": 7,
                    "confidence": 0.85,
                    "rationale": "This approach resonates with C-Level decision makers",
                    "risks": ["may be too technical"],
                    "keywords_to_emphasize": ["automation", "efficiency", "workflow"],
                    "pain_points": ["operational_inefficiency"],
                    "desires": ["efficiency", "cost_reduction"],
                },
                {
                    "id": "idea_002",
                    "platform": "linkedin",
                    "format": "carousel",
                    "tone": "conversational",
                    "persona": "Mid-level managers",
                    "personality_traits": ["helpful", "practical"],
                    "objective": "education",
                    "angle": "Practical guide to getting started",
                    "hook": "Want to automate your workflows but don't know where to start?",
                    "narrative_arc": "how-to",
                    "vocabulary_level": "moderate",
                    "formality": "casual",
                    "key_insights_used": ["insight_1"],
                    "target_emotions": ["curiosity", "confidence"],
                    "primary_emotion": "curiosity",
                    "secondary_emotions": ["confidence", "motivation"],
                    "avoid_emotions": ["overwhelm", "confusion"],
                    "value_proposition": "Step-by-step automation guide",
                    "article_context_for_idea": "This idea focuses on practical implementation",
                    "idea_explanation": "A guide for beginners",
                    "estimated_slides": 5,
                    "confidence": 0.75,
                    "rationale": "Addresses common barriers to adoption",
                    "risks": ["may be too basic"],
                    "keywords_to_emphasize": ["automation", "guide", "steps"],
                    "pain_points": ["lack_of_knowledge", "where_to_start"],
                    "desires": ["clear_guidance", "practical_tips"],
                },
                {
                    "id": "idea_003",
                    "platform": "twitter",
                    "format": "single_image",
                    "tone": "casual",
                    "persona": "Tech enthusiasts",
                    "personality_traits": ["bold", "data-driven"],
                    "objective": "awareness",
                    "angle": "Quick stat with visual impact",
                    "hook": "60% efficiency gain? Here's how.",
                    "narrative_arc": "statistic-led",
                    "vocabulary_level": "simple",
                    "formality": "casual",
                    "key_insights_used": ["insight_1"],
                    "target_emotions": ["surprise", "curiosity"],
                    "primary_emotion": "surprise",
                    "secondary_emotions": ["curiosity"],
                    "avoid_emotions": ["skepticism"],
                    "value_proposition": "Immediate visual impact",
                    "article_context_for_idea": "This idea focuses on quick visual impact",
                    "idea_explanation": "A single powerful statistic",
                    "estimated_slides": 1,
                    "confidence": 0.70,
                    "rationale": "Works well for Twitter's fast-paced environment",
                    "risks": ["may lack depth"],
                    "keywords_to_emphasize": ["60%", "efficiency"],
                    "pain_points": ["information_overload"],
                    "desires": ["quick_insights", "visual_data"],
                },
            ],
        }, ensure_ascii=False)


def test_phase1_generates_ideas(tmp_path, mock_llm_client_with_response, test_result_logger, test_artifact_storage):
        """Test Phase 1 generates ideas successfully."""
        # Create sample article file
        article_file = tmp_path / "test_article.md"
        article_file.write_text("# Test Article\n\nContent here.", encoding="utf-8")
        
        # Configure
        config = IdeationConfig(min_ideas=3, max_ideas=6)
        output_dir = tmp_path / "output"
        
        # Execute Phase 1
        phase1_start = time.time()
        result = run(
            article_path=article_file,
            config=config,
            llm_client=self.mock_llm_client,
            output_dir=output_dir,
        )
        phase1_duration = (time.time() - phase1_start) * 1000
        
        # Verify LLM was called
        mock_llm_client_with_response.generate.assert_called_once()
        
        # Verify result structure
        assert "ideas" in result
        assert "article_summary" in result
        assert "article_slug" in result
        assert "output_path" in result
        assert "ideas_count" in result
        assert "briefs" in result
        
        # Verify ideas count
        assert len(result["ideas"]) >= 3
        assert result["ideas_count"] == len(result["ideas"])
        
        # Verify ideas are distinct
        idea_ids = [idea["id"] for idea in result["ideas"]]
        assert len(idea_ids) == len(set(idea_ids)), "Ideas must be distinct"
        
        # Verify all ideas have required fields
        for idea in result["ideas"]:
            assert "platform" in idea
            assert "tone" in idea
            assert "persona" in idea
            assert "hook" in idea
        
        # Verify output file exists
        output_path = Path(result["output_path"])
        assert output_path.exists()
        
        # Verify output file content
        output_data = json.loads(output_path.read_text(encoding="utf-8"))
        assert "ideas" in output_data
        assert "article_summary" in output_data
        
        # Log results
        test_result_logger.log_phase_result(
            phase="phase1",
            status="passed",
            output={
                "ideas": result["ideas"],
                "ideas_count": len(result["ideas"]),
                "article_summary": result["article_summary"],
                "article_slug": result["article_slug"],
                "validation": {
                    "min_ideas": len(result["ideas"]) >= config.min_ideas,
                    "distinct_ideas": len(set(i["id"] for i in result["ideas"])) == len(result["ideas"]),
                    "all_have_platform": all("platform" in i for i in result["ideas"]),
                    "all_have_tone": all("tone" in i for i in result["ideas"]),
                },
            },
            artifacts={
                "ideas_json": result["output_path"],
            },
            duration_ms=phase1_duration,
        )
        
        # Store artifacts
        test_artifact_storage.save_artifact("phase1", "ideas.json", result["ideas"])
        test_artifact_storage.save_artifact("phase1", "article_summary.json", result["article_summary"])
        
        # Verify logged results
        logged_output = test_result_logger.get_phase_output("phase1")
        assert logged_output is not None
        assert logged_output["ideas_count"] == len(result["ideas"])
        assert logged_output["validation"]["min_ideas"]


def test_phase1_validates_minimum_ideas(tmp_path, mock_llm_client_with_response):
    """Test Phase 1 validates minimum ideas count."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    # Mock response with insufficient ideas
    insufficient_response = json.dumps({
        "article_summary": {"title": "Test"},
        "ideas": [
            {"id": "idea_001", "platform": "linkedin", "tone": "professional"},
        ],
    })
    mock_llm_client_with_response.generate.return_value = insufficient_response
    
    config = IdeationConfig(min_ideas=3)
    
    with pytest.raises(ValueError) as exc_info:
        run(
            article_path=article_file,
            config=config,
            llm_client=mock_llm_client_with_response,
            output_dir=tmp_path / "output",
        )
    
    assert "minimum is 3" in str(exc_info.value)


def test_phase1_handles_missing_article(tmp_path, mock_llm_client_with_response):
    """Test Phase 1 handles missing article file."""
    non_existent_file = tmp_path / "nonexistent.md"
    config = IdeationConfig()
    
    with pytest.raises(FileNotFoundError):
        run(
            article_path=non_existent_file,
            config=config,
            llm_client=mock_llm_client_with_response,
            output_dir=tmp_path / "output",
        )


def test_phase1_generates_briefs(tmp_path, mock_llm_client_with_response, test_result_logger, test_artifact_storage):
    """Test Phase 1 generates coherence briefs for ideas."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent here.", encoding="utf-8")
    
    config = IdeationConfig(min_ideas=3, filter_enabled=False)
    
    result = run(
        article_path=article_file,
        config=config,
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    
    # Verify briefs were generated
    assert "briefs" in result
    assert "briefs_count" in result
    assert result["briefs_count"] >= 1
    
    # Verify each brief is valid
    for brief in result["briefs"]:
        assert_brief_valid(brief)
        assert brief.post_id is not None
        assert brief.platform is not None
        assert brief.palette_id is not None
    
    # Log briefs
    test_result_logger.log_phase_result(
        phase="phase1",
        status="passed",
        output={
            "briefs_count": result["briefs_count"],
            "briefs": [brief.to_dict() for brief in result["briefs"]],
        },
        artifacts={},
        duration_ms=0,
    )
    
    # Store briefs
    test_artifact_storage.save_artifact("phase1", "briefs.json", result["briefs_dict"])


def test_phase1_filters_ideas_when_enabled(tmp_path, mock_llm_client_with_response):
    """Test Phase 1 filters ideas when filter_enabled is True."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    # Add confidence scores to ideas
    sample_response = json.loads(mock_llm_client_with_response.generate.return_value)
    sample_response["ideas"][0]["confidence"] = 0.90  # High confidence
    sample_response["ideas"][1]["confidence"] = 0.60  # Below threshold
    sample_response["ideas"][2]["confidence"] = 0.80  # High confidence
    
    mock_llm_client_with_response.generate.return_value = json.dumps(sample_response)
    
    config = IdeationConfig(
        min_ideas=3,
        filter_enabled=True,
        filter_min_confidence=0.70,
        filter_strategy="top",
        filter_max_count=2,
    )
    
    result = run(
        article_path=article_file,
        config=config,
        llm_client=mock_llm_client_with_response,
        output_dir=tmp_path / "output",
    )
    
    # Verify filtering occurred
    assert "filtered_ideas" in result
    assert len(result["filtered_ideas"]) <= 2
    assert len(result["filtered_ideas"]) <= len(result["ideas"])


def test_phase1_saves_output_files(tmp_path, mock_llm_client_with_response):
    """Test Phase 1 saves output files correctly."""
    article_file = tmp_path / "test_article.md"
    article_file.write_text("# Test Article\n\nContent.", encoding="utf-8")
    
    config = IdeationConfig()
    output_dir = tmp_path / "output"
    
    result = run(
        article_path=article_file,
        config=config,
        llm_client=mock_llm_client_with_response,
        output_dir=output_dir,
    )
    
    # Verify output directory structure
    article_slug = result["article_slug"]
    article_output_dir = output_dir / article_slug
    assert article_output_dir.exists()
    
    # Verify phase1_ideas.json exists
    ideas_file = Path(result["output_path"])
    assert ideas_file.exists()
    
    # Verify coherence briefs file exists
    briefs_file = article_output_dir / "coherence_briefs.json"
    assert briefs_file.exists()
    
    # Verify individual brief files exist
    for brief in result["briefs"]:
        post_dir = article_output_dir / brief.post_id
        brief_file = post_dir / "coherence_brief.json"
        assert brief_file.exists()
