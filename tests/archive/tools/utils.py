"""
Test utilities and helper functions for tool tests.

Provides common utilities for database cleanup, data generation,
assertion helpers, and comparison utilities.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.coherence.brief import CoherenceBrief


def create_temp_db() -> Path:
    """
    Create a temporary database file for testing.
    
    Returns:
        Path to temporary database file
    """
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test_llm_logs.db"
    return db_path


def cleanup_temp_db(db_path: Path) -> None:
    """
    Clean up temporary database file.
    
    Args:
        db_path: Path to database file to remove
    """
    if db_path.exists():
        db_path.unlink()
        # Try to remove parent directory if empty
        try:
            db_path.parent.rmdir()
        except OSError:
            pass  # Directory not empty, ignore


def create_sample_idea(
    idea_id: str = "idea_001",
    platform: str = "linkedin",
    format_type: str = "carousel",
    tone: str = "professional",
    persona: str = "C-Level executives",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a sample idea dictionary for testing.
    
    Args:
        idea_id: Idea identifier
        platform: Target platform
        format_type: Content format
        tone: Content tone
        persona: Target persona
        
    Returns:
        Sample idea dictionary
    """
    idea = {
        "id": idea_id,
        "platform": platform,
        "format": format_type,
        "tone": tone,
        "persona": persona,
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
    }
    # Update with any additional kwargs
    idea.update(kwargs)
    return idea


def create_sample_article_summary(
    main_message: str = "Workflow automation is essential",
) -> Dict[str, Any]:
    """
    Create a sample article summary dictionary for testing.
    
    Args:
        main_message: Main message of the article
        
    Returns:
        Sample article summary dictionary
    """
    return {
        "title": "The Future of Workflow Automation",
        "main_message": main_message,
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


def create_sample_audience_profile() -> Dict[str, Any]:
    """
    Create a sample audience profile for testing.
    
    Returns:
        Sample audience profile dictionary
    """
    return {
        "name": "C-Level Executive",
        "personality_traits": ["authoritative", "strategic", "data_driven"],
        "pain_points": ["operational_inefficiency", "wasted_budgets"],
        "desires": ["efficiency", "roi_rapido"],
        "communication_style": {
            "vocabulary": "sophisticated",
            "formality": "formal",
        },
        "brand_values": ["go_deep_or_go_home"],
    }


def assert_brief_valid(brief: CoherenceBrief) -> None:
    """
    Assert that a CoherenceBrief is valid.
    
    Args:
        brief: CoherenceBrief to validate
        
    Raises:
        AssertionError: If brief is invalid
    """
    assert brief is not None, "Brief should not be None"
    assert brief.post_id, "Brief should have post_id"
    assert brief.idea_id, "Brief should have idea_id"
    assert brief.platform, "Brief should have platform"
    assert brief.format, "Brief should have format"
    assert brief.tone, "Brief should have tone"
    assert brief.palette_id, "Brief should have palette_id"
    assert brief.palette, "Brief should have palette"
    assert brief.typography_id, "Brief should have typography_id"
    assert brief.typography, "Brief should have typography"
    assert brief.canvas, "Brief should have canvas"


def assert_brief_fields_equal(
    brief1: CoherenceBrief,
    brief2: CoherenceBrief,
    fields: Optional[List[str]] = None,
) -> None:
    """
    Assert that specific fields are equal between two briefs.
    
    Args:
        brief1: First brief
        brief2: Second brief
        fields: List of field names to compare (if None, compares all common fields)
    """
    if fields is None:
        fields = [
            "post_id",
            "idea_id",
            "platform",
            "format",
            "tone",
            "palette_id",
            "typography_id",
        ]
    
    for field in fields:
        val1 = getattr(brief1, field, None)
        val2 = getattr(brief2, field, None)
        assert val1 == val2, f"Field {field} should be equal: {val1} != {val2}"
