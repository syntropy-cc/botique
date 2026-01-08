#!/usr/bin/env python3
"""
Test script to validate narrative architect response from database event.

Tests the validation logic with a real response from the database
before running the full pipeline again.
"""

import json
import re
import sys
from pathlib import Path

from src.core.llm_log_queries import get_event_tree
from src.core.llm_log_db import get_db_path
from src.narrative.architect import NarrativeArchitect
from src.core.llm_client import HttpLLMClient


def test_validation_from_event(event_id: str):
    """Test validation with response from database event."""
    print(f"Testing validation with event ID: {event_id}")
    print("=" * 70)
    
    # Get event from database
    db_path = get_db_path()
    event = get_event_tree(event_id, db_path)
    
    if not event:
        print(f"❌ ERROR: Event not found: {event_id}")
        return 1
    
    print(f"✓ Event found: {event.get('name', 'unknown')}")
    print(f"  Trace ID: {event.get('trace_id', 'unknown')}")
    print(f"  Created: {event.get('created_at', 'unknown')}")
    
    # Extract raw response
    output = event.get('output', {})
    raw_response = output.get('content', '')
    
    if not raw_response:
        print("❌ ERROR: No output content found in event")
        return 1
    
    print(f"✓ Raw response length: {len(raw_response)} characters")
    
    # Extract JSON from markdown if needed
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        print("✓ Extracted JSON from markdown code fence")
    else:
        # Try to parse directly
        json_str = raw_response.strip()
        try:
            json.loads(json_str)
            print("✓ Raw response is valid JSON")
        except json.JSONDecodeError:
            print("❌ ERROR: Could not extract JSON from response")
            return 1
    
    # Try to parse JSON to see structure
    try:
        data = json.loads(json_str)
        print(f"✓ JSON parsed successfully")
        
        if 'slides' in data:
            print(f"  Slides count: {len(data['slides'])}")
            if len(data['slides']) > 0:
                first_slide = data['slides'][0]
                print(f"  First slide keys: {list(first_slide.keys())}")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: JSON parse error: {e}")
        return 1
    
    # Now test with the actual validation function
    # We need a minimal brief and architect instance
    print("\n" + "=" * 70)
    print("Testing with NarrativeArchitect._validate_response...")
    print("=" * 70)
    
    try:
        from src.coherence.brief import CoherenceBrief
        
        # Create a minimal brief for validation (semantic checks need it)
        # We'll use dummy values since we're only testing structural validation
        brief = CoherenceBrief(
            post_id="test_post",
            idea_id="test_idea",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["test"],
            vocabulary_level="moderate",
            formality="neutral",
            palette_id="test_palette",
            palette={"primary": "#000000", "secondary": "#FFFFFF"},
            typography_id="test_typography",
            typography={"font": "Arial", "size": "16px"},
            visual_style="modern",
            visual_mood="professional",
            canvas={"width": 1080, "height": 1350, "aspect_ratio": "4:5"},
            primary_emotion="motivation",
            secondary_emotions=["hope"],
            avoid_emotions=["shame"],
            target_emotions=["motivation"],
            keywords_to_emphasize=["test"],
            themes=["test"],
            main_message="Test message",
            value_proposition="Test value",
            angle="Test angle",
            hook="Test hook",
            persona="Test persona",
            pain_points=["test"],
            desires=["test"],
            avoid_topics=["test"],
            required_elements=[],
            objective="engagement",
            narrative_arc="Hook → Problem → Solution → CTA",
            estimated_slides=8,
            article_context="Test context",
            key_insights_used=["insight_1"],
            key_insights_content=[{"id": "insight_1", "content": "Test", "type": "advice", "strength": 9}],
        )
        
        # Create architect instance (we only need it for the validation method)
        # We'll create a dummy LLM client since we won't actually use it
        llm_client = HttpLLMClient(
            api_key="dummy",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )
        architect = NarrativeArchitect(llm_client=llm_client)
        
        # Test validation
        print("\nValidating response structure...")
        payload = architect._validate_response(raw_response, brief)
        
        print("\n✅ VALIDATION SUCCESSFUL!")
        print(f"  Pacing: {payload.get('narrative_pacing')}")
        print(f"  Transition style: {payload.get('transition_style')}")
        print(f"  Slides: {len(payload.get('slides', []))}")
        
        return 0
        
    except ValueError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    event_id = "723f978e-a643-4847-8103-2c6567b1d17f"
    if len(sys.argv) > 1:
        event_id = sys.argv[1]
    
    sys.exit(test_validation_from_event(event_id))

