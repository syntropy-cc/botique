"""
Phase 1: Ideation wrapper

Thin wrapper around IdeaGenerator that handles article reading,
idea generation, validation, and JSON persistence.

Location: src/phases/phase1_ideation.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import IdeationConfig, OUTPUT_DIR
from ..ideas.generator import IdeaGenerator
from ..ideas.filter import IdeaFilter
from ..coherence.builder import CoherenceBriefBuilder
from ..coherence.brief import CoherenceBrief


def run(
    article_path: Path,
    config: IdeationConfig,
    llm_client,
    output_dir: Path = None,
) -> Dict[str, Any]:
    """
    Run Phase 1: Generate ideas from article and coherence briefs.
    
    This is a thin wrapper that:
    1. Reads article from path
    2. Calls IdeaGenerator.generate_ideas()
    3. Validates minimum ideas count
    4. Optionally filters ideas (if filter_enabled)
    5. Generates Coherence Brief for each filtered idea
    6. Saves phase1_ideas.json and coherence briefs
    7. Returns payload with paths
    
    Args:
        article_path: Path to article file
        config: Ideation configuration
        llm_client: LLM client instance
        output_dir: Output directory (defaults to OUTPUT_DIR)
    
    Returns:
        Dict with:
            - ideas: List of idea dicts (all generated)
            - filtered_ideas: List of filtered idea dicts (if filter enabled)
            - article_summary: Article summary dict
            - article_slug: Article identifier
            - output_path: Path to saved JSON
            - ideas_count: Number of ideas generated
            - filtered_count: Number of ideas after filtering
            - briefs: List of CoherenceBrief objects
            - briefs_dict: List of brief dicts (for JSON)
            - briefs_count: Number of briefs generated
    
    Raises:
        FileNotFoundError: If article file doesn't exist
        ValueError: If validation fails or insufficient ideas
    """
    # Read article
    if not article_path.exists():
        raise FileNotFoundError(f"Article not found: {article_path}")
    
    article_text = article_path.read_text(encoding="utf-8")
    article_slug = article_path.stem
    
    # Determine output directory
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    # Create article-specific output directory
    article_output_dir = output_dir / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure LLM client to save raw responses in the article's debug directory
    if hasattr(llm_client, 'raw_responses_dir') or hasattr(llm_client, 'save_raw_responses'):
        # Set raw responses directory for this article
        debug_dir = article_output_dir / "debug"
        llm_client.raw_responses_dir = debug_dir
        llm_client.save_raw_responses = True
    
    # Initialize generator
    generator = IdeaGenerator(llm_client)
    
    # Generate ideas (raw response will be automatically saved by HttpLLMClient.generate())
    payload = generator.generate_ideas(
        article_text, 
        config,
        context=article_slug,  # Pass context for organizing saved responses
    )
    
    # Validate minimum ideas
    ideas = payload["ideas"]
    if len(ideas) < config.min_ideas:
        raise ValueError(
            f"Generated {len(ideas)} ideas, but minimum is {config.min_ideas}"
        )
    
    # Filter ideas if enabled
    filtered_ideas = ideas
    if config.filter_enabled:
        # Filter by confidence first
        filtered_ideas = IdeaFilter.filter_by_confidence(
            ideas, config.filter_min_confidence
        )
        
        # If no ideas meet threshold, warn and use all
        if not filtered_ideas:
            filtered_ideas = ideas
        
        # Apply selection strategy
        if config.filter_strategy == "diverse":
            filtered_ideas = IdeaFilter.select_diverse(
                filtered_ideas,
                config.filter_max_count or len(filtered_ideas)
            )
        elif config.filter_strategy == "top":
            max_count = config.filter_max_count or len(filtered_ideas)
            filtered_ideas = IdeaFilter.select_top_n(filtered_ideas, max_count)
        # else: "all" - use all filtered ideas
        
        if not filtered_ideas:
            raise ValueError(
                f"No ideas selected after filtering. Check min_confidence "
                f"({config.filter_min_confidence}) and max_count "
                f"({config.filter_max_count}) settings."
            )
    
    # Generate Coherence Brief for each filtered idea
    briefs: List[CoherenceBrief] = []
    briefs_dict: List[Dict[str, Any]] = []
    
    for idx, idea in enumerate(filtered_ideas, 1):
        # Create unique post_id
        post_id = f"post_{article_slug}_{idea['id']}"
        
        try:
            # Build coherence brief
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=payload["article_summary"],
                post_id=post_id,
            )
            
            # Validate brief
            CoherenceBriefBuilder.validate_brief(brief)
            
            briefs.append(brief)
            briefs_dict.append(brief.to_dict())
            
            # Save individual brief
            post_dir = article_output_dir / post_id
            post_dir.mkdir(parents=True, exist_ok=True)
            
            brief_path = post_dir / "coherence_brief.json"
            brief_path.write_text(
                json.dumps(brief.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            
        except Exception as exc:
            raise ValueError(
                f"Failed to build coherence brief for idea {idea.get('id', 'unknown')}: {exc}"
            ) from exc
    
    # Save consolidated briefs
    if briefs:
        consolidated_briefs_path = article_output_dir / "coherence_briefs.json"
        consolidated_briefs_path.write_text(
            json.dumps(briefs_dict, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    
    # Save phase1_ideas.json
    output_path = article_output_dir / "phase1_ideas.json"
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    return {
        "ideas": ideas,
        "filtered_ideas": filtered_ideas,
        "article_summary": payload["article_summary"],
        "article_slug": article_slug,
        "output_path": str(output_path),
        "ideas_count": len(ideas),
        "filtered_count": len(filtered_ideas),
        "briefs": briefs,
        "briefs_dict": briefs_dict,
        "briefs_count": len(briefs),
        "output_dir": str(article_output_dir),
    }

