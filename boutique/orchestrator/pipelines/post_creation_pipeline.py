"""
Post Creation Pipeline

Pipeline para criação completa de posts (brief + narrative).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from boutique.agents.narrative_architect_agent import NarrativeArchitectAgent
from boutique.state_management.boutique_state import BoutiqueState
from boutique.state_management.models.coherence_brief import CoherenceBrief


def run_post_creation_pipeline(
    brief: CoherenceBrief,
    article_text: str,
    llm_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executa pipeline de criação de post.
    
    Args:
        brief: CoherenceBrief inicial
        article_text: Texto do artigo
        llm_client: Cliente LLM
        
    Returns:
        Resultado com brief enriquecido e narrative_structure
    """
    state = BoutiqueState()
    state.store_brief(brief)
    
    agent = NarrativeArchitectAgent()
    
    result = agent.execute(
        input_data={
            "brief": brief,
            "article_text": article_text,
            "llm_client": llm_client,
        },
        state=state,
    )
    
    # Enriquece brief com estrutura narrativa
    if hasattr(brief, 'enrich_from_narrative_structure'):
        brief.enrich_from_narrative_structure(result)
        state.store_brief(brief)
    
    return {
        "brief": brief,
        "narrative_structure": result,
    }
