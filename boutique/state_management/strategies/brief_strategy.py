"""
Brief Strategy

Estratégia específica para projeção de briefs.
"""

from typing import Any, Dict, Optional

from framework.core.state_management import EpisodicStrategy, HierarchicalStrategy
from framework.core.universal_state import UniversalState

from ..boutique_state import BoutiqueState


class BriefEpisodicStrategy(EpisodicStrategy):
    """
    Estratégia episódica específica para briefs.
    
    Projeta apenas o brief do post atual.
    """
    
    def __init__(self, post_id: str):
        """
        Inicializa estratégia para um post específico.
        
        Args:
            post_id: Identificador do post
        """
        super().__init__(entity_type="brief", entity_id=post_id)
        self.post_id = post_id
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Projeta brief do post atual.
        
        Args:
            state: UniversalState (deve ser BoutiqueState)
            query: Query opcional
            
        Returns:
            Dict com brief e contexto
        """
        # Se state for BoutiqueState, usa método específico
        if isinstance(state, BoutiqueState):
            brief = state.get_brief(self.post_id)
        else:
            brief = state.retrieve("brief", self.post_id)
        
        if brief:
            # Formata contexto do brief
            if hasattr(brief, 'to_prompt_context'):
                context = brief.to_prompt_context()
            elif hasattr(brief, 'to_narrative_architect_context'):
                context = brief.to_narrative_architect_context()
            else:
                context = str(brief)
            
            return {
                "brief": brief,
                "context": context,
                "post_id": self.post_id,
            }
        
        return {
            "brief": None,
            "context": "",
            "post_id": self.post_id,
        }


class BriefHierarchicalStrategy(HierarchicalStrategy):
    """
    Estratégia hierárquica específica para briefs.
    
    Projeta todos os briefs de um artigo.
    """
    
    def __init__(self, article_slug: str):
        """
        Inicializa estratégia para um artigo.
        
        Args:
            article_slug: Slug do artigo
        """
        super().__init__(
            entity_type="brief",
            context_key="article_slug",
            context_value=article_slug
        )
        self.article_slug = article_slug
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Projeta todos os briefs do artigo.
        
        Args:
            state: UniversalState (deve ser BoutiqueState)
            query: Query opcional
            
        Returns:
            Dict com briefs e contagem
        """
        # Se state for BoutiqueState, usa método específico
        if isinstance(state, BoutiqueState):
            briefs = state.get_all_briefs(article_slug=self.article_slug)
        else:
            briefs = state.query("brief", {"article_slug": self.article_slug})
            # Converte para dict se necessário
            if isinstance(briefs, list):
                briefs_dict = {}
                for brief in briefs:
                    if hasattr(brief, 'post_id'):
                        briefs_dict[brief.post_id] = brief
                    elif isinstance(brief, dict) and 'post_id' in brief:
                        briefs_dict[brief['post_id']] = brief
                briefs = briefs_dict
        
        return {
            "briefs": briefs,
            "count": len(briefs),
            "article_slug": self.article_slug,
        }
