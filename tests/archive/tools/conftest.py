"""
Shared pytest fixtures for tool tests.

Provides fixtures for temporary databases, sample data, and mock objects.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
import pytest

from src.core.llm_log_db import init_database, get_db_path


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
    yield temp_db_path


@pytest.fixture
def sample_idea() -> Dict[str, Any]:
    """
    Sample idea dictionary for testing.
    
    Returns:
        Sample idea dictionary
    """
    return {
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
    }


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
def sample_audience_profile() -> Dict[str, Any]:
    """
    Sample audience profile for testing.
    
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
