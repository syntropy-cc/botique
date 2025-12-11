"""
Phase 2: Selection wrapper

Thin wrapper around IdeaFilter that applies filtering strategy
and saves selected ideas.

Location: src/phases/phase2_selection.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import SelectionConfig, OUTPUT_DIR
from ..ideas.filter import IdeaFilter


def run(
    ideas_payload: Dict[str, Any],
    config: SelectionConfig,
    article_slug: str,
    output_dir: Path = None,
) -> Dict[str, Any]:
    """
    Run Phase 2: Select ideas from generated ideas.
    
    This is a thin wrapper that:
    1. Takes ideas payload + SelectionConfig
    2. Applies filtering strategy (confidence, diversity, etc.)
    3. Saves selected_ideas.json
    4. Returns selected ideas + stats
    
    Args:
        ideas_payload: Output from phase1 (dict with "ideas" key)
        config: Selection configuration
        article_slug: Article identifier for file naming
        output_dir: Output directory (defaults to OUTPUT_DIR)
    
    Returns:
        Dict with:
            - selected_ideas: List of selected idea dicts
            - stats: Selection statistics
            - output_path: Path to saved JSON
            - selection_count: Number of selected ideas
    
    Raises:
        ValueError: If no ideas match criteria
    """
    ideas = ideas_payload.get("ideas", [])
    
    if not ideas:
        raise ValueError("No ideas provided for selection")
    
    # Apply selection strategy
    if config.selected_ids:
        # Manual selection by IDs
        selected = IdeaFilter.select_by_ids(ideas, config.selected_ids)
    elif config.strategy == "diverse":
        # Filter by confidence first
        filtered = IdeaFilter.filter_by_confidence(ideas, config.min_confidence)
        
        # If no ideas meet threshold, warn and use all
        if not filtered:
            filtered = ideas
        
        # Select diverse subset
        selected = IdeaFilter.select_diverse(filtered, config.max_selected)
    else:  # strategy == "top"
        # Filter by confidence
        filtered = IdeaFilter.filter_by_confidence(ideas, config.min_confidence)
        
        # If no ideas meet threshold, warn and use all
        if not filtered:
            filtered = ideas
        
        # Select top N by confidence
        selected = IdeaFilter.select_top_n(filtered, config.max_selected)
    
    if not selected:
        raise ValueError(
            f"No ideas selected. Check min_confidence ({config.min_confidence}) "
            f"and max_selected ({config.max_selected}) settings."
        )
    
    # Calculate statistics
    stats = IdeaFilter.get_statistics(selected)
    
    # Determine output directory
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    # Create article-specific output directory
    article_output_dir = output_dir / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save selected_ideas.json
    output_payload = {
        "selected_ideas": selected,
        "stats": stats,
        "config": {
            "min_confidence": config.min_confidence,
            "max_selected": config.max_selected,
            "strategy": config.strategy,
            "selected_ids": config.selected_ids,
        },
    }
    
    output_path = article_output_dir / "selected_ideas.json"
    output_path.write_text(
        json.dumps(output_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    return {
        "selected_ideas": selected,
        "stats": stats,
        "output_path": str(output_path),
        "selection_count": len(selected),
        "output_dir": str(article_output_dir),
    }

