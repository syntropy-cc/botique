#!/usr/bin/env python3
"""
Production script to test Narrative Architect (Phase 3 - Narrative Structure).

Loads ideas from an existing phase1_ideas.json file, builds coherence briefs
for each selected idea, and then generates a detailed narrative structure
for each brief using the NarrativeArchitect agent.

Uses the complete production workflow with integrated SQL logging.
"""

import json
import os
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from src.core.config import OUTPUT_DIR
from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.coherence.builder import CoherenceBriefBuilder
from src.narrative.architect import NarrativeArchitect


def main() -> int:
    print("=" * 70)
    print("NARRATIVE ARCHITECT - PRODUCTION TEST")
    print("=" * 70)

    # Load environment variables
    load_dotenv()

    # Configuration
    article_slug = os.getenv("ARTICLE_SLUG", "why-tradicional-learning-fails")
    ideas_json_path = OUTPUT_DIR / article_slug / "phase1_ideas.json"

    # Initialize logger with SQL backend only
    print("\n1. Initializing logger...")
    logger = LLMLogger(use_sql=True)

    # Create trace for this execution (automatically sets logger.current_trace_id)
    trace_id = logger.create_trace(
        name="generate_narrative_structures",
        metadata={
            "article_slug": article_slug,
            "script": "generate_narrative_structures_production",
        },
    )
    logger.set_context(article_slug=article_slug)

    print(f"   ✓ Trace created: {trace_id[:8]}...")
    print(f"   ✓ SQL logging: enabled")

    # Check ideas file
    print("\n2. Loading phase1 ideas payload...")
    if not ideas_json_path.exists():
        print(f"❌ ERROR: Ideas file not found: {ideas_json_path}")
        print("   Please run generate_ideas_production.py first.")
        return 1

    print(f"   ✓ Ideas file found: {ideas_json_path}")

    import time

    load_start = time.time()
    try:
        ideas_payload = json.loads(ideas_json_path.read_text(encoding="utf-8"))
        article_summary = ideas_payload.get("article_summary", {})
        all_ideas: List[dict] = ideas_payload.get("ideas", [])

        logger.log_step_event(
            trace_id=trace_id,
            name="load_ideas_json",
            input_text=f"Loading ideas from {ideas_json_path.name}",
            input_obj={
                "file_path": str(ideas_json_path),
                "article_slug": article_slug,
            },
            output_text=f"Loaded {len(all_ideas)} ideas",
            output_obj={
                "ideas_count": len(all_ideas),
                "article_summary": article_summary,
                "total_ideas": len(all_ideas),
            },
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
            status="success",
            metadata={
                "file_path": str(ideas_json_path),
                "article_slug": article_slug,
                "ideas_count": len(all_ideas),
                "article_title": article_summary.get("title"),
            },
        )
    except Exception as exc:
        error_msg = str(exc)
        print(f"❌ ERROR reading JSON file: {error_msg}")
        logger.log_step_event(
            trace_id=trace_id,
            name="load_ideas_json",
            input_obj={"file_path": str(ideas_json_path)},
            error=error_msg,
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
            status="error",
        )
        return 1

    if not all_ideas:
        print("❌ ERROR: No ideas found in phase1_ideas.json")
        return 1

    print(f"   ✓ Payload loaded successfully")
    print(f"   ✓ Total ideas available: {len(all_ideas)}")
    print(f"   ✓ Article title: {article_summary.get('title', 'N/A')}")

    # Select ideas to process (reuse MAX_IDEAS_TO_TEST logic)
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "3"))

    if 0 < max_ideas_to_test < len(all_ideas):
        selected_ideas = all_ideas[:max_ideas_to_test]
        print(f"\n3. Selecting ideas for narrative generation...")
        print(f"   ✓ Selected {len(selected_ideas)} ideas (out of {len(all_ideas)} available)")
    else:
        selected_ideas = all_ideas
        print(f"\n3. Using all ideas for narrative generation...")
        print(f"   ✓ {len(selected_ideas)} ideas will be processed")

    # Preview selected ideas
    print("\n   Selected ideas:")
    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", "N/A")
        platform = idea.get("platform", "N/A")
        format_type = idea.get("format", "N/A")
        tone = idea.get("tone", "N/A")
        hook = idea.get("hook", "N/A")
        if len(hook) > 60:
            hook = hook[:60] + "..."
        print(f"     {idx}. {idea_id}: {platform}/{format_type} - {tone}")
        print(f"        Hook: {hook}")

    # Prepare output directories
    article_output_dir = OUTPUT_DIR / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = article_output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

    # Check API key for LLM
    print("\n4. Initializing LLM client for Narrative Architect...")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERROR: LLM_API_KEY or DEEPSEEK_API_KEY not found in environment")
        return 1

    logger.set_context(article_slug=article_slug)

    llm_client = HttpLLMClient(
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        timeout=int(os.getenv("LLM_TIMEOUT", "180")),
        logger=logger,
        save_raw_responses=True,
        raw_responses_dir=debug_dir,
    )

    print(f"   ✓ LLM client created: model={llm_client.model}, timeout={llm_client.timeout}s")
    print(f"   ✓ Raw responses directory: {debug_dir}")

    # Create Narrative Architect
    print("\n5. Creating Narrative Architect agent...")
    architect = NarrativeArchitect(llm_client=llm_client, logger=logger)
    print("   ✓ Narrative Architect created")

    # Build briefs and generate narrative structures
    print("\n6. Building coherence briefs and generating narrative structures...")
    briefs = []
    failed_items = []

    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        post_id = f"post_{article_slug}_{idx:03d}"

        print(f"   [{idx}/{len(selected_ideas)}] Processing {idea_id} -> {post_id}...", end=" ")

        brief_start = time.time()

        # Log step: start processing this post
        brief_start_event = logger.log_step_event(
            trace_id=trace_id,
            name=f"narrative_build_{post_id}_start",
            input_text=f"Building brief and narrative for idea {idea_id}",
            input_obj={
                "idea_id": idea_id,
                "post_id": post_id,
                "idea": idea,
                "article_summary": article_summary,
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
            # Build brief
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=article_summary,
                post_id=post_id,
            )

            # Validate brief
            CoherenceBriefBuilder.validate_brief(brief)

            # Update logger context with post_id
            logger.set_context(post_id=post_id)

            # Generate narrative structure (this will enrich the brief)
            narrative_payload = architect.generate_structure(
                brief=brief,
                context=post_id,
            )

            brief_duration = (time.time() - brief_start) * 1000

            briefs.append(brief)

            # Log success
            logger.log_step_event(
                trace_id=trace_id,
                name=f"narrative_build_{post_id}_complete",
                input_text=f"Completed brief + narrative for {post_id}",
                output_text=(
                    f"Narrative structure generated: {len(narrative_payload.get('slides', []))} "
                    f"slides, pacing={narrative_payload.get('narrative_pacing')}"
                ),
                output_obj={
                    "post_id": post_id,
                    "platform": brief.platform,
                    "format": brief.format,
                    "tone": brief.tone,
                    "slides": len(narrative_payload.get("slides", [])),
                    "pacing": narrative_payload.get("narrative_pacing"),
                    "transition_style": narrative_payload.get("transition_style"),
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
                },
            )

            print("✓")

            # Save updated brief (with narrative evolution) to disk
            post_dir = article_output_dir / brief.post_id
            post_dir.mkdir(parents=True, exist_ok=True)

            brief_path = post_dir / "coherence_brief.json"
            brief_path.write_text(
                json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        except Exception as exc:
            brief_duration = (time.time() - brief_start) * 1000
            error_msg = str(exc)

            logger.log_step_event(
                trace_id=trace_id,
                name=f"narrative_build_{post_id}_failed",
                input_text=f"Failed brief + narrative for {post_id}",
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

            print(f"❌ ({error_msg[:80]}...)")
            failed_items.append(
                {
                    "idea_id": idea_id,
                    "post_id": post_id,
                    "idea": idea,
                    "error": error_msg,
                }
            )

    if not briefs:
        print("\n   ❌ ERROR: No briefs/narratives were generated successfully!")
        if failed_items:
            print("   Failures:")
            for fail in failed_items:
                print(f"     - {fail['post_id']} ({fail['idea_id']}): {fail['error']}")
        return 1

    print(f"\n   ✓ {len(briefs)} brief(s) with narrative generated successfully")
    if failed_items:
        print(f"   ⚠️  {len(failed_items)} idea(s) failed (continuing with successful ones)")

    # Save consolidated enriched briefs
    print("\n7. Saving consolidated coherence briefs with narrative...")
    briefs_dict = [brief.to_dict() for brief in briefs]
    consolidated_path = article_output_dir / "coherence_briefs_with_narrative.json"
    consolidated_path.write_text(
        json.dumps(briefs_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"   ✓ Consolidated file: {consolidated_path}")

    # Quick validation: check narrative evolution fields
    print("\n8. Validating narrative evolution fields...")
    for idx, brief in enumerate(briefs, 1):
        has_narrative = brief.narrative_structure is not None
        print(
            f"   Brief {idx} ({brief.post_id}): "
            f"narrative_structure={'✓' if has_narrative else '✗'}"
        )

    # Verify SQL logs for this trace
    print("\n9. Verifying SQL database for narrative trace...")
    try:
        from src.core.llm_log_queries import get_trace_with_events
        from src.core.llm_log_db import get_db_path

        db_path = get_db_path()
        trace_data = get_trace_with_events(trace_id, db_path)

        if trace_data:
            events = trace_data.get("events", [])
            print(f"   ✓ Trace found: {trace_id[:8]}..., events: {len(events)}")

            # Simple breakdown by type
            event_types = {}
            for event in events:
                etype = event.get("type", "unknown")
                event_types[etype] = event_types.get(etype, 0) + 1

            print("   ✓ Event breakdown:")
            for etype, count in event_types.items():
                print(f"     - {etype}: {count}")
        else:
            print("   ⚠️  Trace not found in database")
    except Exception as exc:
        print(f"   ⚠️  Error verifying database: {exc}")

    print("\n" + "=" * 70)
    print("✅ NARRATIVE ARCHITECT TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Consolidated briefs with narrative: {consolidated_path}")
    print(f"📁 Output directory: {article_output_dir}")
    print(f"📊 Trace ID: {trace_id}")

    if failed_items:
        print("\n⚠️  WARNINGS:")
        print(f"   - {len(failed_items)} idea(s) failed narrative generation")
        print("   - Review the errors above before using in production")

    return 0


if __name__ == "__main__":
    sys.exit(main())


