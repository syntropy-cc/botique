"""
Shared pytest fixtures for pipeline tests.

Provides fixtures for:
- Temporary databases
- Sample data (articles, ideas, briefs, etc.)
- Mock objects (LLM client, logger, etc.)
- Test result logging fixtures
- Test utilities
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock
import pytest

from src.core.llm_log_db import init_database, get_db_path
from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.coherence.brief import CoherenceBrief
from tests.pipeline.result_logging import TestResultLogger, TestArtifactStorage, init_test_results_db


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def temp_db_path():
    """
    Create a temporary database file for testing.
    
    Yields:
        Path to temporary database file
        
    Cleanup:
        Removes temporary database file after test
    """
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test_llm_logs.db"
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    try:
        temp_dir.rmdir()
    except OSError:
        pass


@pytest.fixture
def initialized_db(temp_db_path):
    """
    Create and initialize a temporary database.
    
    Yields:
        Path to initialized database file
    """
    init_database(temp_db_path)
    init_test_results_db(temp_db_path)
    yield temp_db_path


# ============================================================================
# Mock Objects
# ============================================================================

@pytest.fixture
def mock_llm_client():
    """
    Mock LLM client with configurable responses.
    
    Returns:
        Mock HttpLLMClient instance
    """
    mock = Mock(spec=HttpLLMClient)
    mock.generate = Mock(return_value="Mocked LLM response")
    mock.base_url = "https://api.deepseek.com/v1"
    mock.model = "deepseek-chat"
    return mock


@pytest.fixture
def mock_logger():
    """
    Mock LLM logger.
    
    Returns:
        Mock LLMLogger instance
    """
    mock = Mock(spec=LLMLogger)
    mock.create_trace = Mock(return_value="mock_trace_id")
    mock.log_call = Mock(return_value="mock_event_id")
    mock.log_step_event = Mock(return_value="mock_event_id")
    mock.log_llm_event = Mock(return_value="mock_event_id")
    mock.set_context = Mock()
    return mock


@pytest.fixture
def mock_image_generator():
    """
    Mock image generator (DALL-E/Stable Diffusion client).
    
    Returns:
        Mock image generator instance
    """
    mock = Mock()
    mock.generate = Mock(return_value=b"fake_image_bytes")
    return mock


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_article() -> str:
    """
    Sample article text for testing.
    
    Returns:
        Sample article text
    """
    return """# The Future of Workflow Automation

Workflow automation is transforming how modern businesses operate. Companies that embrace automation see significant improvements in efficiency, cost reduction, and employee satisfaction.

## Key Benefits

1. **Efficiency Gains**: Automation can reduce manual work by up to 60%, allowing teams to focus on strategic initiatives.

2. **Cost Reduction**: Early adopters see ROI within 3 months, with average cost savings of 30-40%.

3. **Scalability**: Automated workflows scale effortlessly, handling increased volume without proportional cost increases.

## Implementation Challenges

While the benefits are clear, implementation requires careful planning. Common challenges include:
- Change management
- Integration complexity
- Initial investment

## Conclusion

The future belongs to businesses that automate intelligently. Start small, measure results, and scale what works.
"""


@pytest.fixture
def sample_article_summary() -> Dict[str, Any]:
    """
    Sample article summary dictionary for testing.
    
    Returns:
        Sample article summary dictionary
    """
    return {
        "title": "The Future of Workflow Automation",
        "main_message": "Workflow automation is essential for modern businesses",
        "themes": ["automation", "efficiency", "business"],
        "keywords": ["workflow", "automation", "efficiency"],
        "key_insights": [
            {
                "id": "insight_1",
                "content": "Automation can reduce manual work by 60%",
                "category": "efficiency",
            },
            {
                "id": "insight_2",
                "content": "Early adopters see ROI within 3 months",
                "category": "roi",
            },
        ],
        "avoid_topics": ["layoffs", "job_loss"],
    }


@pytest.fixture
def sample_ideas() -> list:
    """
    List of sample idea dictionaries for testing.
    
    Returns:
        List of sample idea dictionaries
    """
    return [
        {
            "id": "idea_001",
            "platform": "linkedin",
            "format": "carousel",
            "tone": "professional",
            "persona": "C-Level executives",
            "objective": "engagement",
            "narrative_arc": "problem-solution",
            "estimated_slides": 7,
            "hook": "Did you know that 73% of companies struggle with inefficient workflows?",
            "angle": "Modern businesses need smarter automation",
            "value_proposition": "Increase efficiency by 40% with intelligent automation",
            "key_insights_used": ["insight_1", "insight_2"],
            "keywords_to_emphasize": ["automation", "efficiency", "workflow"],
            "primary_emotion": "urgency",
            "secondary_emotions": ["curiosity", "motivation"],
            "avoid_emotions": ["fear", "confusion"],
            "personality_traits": ["authoritative", "strategic"],
            "pain_points": ["operational_inefficiency"],
            "desires": ["efficiency", "cost_reduction"],
            "vocabulary_level": "sophisticated",
            "formality": "formal",
            "article_context_for_idea": "This idea focuses on workflow automation",
            "idea_explanation": "A detailed explanation of the idea",
            "rationale": "This approach resonates with C-Level decision makers",
        },
        {
            "id": "idea_002",
            "platform": "linkedin",
            "format": "carousel",
            "tone": "conversational",
            "persona": "Mid-level managers",
            "objective": "education",
            "narrative_arc": "how-to",
            "estimated_slides": 5,
            "hook": "Want to automate your workflows but don't know where to start?",
            "angle": "Practical guide to getting started",
            "value_proposition": "Step-by-step automation guide",
            "key_insights_used": ["insight_1"],
            "keywords_to_emphasize": ["automation", "guide", "steps"],
            "primary_emotion": "curiosity",
            "secondary_emotions": ["confidence", "motivation"],
            "avoid_emotions": ["overwhelm", "confusion"],
            "personality_traits": ["helpful", "practical"],
            "pain_points": ["lack_of_knowledge", "where_to_start"],
            "desires": ["clear_guidance", "practical_tips"],
            "vocabulary_level": "moderate",
            "formality": "casual",
            "article_context_for_idea": "This idea focuses on practical implementation",
            "idea_explanation": "A guide for beginners",
            "rationale": "Addresses common barriers to adoption",
        },
        {
            "id": "idea_003",
            "platform": "twitter",
            "format": "single_image",
            "tone": "casual",
            "persona": "Tech enthusiasts",
            "objective": "awareness",
            "narrative_arc": "statistic-led",
            "estimated_slides": 1,
            "hook": "60% efficiency gain? Here's how.",
            "angle": "Quick stat with visual impact",
            "value_proposition": "Immediate visual impact",
            "key_insights_used": ["insight_1"],
            "keywords_to_emphasize": ["60%", "efficiency"],
            "primary_emotion": "surprise",
            "secondary_emotions": ["curiosity"],
            "avoid_emotions": ["skepticism"],
            "personality_traits": ["bold", "data-driven"],
            "pain_points": ["information_overload"],
            "desires": ["quick_insights", "visual_data"],
            "vocabulary_level": "simple",
            "formality": "casual",
            "article_context_for_idea": "This idea focuses on quick visual impact",
            "idea_explanation": "A single powerful statistic",
            "rationale": "Works well for Twitter's fast-paced environment",
        },
    ]


@pytest.fixture
def sample_coherence_brief() -> CoherenceBrief:
    """
    Sample CoherenceBrief object for testing.
    
    Returns:
        Sample CoherenceBrief instance
    """
    return CoherenceBrief(
        post_id="test_post_001",
        idea_id="idea_001",
        platform="linkedin",
        format="carousel",
        tone="professional",
        personality_traits=["authoritative", "strategic"],
        vocabulary_level="sophisticated",
        formality="formal",
        palette_id="blue_professional",
        palette={
            "theme": "professional",
            "primary": "#1E3A8A",
            "accent": "#3B82F6",
            "cta": "#10B981",
        },
        typography_id="modern_sans",
        typography={
            "heading_font": "Inter Bold",
            "body_font": "Inter Regular",
        },
        visual_style="clean and modern",
        visual_mood="confident",
        canvas={
            "width": 1080,
            "height": 1080,
            "aspect_ratio": "1:1",
        },
        primary_emotion="confident",
        secondary_emotions=["inspired", "motivated"],
        avoid_emotions=["anxious", "overwhelmed"],
        target_emotions=["confident", "inspired"],
        keywords_to_emphasize=["productivity", "efficiency", "growth"],
        themes=["productivity", "workplace"],
        main_message="Boost your team's productivity with smart workflows",
        value_proposition="Save 10 hours per week with automated processes",
        angle="Data-driven approach to workflow optimization",
        hook="Are you wasting 10 hours every week on repetitive tasks?",
        persona="Tech-savvy managers looking to optimize team workflows",
        pain_points=["manual processes", "lack of automation", "time waste"],
        desires=["efficiency", "scalability", "team productivity"],
        avoid_topics=["layoffs", "controversial politics"],
        required_elements=["data points", "actionable tips", "professional_cta"],
        objective="engagement",
        narrative_arc="problem-solution-benefit",
        estimated_slides=6,
        article_context="Article about workflow automation and productivity tools",
        key_insights_used=["insight_001", "insight_002"],
        key_insights_content=[
            {
                "id": "insight_001",
                "content": "Companies save 10 hours per week with automation",
                "type": "statistic",
                "strength": 8,
                "source_quote": "According to recent studies...",
            },
            {
                "id": "insight_002",
                "content": "Manual processes reduce team morale",
                "type": "advice",
                "strength": 7,
                "source_quote": "Experts recommend...",
            },
        ],
        idea_explanation="This idea focuses on workflow automation benefits",
    )


@pytest.fixture
def sample_narrative_structure() -> Dict[str, Any]:
    """
    Sample narrative structure dictionary for testing.
    
    Returns:
        Sample narrative structure dictionary
    """
    return {
        "post_id": "test_post_001",
        "slides": [
            {
                "slide_number": 1,
                "module_type": "hook",
                "template_type": "hook",
                "purpose": "Grab attention with a provocative question",
                "copy_direction": "Create curiosity about a common problem professionals face",
                "target_emotions": ["curiosity", "recognition"],
                "content_slots": ["headline"],
            },
            {
                "slide_number": 2,
                "module_type": "value_data",
                "template_type": "value",
                "value_subtype": "data",
                "purpose": "Present compelling statistic",
                "copy_direction": "Show the scale of the problem with a surprising number",
                "target_emotions": ["surprise", "concern"],
                "content_slots": ["headline", "statistic", "source"],
            },
            {
                "slide_number": 3,
                "module_type": "value_insight",
                "template_type": "value",
                "value_subtype": "insight",
                "purpose": "Provide actionable insight",
                "copy_direction": "Offer a practical solution or tip",
                "target_emotions": ["hope", "confidence"],
                "content_slots": ["headline", "body"],
            },
            {
                "slide_number": 4,
                "module_type": "value_solution",
                "template_type": "value",
                "value_subtype": "solution",
                "purpose": "Present the main solution",
                "copy_direction": "Explain how automation solves the problem",
                "target_emotions": ["understanding", "interest"],
                "content_slots": ["headline", "body", "benefits"],
            },
            {
                "slide_number": 5,
                "module_type": "value_example",
                "template_type": "value",
                "value_subtype": "example",
                "purpose": "Show real-world example",
                "copy_direction": "Provide a concrete case study or example",
                "target_emotions": ["trust", "confidence"],
                "content_slots": ["headline", "example", "result"],
            },
            {
                "slide_number": 6,
                "module_type": "transition",
                "template_type": "transition",
                "purpose": "Bridge to CTA",
                "copy_direction": "Smoothly transition from value to action",
                "target_emotions": ["readiness", "motivation"],
                "content_slots": ["headline"],
            },
            {
                "slide_number": 7,
                "module_type": "cta",
                "template_type": "cta",
                "purpose": "Encourage action",
                "copy_direction": "Invite engagement with a clear, professional CTA",
                "target_emotions": ["action", "commitment"],
                "content_slots": ["headline", "cta_text"],
            },
        ],
    }


@pytest.fixture
def sample_slide_content() -> Dict[str, Any]:
    """
    Sample slide content dictionary for testing.
    
    Returns:
        Sample slide content dictionary
    """
    return {
        "slides": [
            {
                "slide_number": 1,
                "title": {
                    "content": "Are you wasting 10 hours every week on repetitive tasks?",
                    "emphasis": ["10 hours", "repetitive tasks"],
                },
            },
            {
                "slide_number": 2,
                "title": {
                    "content": "73% of companies struggle with inefficient workflows",
                    "emphasis": ["73%", "struggle"],
                },
                "subtitle": {
                    "content": "McKinsey Global Institute, 2024",
                    "emphasis": [],
                },
            },
        ],
    }


# ============================================================================
# Test Result Logging Fixtures
# ============================================================================

@pytest.fixture
def test_result_logger(request, initialized_db):
    """
    Fixture that creates and manages test result logging.
    
    Automatically starts test run and saves on completion.
    
    Yields:
        TestResultLogger instance
    """
    # Determine test category from marker or default to "unit"
    test_category = "unit"
    if hasattr(request.node, "keywords"):
        if "integration" in request.node.keywords:
            test_category = "integration"
        elif "e2e" in request.node.keywords or "end_to_end" in request.node.keywords:
            test_category = "e2e"
    
    logger = TestResultLogger(
        test_name=request.node.name,
        test_category=test_category,
        db_path=initialized_db,
    )
    logger.start_test_run()
    
    yield logger
    
    # Auto-save on test completion
    try:
        if hasattr(request.node, "rep_call"):
            if request.node.rep_call.passed:
                logger.end_test_run(status="passed")
            elif request.node.rep_call.failed:
                error_msg = str(request.node.rep_call.longrepr) if hasattr(request.node.rep_call, "longrepr") else "Test failed"
                logger.end_test_run(status="failed", error=error_msg)
            else:
                logger.end_test_run(status="skipped")
        else:
            # Fallback if rep_call not available
            logger.end_test_run(status="passed")
    except Exception:
        # If test failed before rep_call is set, mark as failed
        logger.end_test_run(status="failed", error="Unknown error")
    
    logger.save_to_db()


@pytest.fixture
def test_artifact_storage(test_result_logger, initialized_db):
    """
    Fixture that creates artifact storage for test run.
    
    Yields:
        TestArtifactStorage instance
    """
    storage = TestArtifactStorage(
        test_run_id=test_result_logger.test_run_id,
        db_path=initialized_db,
    )
    yield storage


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Create temporary output directory for tests.
    
    Yields:
        Path to temporary output directory
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    yield output_dir


@pytest.fixture
def sample_article_file(sample_article, tmp_path) -> Path:
    """
    Create a temporary article file for testing.
    
    Yields:
        Path to article file
    """
    article_file = tmp_path / "test_article.md"
    article_file.write_text(sample_article, encoding="utf-8")
    yield article_file


# ============================================================================
# Helper Functions
# ============================================================================

def assert_brief_valid(brief: CoherenceBrief) -> None:
    """
    Assert that a coherence brief is valid.
    
    Args:
        brief: CoherenceBrief instance to validate
        
    Raises:
        AssertionError: If brief is invalid
    """
    assert brief.post_id is not None, "Brief must have post_id"
    assert brief.platform is not None, "Brief must have platform"
    assert brief.tone is not None, "Brief must have tone"
    assert brief.palette_id is not None, "Brief must have palette_id"
    assert brief.typography_id is not None, "Brief must have typography_id"


def assert_narrative_structure_valid(narrative_structure: Dict[str, Any]) -> None:
    """
    Assert that a narrative structure is valid.
    
    Args:
        narrative_structure: Narrative structure dictionary to validate
        
    Raises:
        AssertionError: If structure is invalid
    """
    assert "slides" in narrative_structure, "Narrative structure must have slides"
    assert len(narrative_structure["slides"]) >= 1, "Narrative structure must have at least 1 slide"
    
    for slide in narrative_structure["slides"]:
        assert "slide_number" in slide, "Slide must have slide_number"
        assert "template_type" in slide, "Slide must have template_type"
        assert "purpose" in slide, "Slide must have purpose"


# ============================================================================
# Environment Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def clean_env():
    """
    Clean up environment variables before and after each test.
    
    Ensures tests don't affect each other through environment variables.
    """
    # Save original values
    original_db_path = os.environ.get("LLM_LOGS_DB_PATH")
    original_db_url = os.environ.get("DB_URL")
    
    # Clean up
    if "LLM_LOGS_DB_PATH" in os.environ:
        del os.environ["LLM_LOGS_DB_PATH"]
    if "DB_URL" in os.environ:
        del os.environ["DB_URL"]
    
    yield
    
    # Restore original values
    if original_db_path:
        os.environ["LLM_LOGS_DB_PATH"] = original_db_path
    if original_db_url:
        os.environ["DB_URL"] = original_db_url
    elif "DB_URL" in os.environ:
        del os.environ["DB_URL"]
