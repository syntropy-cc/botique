"""
Brand Strategy

Estratégia específica para projeção de brand.
"""

from typing import Any, Dict, Optional

from framework.core.state_management import StateManagementStrategy
from framework.core.universal_state import UniversalState

from ..boutique_state import BoutiqueState


class BrandStrategy(StateManagementStrategy):
    """
    Estratégia para projeção de brand.
    
    Projeta informações de brand (palettes, typography, etc.)
    para uso em geração de conteúdo.
    """
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Projeta brand do estado.
        
        Args:
            state: UniversalState (deve ser BoutiqueState)
            query: Query opcional (pode especificar platform, tone, persona)
            
        Returns:
            Dict com brand library e informações relevantes
        """
        # Se state for BoutiqueState, usa método específico
        if isinstance(state, BoutiqueState):
            brand_library = state.get_brand()
        else:
            brand_library = state.retrieve("brand", "default")
        
        if brand_library is None:
            return {
                "brand": None,
                "palettes": {},
                "typography": {},
            }
        
        # Extrai informações relevantes do brand
        result = {
            "brand": brand_library,
        }
        
        # Se query especifica platform/tone/persona, seleciona palette
        if query and isinstance(query, dict):
            platform = query.get("platform")
            tone = query.get("tone")
            persona = query.get("persona")
            
            if platform and tone and hasattr(brand_library, 'select_palette'):
                try:
                    palette = brand_library.select_palette(platform, tone, persona)
                    result["selected_palette"] = palette
                except Exception:
                    pass
            
            if platform and hasattr(brand_library, 'select_typography'):
                try:
                    typography = brand_library.select_typography(platform, persona)
                    result["selected_typography"] = typography
                except Exception:
                    pass
        
        return result
