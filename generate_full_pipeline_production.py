#!/usr/bin/env python3
"""
Production script to test the complete pipeline: Ideation -> Narrative -> Copywriting.

Loads an article, generates ideas (Phase 1), builds coherence briefs,
generates narrative structures (Phase 3), and then generates slide copy
with positioning and emphasis (Phase 4 - Copywriter).

All phases update the coherence brief as they progress.
Uses the complete production workflow with integrated SQL logging.
"""

import json
import os
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from src.core.config import IdeationConfig, OUTPUT_DIR
from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.core.prompt_registry import get_latest_prompt
from src.coherence.builder import CoherenceBriefBuilder
from src.ideas.generator import IdeaGenerator
from src.narrative.architect import NarrativeArchitect
from src.copywriting.writer import Copywriter


def main() -> int:
    print("=" * 70)
    print("FULL PIPELINE TEST - IDEATION -> NARRATIVE -> COPYWRITING")
    print("=" * 70)

    # Load environment variables
    load_dotenv()

    # Configuration
    article_path = Path(os.getenv("ARTICLE_PATH", "articles/why-tradicional-learning-fails.md"))
    article_slug = article_path.stem if article_path.suffix else "why-tradicional-learning-fails"

    # Initialize logger with SQL backend
    print("\n1. Initializing logger...")
    logger = LLMLogger(use_sql=True)

    # Create trace for this execution
    trace_id = logger.create_trace(
        name="full_pipeline_test",
        metadata={
            "article_slug": article_slug,
            "article_path": str(article_path),
            "script": "generate_full_pipeline_production",
        },
    )
    logger.set_context(article_slug=article_slug)

    print(f"   ✓ Trace created: {trace_id[:8]}...")
    print(f"   ✓ SQL logging: enabled")

    # Check article file
    print("\n2. Loading article...")
    if not article_path.exists():
        print(f"❌ ERROR: Article file not found: {article_path}")
        return 1

    import time

    load_start = time.time()
    try:
        article_text = article_path.read_text(encoding="utf-8")
        logger.log_step_event(
            trace_id=trace_id,
            name="load_article",
            input_text=f"Loading article from {article_path.name}",
            input_obj={"file_path": str(article_path)},
            output_text=f"Article loaded: {len(article_text)} characters",
            output_obj={"article_length": len(article_text)},
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
            status="success",
        )
    except Exception as exc:
        error_msg = str(exc)
        print(f"❌ ERROR reading article: {error_msg}")
        logger.log_step_event(
            trace_id=trace_id,
            name="load_article",
            input_obj={"file_path": str(article_path)},
            error=error_msg,
            duration_ms=(time.time() - load_start) * 1000,
            type="preprocess",
            status="error",
        )
        return 1

    print(f"   ✓ Article loaded: {len(article_text)} characters")

    # Check API key
    print("\n3. Initializing LLM client...")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERROR: LLM_API_KEY or DEEPSEEK_API_KEY not found in environment")
        return 1

    # Prepare output directories
    article_output_dir = OUTPUT_DIR / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = article_output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

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

    # =====================================================================
    # PHASE 1: IDEATION
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 1: IDEATION")
    print("=" * 70)

    # Verify post_ideator prompt
    print("\n4. Verifying post_ideator prompt...")
    ideator_prompt_key = "post_ideator"
    ideator_prompt_data = get_latest_prompt(ideator_prompt_key)
    if not ideator_prompt_data:
        print(f"   ❌ ERROR: Prompt '{ideator_prompt_key}' not found in database!")
        print(f"   📝 Please register the prompt first.")
        return 1

    print(f"   ✓ Prompt found: {ideator_prompt_key} (version {ideator_prompt_data.get('version', 'N/A')})")

    # Create idea generator
    print("\n5. Creating Idea Generator...")
    idea_generator = IdeaGenerator(llm_client)
    print("   ✓ Idea Generator created")

    # Configure ideation
    ideation_config = IdeationConfig(
        num_ideas_min=3,
        num_ideas_max=5,
        num_insights_min=3,
        num_insights_max=5,
    )

    print(f"\n6. Generating ideas from article...")
    print(f"   ⏳ This may take a while...")
    try:
        ideas_payload = idea_generator.generate_ideas(
            article_text,
            ideation_config,
            context=article_slug,
        )
        print("   ✓ Ideas generated successfully!")

        # Save ideas payload
        ideas_json_path = article_output_dir / "phase1_ideas.json"
        ideas_json_path.write_text(
            json.dumps(ideas_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"   ✓ Ideas saved: {ideas_json_path}")

    except Exception as exc:
        error_msg = str(exc)
        print(f"   ❌ ERROR generating ideas: {error_msg}")
        return 1

    article_summary = ideas_payload.get("article_summary", {})
    all_ideas = ideas_payload.get("ideas", [])

    print(f"   ✓ Total ideas generated: {len(all_ideas)}")
    print(f"   ✓ Article title: {article_summary.get('title', 'N/A')}")

    # Select ideas to process (first N)
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "2"))
    if 0 < max_ideas_to_test < len(all_ideas):
        selected_ideas = all_ideas[:max_ideas_to_test]
        print(f"\n   Selected {len(selected_ideas)} ideas for full pipeline test")
    else:
        selected_ideas = all_ideas
        print(f"\n   Using all {len(selected_ideas)} ideas for full pipeline test")

    # =====================================================================
    # PHASE 2: COHERENCE BRIEFS
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 2: BUILDING COHERENCE BRIEFS")
    print("=" * 70)

    print("\n7. Building coherence briefs from ideas...")
    briefs = []

    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        post_id = f"post_{article_slug}_{idx:03d}"

        print(f"   [{idx}/{len(selected_ideas)}] Building brief for {idea_id}...", end=" ")

        try:
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=article_summary,
                post_id=post_id,
            )

            CoherenceBriefBuilder.validate_brief(brief)
            briefs.append(brief)
            print("✓")

        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ ({error_msg[:60]}...)")
            return 1

    print(f"   ✓ {len(briefs)} coherence brief(s) built successfully")

    # =====================================================================
    # PHASE 3: NARRATIVE ARCHITECT
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 3: NARRATIVE ARCHITECT")
    print("=" * 70)

    # Verify narrative_architect prompt
    print("\n8. Verifying narrative_architect prompt...")
    narrative_prompt_key = "narrative_architect"
    narrative_prompt_data = get_latest_prompt(narrative_prompt_key)
    if not narrative_prompt_data:
        print(f"   ❌ ERROR: Prompt '{narrative_prompt_key}' not found in database!")
        return 1

    print(f"   ✓ Prompt found: {narrative_prompt_key} (version {narrative_prompt_data.get('version', 'N/A')})")

    # Create Narrative Architect
    print("\n9. Creating Narrative Architect...")
    architect = NarrativeArchitect(llm_client=llm_client, logger=logger)
    print("   ✓ Narrative Architect created")

    print("\n10. Generating narrative structures...")
    narrative_results = []

    for idx, brief in enumerate(briefs, 1):
        print(f"   [{idx}/{len(briefs)}] Generating narrative for {brief.post_id}...", end=" ")

        try:
            logger.set_context(post_id=brief.post_id)

            narrative_payload = architect.generate_structure(
                brief=brief,
                context=brief.post_id,
            )

            narrative_results.append({
                "brief": brief,
                "narrative_payload": narrative_payload,
            })

            print("✓")

            # Save updated brief (with narrative evolution)
            post_dir = article_output_dir / brief.post_id
            post_dir.mkdir(parents=True, exist_ok=True)
            brief_path = post_dir / "coherence_brief.json"
            brief_path.write_text(
                json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ ({error_msg[:60]}...)")
            return 1

    print(f"   ✓ {len(narrative_results)} narrative structure(s) generated successfully")

    # =====================================================================
    # PHASE 4: COPYWRITER
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 4: COPYWRITER")
    print("=" * 70)

    # Verify copywriter prompt
    print("\n11. Verifying copywriter prompt...")
    copywriter_prompt_key = "copywriter"
    copywriter_prompt_data = get_latest_prompt(copywriter_prompt_key)
    if not copywriter_prompt_data:
        print(f"   ❌ ERROR: Prompt '{copywriter_prompt_key}' not found in database!")
        print(f"   📝 Please register the prompt first:")
        print(f"      python -m src.cli.commands prompts register prompts/copywriter.md")
        return 1

    print(f"   ✓ Prompt found: {copywriter_prompt_key} (version {copywriter_prompt_data.get('version', 'N/A')})")

    # Create Copywriter
    print("\n12. Creating Copywriter...")
    copywriter = Copywriter(llm_client=llm_client, logger=logger)
    print("   ✓ Copywriter created")

    print("\n13. Generating slide copy for all slides...")
    all_copy_results = []

    for result_idx, result in enumerate(narrative_results, 1):
        brief = result["brief"]
        narrative_payload = result["narrative_payload"]
        slides = narrative_payload.get("slides", [])

        print(f"\n   Post {result_idx}/{len(narrative_results)}: {brief.post_id} ({len(slides)} slides)")

        post_copy_results = []

        for slide_idx, slide_info in enumerate(slides, 1):
            slide_number = slide_info.get("slide_number", slide_idx)
            print(f"      Slide {slide_idx}/{len(slides)} (slide_number={slide_number})...", end=" ")

            try:
                logger.set_context(post_id=brief.post_id)

                slide_content = copywriter.generate_slide_copy(
                    brief=brief,
                    slide_info=slide_info,
                    article_text=article_text,
                    context=f"{brief.post_id}_slide_{slide_number}",
                )

                post_copy_results.append({
                    "slide_number": slide_number,
                    "slide_info": slide_info,
                    "slide_content": slide_content,
                })

                print("✓")

                # Save individual slide content
                post_dir = article_output_dir / brief.post_id
                slide_content_path = post_dir / f"slide_{slide_number}_content.json"
                slide_content_path.write_text(
                    json.dumps(slide_content, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            except Exception as exc:
                error_msg = str(exc)
                print(f"❌ ({error_msg[:60]}...)")
                return 1

        all_copy_results.append({
            "brief": brief,
            "narrative_payload": narrative_payload,
            "slide_contents": post_copy_results,
        })

        # Save updated brief (with copywriting evolution)
        post_dir = article_output_dir / brief.post_id
        brief_path = post_dir / "coherence_brief.json"
        brief_path.write_text(
            json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"      ✓ {len(post_copy_results)} slide(s) processed")

    total_slides = sum(len(r["slide_contents"]) for r in all_copy_results)
    print(f"\n   ✓ {total_slides} total slide(s) processed successfully")

    # =====================================================================
    # SUMMARY AND VALIDATION
    # =====================================================================
    print("\n" + "=" * 70)
    print("SUMMARY AND VALIDATION")
    print("=" * 70)

    print("\n14. Pipeline summary:")

    print(f"\n   Phase 1 (Ideation):")
    print(f"     ✓ Ideas generated: {len(all_ideas)}")
    print(f"     ✓ Ideas processed: {len(selected_ideas)}")

    print(f"\n   Phase 2 (Coherence Briefs):")
    print(f"     ✓ Briefs built: {len(briefs)}")

    print(f"\n   Phase 3 (Narrative Architect):")
    print(f"     ✓ Narrative structures: {len(narrative_results)}")
    for idx, result in enumerate(narrative_results, 1):
        slides_count = len(result["narrative_payload"].get("slides", []))
        print(f"       - Brief {idx}: {slides_count} slides")

    print(f"\n   Phase 4 (Copywriter):")
    print(f"     ✓ Total slides with copy: {total_slides}")
    for idx, result in enumerate(all_copy_results, 1):
        slides_count = len(result["slide_contents"])
        print(f"       - Post {idx}: {slides_count} slides")

    # Validate coherence brief evolution
    print("\n15. Validating coherence brief evolution...")
    for idx, brief in enumerate(briefs, 1):
        has_narrative = brief.narrative_structure is not None
        has_copy_guidelines = brief.copy_guidelines is not None
        has_cta_guidelines = brief.cta_guidelines is not None

        print(f"   Brief {idx} ({brief.post_id}):")
        print(f"     - Narrative structure: {'✓' if has_narrative else '✗'}")
        print(f"     - Copy guidelines: {'✓' if has_copy_guidelines else '✗'}")
        print(f"     - CTA guidelines: {'✓' if has_cta_guidelines else '✗'}")

    # Save consolidated results
    print("\n16. Saving consolidated results...")

    consolidated_briefs = [brief.to_dict() for brief in briefs]
    consolidated_path = article_output_dir / "coherence_briefs_final.json"
    consolidated_path.write_text(
        json.dumps(consolidated_briefs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   ✓ Consolidated briefs: {consolidated_path}")

    # Save all slide contents per post
    for result in all_copy_results:
        brief = result["brief"]
        post_dir = article_output_dir / brief.post_id
        all_slides_content = {
            "post_id": brief.post_id,
            "slides": [
                {
                    "slide_number": sc["slide_number"],
                    "content": sc["slide_content"],
                }
                for sc in result["slide_contents"]
            ],
        }
        all_slides_path = post_dir / "all_slides_content.json"
        all_slides_path.write_text(
            json.dumps(all_slides_content, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"   ✓ All slides content: {all_slides_path}")

    # Verify SQL database
    print("\n17. Verifying SQL database...")
    try:
        from src.core.llm_log_queries import get_trace_with_events
        from src.core.llm_log_db import get_db_path

        db_path = get_db_path()
        trace_data = get_trace_with_events(trace_id, db_path)

        if trace_data:
            events = trace_data.get("events", [])
            print(f"   ✓ Trace found: {trace_id[:8]}..., events: {len(events)}")

            # Event breakdown by type
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
    print("✅ FULL PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Output directory: {article_output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    print(f"📈 Total slides processed: {total_slides}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

