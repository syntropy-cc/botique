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
import warnings
from pathlib import Path
from typing import Any, Dict, List

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
                for idx, emph in enumerate(title_emphasis, 1):
                    emph_text = emph.get("text", "")
                    start_idx = emph.get("start_index", "N/A")
                    end_idx = emph.get("end_index", "N/A")
                    styles = ", ".join(emph.get("styles", []))
                    print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
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
                for idx, emph in enumerate(subtitle_emphasis, 1):
                    emph_text = emph.get("text", "")
                    start_idx = emph.get("start_index", "N/A")
                    end_idx = emph.get("end_index", "N/A")
                    styles = ", ".join(emph.get("styles", []))
                    print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
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
                for idx, emph in enumerate(body_emphasis, 1):
                    emph_text = emph.get("text", "")
                    start_idx = emph.get("start_index", "N/A")
                    end_idx = emph.get("end_index", "N/A")
                    styles = ", ".join(emph.get("styles", []))
                    print(f"     [{idx}] '{emph_text}' (indices {start_idx}-{end_idx}) → [{styles}]")
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
) -> None:
    """
    Gera um documento Markdown detalhado com todo o workflow e outputs.
    
    Args:
        trace_id: ID do trace para buscar eventos do banco de dados
        article_slug: Slug do artigo processado
        article_text: Texto completo do artigo
        all_ideas: Lista de todas as ideias geradas
        all_copy_results: Lista de todos os resultados de copywriting
        logger: LLMLogger com as chamadas
        article_output_dir: Diretório de output do artigo
    """
    from datetime import datetime
    
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
    
    # Tabela de Conteúdo
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Overview](#overview)")
    lines.append("2. [Article Content](#article-content)")
    lines.append("3. [Phase 1: Ideation](#phase-1-ideation)")
    lines.append("4. [Phase 2: Coherence Briefs](#phase-2-coherence-briefs)")
    lines.append("5. [Phase 3: Narrative Architect](#phase-3-narrative-architect)")
    lines.append("6. [Phase 4: Copywriter](#phase-4-copywriter)")
    lines.append("7. [LLM Events & Responses](#llm-events--responses)")
    lines.append("8. [Metrics Summary](#metrics-summary)")
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
        total_slides = sum(len(r["slide_contents"]) for r in all_copy_results)
        lines.append(f"- **Total Slides Generated:** {total_slides}")
        lines.append(f"- **Trace Created:** {trace_data.get('created_at', 'N/A')}")
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
        if narrative_payload:
            lines.append("### Narrative Structure Overview")
            lines.append("")
            lines.append(f"- **Pacing:** {narrative_payload.get('pacing', 'N/A')}")
            lines.append(f"- **Transition Style:** {narrative_payload.get('transition_style', 'N/A')}")
            lines.append(f"- **Total Slides:** {len(narrative_payload.get('slides', []))}")
            if narrative_payload.get('arc_refined'):
                lines.append(f"- **Arc Refined:** {narrative_payload.get('arc_refined', 'N/A')}")
            lines.append("")
        
        # Combine narrative structure and copy for each slide
        lines.append("### Slides: Narrative Structure & Copy")
        lines.append("")
        
        # Create maps for easy lookup
        slides_narrative = {}
        if narrative_payload:
            for slide in narrative_payload.get("slides", []):
                slide_num = slide.get("slide_number", "?")
                slides_narrative[slide_num] = slide
        
        slides_copy_map = {}
        for slide_result in slide_contents:
            slide_num = slide_result["slide_number"]
            slides_copy_map[slide_num] = slide_result["slide_content"]
        
        # Get all slide numbers in order
        all_slide_nums = sorted(set(list(slides_narrative.keys()) + list(slides_copy_map.keys())))
        
        for slide_num in all_slide_nums:
            slide_narrative = slides_narrative.get(slide_num)
            slide_content = slides_copy_map.get(slide_num)
            
            lines.append(f"#### Slide {slide_num}")
            lines.append("")
            
            # Narrative Structure for this slide
            if slide_narrative:
                module_type = slide_narrative.get("module_type", "unknown")
                lines.append(f"**Type:** {module_type}")
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
                        
                        if title_emphasis:
                            lines.append(f"- **Emphasis Spans:** {len(title_emphasis)}")
                            lines.append("")
                            for idx, emph in enumerate(title_emphasis, 1):
                                emph_text = emph.get("text", "")
                                start_idx = emph.get("start_index", "N/A")
                                end_idx = emph.get("end_index", "N/A")
                                styles = ", ".join(emph.get("styles", []))
                                lines.append(f"  {idx}. Text: `{emph_text}`")
                                lines.append(f"     Indices: {start_idx}-{end_idx}")
                                lines.append(f"     Styles: `{styles}`")
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
                        
                        if subtitle_emphasis:
                            lines.append(f"- **Emphasis Spans:** {len(subtitle_emphasis)}")
                            lines.append("")
                            for idx, emph in enumerate(subtitle_emphasis, 1):
                                emph_text = emph.get("text", "")
                                start_idx = emph.get("start_index", "N/A")
                                end_idx = emph.get("end_index", "N/A")
                                styles = ", ".join(emph.get("styles", []))
                                lines.append(f"  {idx}. Text: `{emph_text}`")
                                lines.append(f"     Indices: {start_idx}-{end_idx}")
                                lines.append(f"     Styles: `{styles}`")
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
                        
                        if body_emphasis:
                            lines.append(f"- **Emphasis Spans:** {len(body_emphasis)}")
                            lines.append("")
                            for idx, emph in enumerate(body_emphasis, 1):
                                emph_text = emph.get("text", "")
                                start_idx = emph.get("start_index", "N/A")
                                end_idx = emph.get("end_index", "N/A")
                                styles = ", ".join(emph.get("styles", []))
                                lines.append(f"  {idx}. Text: `{emph_text}`")
                                lines.append(f"     Indices: {start_idx}-{end_idx}")
                                lines.append(f"     Styles: `{styles}`")
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
    
    # Escrever arquivo
    doc_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n   📄 Workflow documentation saved: {doc_path}")
    
    return doc_path


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
        print(f"   ⚠️  WARNING: Error generating ideas: {error_msg}")
        print(f"   ℹ️  Cannot continue without ideas. Exiting.")
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
            print(f"   ⚠️  WARNING: Error building brief for {idea_id}: {error_msg}")
            print(f"   ℹ️  Skipping this idea and continuing...")
            # Continue to next idea instead of returning 1

    if not briefs:
        print(f"   ❌ ERROR: No coherence briefs were built successfully. Cannot continue.")
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
                    print(f"   ⚠️  WARNING: {warning.message}")
                    if hasattr(warning, 'filename') and hasattr(warning, 'lineno'):
                        print(f"      (from {warning.filename}:{warning.lineno})")

            narrative_results.append({
                "brief": brief,
                "narrative_payload": narrative_payload,
            })

            # Print updated brief with narrative evolution
            print_brief_details(brief, phase="Phase 3 - After Narrative")
            
            # Print narrative structure summary
            slides = narrative_payload.get("slides", [])
            pacing = narrative_payload.get("pacing", "N/A")
            transition = narrative_payload.get("transition_style", "N/A")
            print(f"\n   📖 NARRATIVE STRUCTURE:")
            print(f"      • Slides: {len(slides)}")
            print(f"      • Pacing: {pacing}")
            print(f"      • Transition Style: {transition}")
            if narrative_payload.get("arc_refined"):
                arc = narrative_payload.get("arc_refined", "")
                print(f"      • Arc Refined: {arc[:100]}..." if len(arc) > 100 else f"      • Arc Refined: {arc}")
            
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
            print(f"   ⚠️  WARNING: {error_msg}")
            print(f"   ℹ️  Continuing with next brief...")
            # Continue instead of returning 1

    print(f"\n   ✓ {len(narrative_results)} narrative structure(s) generated successfully")

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

        try:
            logger.set_context(post_id=brief.post_id)

            print(f"\n      Generating copy for all {len(slides)} slides...")

            # Capture warnings and display them as informational messages
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
                    print(f"      ⚠️  WARNING: {warning.message}")

            # Extract slides from response
            slides_copy = post_copy_result.get("slides", [])
            
            if len(slides_copy) != len(slides):
                print(f"      ⚠️  WARNING: Expected {len(slides)} slides, got {len(slides_copy)}")
            
            # Match slides copy with slides info by slide_number
            slides_copy_dict = {s.get("slide_number"): s for s in slides_copy}
            
            for slide_idx, slide_info in enumerate(slides, 1):
                slide_number = slide_info.get("slide_number", slide_idx)
                module_type = slide_info.get("module_type", "unknown")
                
                slide_content = slides_copy_dict.get(slide_number)
                if not slide_content:
                    print(f"      ⚠️  WARNING: No copy found for slide {slide_number}")
                    continue
                
                post_copy_results.append({
                    "slide_number": slide_number,
                    "slide_info": slide_info,
                    "slide_content": slide_content,
                })

                # Print detailed slide copy information
                print_slide_copy_details(slide_content, slide_info, slide_number)

                # Save individual slide content
                post_dir = article_output_dir / brief.post_id
                slide_content_path = post_dir / f"slide_{slide_number}_content.json"
                slide_content_path.write_text(
                    json.dumps(slide_content, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            # Save complete post copy result
            post_dir = article_output_dir / brief.post_id
            post_copy_path = post_dir / "post_copy.json"
            post_copy_path.write_text(
                json.dumps(post_copy_result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"      ✓ Post copy saved: {post_copy_path}")

        except Exception as exc:
            error_msg = str(exc)
            print(f"      ⚠️  WARNING: {error_msg}")
            print(f"      ℹ️  Skipping this post and continuing...")
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

    # Generate comprehensive workflow documentation
    print("\n19. Generating workflow documentation...")
    try:
        doc_path = generate_workflow_documentation(
            trace_id=trace_id,
            article_slug=article_slug,
            article_text=article_text,
            all_ideas=all_ideas,
            all_copy_results=all_copy_results,
            logger=logger,
            article_output_dir=article_output_dir,
        )
        print(f"   ✓ Workflow documentation generated successfully")
    except Exception as exc:
        print(f"   ⚠️  WARNING: Error generating documentation: {exc}")
        print(f"   ℹ️  Continuing anyway...")

    print("\n" + "=" * 70)
    print("✅ FULL PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📄 Output directory: {article_output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    print(f"📈 Total slides processed: {total_slides}")
    print(f"📋 Total briefs: {len(briefs)}")
    print(f"📖 Total narrative structures: {len(narrative_results)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

