"""
Phase 3: Coherence wrapper

Thin wrapper around CoherenceBriefBuilder that builds briefs
for each selected idea and saves them.

Location: src/phases/phase3_coherence.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import OUTPUT_DIR
# Try new location first, fallback to old location
try:
    from boutique.state_management.models.coherence_brief import CoherenceBrief
    from boutique.state_management.models.coherence_brief import CoherenceBriefBuilder
except ImportError:
    from ..coherence.builder import CoherenceBriefBuilder
    from ..coherence.brief import CoherenceBrief


def run(
    selected_ideas: List[Dict[str, Any]],
    article_summary: Dict[str, Any],
    article_slug: str,
    output_dir: Path = None,
) -> Dict[str, Any]:
    """
    Run Phase 3: Build coherence briefs for selected ideas.
    
    This is a thin wrapper that:
    1. Takes selected ideas + article summary
    2. For each idea: builds CoherenceBrief using CoherenceBriefBuilder
    3. Saves individual briefs (one per post)
    4. Saves consolidated coherence_briefs.json
    5. Returns list of CoherenceBrief objects
    
    Args:
        selected_ideas: List of selected idea dicts
        article_summary: Article summary dict from phase1
        article_slug: Article identifier for file naming
        output_dir: Output directory (defaults to OUTPUT_DIR)
    
    Returns:
        Dict with:
            - briefs: List of CoherenceBrief objects
            - briefs_dict: List of brief dicts (for JSON serialization)
            - output_path: Path to consolidated JSON
            - briefs_count: Number of briefs generated
    
    Raises:
        ValueError: If brief validation fails
    """
    if not selected_ideas:
        raise ValueError("No selected ideas provided")
    
    briefs = []
    
    # Build brief for each selected idea
    for idx, idea in enumerate(selected_ideas, 1):
        post_id = f"post_{article_slug}_{idx:03d}"
        
        try:
            brief = CoherenceBriefBuilder.build_from_idea(
                idea=idea,
                article_summary=article_summary,
                post_id=post_id,
            )
            
            # Validate brief
            CoherenceBriefBuilder.validate_brief(brief)
            
            briefs.append(brief)
            
        except Exception as exc:
            raise ValueError(
                f"Failed to build coherence brief for idea {idea.get('id', 'unknown')}: {exc}"
            ) from exc
    
    # Determine output directory
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    # Create article-specific output directory
    article_output_dir = output_dir / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual briefs (one per post)
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
    
    return {
        "briefs": briefs,
        "briefs_dict": briefs_dict,
        "output_path": str(consolidated_path),
        "briefs_count": len(briefs),
        "output_dir": str(article_output_dir),
    }

