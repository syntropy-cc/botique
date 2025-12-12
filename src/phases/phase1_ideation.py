"""
Phase 1: Ideation wrapper

Thin wrapper around IdeaGenerator that handles article reading,
idea generation, validation, and JSON persistence.

Location: src/phases/phase1_ideation.py
"""

import json
from pathlib import Path
from typing import Any, Dict

from ..core.config import IdeationConfig, OUTPUT_DIR
from ..ideas.generator import IdeaGenerator


def run(
    article_path: Path,
    config: IdeationConfig,
    llm_client,
    output_dir: Path = None,
) -> Dict[str, Any]:
    """
    Run Phase 1: Generate ideas from article.
    
    This is a thin wrapper that:
    1. Reads article from path
    2. Calls IdeaGenerator.generate_ideas()
    3. Validates minimum ideas count
    4. Saves phase1_ideas.json
    5. Returns payload with paths
    
    Args:
        article_path: Path to article file
        config: Ideation configuration
        llm_client: LLM client instance
        output_dir: Output directory (defaults to OUTPUT_DIR)
    
    Returns:
        Dict with:
            - ideas: List of idea dicts
            - article_summary: Article summary dict
            - article_slug: Article identifier
            - output_path: Path to saved JSON
            - ideas_count: Number of ideas generated
    
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
    
    # Initialize generator
    generator = IdeaGenerator(llm_client)
    
    # Prepare path for raw response (save even if validation fails)
    debug_dir = article_output_dir / "debug"
    raw_response_path = debug_dir / "raw_llm_response.txt"
    
    # Generate ideas (raw response will be saved automatically)
    payload = generator.generate_ideas(
        article_text, 
        config,
        save_raw_response=True,
        raw_response_path=raw_response_path,
    )
    
    # Validate minimum ideas
    ideas = payload["ideas"]
    if len(ideas) < config.min_ideas:
        raise ValueError(
            f"Generated {len(ideas)} ideas, but minimum is {config.min_ideas}"
        )
    
    # Save phase1_ideas.json
    output_path = article_output_dir / "phase1_ideas.json"
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    return {
        "ideas": ideas,
        "article_summary": payload["article_summary"],
        "article_slug": article_slug,
        "output_path": str(output_path),
        "ideas_count": len(ideas),
        "output_dir": str(article_output_dir),
    }

