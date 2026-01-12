"""
Ideation Pipeline

Pipeline para geração de ideias de posts.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from boutique.agents.post_ideator_agent import PostIdeatorAgent
from boutique.state_management.boutique_state import BoutiqueState


def run_ideation_pipeline(
    article_path: Path,
    config: Optional[Any] = None,
    llm_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executa pipeline de ideação.
    
    Args:
        article_path: Caminho para artigo
        config: Configuração de ideação
        llm_client: Cliente LLM
        
    Returns:
        Resultado com article_summary e ideas
    """
    article_text = article_path.read_text(encoding="utf-8")
    article_slug = article_path.stem
    
    state = BoutiqueState()
    state.article_slug = article_slug
    
    agent = PostIdeatorAgent()
    
    result = agent.execute(
        input_data={
            "article": article_text,
            "article_slug": article_slug,
            "config": config,
            "llm_client": llm_client,
        },
        state=state,
    )
    
    return result
