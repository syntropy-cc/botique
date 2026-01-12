"""
Brand audience module

Functions for enriching ideas with audience profile data.

Location: src/brand/audience.py
"""

from typing import Any, Dict, Optional


def get_audience_profile(persona: str) -> Optional[Dict[str, Any]]:
    """
    Get audience profile for a persona.
    
    Args:
        persona: Persona description (e.g., "C-level execs", "Founders")
    
    Returns:
        Audience profile dict or None if not found
    """
    persona_lower = persona.lower()
    
    # Simple profile mapping
    profiles = {
        "c_level": {
            "personality_traits": ["data-driven", "results-oriented", "strategic"],
            "pain_points": ["wasted budgets", "inefficient processes", "missed opportunities"],
            "desires": ["roi", "efficiency", "competitive advantage"],
            "vocabulary_level": "sophisticated",
            "formality": "formal",
        },
        "founder": {
            "personality_traits": ["visionary", "action-oriented", "resilient"],
            "pain_points": ["scaling challenges", "resource constraints", "market fit"],
            "desires": ["growth", "impact", "autonomy"],
            "vocabulary_level": "moderate",
            "formality": "casual",
        },
        "developer": {
            "personality_traits": ["technical", "detail-oriented", "problem-solver"],
            "pain_points": ["technical debt", "inefficient tools", "complexity"],
            "desires": ["clean code", "best practices", "innovation"],
            "vocabulary_level": "technical",
            "formality": "neutral",
        },
    }
    
    # Match persona to profile
    for key, profile in profiles.items():
        if key in persona_lower:
            return profile
    
    # Check for keywords
    if any(x in persona_lower for x in ["c-level", "executive", "ceo", "cto"]):
        return profiles["c_level"]
    elif any(x in persona_lower for x in ["founder", "startup", "visionary"]):
        return profiles["founder"]
    elif any(x in persona_lower for x in ["developer", "dev", "engineer"]):
        return profiles["developer"]
    
    return None


def enrich_idea_with_audience(
    idea: Dict[str, Any],
    audience_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich idea dict with audience profile data.
    
    Args:
        idea: Idea dict to enrich
        audience_profile: Audience profile dict
    
    Returns:
        Enriched idea dict (new dict, doesn't modify original)
    """
    enriched = idea.copy()
    
    # Add audience attributes if not already present
    if "personality_traits" not in enriched or not enriched["personality_traits"]:
        enriched["personality_traits"] = audience_profile.get("personality_traits", [])
    
    if "pain_points" not in enriched or not enriched["pain_points"]:
        enriched["pain_points"] = audience_profile.get("pain_points", [])
    
    if "desires" not in enriched or not enriched["desires"]:
        enriched["desires"] = audience_profile.get("desires", [])
    
    if "vocabulary_level" not in enriched:
        enriched["vocabulary_level"] = audience_profile.get("vocabulary_level", "moderate")
    
    if "formality" not in enriched:
        enriched["formality"] = audience_profile.get("formality", "neutral")
    
    return enriched

