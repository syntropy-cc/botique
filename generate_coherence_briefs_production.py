#!/usr/bin/env python3
"""
Production script to test Coherence Brief generation.

Loads ideas from an existing phase1_ideas.json file and generates
the corresponding coherence briefs using Phase 3.

Uses the complete production workflow with integrated validation.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.core.config import OUTPUT_DIR
from src.core.llm_logger import LLMLogger
from src.phases.phase3_coherence import run as run_phase3

# Load environment variables
load_dotenv()


def main():
    print("=" * 70)
    print("COHERENCE BRIEF GENERATION - PRODUCTION")
    print("=" * 70)
    
    # Initialize logger with SQL backend
    logger = LLMLogger(
        output_dir=OUTPUT_DIR,
        use_sql=True,
        use_json=True,  # Keep JSON for compatibility
    )
    
    # Paths
    article_slug = "why-tradicional-learning-fails"
    ideas_json_path = OUTPUT_DIR / article_slug / "phase1_ideas.json"
    
    # Create trace for this execution
    trace_id = logger.create_trace(
        name="generate_coherence_briefs",
        metadata={"article_slug": article_slug, "script": "generate_coherence_briefs_production"},
    )
    logger.set_context(article_slug=article_slug)
    print(f"✓ Trace created: {trace_id[:8]}...")
    print(f"✓ SQL logging: enabled")
    
    if not ideas_json_path.exists():
        print(f"❌ ERROR: Ideas file not found: {ideas_json_path}")
        print(f"   Please run generate_ideas_production.py first to generate the ideas.")
        return 1
    
    print(f"✓ Ideas file found: {ideas_json_path}")
    
    # Load ideas payload
    print(f"\n1. Loading ideas...")
    import time
    load_start = time.time()
    
    try:
        ideas_payload = json.loads(ideas_json_path.read_text(encoding="utf-8"))
        
        # Log step: loading ideas
        logger.log_step_event(
            trace_id=trace_id,
            name="load_ideas_json",
            input_text=f"Loading ideas from {ideas_json_path.name}",
            input_obj={
                "file_path": str(ideas_json_path),
                "article_slug": article_slug,
            },
            output_text=f"Loaded {len(ideas_payload.get('ideas', []))} ideas",
            output_obj={
                "ideas_count": len(ideas_payload.get("ideas", [])),
                "article_summary": article_summary,
                "total_ideas": len(ideas_payload.get("ideas", [])),
            },
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
            status="success",
            metadata={
                "file_path": str(ideas_json_path),
                "article_slug": article_slug,
                "ideas_count": len(ideas_payload.get("ideas", [])),
                "article_title": article_summary.get("title"),
            },
        )
    except Exception as e:
        print(f"❌ ERROR reading JSON file: {e}")
        logger.log_step_event(
            trace_id=trace_id,
            name="load_ideas_json",
            input_obj={"file_path": str(ideas_json_path)},
            error=str(e),
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
        )
        return 1
    
    article_summary = ideas_payload.get("article_summary", {})
    all_ideas = ideas_payload.get("ideas", [])
    
    print(f"   ✓ Payload loaded successfully")
    print(f"   ✓ Total ideas available: {len(all_ideas)}")
    print(f"   ✓ Article title: {article_summary.get('title', 'N/A')}")
    
    if not all_ideas:
        print(f"❌ ERROR: No ideas found in file")
        return 1
    
    # Select ideas to test (first 3 for quick test, or all)
    # Can be configured via environment variable
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "3"))
    
    if max_ideas_to_test > 0 and max_ideas_to_test < len(all_ideas):
        selected_ideas = all_ideas[:max_ideas_to_test]
        print(f"\n2. Selecting ideas for testing...")
        print(f"   ✓ Selected {len(selected_ideas)} ideas (out of {len(all_ideas)} available)")
    else:
        selected_ideas = all_ideas
        print(f"\n2. Using all ideas...")
        print(f"   ✓ {len(selected_ideas)} ideas will be processed")
    
    # Show preview of selected ideas
    print(f"\n   Selected ideas:")
    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", "N/A")
        platform = idea.get("platform", "N/A")
        format_type = idea.get("format", "N/A")
        tone = idea.get("tone", "N/A")
        hook = idea.get("hook", "N/A")[:60] + "..." if len(idea.get("hook", "")) > 60 else idea.get("hook", "N/A")
        print(f"     {idx}. {idea_id}: {platform}/{format_type} - {tone}")
        print(f"        Hook: {hook}")
    
    # Create output directory
    output_dir = OUTPUT_DIR / article_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate coherence briefs (process one at a time to continue even with errors)
    print(f"\n3. Generating coherence briefs (Phase 3)...")
    print(f"   ⏳ Building briefs from selected ideas...")
    
    briefs = []
    failed_ideas = []
    
    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        print(f"   [{idx}/{len(selected_ideas)}] Processing {idea_id}...", end=" ")
        
        brief_start = time.time()
        post_id = f"post_{article_slug}_{idx:03d}"
        
        # Log step: start processing brief
        brief_start_event = logger.log_step_event(
            trace_id=trace_id,
            name=f"build_brief_{post_id}",
            input_text=f"Building coherence brief for idea {idea_id}",
            input_obj={
                "idea_id": idea_id,
                "post_id": post_id,
                "idea": idea,  # Full idea object
                "article_summary": article_summary,  # Context
            },
            type="preprocess",
            metadata={
                "idea_id": idea_id,
                "post_id": post_id,
                "platform": idea.get("platform"),
                "format": idea.get("format"),
                "tone": idea.get("tone"),
            },
        )
        
        try:
            # Build brief individually
            from src.coherence.builder import CoherenceBriefBuilder
            
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=article_summary,
                post_id=post_id,
            )
            
            # Validate brief
            CoherenceBriefBuilder.validate_brief(brief)
            
            briefs.append(brief)
            brief_duration = (time.time() - brief_start) * 1000
            
            # Log step: brief built successfully
            logger.log_step_event(
                trace_id=trace_id,
                name=f"build_brief_{post_id}_complete",
                input_text=f"Completed building brief for {post_id}",
                output_text=f"Coherence brief generated: {brief.platform}/{brief.format} - {brief.tone}",
                output_obj={
                    "post_id": post_id,
                    "platform": brief.platform,
                    "format": brief.format,
                    "tone": brief.tone,
                    "brief": brief.to_dict(),  # Full brief object
                },
                duration_ms=brief_duration,
                parent_id=brief_start_event,
                type="postprocess",
                status="success",
                metadata={
                    "post_id": post_id,
                    "platform": brief.platform,
                    "format": brief.format,
                    "tone": brief.tone,
                    "palette_id": brief.palette_id,
                    "typography_id": brief.typography_id,
                    "estimated_slides": brief.estimated_slides,
                },
            )
            
            print(f"✓")
            
        except Exception as e:
            brief_duration = (time.time() - brief_start) * 1000
            error_msg = str(e)
            
            # Log step: brief failed
            logger.log_step_event(
                trace_id=trace_id,
                name=f"build_brief_{post_id}_failed",
                input_text=f"Failed building brief for {post_id}",
                output_text=None,
                output_obj={"error": error_msg, "idea_id": idea_id},
                duration_ms=brief_duration,
                parent_id=brief_start_event,
                type="postprocess",
                status="error",
                error=error_msg,
                metadata={
                    "post_id": post_id,
                    "idea_id": idea_id,
                    "error": error_msg,
                },
            )
            
            print(f"❌ ({error_msg[:60]}...)")
            failed_ideas.append({
                "idea_id": idea_id,
                "idea": idea,
                "error": error_msg
            })
    
    if not briefs:
        print(f"\n   ❌ ERROR: No briefs were generated successfully!")
        print(f"   Failures:")
        for fail in failed_ideas:
            print(f"     - {fail['idea_id']}: {fail['error']}")
        return 1
    
    print(f"\n   ✓ {len(briefs)} brief(s) generated successfully")
    if failed_ideas:
        print(f"   ⚠️  {len(failed_ideas)} idea(s) failed (continuing with successful ones)")
    
    # Save briefs manually (since we're not using run_phase3 directly)
    article_output_dir = OUTPUT_DIR / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual briefs
    for brief in briefs:
        post_dir = article_output_dir / brief.post_id
        post_dir.mkdir(parents=True, exist_ok=True)
        
        brief_path = post_dir / "coherence_brief.json"
        brief_path.write_text(
            json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    
    # Save consolidated briefs
    briefs_dict = [brief.to_dict() for brief in briefs]
    consolidated_path = article_output_dir / "coherence_briefs.json"
    consolidated_path.write_text(
        json.dumps(briefs_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    phase3_result = {
        "briefs": briefs,
        "briefs_dict": briefs_dict,
        "output_path": str(consolidated_path),
        "briefs_count": len(briefs),
        "output_dir": str(article_output_dir),
        "failed_ideas": failed_ideas,
    }
    
    # Validate result
    briefs = phase3_result.get("briefs", [])
    briefs_dict = phase3_result.get("briefs_dict", [])
    briefs_count = phase3_result.get("briefs_count", 0)
    output_path = phase3_result.get("output_path", "")
    failed_ideas = phase3_result.get("failed_ideas", [])
    
    print(f"\n4. Results:")
    print(f"   ✓ Total briefs generated: {briefs_count}")
    print(f"   ✓ Consolidated file: {output_path}")
    
    if briefs_count == 0:
        print(f"   ⚠️  WARNING: No briefs were generated")
        return 1
    
    # Validate each brief individually
    print(f"\n5. Brief validation...")
    validation_errors = []
    
    for idx, brief in enumerate(briefs, 1):
        errors = brief.validate()
        if errors:
            validation_errors.append({
                "brief_index": idx,
                "post_id": brief.post_id,
                "errors": errors
            })
            print(f"   ❌ Brief {idx} ({brief.post_id}): {len(errors)} error(s)")
            for error in errors:
                print(f"      - {error}")
        else:
            print(f"   ✓ Brief {idx} ({brief.post_id}): valid")
    
    if validation_errors:
        print(f"\n   ⚠️  WARNING: {len(validation_errors)} brief(s) with validation errors")
    else:
        print(f"\n   ✓ All briefs passed validation!")
    
    # Show ideas that failed
    if failed_ideas:
        print(f"\n   ⚠️  IDEAS THAT FAILED GENERATION:")
        for fail in failed_ideas:
            print(f"     - {fail['idea_id']}: {fail['error'][:100]}")
    
    # Detailed summary of briefs
    print(f"\n6. Detailed coherence brief summary:")
    print("=" * 70)
    
    for idx, brief in enumerate(briefs, 1):
        print(f"\n📋 BRIEF {idx}: {brief.post_id}")
        print(f"   Idea ID: {brief.idea_id}")
        print(f"   Platform: {brief.platform} | Format: {brief.format}")
        print(f"")
        print(f"   VOICE:")
        print(f"     - Tone: {brief.tone}")
        print(f"     - Personality traits: {', '.join(brief.personality_traits[:3])}")
        print(f"     - Vocabulary level: {brief.vocabulary_level}")
        print(f"     - Formality: {brief.formality}")
        print(f"")
        print(f"   VISUAL:")
        print(f"     - Palette ID: {brief.palette_id}")
        print(f"     - Palette theme: {brief.palette.get('theme', 'N/A')}")
        print(f"     - Primary color: {brief.palette.get('primary', 'N/A')}")
        print(f"     - Accent color: {brief.palette.get('accent', 'N/A')}")
        print(f"     - Typography ID: {brief.typography_id}")
        print(f"     - Heading font: {brief.typography.get('heading_font', 'N/A')}")
        print(f"     - Visual style: {brief.visual_style}")
        print(f"     - Visual mood: {brief.visual_mood}")
        print(f"     - Canvas: {brief.canvas.get('width', 'N/A')}x{brief.canvas.get('height', 'N/A')} ({brief.canvas.get('aspect_ratio', 'N/A')})")
        print(f"")
        print(f"   EMOTIONS:")
        print(f"     - Primary emotion: {brief.primary_emotion}")
        print(f"     - Secondary emotions: {', '.join(brief.secondary_emotions[:3])}")
        print(f"     - Emotions to avoid: {', '.join(brief.avoid_emotions[:3]) if brief.avoid_emotions else 'N/A'}")
        print(f"")
        print(f"   CONTENT:")
        print(f"     - Main message: {brief.main_message[:80]}..." if len(brief.main_message) > 80 else f"     - Main message: {brief.main_message}")
        print(f"     - Value proposition: {brief.value_proposition[:80]}..." if len(brief.value_proposition) > 80 else f"     - Value proposition: {brief.value_proposition}")
        print(f"     - Hook: {brief.hook[:80]}..." if len(brief.hook) > 80 else f"     - Hook: {brief.hook}")
        print(f"     - Angle: {brief.angle[:80]}..." if len(brief.angle) > 80 else f"     - Angle: {brief.angle}")
        print(f"     - Keywords: {', '.join(brief.keywords_to_emphasize[:5])}")
        print(f"")
        print(f"   AUDIENCE:")
        print(f"     - Persona: {brief.persona}")
        print(f"     - Pain points: {', '.join(brief.pain_points[:3]) if brief.pain_points else 'N/A'}")
        print(f"     - Desires: {', '.join(brief.desires[:3]) if brief.desires else 'N/A'}")
        print(f"")
        print(f"   STRUCTURE:")
        print(f"     - Objective: {brief.objective}")
        print(f"     - Narrative arc: {brief.narrative_arc}")
        print(f"     - Estimated slides: {brief.estimated_slides}")
        print(f"")
        print(f"   CONTEXT:")
        print(f"     - Insights used: {len(brief.key_insights_used)} insight(s)")
        print(f"     - Insight content: {len(brief.key_insights_content)} item(s)")
        print(f"")
        print(f"   BRAND:")
        print(f"     - Brand values: {', '.join(brief.brand_values) if brief.brand_values else 'N/A'}")
        print(f"     - Handle: {brief.brand_assets.get('handle', 'N/A')}")
        print(f"     - Tagline: {brief.brand_assets.get('tagline', 'N/A')}")
        print(f"")
        print(f"   EVOLUTION (fields added by subsequent phases):")
        print(f"     - Narrative structure: {'✓' if brief.narrative_structure else '✗'} (Phase 3)")
        print(f"     - Copy guidelines: {'✓' if brief.copy_guidelines else '✗'} (Phase 4)")
        print(f"     - Visual preferences: {'✓' if brief.visual_preferences else '✗'} (Phase 4)")
        print(f"     - Platform constraints: {'✓' if brief.platform_constraints else '✗'} (Phase 5)")
        print("-" * 70)
    
    # Verify saved files
    print(f"\n7. Verifying saved files...")
    
    consolidated_path = Path(output_path)
    if consolidated_path.exists():
        file_size = consolidated_path.stat().st_size
        print(f"   ✓ Consolidated file exists: {consolidated_path}")
        print(f"     Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    
    # Verify individual briefs
    for brief in briefs:
        post_dir = output_dir / brief.post_id
        brief_path = post_dir / "coherence_brief.json"
        if brief_path.exists():
            file_size = brief_path.stat().st_size
            print(f"   ✓ Individual brief: {brief_path.relative_to(OUTPUT_DIR)} ({file_size:,} bytes)")
        else:
            print(f"   ⚠️  Individual brief not found: {brief_path}")
    
    # General statistics
    print(f"\n8. General statistics:")
    
    # Distribution by platform
    platforms = {}
    for brief in briefs:
        platform = brief.platform
        platforms[platform] = platforms.get(platform, 0) + 1
    
    print(f"   Distribution by platform:")
    for platform, count in platforms.items():
        print(f"     - {platform}: {count} brief(s)")
    
    # Distribution by format
    formats = {}
    for brief in briefs:
        format_type = brief.format
        formats[format_type] = formats.get(format_type, 0) + 1
    
    print(f"   Distribution by format:")
    for format_type, count in formats.items():
        print(f"     - {format_type}: {count} brief(s)")
    
    # Distribution by tone
    tones = {}
    for brief in briefs:
        tone = brief.tone
        tones[tone] = tones.get(tone, 0) + 1
    
    print(f"   Distribution by tone:")
    for tone, count in tones.items():
        print(f"     - {tone}: {count} brief(s)")
    
    # Palettes used
    palettes = {}
    for brief in briefs:
        palette_id = brief.palette_id
        palettes[palette_id] = palettes.get(palette_id, 0) + 1
    
    print(f"   Palettes used:")
    for palette_id, count in palettes.items():
        print(f"     - {palette_id}: {count} brief(s)")
    
    # Brand values detected
    all_brand_values = set()
    for brief in briefs:
        all_brand_values.update(brief.brand_values)
    
    print(f"   Brand values detected: {', '.join(sorted(all_brand_values))}")
    
    # Verify SQL database
    print(f"\n9. Verifying SQL database...")
    try:
        from src.core.llm_log_queries import get_trace_with_events, get_cost_summary
        from src.core.llm_log_db import get_db_path
        
        db_path = get_db_path()
        trace_data = get_trace_with_events(trace_id, db_path)
        
        if trace_data:
            event_count = len(trace_data.get("events", []))
            print(f"   ✓ Trace found in database: {trace_id[:8]}...")
            print(f"   ✓ Events saved: {event_count}")
            
            # Count event types
            event_types = {}
            for event in trace_data.get("events", []):
                event_type = event.get("type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print(f"   ✓ Event breakdown:")
            for etype, count in event_types.items():
                print(f"     - {etype}: {count}")
        else:
            print(f"   ⚠️  Trace not found in database")
    except Exception as e:
        print(f"   ⚠️  Error verifying database: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ COHERENCE BRIEF GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Consolidated file: {output_path}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    
    if validation_errors or failed_ideas:
        print(f"\n⚠️  WARNINGS:")
        if validation_errors:
            print(f"   - {len(validation_errors)} brief(s) with validation errors")
        if failed_ideas:
            print(f"   - {len(failed_ideas)} idea(s) failed generation")
        print(f"   - Review the errors above before using in production")
    
    return 0


if __name__ == "__main__":
    exit(main())
