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
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.core.config import IdeationConfig, OUTPUT_DIR
from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.core.llm_log_queries import get_trace_with_events
from src.core.llm_log_db import get_db_path
from src.core.prompt_registry import get_latest_prompt
from src.coherence.builder import CoherenceBriefBuilder
from src.coherence.brief import CoherenceBrief
from src.ideas.generator import IdeaGenerator
from src.narrative.architect import NarrativeArchitect
from src.copywriting.writer import Copywriter


def print_slide_copy_details(
    slide_content: Dict[str, Any],
    slide_info: Dict[str, Any],
    slide_number: int,
) -> None:
    """
    Imprime detalhes completos do conteúdo gerado pelo copywriter para um slide.
    
    Args:
        slide_content: Conteúdo retornado pelo copywriter (title, subtitle, body, etc.)
        slide_info: Informações do slide do narrative structure
        slide_number: Número do slide
    """
    print(f"\n{'─' * 70}")
    print(f"📝 SLIDE COPY DETAILS - Slide {slide_number}")
    print(f"{'─' * 70}")
    
    # Informações do slide
    module_type = slide_info.get("module_type", "unknown")
    purpose = slide_info.get("purpose", "N/A")
    copy_direction = slide_info.get("copy_direction", "N/A")
    
    print(f"\n📌 SLIDE INFO:")
    print(f"   • Module Type: {module_type}")
    print(f"   • Purpose: {purpose}")
    if copy_direction and copy_direction != "N/A":
        print(f"   • Copy Direction: {copy_direction[:100]}..." if len(copy_direction) > 100 else f"   • Copy Direction: {copy_direction}")
    
    # Title
    title_obj = slide_content.get("title")
    if title_obj:
        if isinstance(title_obj, dict):
            title_content = title_obj.get("content", "")
            title_position = title_obj.get("position", {})
            title_emphasis = title_obj.get("emphasis", [])
            
            print(f"\n📰 TITLE:")
            print(f"   • Content: {title_content}")
            if title_position:
                print(f"   • Position: x={title_position.get('x', 'N/A')}, y={title_position.get('y', 'N/A')}")
            if title_emphasis:
                print(f"   • Emphasis ({len(title_emphasis)} span(s)):")
                print(f"      🔍 Emphasis format: {type(title_emphasis).__name__}, items: {[type(item).__name__ for item in title_emphasis[:3]]}")
                for idx, emph in enumerate(title_emphasis, 1):
                    if isinstance(emph, dict):
                        # Handle dict format (legacy format with text, start_index, end_index, styles)
                        emph_text = emph.get("text", "")
                        start_idx = emph.get("start_index", "N/A")
                        end_idx = emph.get("end_index", "N/A")
                        styles = ", ".join(emph.get("styles", []))
                        print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
                    elif isinstance(emph, str):
                        # Handle string format (current format - simple list of strings)
                        print(f"     [{idx}] '{emph}'")
                    else:
                        print(f"     [{idx}] ⚠️  Unexpected type: {type(emph).__name__} - {str(emph)[:50]}")
        else:
            print(f"\n📰 TITLE: {title_obj}")
    else:
        print(f"\n📰 TITLE: (null)")
    
    # Subtitle
    subtitle_obj = slide_content.get("subtitle")
    if subtitle_obj:
        if isinstance(subtitle_obj, dict):
            subtitle_content = subtitle_obj.get("content", "")
            subtitle_position = subtitle_obj.get("position", {})
            subtitle_emphasis = subtitle_obj.get("emphasis", [])
            
            print(f"\n📄 SUBTITLE:")
            print(f"   • Content: {subtitle_content}")
            if subtitle_position:
                print(f"   • Position: x={subtitle_position.get('x', 'N/A')}, y={subtitle_position.get('y', 'N/A')}")
            if subtitle_emphasis:
                print(f"   • Emphasis ({len(subtitle_emphasis)} span(s)):")
                print(f"      🔍 Emphasis format: {type(subtitle_emphasis).__name__}, items: {[type(item).__name__ for item in subtitle_emphasis[:3]]}")
                for idx, emph in enumerate(subtitle_emphasis, 1):
                    if isinstance(emph, dict):
                        # Handle dict format (legacy format with text, start_index, end_index, styles)
                        emph_text = emph.get("text", "")
                        start_idx = emph.get("start_index", "N/A")
                        end_idx = emph.get("end_index", "N/A")
                        styles = ", ".join(emph.get("styles", []))
                        print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
                    elif isinstance(emph, str):
                        # Handle string format (current format - simple list of strings)
                        print(f"     [{idx}] '{emph}'")
                    else:
                        print(f"     [{idx}] ⚠️  Unexpected type: {type(emph).__name__} - {str(emph)[:50]}")
        else:
            print(f"\n📄 SUBTITLE: {subtitle_obj}")
    else:
        print(f"\n📄 SUBTITLE: (null)")
    
    # Body
    body_obj = slide_content.get("body")
    if body_obj:
        if isinstance(body_obj, dict):
            body_content = body_obj.get("content", "")
            body_position = body_obj.get("position", {})
            body_emphasis = body_obj.get("emphasis", [])
            
            print(f"\n📝 BODY:")
            print(f"   • Content ({len(body_content)} chars):")
            # Mostrar body com quebras de linha se for muito longo
            if len(body_content) > 200:
                print(f"     {body_content[:200]}...")
                print(f"     ... ({len(body_content) - 200} more chars)")
            else:
                # Mostrar em múltiplas linhas se tiver quebras
                lines = body_content.split('\n')
                for line in lines:
                    print(f"     {line}")
            if body_position:
                print(f"   • Position: x={body_position.get('x', 'N/A')}, y={body_position.get('y', 'N/A')}")
            if body_emphasis:
                print(f"   • Emphasis ({len(body_emphasis)} span(s)):")
                print(f"      🔍 Emphasis format: {type(body_emphasis).__name__}, items: {[type(item).__name__ for item in body_emphasis[:3]]}")
                for idx, emph in enumerate(body_emphasis, 1):
                    if isinstance(emph, dict):
                        # Handle dict format (legacy format with text, start_index, end_index, styles)
                        emph_text = emph.get("text", "")
                        start_idx = emph.get("start_index", "N/A")
                        end_idx = emph.get("end_index", "N/A")
                        styles = ", ".join(emph.get("styles", []))
                        print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
                    elif isinstance(emph, str):
                        # Handle string format (current format - simple list of strings)
                        print(f"     [{idx}] '{emph}'")
                    else:
                        print(f"     [{idx}] ⚠️  Unexpected type: {type(emph).__name__} - {str(emph)[:50]}")
        else:
            print(f"\n📝 BODY: {body_obj}")
    else:
        print(f"\n📝 BODY: (null)")
    
    # Copy Guidelines
    copy_guidelines = slide_content.get("copy_guidelines", {})
    if copy_guidelines:
        print(f"\n✍️  COPY GUIDELINES:")
        headline_style = copy_guidelines.get("headline_style")
        body_style = copy_guidelines.get("body_style")
        if headline_style:
            print(f"   • Headline Style: {headline_style}")
        if body_style:
            print(f"   • Body Style: {body_style}")
        if not headline_style and not body_style:
            print(f"   • (empty guidelines)")
    else:
        print(f"\n✍️  COPY GUIDELINES: (null)")
    
    # CTA Guidelines
    cta_guidelines = slide_content.get("cta_guidelines")
    if cta_guidelines:
        print(f"\n🎯 CTA GUIDELINES:")
        if isinstance(cta_guidelines, dict):
            for key, value in cta_guidelines.items():
                if isinstance(value, (str, int, float, bool)):
                    print(f"   • {key}: {value}")
                elif isinstance(value, list):
                    print(f"   • {key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"   • {key}: {json.dumps(value, ensure_ascii=False)[:100]}...")
        else:
            print(f"   • {cta_guidelines}")
    else:
        print(f"\n🎯 CTA GUIDELINES: (null)")
    
    print(f"{'─' * 70}\n")


def generate_workflow_documentation(
    trace_id: str,
    article_slug: str,
    article_text: str,
    all_ideas: List[Dict[str, Any]],
    all_copy_results: List[Dict[str, Any]],
    logger: LLMLogger,
    article_output_dir: Path,
    execution_metrics: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Generate a detailed Markdown document with complete workflow and outputs.
    
    Args:
        trace_id: Trace ID to fetch events from database
        article_slug: Slug of processed article
        article_text: Full article text
        all_ideas: List of all generated ideas
        all_copy_results: List of all copywriting results
        logger: LLMLogger with calls
        article_output_dir: Article output directory
        execution_metrics: Optional execution metrics including phase timings, errors, warnings
        
    Returns:
        Path to the generated documentation file
        
    Raises:
        Exception: If documentation generation fails, with full traceback information
    """
    
    # Buscar trace completo do banco de dados
    db_path = get_db_path()
    trace_data = get_trace_with_events(trace_id, db_path)
    
    # Criar diretório para documentação
    doc_dir = article_output_dir / "workflow_documentation"
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_path = doc_dir / f"workflow_{article_slug}_{timestamp}.md"
    
    # Começar a construir o documento
    lines = []
    
    # Cabeçalho
    lines.append(f"# Workflow Documentation - {article_slug}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Trace ID:** `{trace_id}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Overview](#overview)")
    lines.append("2. [Performance Metrics](#performance-metrics)")
    lines.append("3. [Execution Timeline](#execution-timeline)")
    lines.append("4. [Errors and Warnings](#errors-and-warnings)")
    lines.append("5. [Article Content](#article-content)")
    lines.append("6. [Phase 1: Ideation](#phase-1-ideation)")
    lines.append("7. [Phase 2: Coherence Briefs](#phase-2-coherence-briefs)")
    lines.append("8. [Phase 3: Narrative Architect](#phase-3-narrative-architect)")
    lines.append("9. [Template Selection System](#template-selection-system)")
    lines.append("10. [Phase 4: Copywriter](#phase-4-copywriter)")
    lines.append("11. [LLM Events & Responses](#llm-events--responses)")
    lines.append("12. [Metrics Summary](#metrics-summary)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Overview
    lines.append("## Overview")
    lines.append("")
    if trace_data:
        trace_metadata = trace_data.get("metadata", {})
        lines.append(f"- **Article:** {trace_metadata.get('article_slug', article_slug)}")
        lines.append(f"- **Total Ideas Generated:** {len(all_ideas)}")
        lines.append(f"- **Total Posts Processed:** {len(all_copy_results)}")
        total_slides = sum(len(r.get("slide_contents", [])) if isinstance(r.get("slide_contents"), list) else 0 for r in all_copy_results)
        lines.append(f"- **Total Slides Generated:** {total_slides}")
        lines.append(f"- **Trace Created:** {trace_data.get('created_at', 'N/A')}")
    
    # Add overall execution time if available
    if execution_metrics and execution_metrics.get("pipeline_start_time") and execution_metrics.get("pipeline_end_time"):
        total_duration = execution_metrics["pipeline_end_time"] - execution_metrics["pipeline_start_time"]
        lines.append(f"- **Total Pipeline Duration:** {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    
    # Add error/warning summary if available
    if execution_metrics:
        errors = execution_metrics.get("errors", [])
        warnings = execution_metrics.get("warnings", [])
        if errors or warnings:
            lines.append(f"- **Errors:** {len(errors)}")
            lines.append(f"- **Warnings:** {len(warnings)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Performance Metrics
    lines.append("## Performance Metrics")
    lines.append("")
    if execution_metrics and execution_metrics.get("phase_timings"):
        phase_timings = execution_metrics["phase_timings"]
        lines.append("### Phase Execution Times")
        lines.append("")
        lines.append("| Phase | Duration (seconds) | Duration (minutes) | Status |")
        lines.append("|-------|-------------------|-------------------|--------|")
        
        for phase_name, phase_data in phase_timings.items():
            if isinstance(phase_data, dict):
                duration = phase_data.get("duration", 0)
                status = phase_data.get("status", "completed")
                status_icon = "✓" if status == "completed" else "✗" if status == "failed" else "⚠"
                lines.append(f"| {phase_name} | {duration:.2f} | {duration/60:.2f} | {status_icon} {status} |")
        
        lines.append("")
        
        # Calculate averages if multiple items processed
        if execution_metrics.get("items_processed"):
            items = execution_metrics["items_processed"]
            if items.get("ideas") and items["ideas"].get("count", 0) > 0:
                ideation_time = phase_timings.get("Phase 1: Ideation", {}).get("duration", 0)
                if ideation_time > 0:
                    time_per_idea = ideation_time / items["ideas"]["count"]
                    lines.append(f"- **Average time per idea:** {time_per_idea:.2f} seconds")
            
            if items.get("posts") and items["posts"].get("count", 0) > 0:
                copywriting_time = phase_timings.get("Phase 4: Copywriting", {}).get("duration", 0)
                if copywriting_time > 0:
                    time_per_post = copywriting_time / items["posts"]["count"]
                    lines.append(f"- **Average time per post:** {time_per_post:.2f} seconds")
            
            total_slides = sum(len(r.get("slide_contents", [])) if isinstance(r.get("slide_contents"), list) else 0 for r in all_copy_results)
            if total_slides > 0:
                copywriting_time = phase_timings.get("Phase 4: Copywriting", {}).get("duration", 0)
                if copywriting_time > 0:
                    time_per_slide = copywriting_time / total_slides
                    lines.append(f"- **Average time per slide:** {time_per_slide:.2f} seconds")
                    lines.append(f"- **Slide generation rate:** {total_slides/copywriting_time:.2f} slides/second")
        
        lines.append("")
    else:
        lines.append("*No performance metrics available*")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Execution Timeline
    lines.append("## Execution Timeline")
    lines.append("")
    if execution_metrics and execution_metrics.get("phase_timings"):
        phase_timings = execution_metrics["phase_timings"]
        lines.append("### Timeline of Pipeline Phases")
        lines.append("")
        
        # Sort phases by start time if available
        sorted_phases = sorted(
            phase_timings.items(),
            key=lambda x: x[1].get("start_time", 0) if isinstance(x[1], dict) else 0
        )
        
        for phase_name, phase_data in sorted_phases:
            if isinstance(phase_data, dict):
                start_time = phase_data.get("start_time")
                end_time = phase_data.get("end_time")
                duration = phase_data.get("duration", 0)
                
                lines.append(f"#### {phase_name}")
                lines.append("")
                if start_time:
                    start_str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                    lines.append(f"- **Started:** {start_str}")
                if end_time:
                    end_str = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                    lines.append(f"- **Ended:** {end_str}")
                lines.append(f"- **Duration:** {duration:.2f} seconds")
                
                # Add phase-specific details if available
                if phase_data.get("details"):
                    lines.append(f"- **Details:** {phase_data['details']}")
                lines.append("")
    else:
        lines.append("*No timeline data available*")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Errors and Warnings
    lines.append("## Errors and Warnings")
    lines.append("")
    if execution_metrics:
        errors = execution_metrics.get("errors", [])
        warnings = execution_metrics.get("warnings", [])
        
        if errors:
            lines.append("### Errors")
            lines.append("")
            for idx, error in enumerate(errors, 1):
                error_phase = error.get("phase", "Unknown")
                error_message = error.get("message", "No message")
                error_time = error.get("timestamp")
                error_type = error.get("type", "Error")
                
                lines.append(f"#### Error {idx}: {error_type}")
                lines.append("")
                lines.append(f"- **Phase:** {error_phase}")
                if error_time:
                    time_str = datetime.fromtimestamp(error_time).strftime('%Y-%m-%d %H:%M:%S')
                    lines.append(f"- **Time:** {time_str}")
                lines.append(f"- **Message:** {error_message}")
                
                # Add full traceback if available
                if error.get("traceback"):
                    lines.append("")
                    lines.append("**Full Traceback:**")
                    lines.append("")
                    lines.append("```")
                    lines.append(error["traceback"])
                    lines.append("```")
                lines.append("")
        else:
            lines.append("### Errors")
            lines.append("")
            lines.append("*No errors occurred during execution*")
            lines.append("")
        
        if warnings:
            lines.append("### Warnings")
            lines.append("")
            for idx, warning in enumerate(warnings, 1):
                warning_phase = warning.get("phase", "Unknown")
                warning_message = warning.get("message", "No message")
                warning_time = warning.get("timestamp")
                
                lines.append(f"#### Warning {idx}")
                lines.append("")
                lines.append(f"- **Phase:** {warning_phase}")
                if warning_time:
                    time_str = datetime.fromtimestamp(warning_time).strftime('%Y-%m-%d %H:%M:%S')
                    lines.append(f"- **Time:** {time_str}")
                lines.append(f"- **Message:** {warning_message}")
                lines.append("")
        else:
            lines.append("### Warnings")
            lines.append("")
            lines.append("*No warnings during execution*")
            lines.append("")
    else:
        lines.append("*No error/warning tracking data available*")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Article Content
    lines.append("## Article Content")
    lines.append("")
    lines.append(f"**Length:** {len(article_text)} characters")
    lines.append("")
    lines.append("```")
    lines.append(article_text[:2000] + ("..." if len(article_text) > 2000 else ""))
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Phase 1: Ideation
    lines.append("## Phase 1: Ideation")
    lines.append("")
    lines.append(f"**Total Ideas:** {len(all_ideas)}")
    lines.append("")
    for idx, idea in enumerate(all_ideas, 1):
        lines.append(f"### Idea {idx}: {idea.get('id', 'unknown')}")
        lines.append("")
        lines.append(f"- **Platform:** {idea.get('platform', 'N/A')}")
        lines.append(f"- **Format:** {idea.get('format', 'N/A')}")
        lines.append(f"- **Tone:** {idea.get('tone', 'N/A')}")
        lines.append(f"- **Objective:** {idea.get('objective', 'N/A')}")
        lines.append(f"- **Hook:** {idea.get('hook', 'N/A')}")
        lines.append(f"- **Estimated Slides:** {idea.get('estimated_slides', 'N/A')}")
        lines.append(f"- **Confidence:** {idea.get('confidence', 'N/A')}")
        lines.append("")
        if idea.get('rationale'):
            lines.append("**Rationale:**")
            lines.append("")
            lines.append(idea['rationale'])
            lines.append("")
        if idea.get('idea_explanation'):
            lines.append("**Idea Explanation:**")
            lines.append("")
            lines.append(idea['idea_explanation'][:500] + ("..." if len(idea.get('idea_explanation', '')) > 500 else ""))
            lines.append("")
        lines.append("---")
        lines.append("")
    
    # Phase 2 & 3 & 4: Para cada post
    for result_idx, result in enumerate(all_copy_results, 1):
        brief = result["brief"]
        narrative_payload = result.get("narrative_payload", {})
        slide_contents = result.get("slide_contents", [])
        
        # Ensure narrative_payload is a dict (not a string or other type)
        if not isinstance(narrative_payload, dict):
            if isinstance(narrative_payload, str):
                try:
                    import json
                    narrative_payload = json.loads(narrative_payload)
                except (json.JSONDecodeError, ValueError):
                    narrative_payload = {}
            else:
                narrative_payload = {}
        
        # Ensure slide_contents is a list
        if not isinstance(slide_contents, list):
            slide_contents = []
        
        lines.append(f"## Post {result_idx}: {brief.post_id}")
        lines.append("")
        
        # Coherence Brief
        lines.append("### Coherence Brief")
        lines.append("")
        lines.append(f"- **Platform:** {brief.platform}")
        lines.append(f"- **Format:** {brief.format}")
        lines.append(f"- **Tone:** {brief.tone}")
        lines.append(f"- **Persona:** {brief.persona}")
        lines.append(f"- **Main Message:** {brief.main_message}")
        lines.append(f"- **Value Proposition:** {brief.value_proposition}")
        lines.append(f"- **Hook:** {brief.hook}")
        lines.append(f"- **Keywords:** {', '.join(brief.keywords_to_emphasize[:10])}")
        lines.append("")
        
        # Narrative Structure Overview
        if narrative_payload and isinstance(narrative_payload, dict):
            lines.append("### Narrative Structure Overview")
            lines.append("")
            # Support both "pacing" (normalized) and "narrative_pacing" (raw response)
            pacing_value = narrative_payload.get('narrative_pacing') or narrative_payload.get('pacing', 'N/A')
            lines.append(f"- **Pacing:** {pacing_value}")
            lines.append(f"- **Transition Style:** {narrative_payload.get('transition_style', 'N/A')}")
            lines.append(f"- **Total Slides:** {len(narrative_payload.get('slides', []))}")
            slides = narrative_payload.get("slides", [])
            if narrative_payload.get('arc_refined'):
                lines.append(f"- **Arc Refined:** {narrative_payload.get('arc_refined', 'N/A')}")
            lines.append("")
            
            # Template Selection Details
            template_selection_stats = narrative_payload.get("_template_selection_stats", {})
            if template_selection_stats or (isinstance(slides, list) and any(isinstance(slide, dict) and slide.get("template_id") for slide in slides)):
                lines.append("### Template Selection System")
                lines.append("")
                
                # Template statistics
                if template_selection_stats:
                    total_slides = template_selection_stats.get("total_slides", 0)
                    templates_selected = template_selection_stats.get("templates_selected", 0)
                    templates_missing = template_selection_stats.get("templates_missing", 0)
                    avg_confidence = template_selection_stats.get("avg_confidence", 0.0)
                    
                    lines.append("#### Template Selection Statistics")
                    lines.append("")
                    lines.append(f"- **Total Slides:** {total_slides}")
                    lines.append(f"- **Templates Selected:** {templates_selected}")
                    if templates_missing > 0:
                        lines.append(f"- **Templates Missing:** {templates_missing} ⚠️")
                    if avg_confidence > 0:
                        lines.append(f"- **Average Confidence:** {avg_confidence:.2f}")
                    lines.append("")
                
                # Template breakdown by slide
                lines.append("#### Templates by Slide")
                lines.append("")
                template_ids = set()
                for slide in slides:
                    slide_num = slide.get("slide_number", "?")
                    template_type = slide.get("template_type", "unknown")
                    value_subtype = slide.get("value_subtype")
                    template_id = slide.get("template_id")
                    template_confidence = slide.get("template_confidence")
                    template_justification = slide.get("template_justification", "")
                    
                    template_type_display = f"{template_type}/{value_subtype}" if value_subtype else template_type
                    
                    if template_id:
                        template_ids.add(template_id)
                        status_icon = "✓"
                        lines.append(f"- **Slide {slide_num}** ({template_type_display}): `{template_id}`")
                        if template_confidence is not None:
                            lines.append(f"  - Confidence: {template_confidence:.2f}")
                        if template_justification:
                            justification_preview = template_justification[:200] + "..." if len(template_justification) > 200 else template_justification
                            lines.append(f"  - Justification: {justification_preview}")
                    else:
                        status_icon = "✗"
                        lines.append(f"- **Slide {slide_num}** ({template_type_display}): *(no template selected)* ⚠️")
                    lines.append("")
                
                if template_ids:
                    lines.append(f"- **Unique Templates Used:** {len(template_ids)}")
                    lines.append("")
        
        # Combine narrative structure and copy for each slide
        lines.append("### Slides: Narrative Structure & Copy")
        lines.append("")
        
        # Normalize slide_numbers to int for consistent matching
        def normalize_slide_number(num):
            """Normalize slide_number to int for consistent dict lookups."""
            if num is None or num == "?":
                return None
            try:
                return int(num)
            except (ValueError, TypeError):
                return num
        
        # Create maps for easy lookup
        slides_narrative = {}
        if narrative_payload and isinstance(narrative_payload, dict):
            slides_list = narrative_payload.get("slides", [])
            if isinstance(slides_list, list):
                for slide in slides_list:
                    if isinstance(slide, dict):
                        slide_num_raw = slide.get("slide_number", "?")
                        slide_num = normalize_slide_number(slide_num_raw)
                        # Store with normalized key
                        if slide_num is not None:
                            slides_narrative[slide_num] = slide
                            # Also store with original value if different
                            if slide_num != slide_num_raw:
                                slides_narrative[slide_num_raw] = slide
        
        slides_copy_map = {}
        if isinstance(slide_contents, list):
            for slide_result in slide_contents:
                if isinstance(slide_result, dict):
                    slide_num_raw = slide_result.get("slide_number")
                    slide_num = normalize_slide_number(slide_num_raw)
                    if slide_num is not None:
                        # Store with normalized key
                        slides_copy_map[slide_num] = slide_result.get("slide_content")
                        # Also store with original value if different
                        if slide_num != slide_num_raw:
                            slides_copy_map[slide_num_raw] = slide_result.get("slide_content")
        
        # Get all slide numbers in order (normalize for comparison)
        all_slide_nums_raw = set(list(slides_narrative.keys()) + list(slides_copy_map.keys()))
        all_slide_nums_normalized = set()
        for num in all_slide_nums_raw:
            normalized = normalize_slide_number(num)
            if normalized is not None:
                all_slide_nums_normalized.add(normalized)
            else:
                all_slide_nums_normalized.add(num)
        all_slide_nums = sorted(all_slide_nums_normalized)
        
        for slide_num in all_slide_nums:
            # Try normalized lookup first, then fallback to raw
            slide_narrative = slides_narrative.get(slide_num)
            if not slide_narrative:
                # Try to find by iterating through keys
                for key in slides_narrative.keys():
                    if normalize_slide_number(key) == slide_num:
                        slide_narrative = slides_narrative[key]
                        break
            
            slide_content = slides_copy_map.get(slide_num)
            if not slide_content:
                # Try to find by iterating through keys
                for key in slides_copy_map.keys():
                    if normalize_slide_number(key) == slide_num:
                        slide_content = slides_copy_map[key]
                        break
            
            lines.append(f"#### Slide {slide_num}")
            lines.append("")
            
            # Narrative Structure for this slide
            if slide_narrative:
                template_type = slide_narrative.get("template_type", "unknown")
                value_subtype = slide_narrative.get("value_subtype")
                type_display = f"{template_type}/{value_subtype}" if value_subtype else template_type
                lines.append(f"**Type:** {type_display}")
                lines.append("")
                
                template_id = slide_narrative.get("template_id")
                template_justification = slide_narrative.get("template_justification")
                template_confidence = slide_narrative.get("template_confidence")
                if template_id:
                    lines.append(f"**Template ID:** {template_id}")
                    lines.append("")
                if template_justification:
                    lines.append("**Template Justification:**")
                    lines.append("")
                    lines.append(template_justification[:400] + ("..." if len(template_justification) > 400 else ""))
                    lines.append("")
                if template_confidence is not None:
                    lines.append(f"**Template Confidence:** {template_confidence}")
                    lines.append("")
                
                lines.append(f"**Purpose:** {slide_narrative.get('purpose', 'N/A')}")
                lines.append("")
                
                copy_dir = slide_narrative.get("copy_direction", "")
                if copy_dir:
                    lines.append(f"**Copy Direction:**")
                    lines.append("")
                    lines.append(copy_dir[:400] + ("..." if len(copy_dir) > 400 else ""))
                    lines.append("")
                
                visual_dir = slide_narrative.get("visual_direction", "")
                if visual_dir:
                    lines.append(f"**Visual Direction:**")
                    lines.append("")
                    lines.append(visual_dir[:400] + ("..." if len(visual_dir) > 400 else ""))
                    lines.append("")
                
                key_elements = slide_narrative.get("key_elements", [])
                if key_elements:
                    lines.append(f"**Key Elements:** {', '.join(key_elements)}")
                    lines.append("")
                
                insights_ref = slide_narrative.get("insights_referenced", [])
                if insights_ref:
                    lines.append(f"**Insights Referenced:** {', '.join(insights_ref)}")
                    lines.append("")
            
            lines.append("---")
            lines.append("")
            
            # Copy Content for this slide
            if slide_content:
                lines.append(f"**Generated Copy:**")
                lines.append("")
                
                # Title
                title_obj = slide_content.get("title")
                if title_obj:
                    if isinstance(title_obj, dict):
                        title_content = title_obj.get("content", "")
                        title_position = title_obj.get("position", {})
                        title_emphasis = title_obj.get("emphasis", [])
                        
                        lines.append(f"##### Title")
                        lines.append("")
                        lines.append(f"**Content:** {title_content}")
                        lines.append("")
                        
                        if title_position:
                            pos_x = title_position.get("x", "N/A")
                            pos_y = title_position.get("y", "N/A")
                            lines.append(f"- **Position:** x={pos_x}, y={pos_y}")
                        
                        if title_emphasis and isinstance(title_emphasis, list):
                            lines.append(f"- **Emphasis Spans:** {len(title_emphasis)}")
                            lines.append("")
                            for idx, emph_item in enumerate(title_emphasis, 1):
                                if isinstance(emph_item, str):
                                    lines.append(f"  {idx}. Text: `{emph_item}`")
                                else:
                                    lines.append(f"  {idx}. Text: `{str(emph_item)}`")
                        else:
                            lines.append(f"- **Emphasis Spans:** None")
                        lines.append("")
                    else:
                        lines.append(f"##### Title")
                        lines.append("")
                        lines.append(f"{title_obj}")
                        lines.append("")
                else:
                    lines.append(f"##### Title")
                    lines.append("")
                    lines.append(f"*(null)*")
                    lines.append("")
                
                # Subtitle
                subtitle_obj = slide_content.get("subtitle")
                if subtitle_obj:
                    if isinstance(subtitle_obj, dict):
                        subtitle_content = subtitle_obj.get("content", "")
                        subtitle_position = subtitle_obj.get("position", {})
                        subtitle_emphasis = subtitle_obj.get("emphasis", [])
                        
                        lines.append(f"##### Subtitle")
                        lines.append("")
                        lines.append(f"**Content:** {subtitle_content}")
                        lines.append("")
                        
                        if subtitle_position:
                            pos_x = subtitle_position.get("x", "N/A")
                            pos_y = subtitle_position.get("y", "N/A")
                            lines.append(f"- **Position:** x={pos_x}, y={pos_y}")
                        
                        if subtitle_emphasis and isinstance(subtitle_emphasis, list):
                            lines.append(f"- **Emphasis Spans:** {len(subtitle_emphasis)}")
                            lines.append("")
                            for idx, emph_item in enumerate(subtitle_emphasis, 1):
                                if isinstance(emph_item, str):
                                    lines.append(f"  {idx}. Text: `{emph_item}`")
                                else:
                                    lines.append(f"  {idx}. Text: `{str(emph_item)}`")
                        else:
                            lines.append(f"- **Emphasis Spans:** None")
                        lines.append("")
                    else:
                        lines.append(f"##### Subtitle")
                        lines.append("")
                        lines.append(f"{subtitle_obj}")
                        lines.append("")
                else:
                    lines.append(f"##### Subtitle")
                    lines.append("")
                    lines.append(f"*(null)*")
                    lines.append("")
                
                # Body
                body_obj = slide_content.get("body")
                if body_obj:
                    if isinstance(body_obj, dict):
                        body_content = body_obj.get("content", "")
                        body_position = body_obj.get("position", {})
                        body_emphasis = body_obj.get("emphasis", [])
                        
                        lines.append(f"##### Body")
                        lines.append("")
                        lines.append(f"**Content:** ({len(body_content)} characters)")
                        lines.append("")
                        
                        if body_content:
                            lines.append("```")
                            # Show full body content with proper formatting
                            for line in body_content.split('\n'):
                                lines.append(line)
                            lines.append("```")
                            lines.append("")
                        
                        if body_position:
                            pos_x = body_position.get("x", "N/A")
                            pos_y = body_position.get("y", "N/A")
                            lines.append(f"- **Position:** x={pos_x}, y={pos_y}")
                        
                        if body_emphasis and isinstance(body_emphasis, list):
                            lines.append(f"- **Emphasis Spans:** {len(body_emphasis)}")
                            lines.append("")
                            for idx, emph_item in enumerate(body_emphasis, 1):
                                if isinstance(emph_item, str):
                                    lines.append(f"  {idx}. Text: `{emph_item}`")
                                else:
                                    lines.append(f"  {idx}. Text: `{str(emph_item)}`")
                        else:
                            lines.append(f"- **Emphasis Spans:** None")
                        lines.append("")
                    else:
                        lines.append(f"##### Body")
                        lines.append("")
                        lines.append(f"{body_obj}")
                        lines.append("")
                else:
                    lines.append(f"##### Body")
                    lines.append("")
                    lines.append(f"*(null)*")
                    lines.append("")
                
                # Copy Guidelines
                copy_guidelines = slide_content.get("copy_guidelines", {})
                if copy_guidelines:
                    headline_style = copy_guidelines.get("headline_style")
                    body_style = copy_guidelines.get("body_style")
                    if headline_style or body_style:
                        lines.append(f"##### Copy Guidelines")
                        lines.append("")
                        if headline_style:
                            lines.append(f"- **Headline Style:** {headline_style}")
                        if body_style:
                            lines.append(f"- **Body Style:** {body_style}")
                        lines.append("")
                
                # CTA Guidelines
                cta_guidelines = slide_content.get("cta_guidelines")
                if cta_guidelines:
                    lines.append(f"##### CTA Guidelines")
                    lines.append("")
                    if isinstance(cta_guidelines, dict):
                        for key, value in cta_guidelines.items():
                            if isinstance(value, (str, int, float, bool)):
                                lines.append(f"- **{key}:** {value}")
                            elif isinstance(value, list):
                                lines.append(f"- **{key}:** {', '.join(str(v) for v in value)}")
                            else:
                                lines.append(f"- **{key}:** `{json.dumps(value, ensure_ascii=False)}`")
                    else:
                        lines.append(f"{cta_guidelines}")
                    lines.append("")
            else:
                lines.append("**Generated Copy:**")
                lines.append("")
                lines.append("*Copy not generated for this slide*")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Template Selection System (Global Section)
    lines.append("## Template Selection System")
    lines.append("")
    lines.append("This section provides an overview of the template-based architecture and template selection results.")
    lines.append("")
    
    # Check if any templates were selected
    all_template_stats = []
    all_template_ids = set()
    for result in all_copy_results:
        narrative_payload = result.get("narrative_payload", {})
        
        # Ensure narrative_payload is a dict
        if not isinstance(narrative_payload, dict):
            if isinstance(narrative_payload, str):
                try:
                    import json
                    narrative_payload = json.loads(narrative_payload)
                except (json.JSONDecodeError, ValueError):
                    narrative_payload = {}
            else:
                narrative_payload = {}
        
        template_stats = narrative_payload.get("_template_selection_stats", {})
        if template_stats and isinstance(template_stats, dict):
            all_template_stats.append(template_stats)
        
        slides = narrative_payload.get("slides", [])
        if isinstance(slides, list):
            for slide in slides:
                if isinstance(slide, dict):
                    template_id = slide.get("template_id")
                    if template_id:
                        all_template_ids.add(template_id)
    
    if all_template_stats or all_template_ids:
        lines.append("### Overall Template Selection Statistics")
        lines.append("")
        if all_template_stats:
            total_slides = sum(s.get("total_slides", 0) for s in all_template_stats)
            total_selected = sum(s.get("templates_selected", 0) for s in all_template_stats)
            total_missing = sum(s.get("templates_missing", 0) for s in all_template_stats)
            all_confidences = []
            for stats in all_template_stats:
                if stats.get("avg_confidence", 0) > 0:
                    all_confidences.append(stats["avg_confidence"])
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
            
            lines.append(f"- **Total Slides Processed:** {total_slides}")
            lines.append(f"- **Templates Successfully Selected:** {total_selected}")
            if total_missing > 0:
                lines.append(f"- **Templates Missing:** {total_missing} ⚠️")
                lines.append(f"- **Success Rate:** {(total_selected / total_slides * 100):.1f}%")
            if avg_confidence > 0:
                lines.append(f"- **Average Confidence:** {avg_confidence:.2f}")
            if all_template_ids:
                lines.append(f"- **Unique Templates Used:** {len(all_template_ids)}")
                lines.append(f"- **Template IDs:** {', '.join(sorted(all_template_ids))}")
        lines.append("")
    
    lines.append("### Template System Architecture")
    lines.append("")
    lines.append("The template-based architecture uses semantic analysis to select appropriate textual templates for each slide:")
    lines.append("")
    lines.append("1. **Narrative Architect** generates narrative structure with `template_type` and `value_subtype`")
    lines.append("2. **Template Selector** uses embeddings (or fallback method) to select specific `template_id`")
    lines.append("3. **Copywriter** uses `template_id` and template structures to generate copy")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # LLM Events & Responses
    lines.append("## LLM Events & Responses")
    lines.append("")
    if trace_data and trace_data.get("events"):
        events = trace_data["events"]
        llm_events = [e for e in events if e.get("type") == "llm"]
        
        lines.append(f"**Total LLM Events:** {len(llm_events)}")
        lines.append("")
        
        # Agrupar por fase
        events_by_phase = {}
        for event in llm_events:
            phase = event.get("phase", "unknown")
            if phase not in events_by_phase:
                events_by_phase[phase] = []
            events_by_phase[phase].append(event)
        
        for phase, phase_events in sorted(events_by_phase.items()):
            lines.append(f"### Phase: {phase}")
            lines.append("")
            
            for idx, event in enumerate(phase_events, 1):
                event_name = event.get("name", "unknown")
                metadata = event.get("metadata") or {}
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                function_name = metadata.get("function", "unknown") if isinstance(metadata, dict) else "unknown"
                
                lines.append(f"#### Event {idx}: {event_name}")
                lines.append("")
                lines.append(f"- **Function:** {function_name}")
                lines.append(f"- **Model:** {event.get('model', 'N/A')}")
                lines.append(f"- **Status:** {event.get('status', 'N/A')}")
                duration = event.get('duration_ms') or event.get('duration_ms', 0)
                lines.append(f"- **Duration:** {float(duration):.0f} ms")
                tokens_input = event.get('tokens_input', 0) or 0
                tokens_output = event.get('tokens_output', 0) or 0
                lines.append(f"- **Tokens:** {tokens_input:,} in / {tokens_output:,} out")
                cost = event.get('cost_estimate') or event.get('cost', 0) or 0.0
                lines.append(f"- **Cost:** ${float(cost):.6f}")
                lines.append("")
                
                # Input
                input_text = event.get("input_text", "")
                input_obj = event.get("input_obj") or {}
                if isinstance(input_obj, dict) and input_obj.get("prompt"):
                    input_text = input_obj.get("prompt", input_text)
                
                if input_text:
                    lines.append("**Input Prompt:**")
                    lines.append("")
                    lines.append("```")
                    lines.append(input_text[:2000] + ("..." if len(input_text) > 2000 else ""))
                    lines.append("```")
                    lines.append("")
                
                # Output
                output_text = event.get("output_text", "")
                output_json = event.get("output_json") or event.get("output_obj")
                
                if output_json:
                    lines.append("**Output (JSON):**")
                    lines.append("")
                    lines.append("```json")
                    if isinstance(output_json, dict):
                        output_json_str = json.dumps(output_json, indent=2, ensure_ascii=False)
                    else:
                        output_json_str = str(output_json)
                    lines.append(output_json_str[:5000] + ("..." if len(output_json_str) > 5000 else ""))
                    lines.append("```")
                    lines.append("")
                elif output_text:
                    lines.append("**Output:**")
                    lines.append("")
                    lines.append("```")
                    lines.append(output_text[:2000] + ("..." if len(output_text) > 2000 else ""))
                    lines.append("```")
                    lines.append("")
                
                if event.get("error"):
                    lines.append(f"**Error:** {event.get('error')}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
    
    # Metrics Summary
    lines.append("## Metrics Summary")
    lines.append("")
    
    if logger and logger.calls:
        total_tokens_input = sum(c.get("metrics", {}).get("tokens_input", 0) or 0 for c in logger.calls)
        total_tokens_output = sum(c.get("metrics", {}).get("tokens_output", 0) or 0 for c in logger.calls)
        total_tokens = sum(c.get("metrics", {}).get("tokens_total", 0) or 0 for c in logger.calls)
        total_duration = sum(c.get("metrics", {}).get("duration_ms", 0) or 0 for c in logger.calls)
        total_cost = sum(c.get("metrics", {}).get("cost_estimate", 0) or 0.0 for c in logger.calls)
        success_count = sum(1 for c in logger.calls if c.get("status") == "success")
        error_count = len(logger.calls) - success_count
        
        lines.append(f"- **Total LLM Calls:** {len(logger.calls)}")
        lines.append(f"- **Success:** {success_count}")
        lines.append(f"- **Errors:** {error_count}")
        lines.append(f"- **Total Tokens:** {total_tokens:,} (in: {total_tokens_input:,}, out: {total_tokens_output:,})")
        lines.append(f"- **Total Duration:** {total_duration/1000:.2f}s ({total_duration:.0f} ms)")
        lines.append(f"- **Total Cost:** ${total_cost:.6f}")
        lines.append("")
    
    if trace_data:
        trace_tokens = trace_data.get("tokens_total", 0)
        trace_cost = trace_data.get("cost_total", 0.0)
        if trace_tokens or trace_cost:
            lines.append("**From Database Trace:**")
            lines.append("")
            if trace_tokens:
                lines.append(f"- **Total Tokens:** {trace_tokens:,}")
            if trace_cost:
                lines.append(f"- **Total Cost:** ${trace_cost:.6f}")
            lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Document generated automatically by the Botique pipeline*")
    lines.append(f"*Trace ID: {trace_id}*")
    
    # Write file with proper error handling
    try:
        doc_path.write_text("\n".join(lines), encoding="utf-8")
        
        # Verify file was created and has content
        if not doc_path.exists():
            raise FileNotFoundError(f"Documentation file was not created at {doc_path}")
        
        file_size = doc_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"Documentation file was created but is empty at {doc_path}")
        
        print(f"\n   ✓ Workflow documentation saved: {doc_path}")
        print(f"   ✓ File size: {file_size:,} bytes")
        
        return doc_path
        
    except Exception as file_error:
        # Log detailed error information
        import traceback
        error_traceback = traceback.format_exc()
        error_message = (
            f"Failed to write workflow documentation file:\n"
            f"  Path: {doc_path}\n"
            f"  Error: {str(file_error)}\n"
            f"  Type: {type(file_error).__name__}\n"
            f"  Traceback:\n{error_traceback}"
        )
        print(f"\n   ❌ ERROR: {error_message}")
        
        # Try to write error to a log file
        try:
            error_log_path = article_output_dir / "workflow_documentation_error.log"
            error_log_path.write_text(error_message, encoding="utf-8")
            print(f"   📝 Error details written to: {error_log_path}")
        except Exception:
            pass
        
        # Re-raise with full context
        raise RuntimeError(error_message) from file_error


def print_brief_details(brief: CoherenceBrief, phase: str = "") -> None:
    """
    Imprime detalhes completos do Coherence Brief de forma organizada.
    
    Args:
        brief: CoherenceBrief a ser exibido
        phase: Nome da fase atual (opcional)
    """
    phase_label = f" [{phase}]" if phase else ""
    print(f"\n{'─' * 70}")
    print(f"📋 COHERENCE BRIEF{phase_label}: {brief.post_id}")
    print(f"{'─' * 70}")
    
    # Metadata
    print(f"\n📌 METADATA:")
    print(f"   • Post ID: {brief.post_id}")
    print(f"   • Idea ID: {brief.idea_id}")
    print(f"   • Platform: {brief.platform}")
    print(f"   • Format: {brief.format}")
    
    # Voice
    print(f"\n🎤 VOICE:")
    print(f"   • Tone: {brief.tone}")
    print(f"   • Personality: {', '.join(brief.personality_traits[:3])}")
    print(f"   • Vocabulary: {brief.vocabulary_level}")
    print(f"   • Formality: {brief.formality}")
    
    # Visual
    print(f"\n🎨 VISUAL:")
    print(f"   • Palette: {brief.palette_id} ({brief.palette.get('theme', 'N/A')})")
    print(f"   • Primary: {brief.palette.get('primary', 'N/A')}")
    print(f"   • Accent: {brief.palette.get('accent', 'N/A')}")
    print(f"   • Typography: {brief.typography.get('heading_font', 'N/A')} / {brief.typography.get('body_font', 'N/A')}")
    print(f"   • Canvas: {brief.canvas.get('width', 'N/A')}x{brief.canvas.get('height', 'N/A')} ({brief.canvas.get('aspect_ratio', 'N/A')})")
    print(f"   • Style: {brief.visual_style}")
    print(f"   • Mood: {brief.visual_mood}")
    
    # Emotions
    print(f"\n💭 EMOTIONS:")
    print(f"   • Primary: {brief.primary_emotion}")
    print(f"   • Secondary: {', '.join(brief.secondary_emotions[:3])}")
    print(f"   • Avoid: {', '.join(brief.avoid_emotions[:3]) if brief.avoid_emotions else 'None'}")
    
    # Content
    print(f"\n📝 CONTENT:")
    print(f"   • Main Message: {brief.main_message[:80]}..." if len(brief.main_message) > 80 else f"   • Main Message: {brief.main_message}")
    print(f"   • Value Prop: {brief.value_proposition[:80]}..." if len(brief.value_proposition) > 80 else f"   • Value Prop: {brief.value_proposition}")
    print(f"   • Keywords: {', '.join(brief.keywords_to_emphasize[:5])}")
    print(f"   • Angle: {brief.angle[:80]}..." if len(brief.angle) > 80 else f"   • Angle: {brief.angle}")
    print(f"   • Hook: {brief.hook[:80]}..." if len(brief.hook) > 80 else f"   • Hook: {brief.hook}")
    
    # Audience
    print(f"\n👥 AUDIENCE:")
    print(f"   • Persona: {brief.persona}")
    print(f"   • Pain Points: {', '.join(brief.pain_points[:3])}")
    print(f"   • Desires: {', '.join(brief.desires[:3])}")
    
    # Structure
    print(f"\n📐 STRUCTURE:")
    print(f"   • Objective: {brief.objective}")
    print(f"   • Arc: {brief.narrative_arc}")
    print(f"   • Estimated Slides: {brief.estimated_slides}")
    
    # Brand
    if brief.brand_values:
        print(f"\n🏢 BRAND:")
        print(f"   • Values: {', '.join(brief.brand_values)}")
        print(f"   • Handle: {brief.brand_assets.get('handle', 'N/A')}")
    
    # Evolution (se houver)
    if brief.narrative_structure:
        print(f"\n🔄 EVOLUTION:")
        print(f"   • Narrative Pacing: {brief.narrative_pacing or 'N/A'}")
        print(f"   • Transition Style: {brief.transition_style or 'N/A'}")
        if brief.arc_refined:
            print(f"   • Arc Refined: {brief.arc_refined[:80]}..." if len(brief.arc_refined) > 80 else f"   • Arc Refined: {brief.arc_refined}")
        if brief.narrative_structure:
            slides_count = len(brief.narrative_structure.get('slides', []))
            print(f"   • Slides Defined: {slides_count}")
            slides = brief.narrative_structure.get("slides", [])
            if slides:
                print(f"\n📋 TEMPLATES:")
                for slide in slides:
                    slide_num = slide.get("slide_number", "?")
                    template_id = slide.get("template_id", "N/A")
                    template_type = slide.get("template_type", "N/A")
                    confidence = slide.get("template_confidence", 0.0)
                    print(f"   • Slide {slide_num}: {template_id} ({template_type}, confidence={confidence:.2f})")
        if brief.copy_guidelines:
            print(f"   • Copy Guidelines: ✓")
        if brief.cta_guidelines:
            print(f"   • CTA Guidelines: ✓")
    
    print(f"{'─' * 70}\n")


def print_llm_metrics(logger: LLMLogger, phase: str = "", context: str = "") -> None:
    """
    Imprime métricas do LLM para chamadas recentes.
    
    Args:
        logger: LLMLogger com as chamadas
        phase: Nome da fase (opcional)
        context: Contexto adicional (opcional)
    """
    if not logger.calls:
        return
    
    # Filtrar chamadas recentes (últimas 5 ou todas se menos de 5)
    recent_calls = logger.calls[-5:] if len(logger.calls) > 5 else logger.calls
    
    phase_label = f" [{phase}]" if phase else ""
    context_label = f" - {context}" if context else ""
    
    print(f"\n{'─' * 70}")
    print(f"📊 LLM METRICS{phase_label}{context_label}")
    print(f"{'─' * 70}")
    
    total_tokens_input = 0
    total_tokens_output = 0
    total_tokens = 0
    total_duration = 0
    total_cost = 0.0
    success_count = 0
    error_count = 0
    
    for call in recent_calls:
        metrics = call.get("metrics", {})
        tokens_input = metrics.get("tokens_input") or 0
        tokens_output = metrics.get("tokens_output") or 0
        tokens_total = metrics.get("tokens_total") or 0
        duration = metrics.get("duration_ms") or 0
        cost = metrics.get("cost_estimate") or 0.0
        
        total_tokens_input += tokens_input
        total_tokens_output += tokens_output
        total_tokens += tokens_total
        total_duration += duration
        total_cost += cost
        
        if call.get("status") == "success":
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n📈 RECENT CALLS ({len(recent_calls)}):")
    for idx, call in enumerate(recent_calls, 1):
        metrics = call.get("metrics", {})
        status_icon = "✓" if call.get("status") == "success" else "✗"
        phase_info = call.get("phase", "unknown")
        function_info = call.get("function", "unknown")
        
        print(f"   {idx}. {status_icon} {phase_info}/{function_info}")
        if metrics.get("tokens_total"):
            print(f"      Tokens: {metrics.get('tokens_total'):,} "
                  f"(in: {metrics.get('tokens_input', 0):,}, "
                  f"out: {metrics.get('tokens_output', 0):,})")
        if metrics.get("duration_ms"):
            print(f"      Duration: {metrics.get('duration_ms'):.0f} ms")
        if metrics.get("cost_estimate"):
            print(f"      Cost: ${metrics.get('cost_estimate'):.6f}")
        if call.get("error"):
            print(f"      Error: {call.get('error')[:60]}...")
    
    print(f"\n📊 TOTALS (Recent {len(recent_calls)} calls):")
    if total_tokens > 0:
        print(f"   • Total Tokens: {total_tokens:,} (in: {total_tokens_input:,}, out: {total_tokens_output:,})")
    if total_duration > 0:
        print(f"   • Total Duration: {total_duration:.0f} ms ({total_duration/1000:.2f}s)")
    if total_cost > 0:
        print(f"   • Total Cost: ${total_cost:.6f}")
    print(f"   • Success: {success_count}, Errors: {error_count}")
    
    print(f"{'─' * 70}\n")


def print_llm_summary(logger: LLMLogger) -> None:
    """
    Imprime resumo consolidado de todas as chamadas LLM.
    
    Args:
        logger: LLMLogger com todas as chamadas
    """
    if not logger.calls:
        print("\n⚠️  No LLM calls logged")
        return
    
    print(f"\n{'═' * 70}")
    print(f"📊 LLM SUMMARY - ALL CALLS")
    print(f"{'═' * 70}")
    
    total_calls = len(logger.calls)
    total_tokens_input = 0
    total_tokens_output = 0
    total_tokens = 0
    total_duration = 0
    total_cost = 0.0
    success_count = 0
    error_count = 0
    
    # Agrupar por fase
    calls_by_phase = {}
    for call in logger.calls:
        phase = call.get("phase", "unknown")
        if phase not in calls_by_phase:
            calls_by_phase[phase] = []
        calls_by_phase[phase].append(call)
    
    for call in logger.calls:
        metrics = call.get("metrics", {})
        total_tokens_input += metrics.get("tokens_input") or 0
        total_tokens_output += metrics.get("tokens_output") or 0
        total_tokens += metrics.get("tokens_total") or 0
        total_duration += metrics.get("duration_ms") or 0
        total_cost += metrics.get("cost_estimate") or 0.0
        
        if call.get("status") == "success":
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   • Total Calls: {total_calls}")
    if total_calls > 0:
        print(f"   • Success: {success_count} ({success_count/total_calls*100:.1f}%)")
        if error_count > 0:
            print(f"   • Errors: {error_count} ({error_count/total_calls*100:.1f}%)")
    
    if total_tokens > 0:
        print(f"\n💬 TOKENS:")
        print(f"   • Total: {total_tokens:,}")
        if total_tokens > 0:
            print(f"   • Input: {total_tokens_input:,} ({total_tokens_input/total_tokens*100:.1f}%)")
            print(f"   • Output: {total_tokens_output:,} ({total_tokens_output/total_tokens*100:.1f}%)")
        if total_calls > 0:
            print(f"   • Avg per call: {total_tokens/total_calls:,.0f}")
    
    if total_duration > 0:
        print(f"\n⏱️  DURATION:")
        print(f"   • Total: {total_duration/1000:.2f}s ({total_duration:.0f} ms)")
        if total_calls > 0:
            print(f"   • Avg per call: {total_duration/total_calls:.0f} ms")
    
    if total_cost > 0:
        print(f"\n💰 COST:")
        print(f"   • Total: ${total_cost:.6f}")
        if total_calls > 0:
            print(f"   • Avg per call: ${total_cost/total_calls:.6f}")
    
    if calls_by_phase:
        print(f"\n📂 BY PHASE:")
        for phase, phase_calls in sorted(calls_by_phase.items()):
            phase_tokens = sum(c.get("metrics", {}).get("tokens_total", 0) or 0 for c in phase_calls)
            phase_cost = sum(c.get("metrics", {}).get("cost_estimate", 0) or 0.0 for c in phase_calls)
            phase_duration = sum(c.get("metrics", {}).get("duration_ms", 0) or 0 for c in phase_calls)
            
            print(f"   • {phase}: {len(phase_calls)} calls, "
                  f"{phase_tokens:,} tokens, "
                  f"${phase_cost:.6f}, "
                  f"{phase_duration/1000:.2f}s")
    
    print(f"{'═' * 70}\n")


def test_validation_from_db(trace_id: str) -> int:
    """
    Test validation fix by loading events from database and replaying validation.
    
    Args:
        trace_id: Trace ID to load from database
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 70)
    print("TESTING VALIDATION FIX FROM DATABASE")
    print("=" * 70)
    
    # Load trace from database
    print(f"\n1. Loading trace {trace_id[:8]}...")
    db_path = get_db_path()
    trace_data = get_trace_with_events(trace_id, db_path)
    
    if not trace_data:
        print(f"❌ ERROR: Trace not found in database")
        return 1
    
    events = trace_data.get("events", [])
    print(f"   ✓ Found {len(events)} events")
    
    # Find copywriter LLM events with output
    copywriter_events = [
        e for e in events 
        if e.get("type") == "llm" 
        and "copywriter" in e.get("name", "").lower()
        and e.get("output_json")
    ]
    
    print(f"   ✓ Found {len(copywriter_events)} copywriter LLM events with output")
    
    if not copywriter_events:
        print("   ⚠️  No copywriter events with output found")
        return 1
    
    # Get metadata to find article and post info
    metadata = trace_data.get("metadata", {})
    article_slug = metadata.get("article_slug", "why-tradicional-learning-fails")
    
    # Load article
    article_path = Path(os.getenv("ARTICLE_PATH", f"articles/{article_slug}.md"))
    if not article_path.exists():
        print(f"   ⚠️  Article not found: {article_path}, skipping article text")
        article_text = ""
    else:
        article_text = article_path.read_text(encoding="utf-8")
        print(f"   ✓ Article loaded: {len(article_text)} characters")
    
    # Initialize logger and copywriter (for validation only)
    logger = LLMLogger(use_sql=False)
    llm_client = HttpLLMClient(
        api_key="dummy",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        logger=logger,
    )
    copywriter = Copywriter(llm_client=llm_client, logger=logger)
    
    # Try to load briefs and narrative structures
    article_output_dir = OUTPUT_DIR / article_slug
    post_dirs = [d for d in article_output_dir.iterdir() if d.is_dir() and d.name.startswith("post_")]
    
    if not post_dirs:
        print(f"   ⚠️  No post directories found in {article_output_dir}")
        print(f"   Testing validation with minimal context...")
        
        # Test with minimal context
        success_count = 0
        error_count = 0
        
        for event in copywriter_events:
            output_json = event.get("output_json", {})
            if not output_json:
                continue
            
            # Create minimal slide_info and brief for validation
            slide_number = output_json.get("slide_number", 1)
            slide_info = {
                "slide_number": slide_number,
                "module_type": "unknown",
                "content_slots": {},
            }
            
            # Create minimal brief
            brief_dict = {
                "post_id": f"post_{article_slug}_001",
                "platform": "linkedin",
                "format": "carousel",
                "tone": "professional",
                "canvas": {"width": 1080, "height": 1350, "aspect_ratio": "4:5"},
            }
            brief = CoherenceBrief.from_dict(brief_dict)
            
            try:
                result = copywriter._validate_response(
                    raw_response=json.dumps(output_json),
                    slide_info=slide_info,
                    brief=brief,
                )
                success_count += 1
                print(f"   ✓ Event {event.get('name', 'unknown')}: Validation passed")
            except ValueError as e:
                error_count += 1
                error_msg = str(e)
                print(f"   ❌ Event {event.get('name', 'unknown')}: {error_msg[:80]}...")
        
        print(f"\n   Results: {success_count} passed, {error_count} failed")
        return 0 if error_count == 0 else 1
    
    # Test with full context from files
    print(f"\n2. Testing validation with full context from {len(post_dirs)} post(s)...")
    
    success_count = 0
    error_count = 0
    
    for post_dir in post_dirs:
        brief_path = post_dir / "coherence_brief.json"
        narrative_path = post_dir / "narrative_structure.json"
        
        if not brief_path.exists() or not narrative_path.exists():
            continue
        
        brief_dict = json.loads(brief_path.read_text(encoding="utf-8"))
        brief = CoherenceBrief.from_dict(brief_dict)
        
        narrative_data = json.loads(narrative_path.read_text(encoding="utf-8"))
        slides = narrative_data.get("slides", [])
        
        # Match events to slides by slide_number
        for slide_info in slides:
            slide_number = slide_info.get("slide_number")
            
            # Find matching event
            matching_event = None
            for event in copywriter_events:
                event_output = event.get("output_json", {})
                if event_output.get("slide_number") == slide_number:
                    matching_event = event
                    break
            
            if not matching_event:
                continue
            
            output_json = matching_event.get("output_json", {})
            
            try:
                result = copywriter._validate_response(
                    raw_response=json.dumps(output_json),
                    slide_info=slide_info,
                    brief=brief,
                )
                success_count += 1
                print(f"   ✓ {brief.post_id} slide {slide_number}: Validation passed")
            except ValueError as e:
                error_count += 1
                error_msg = str(e)
                print(f"   ❌ {brief.post_id} slide {slide_number}: {error_msg[:80]}...")
    
    print(f"\n   Results: {success_count} passed, {error_count} failed")
    
    if error_count == 0:
        print("\n" + "=" * 70)
        print("✅ VALIDATION TEST PASSED!")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"⚠️  VALIDATION TEST COMPLETED WITH {error_count} ERROR(S)")
        print("=" * 70)
        return 1


def main() -> int:
    # Check if we should test from database instead
    test_trace_id = os.getenv("TEST_TRACE_ID")
    if test_trace_id:
        return test_validation_from_db(test_trace_id)
    
    print("=" * 70)
    print("FULL PIPELINE TEST - IDEATION -> NARRATIVE -> COPYWRITING")
    print("=" * 70)

    # Load environment variables
    load_dotenv()
    
    # Initialize execution metrics tracking
    pipeline_start_time = time.time()
    execution_metrics = {
        "pipeline_start_time": pipeline_start_time,
        "pipeline_end_time": None,
        "phase_timings": {},
        "errors": [],
        "warnings": [],
        "items_processed": {
            "ideas": {"count": 0},
            "posts": {"count": 0},
            "slides": {"count": 0},
        },
    }

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
        execution_metrics["errors"].append({
            "phase": "Initialization",
            "type": "FileNotFoundError",
            "message": f"Article file not found: {article_path}",
            "timestamp": time.time(),
        })
        return 1

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
    
    phase1_start_time = time.time()
    execution_metrics["phase_timings"]["Phase 1: Ideation"] = {
        "start_time": phase1_start_time,
        "end_time": None,
        "duration": 0,
        "status": "in_progress",
    }

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
        import traceback
        error_traceback = traceback.format_exc()
        print(f"   ⚠️  WARNING: Error generating ideas: {error_msg}")
        print(f"   ℹ️  Cannot continue without ideas. Exiting.")
        
        execution_metrics["errors"].append({
            "phase": "Phase 1: Ideation",
            "type": type(exc).__name__,
            "message": error_msg,
            "traceback": error_traceback,
            "timestamp": time.time(),
        })
        
        phase1_end_time = time.time()
        execution_metrics["phase_timings"]["Phase 1: Ideation"].update({
            "end_time": phase1_end_time,
            "duration": phase1_end_time - phase1_start_time,
            "status": "failed",
        })
        
        return 1

    article_summary = ideas_payload.get("article_summary", {})
    all_ideas = ideas_payload.get("ideas", [])
    
    # Update phase 1 metrics
    phase1_end_time = time.time()
    execution_metrics["phase_timings"]["Phase 1: Ideation"].update({
        "end_time": phase1_end_time,
        "duration": phase1_end_time - phase1_start_time,
        "status": "completed",
        "details": f"Generated {len(all_ideas)} ideas",
    })
    execution_metrics["items_processed"]["ideas"]["count"] = len(all_ideas)

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
    
    phase2_start_time = time.time()
    execution_metrics["phase_timings"]["Phase 2: Coherence Briefs"] = {
        "start_time": phase2_start_time,
        "end_time": None,
        "duration": 0,
        "status": "in_progress",
    }

    print("\n7. Building coherence briefs from ideas...")
    briefs = []
    phase2_errors = []

    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        post_id = f"post_{article_slug}_{idx:03d}"

        print(f"\n   [{idx}/{len(selected_ideas)}] Building brief for {idea_id}...")

        try:
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=article_summary,
                post_id=post_id,
            )

            CoherenceBriefBuilder.validate_brief(brief)
            briefs.append(brief)
            
            # Print detailed brief information
            print_brief_details(brief, phase="Phase 2 - Initial")
            
            # Print LLM metrics after ideation
            print_llm_metrics(logger, phase="Phase 1", context=f"idea_{idx}")

        except Exception as exc:
            error_msg = str(exc)
            import traceback
            error_traceback = traceback.format_exc()
            print(f"   ⚠️  WARNING: Error building brief for {idea_id}: {error_msg}")
            print(f"   ℹ️  Skipping this idea and continuing...")
            
            phase2_errors.append({
                "phase": "Phase 2: Coherence Briefs",
                "type": type(exc).__name__,
                "message": f"Error building brief for {idea_id}: {error_msg}",
                "traceback": error_traceback,
                "timestamp": time.time(),
                "idea_id": idea_id,
            })
            execution_metrics["warnings"].append({
                "phase": "Phase 2: Coherence Briefs",
                "message": f"Brief for {idea_id} failed, skipped",
                "timestamp": time.time(),
            })
            # Continue to next idea instead of returning 1

    phase2_end_time = time.time()
    execution_metrics["phase_timings"]["Phase 2: Coherence Briefs"].update({
        "end_time": phase2_end_time,
        "duration": phase2_end_time - phase2_start_time,
        "status": "completed" if briefs else "failed",
        "details": f"Built {len(briefs)} brief(s), {len(phase2_errors)} failed",
    })
    execution_metrics["errors"].extend(phase2_errors)
    
    if not briefs:
        print(f"   ❌ ERROR: No coherence briefs were built successfully. Cannot continue.")
        execution_metrics["errors"].append({
            "phase": "Phase 2: Coherence Briefs",
            "type": "ValidationError",
            "message": "No coherence briefs were built successfully",
            "timestamp": time.time(),
        })
        return 1
    
    print(f"   ✓ {len(briefs)} coherence brief(s) built successfully")

    # =====================================================================
    # PHASE 3: NARRATIVE ARCHITECT
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 3: NARRATIVE ARCHITECT")
    print("=" * 70)
    
    phase3_start_time = time.time()
    execution_metrics["phase_timings"]["Phase 3: Narrative Architect"] = {
        "start_time": phase3_start_time,
        "end_time": None,
        "duration": 0,
        "status": "in_progress",
    }

    # Verify narrative_architect prompt
    print("\n8. Verifying narrative_architect prompt...")
    narrative_prompt_key = "narrative_architect"
    narrative_prompt_data = get_latest_prompt(narrative_prompt_key)
    if not narrative_prompt_data:
        print(f"   ❌ ERROR: Prompt '{narrative_prompt_key}' not found in database!")
        return 1

    print(f"   ✓ Prompt found: {narrative_prompt_key} (version {narrative_prompt_data.get('version', 'N/A')})")

    # Verify Template System
    print("\n8a. Verifying Template System...")
    from src.templates.library import TemplateLibrary
    from src.templates.selector import TemplateSelector
    
    try:
        # Test Template Library
        template_library = TemplateLibrary()
        total_templates = len(template_library.templates)
        print(f"   ✓ Template Library loaded: {total_templates} templates available")
        
        # Show template breakdown by type
        template_types = {}
        for template in template_library.templates.values():
            template_type = template.module_type
            template_types[template_type] = template_types.get(template_type, 0) + 1
        
        print(f"   📋 Template breakdown by type:")
        for template_type, count in sorted(template_types.items()):
            print(f"      • {template_type}: {count} templates")
        
        # Test Template Selector
        print(f"\n   🔍 Initializing Template Selector...")
        template_selector = TemplateSelector()
        
        # Check if embeddings are available
        try:
            from sentence_transformers import SentenceTransformer
            embeddings_available = True
            print(f"   ✓ Embeddings available: {template_selector.model_name}")
            if template_selector.model:
                print(f"   ✓ Embeddings model loaded successfully")
                print(f"   ✓ Template embeddings pre-computed: {len(template_selector.template_embeddings_cache)} templates")
            else:
                print(f"   ⚠️  Embeddings model not loaded (using fallback method)")
                embeddings_available = False
        except ImportError:
            embeddings_available = False
            print(f"   ⚠️  sentence-transformers not installed (using fallback method)")
            print(f"   💡 For better template selection, install: pip install sentence-transformers")
        
        # Test template selection with a simple example
        print(f"\n   🧪 Testing template selection...")
        try:
            test_template_id, test_justification, test_confidence = template_selector.select_template(
                template_type="hook",
                value_subtype=None,
                purpose="Grab attention with a provocative question",
                copy_direction="Create curiosity about a common problem professionals face",
                key_elements=["certificates", "skills"],
                persona="Professional developers",
                tone="professional",
                platform="linkedin",
            )
            print(f"   ✓ Template selection working: {test_template_id} (confidence: {test_confidence:.2f})")
            print(f"      Justification: {test_justification[:100]}..." if len(test_justification) > 100 else f"      Justification: {test_justification}")
        except Exception as test_error:
            print(f"   ⚠️  Template selection test failed: {test_error}")
            print(f"   💡 Template selection may not work correctly")
        
    except Exception as template_error:
        print(f"   ❌ ERROR: Template system verification failed: {template_error}")
        print(f"   💡 This may cause issues in template selection")
        import traceback
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            traceback.print_exc()

    # Create Narrative Architect
    print("\n9. Creating Narrative Architect...")
    architect = NarrativeArchitect(llm_client=llm_client, logger=logger)
    print("   ✓ Narrative Architect created")

    print("\n10. Generating narrative structures...")
    narrative_results = []
    phase3_errors = []
    phase3_warnings = []

    for idx, brief in enumerate(briefs, 1):
        print(f"\n   [{idx}/{len(briefs)}] Generating narrative for {brief.post_id}...")

        try:
            logger.set_context(post_id=brief.post_id)

            # Capture warnings and display them as informational messages
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                narrative_payload = architect.generate_structure(
                    brief=brief,
                    context=brief.post_id,
                )
                
                # Display any warnings as informational messages
                for warning in w:
                    warning_msg = str(warning.message)
                    print(f"   ⚠️  WARNING: {warning_msg}")
                    if hasattr(warning, 'filename') and hasattr(warning, 'lineno'):
                        print(f"      (from {warning.filename}:{warning.lineno})")
                    
                    phase3_warnings.append({
                        "phase": "Phase 3: Narrative Architect",
                        "message": f"{brief.post_id}: {warning_msg}",
                        "timestamp": time.time(),
                    })

            narrative_results.append({
                "brief": brief,
                "narrative_payload": narrative_payload,
            })

            # Print updated brief with narrative evolution
            print_brief_details(brief, phase="Phase 3 - After Narrative")
            
            # Print narrative structure summary
            slides = narrative_payload.get("slides", [])
            # Support both "pacing" (normalized) and "narrative_pacing" (raw response)
            pacing = narrative_payload.get("narrative_pacing") or narrative_payload.get("pacing", "N/A")
            transition = narrative_payload.get("transition_style", "N/A")
            print(f"\n   📖 NARRATIVE STRUCTURE:")
            print(f"      • Slides: {len(slides)}")
            print(f"      • Pacing: {pacing}")
            print(f"      • Transition Style: {transition}")
            if narrative_payload.get("arc_refined"):
                arc = narrative_payload.get("arc_refined", "")
                print(f"      • Arc Refined: {arc[:100]}..." if len(arc) > 100 else f"      • Arc Refined: {arc}")
            print(f"\n   🎯 TEMPLATE SELECTION RESULTS:")
            templates_by_type = {}
            template_selection_stats = {
                "total_slides": len(slides),
                "templates_selected": 0,
                "templates_missing": 0,
                "avg_confidence": 0.0,
                "method": "unknown",
            }
            
            confidences = []
            for slide in slides:
                slide_num = slide.get("slide_number")
                template_type = slide.get("template_type", "unknown")
                value_subtype = slide.get("value_subtype")
                template_id = slide.get("template_id")
                template_confidence = slide.get("template_confidence", 0.0)
                template_justification = slide.get("template_justification", "")
                
                if template_type not in templates_by_type:
                    templates_by_type[template_type] = []
                
                if template_id:
                    template_selection_stats["templates_selected"] += 1
                    confidences.append(template_confidence)
                    templates_by_type[template_type].append({
                        "slide_num": slide_num,
                        "template_id": template_id,
                        "confidence": template_confidence,
                        "value_subtype": value_subtype,
                    })
                    template_type_display = f"{template_type}/{value_subtype}" if value_subtype else template_type
                    print(f"      ✓ Slide {slide_num} ({template_type_display}): {template_id} (confidence: {template_confidence:.2f})")
                    if template_justification:
                        justification_preview = template_justification[:150] + "..." if len(template_justification) > 150 else template_justification
                        print(f"        └─ {justification_preview}")
                else:
                    template_selection_stats["templates_missing"] += 1
                    template_type_display = f"{template_type}/{value_subtype}" if value_subtype else template_type
                    print(f"      ✗ Slide {slide_num} ({template_type_display}): (no template selected)")
            
            # Calculate average confidence
            if confidences:
                template_selection_stats["avg_confidence"] = sum(confidences) / len(confidences)
            
            # Show summary
            print(f"\n   📊 Template Selection Summary:")
            print(f"      • Total slides: {template_selection_stats['total_slides']}")
            print(f"      • Templates selected: {template_selection_stats['templates_selected']}")
            if template_selection_stats["templates_missing"] > 0:
                print(f"      • Templates missing: {template_selection_stats['templates_missing']} ⚠️")
            if template_selection_stats["avg_confidence"] > 0:
                print(f"      • Average confidence: {template_selection_stats['avg_confidence']:.2f}")
            
            # Store stats for later use
            narrative_payload["_template_selection_stats"] = template_selection_stats
            
            # Print LLM metrics for this narrative generation
            print_llm_metrics(logger, phase="Phase 3", context=brief.post_id)

            # Save updated brief (with narrative evolution)
            post_dir = article_output_dir / brief.post_id
            post_dir.mkdir(parents=True, exist_ok=True)
            brief_path = post_dir / "coherence_brief.json"
            brief_path.write_text(
                json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            
            # Save narrative structure
            narrative_path = post_dir / "narrative_structure.json"
            narrative_path.write_text(
                json.dumps(narrative_payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"      ✓ Saved: {narrative_path}")

        except Exception as exc:
            error_msg = str(exc)
            error_type = type(exc).__name__
            import traceback
            error_traceback = traceback.format_exc()
            print(f"   ❌ ERROR: {error_type}: {error_msg}")
            
            phase3_errors.append({
                "phase": "Phase 3: Narrative Architect",
                "type": error_type,
                "message": f"{brief.post_id}: {error_msg}",
                "traceback": error_traceback,
                "timestamp": time.time(),
                "post_id": brief.post_id,
            })
            
            # Try to get more context about the error
            if isinstance(exc, ValueError):
                # For validation errors, try to show what was expected vs received
                if "Missing required keys" in error_msg or "Invalid item" in error_msg:
                    print(f"   📋 This appears to be a validation error.")
                    print(f"   💡 The LLM response may not match the expected structure.")
                    print(f"   🔍 Check the debug output directory for raw response files.")
                    
                    # Try to load and show raw response if available
                    debug_dir = article_output_dir / brief.post_id / "debug"
                    if debug_dir.exists():
                        raw_response_files = list(debug_dir.glob("raw_response_*.txt"))
                        if raw_response_files:
                            latest_response = max(raw_response_files, key=lambda p: p.stat().st_mtime)
                            print(f"   📄 Latest raw response: {latest_response}")
                            try:
                                response_content = latest_response.read_text(encoding="utf-8")[:1000]
                                print(f"   📝 Response preview (first 1000 chars):")
                                print(f"   {response_content}")
                            except Exception:
                                pass
            
            # Print traceback for debugging if needed
            if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
                print(f"   🔍 Full traceback:")
                traceback.print_exc()
            
            print(f"   ℹ️  Continuing with next brief...")
            # Continue instead of returning 1
    
    phase3_end_time = time.time()
    execution_metrics["phase_timings"]["Phase 3: Narrative Architect"].update({
        "end_time": phase3_end_time,
        "duration": phase3_end_time - phase3_start_time,
        "status": "completed" if narrative_results else "failed",
        "details": f"Generated {len(narrative_results)} narrative structure(s), {len(phase3_errors)} errors, {len(phase3_warnings)} warnings",
    })
    execution_metrics["errors"].extend(phase3_errors)
    execution_metrics["warnings"].extend(phase3_warnings)

    print(f"\n   ✓ {len(narrative_results)} narrative structure(s) generated successfully")

    # =====================================================================
    # PHASE 4: COPYWRITER
    # =====================================================================
    print("\n" + "=" * 70)
    print("PHASE 4: COPYWRITER")
    print("=" * 70)
    
    phase4_start_time = time.time()
    execution_metrics["phase_timings"]["Phase 4: Copywriting"] = {
        "start_time": phase4_start_time,
        "end_time": None,
        "duration": 0,
        "status": "in_progress",
    }

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
    phase4_errors = []
    phase4_warnings = []

    for result_idx, result in enumerate(narrative_results, 1):
        brief = result["brief"]
        narrative_payload = result["narrative_payload"]
        slides = narrative_payload.get("slides", [])

        print(f"\n   Post {result_idx}/{len(narrative_results)}: {brief.post_id} ({len(slides)} slides)")

        post_copy_results = []

        try:
            logger.set_context(post_id=brief.post_id)

            print(f"\n      Generating copy for all {len(slides)} slides...")
            print(f"      📋 Post details: Platform={brief.platform}, Format={brief.format}, Tone={brief.tone}")
            
            # Pre-flight checks
            slides_without_template = []
            for slide_info in slides:
                template_id = slide_info.get("template_id")
                if not template_id:
                    slide_num = slide_info.get("slide_number", "?")
                    slides_without_template.append(slide_num)
                    print(f"      ⚠️  WARNING: Slide {slide_num} missing template_id before copywriting")
            
            if slides_without_template:
                print(f"      ⚠️  Found {len(slides_without_template)} slide(s) without template_id: {slides_without_template}")

            # Capture warnings and display them as informational messages
            print(f"\n      🤖 Calling LLM to generate copy for {len(slides)} slides...")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                # Generate copy for all slides in one LLM call
                post_copy_result = copywriter.generate_post_copy(
                    brief=brief,
                    slides_info=slides,
                    article_text=article_text,
                    context=f"{brief.post_id}_post_copy",
                )
                
                # Display any warnings as informational messages
                for warning in w:
                    warning_msg = str(warning.message)
                    print(f"      ⚠️  WARNING: {warning_msg}")
                    phase4_warnings.append({
                        "phase": "Phase 4: Copywriting",
                        "message": f"{brief.post_id}: {warning_msg}",
                        "timestamp": time.time(),
                    })

            # Extract slides from response
            slides_copy = post_copy_result.get("slides", [])
            print(f"      ✅ LLM response received: {len(slides_copy)} slide(s) returned")
            
            if len(slides_copy) != len(slides):
                print(f"      ⚠️  WARNING: Expected {len(slides)} slides, got {len(slides_copy)}")
                print(f"         This may indicate a mismatch in the response structure.")
            
            # Match slides copy with slides info by slide_number
            # Normalize slide_numbers to int for consistent matching
            def normalize_slide_number(num):
                """Normalize slide_number to int for consistent dict lookups."""
                if num is None:
                    return None
                try:
                    return int(num)
                except (ValueError, TypeError):
                    return num
            
            # Build dictionary with normalized keys (store with both int and original value as keys for compatibility)
            print(f"\n      🔍 Matching {len(slides_copy)} copy response(s) with {len(slides)} narrative slide(s)...")
            slides_copy_dict = {}
            for s in slides_copy:
                slide_num = s.get("slide_number")
                if slide_num is not None:
                    normalized = normalize_slide_number(slide_num)
                    # Store with normalized (int) key as primary
                    slides_copy_dict[normalized] = s
                    # Also store with original value if different (for backwards compatibility)
                    if normalized != slide_num:
                        slides_copy_dict[slide_num] = s
            
            copy_slide_numbers = sorted([normalize_slide_number(s.get("slide_number")) for s in slides_copy if s.get("slide_number") is not None])
            narrative_slide_numbers = sorted([normalize_slide_number(s.get("slide_number", idx)) for idx, s in enumerate(slides, 1)])
            print(f"         Copy response slide_numbers: {copy_slide_numbers}")
            print(f"         Narrative slide_numbers: {narrative_slide_numbers}")
            
            matched_count = 0
            unmatched_count = 0
            
            for slide_idx, slide_info in enumerate(slides, 1):
                slide_number_raw = slide_info.get("slide_number", slide_idx)
                slide_number = normalize_slide_number(slide_number_raw)
                module_type = slide_info.get("module_type", "unknown")
                template_type = slide_info.get("template_type", "unknown")
                
                print(f"\n      📝 Processing Slide {slide_number} ({template_type})...")
                
                # Try multiple lookup strategies
                slide_content = slides_copy_dict.get(slide_number)
                lookup_strategy = "normalized"
                if not slide_content and slide_number != slide_number_raw:
                    # Try with original value if different
                    slide_content = slides_copy_dict.get(slide_number_raw)
                    lookup_strategy = "original"
                
                if not slide_content:
                    unmatched_count += 1
                    # Detailed logging for debugging
                    available_numbers = sorted(set(
                        normalize_slide_number(s.get("slide_number")) 
                        for s in slides_copy 
                        if s.get("slide_number") is not None
                    ))
                    narrative_numbers = sorted(set(
                        normalize_slide_number(s.get("slide_number", idx))
                        for idx, s in enumerate(slides, 1)
                    ))
                    print(f"         ❌ No copy found for slide {slide_number} (raw: {slide_number_raw}, type: {type(slide_number).__name__})")
                    print(f"            Available copy slide_numbers: {available_numbers}")
                    print(f"            Expected narrative slide_numbers: {narrative_numbers}")
                    print(f"            Slide info: template_type={slide_info.get('template_type')}, purpose={slide_info.get('purpose', 'N/A')[:50]}")
                    phase4_warnings.append({
                        "phase": "Phase 4: Copywriting",
                        "message": f"{brief.post_id}: No copy found for slide {slide_number}. Available: {available_numbers}, Expected: {narrative_numbers}",
                        "timestamp": time.time(),
                    })
                    continue
                
                matched_count += 1
                print(f"         ✅ Copy found (lookup: {lookup_strategy})")
                
                # Extract quick summary of copy content
                title_obj = slide_content.get("title")
                subtitle_obj = slide_content.get("subtitle")
                body_obj = slide_content.get("body")
                
                title_text = title_obj.get("content", "") if isinstance(title_obj, dict) else (str(title_obj) if title_obj else "")
                subtitle_text = subtitle_obj.get("content", "") if isinstance(subtitle_obj, dict) else (str(subtitle_obj) if subtitle_obj else "")
                body_text = body_obj.get("content", "") if isinstance(body_obj, dict) else (str(body_obj) if body_obj else "")
                
                elements_count = sum(1 for elem in [title_text, subtitle_text, body_text] if elem)
                elements_list = []
                if title_text:
                    elements_list.append("Title")
                if subtitle_text:
                    elements_list.append("Subtitle")
                if body_text:
                    elements_list.append("Body")
                elements_str = " + ".join(elements_list) if elements_list else "None"
                print(f"         📄 Copy elements: {elements_count} ({elements_str})")
                if title_text:
                    print(f"            Title: {title_text[:60]}{'...' if len(title_text) > 60 else ''}")
                if subtitle_text and not title_text:
                    print(f"            Subtitle: {subtitle_text[:60]}{'...' if len(subtitle_text) > 60 else ''}")
                if body_text and not title_text and not subtitle_text:
                    print(f"            Body: {body_text[:60]}{'...' if len(body_text) > 60 else ''} ({len(body_text)} chars)")
                
                post_copy_results.append({
                    "slide_number": slide_number,
                    "slide_info": slide_info,
                    "slide_content": slide_content,
                })

                # Print detailed slide copy information
                try:
                    print_slide_copy_details(slide_content, slide_info, slide_number)
                except Exception as detail_exc:
                    print(f"         ⚠️  WARNING: Error printing slide details: {detail_exc}")
                    print(f"         ℹ️  Slide copy is valid, continuing with next slide...")
                    import traceback
                    if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
                        print(f"         🔍 Debug traceback:")
                        traceback.print_exc()

                # Save individual slide content
                post_dir = article_output_dir / brief.post_id
                slide_content_path = post_dir / f"slide_{slide_number}_content.json"
                slide_content_path.write_text(
                    json.dumps(slide_content, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"         💾 Saved: {slide_content_path.name}")

            # Summary of matching process
            print(f"\n      📊 Matching Summary:")
            print(f"         ✅ Matched: {matched_count}/{len(slides)} slides")
            if unmatched_count > 0:
                print(f"         ❌ Unmatched: {unmatched_count}/{len(slides)} slides")
            
            # Save complete post copy result
            post_dir = article_output_dir / brief.post_id
            post_copy_path = post_dir / "post_copy.json"
            post_copy_path.write_text(
                json.dumps(post_copy_result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"\n      ✅ Post copy processing complete!")
            print(f"         • Total slides processed: {len(post_copy_results)}")
            print(f"         • Files saved: post_copy.json + {len(post_copy_results)} slide content file(s)")
            print(f"         • Output path: {post_copy_path}")

        except Exception as exc:
            error_msg = str(exc)
            error_type = type(exc).__name__
            import traceback
            error_traceback = traceback.format_exc()
            print(f"      ⚠️  WARNING: {error_msg}")
            print(f"      ℹ️  Skipping this post and continuing...")
            
            phase4_errors.append({
                "phase": "Phase 4: Copywriting",
                "type": error_type,
                "message": f"{brief.post_id}: {error_msg}",
                "traceback": error_traceback,
                "timestamp": time.time(),
                "post_id": brief.post_id,
            })
            # Continue to next post instead of returning 1

        all_copy_results.append({
            "brief": brief,
            "narrative_payload": narrative_payload,
            "slide_contents": post_copy_results,
        })

        # Print post summary with all slides
        print(f"\n{'═' * 70}")
        print(f"📊 POST SUMMARY - {brief.post_id}")
        print(f"{'═' * 70}")
        print(f"\n📌 OVERVIEW:")
        print(f"   • Platform: {brief.platform}")
        print(f"   • Format: {brief.format}")
        print(f"   • Total Slides: {len(post_copy_results)}")
        print(f"   • Main Message: {brief.main_message[:100]}..." if len(brief.main_message) > 100 else f"   • Main Message: {brief.main_message}")
        
        print(f"\n📝 SLIDES BREAKDOWN:")
        for slide_result in post_copy_results:
            slide_num = slide_result["slide_number"]
            slide_info = slide_result["slide_info"]
            slide_content = slide_result["slide_content"]
            module_type = slide_info.get("module_type", "unknown")
            
            # Extract text content summaries
            title_obj = slide_content.get("title")
            title_text = title_obj.get("content", "") if isinstance(title_obj, dict) else ""
            
            subtitle_obj = slide_content.get("subtitle")
            subtitle_text = subtitle_obj.get("content", "") if isinstance(subtitle_obj, dict) else ""
            
            body_obj = slide_content.get("body")
            body_text = body_obj.get("content", "") if isinstance(body_obj, dict) else ""
            
            print(f"\n   Slide {slide_num} ({module_type}):")
            if title_text:
                print(f"     Title: {title_text[:80]}..." if len(title_text) > 80 else f"     Title: {title_text}")
            if subtitle_text:
                print(f"     Subtitle: {subtitle_text[:80]}..." if len(subtitle_text) > 80 else f"     Subtitle: {subtitle_text}")
            if body_text:
                print(f"     Body: {len(body_text)} chars")
            else:
                print(f"     Body: (empty)")
        
        print(f"\n{'═' * 70}\n")

        # Print updated brief with copywriting evolution
        print_brief_details(brief, phase="Phase 4 - After Copywriting")
        
        # Print LLM metrics for this post's copywriting
        print_llm_metrics(logger, phase="Phase 4", context=brief.post_id)

        # Save updated brief (with copywriting evolution)
        post_dir = article_output_dir / brief.post_id
        brief_path = post_dir / "coherence_brief.json"
        brief_path.write_text(
            json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"      ✓ {len(post_copy_results)} slide(s) processed for {brief.post_id}")
    
    phase4_end_time = time.time()
    total_slides = sum(len(r.get("slide_contents", [])) if isinstance(r.get("slide_contents"), list) else 0 for r in all_copy_results)
    execution_metrics["phase_timings"]["Phase 4: Copywriting"].update({
        "end_time": phase4_end_time,
        "duration": phase4_end_time - phase4_start_time,
        "status": "completed" if all_copy_results else "failed",
        "details": f"Generated copy for {total_slides} slide(s) across {len(all_copy_results)} post(s), {len(phase4_errors)} errors, {len(phase4_warnings)} warnings",
    })
    execution_metrics["errors"].extend(phase4_errors)
    execution_metrics["warnings"].extend(phase4_warnings)
    execution_metrics["items_processed"]["posts"]["count"] = len(all_copy_results)
    execution_metrics["items_processed"]["slides"]["count"] = total_slides
    
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

    print(f"\n   Template Selection System:")
    
    # Collect template statistics
    template_confidences = []
    template_ids = set()
    template_selection_stats_all = {
        "total_slides": 0,
        "templates_selected": 0,
        "templates_missing": 0,
        "unique_templates": set(),
    }
    
    for result in narrative_results:
        slides = result["narrative_payload"].get("slides", [])
        template_stats = result["narrative_payload"].get("_template_selection_stats", {})
        
        template_selection_stats_all["total_slides"] += len(slides)
        template_selection_stats_all["templates_selected"] += template_stats.get("templates_selected", 0)
        template_selection_stats_all["templates_missing"] += template_stats.get("templates_missing", 0)
        
        for slide in slides:
            template_id = slide.get("template_id")
            if template_id:
                template_ids.add(template_id)
                template_confidences.append(slide.get("template_confidence", 0.0))
    
    template_selection_stats_all["unique_templates"] = template_ids
    avg_confidence = sum(template_confidences) / len(template_confidences) if template_confidences else 0.0
    
    print(f"     ✓ Total slides: {template_selection_stats_all['total_slides']}")
    print(f"     ✓ Templates selected: {template_selection_stats_all['templates_selected']}")
    if template_selection_stats_all["templates_missing"] > 0:
        success_rate = (template_selection_stats_all["templates_selected"] / template_selection_stats_all["total_slides"] * 100) if template_selection_stats_all["total_slides"] > 0 else 0.0
        print(f"     ⚠️  Templates missing: {template_selection_stats_all['templates_missing']} (success rate: {success_rate:.1f}%)")
    else:
        print(f"     ✓ All slides have templates selected")
    print(f"     ✓ Unique templates used: {len(template_selection_stats_all['unique_templates'])}")
    if avg_confidence > 0:
        print(f"     ✓ Average confidence: {avg_confidence:.2f}")
    if template_ids:
        print(f"     ✓ Template IDs: {', '.join(sorted(list(template_ids))[:10])}{'...' if len(template_ids) > 10 else ''}")

    # Validate coherence brief evolution
    print("\n15. Validating coherence brief evolution...")
    for idx, brief in enumerate(briefs, 1):
        has_narrative = brief.narrative_structure is not None
        has_copy_guidelines = brief.copy_guidelines is not None
        has_cta_guidelines = brief.cta_guidelines is not None
        has_narrative_pacing = brief.narrative_pacing is not None
        has_transition_style = brief.transition_style is not None
        has_arc_refined = brief.arc_refined is not None

        print(f"\n   Brief {idx} ({brief.post_id}):")
        print(f"     📐 Structure:")
        print(f"        - Narrative structure: {'✓' if has_narrative else '✗'}")
        if has_narrative:
            slides_count = len(brief.narrative_structure.get('slides', [])) if brief.narrative_structure else 0
            print(f"        - Slides defined: {slides_count}")
        print(f"        - Narrative pacing: {'✓' if has_narrative_pacing else '✗'} ({brief.narrative_pacing or 'N/A'})")
        print(f"        - Transition style: {'✓' if has_transition_style else '✗'} ({brief.transition_style or 'N/A'})")
        print(f"        - Arc refined: {'✓' if has_arc_refined else '✗'}")
        print(f"     ✍️  Copywriting:")
        print(f"        - Copy guidelines: {'✓' if has_copy_guidelines else '✗'}")
        print(f"        - CTA guidelines: {'✓' if has_cta_guidelines else '✗'}")
        
        # Print final brief details
        print_brief_details(brief, phase="Final")

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

    # Print comprehensive LLM summary
    print("\n17. LLM Usage Summary...")
    print_llm_summary(logger)

    # Verify SQL database
    print("\n18. Verifying SQL database...")
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
            for etype, count in sorted(event_types.items()):
                print(f"     - {etype}: {count}")
            
            # LLM events breakdown
            llm_events = [e for e in events if e.get("type") == "llm"]
            if llm_events:
                print(f"\n   ✓ LLM Events: {len(llm_events)}")
                # Group by phase
                llm_by_phase = {}
                for event in llm_events:
                    phase = event.get("phase", "unknown")
                    llm_by_phase[phase] = llm_by_phase.get(phase, 0) + 1
                for phase, count in sorted(llm_by_phase.items()):
                    print(f"     - {phase}: {count}")
        else:
            print("   ⚠️  Trace not found in database")
    except Exception as exc:
        print(f"   ⚠️  Error verifying database: {exc}")

    # Finalize execution metrics
    pipeline_end_time = time.time()
    execution_metrics["pipeline_end_time"] = pipeline_end_time
    
    # Generate comprehensive workflow documentation
    print("\n19. Generating workflow documentation...")
    doc_path = None
    try:
        doc_path = generate_workflow_documentation(
            trace_id=trace_id,
            article_slug=article_slug,
            article_text=article_text,
            all_ideas=all_ideas,
            all_copy_results=all_copy_results,
            logger=logger,
            article_output_dir=article_output_dir,
            execution_metrics=execution_metrics,
        )
        print(f"   ✓ Workflow documentation generated successfully")
        print(f"   ✓ Path: {doc_path}")
    except Exception as exc:
        import traceback
        error_traceback = traceback.format_exc()
        error_message = f"Error generating documentation: {str(exc)}"
        print(f"   ❌ ERROR: {error_message}")
        print(f"   📝 Full traceback:")
        print(f"   {error_traceback}")
        
        # Log this as an error in metrics
        execution_metrics["errors"].append({
            "phase": "Documentation Generation",
            "type": type(exc).__name__,
            "message": error_message,
            "traceback": error_traceback,
            "timestamp": time.time(),
        })
        
        # Try to save execution metrics even if documentation fails
        try:
            metrics_path = article_output_dir / "execution_metrics.json"
            metrics_path.write_text(
                json.dumps(execution_metrics, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            print(f"   ✓ Execution metrics saved to: {metrics_path}")
        except Exception as metrics_error:
            print(f"   ⚠️  WARNING: Failed to save execution metrics: {metrics_error}")
        
        # Don't return error code - documentation failure shouldn't fail the whole pipeline
        print(f"   ℹ️  Continuing anyway...")

    print("\n" + "=" * 70)
    print("✅ FULL PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Output directory: {article_output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    print(f"📈 Total slides processed: {total_slides}")
    print(f"📋 Total briefs: {len(briefs)}")
    print(f"📖 Total narrative structures: {len(narrative_results)}")
    
    # Print execution summary
    total_duration = pipeline_end_time - pipeline_start_time
    print(f"\n⏱️  EXECUTION SUMMARY:")
    print(f"   • Total pipeline duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"   • Errors: {len(execution_metrics['errors'])}")
    print(f"   • Warnings: {len(execution_metrics['warnings'])}")
    if doc_path:
        print(f"   • Documentation: {doc_path}")
    else:
        print(f"   • Documentation: Failed to generate")

    return 0


if __name__ == "__main__":
    sys.exit(main())

