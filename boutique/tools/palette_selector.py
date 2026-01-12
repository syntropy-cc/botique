"""
Palette Selector Tool

Tool para seleção de paletas baseado em critérios (platform, tone, persona).
"""

from typing import Any, Dict, Optional

from framework.core.tool import Tool


class PaletteSelectorTool(Tool):
    """Tool para seleção de paletas baseado em critérios"""
    
    def __init__(self):
        super().__init__(
            sig=("platform", "tone", "persona"),
            f=self._select_palette,
            effects={"state"},  # Modifica estado (seleciona palette)
            pre=self._check_brand_loaded,
            post=self._validate_palette,
            name="palette_selector",
            description="Selects color palette based on platform, tone, and persona",
        )
    
    def _check_brand_loaded(self, input_data: Any, state: Any) -> bool:
        """Precondition: Brand library deve estar disponível"""
        if state is None:
            return False
        # Verifica se brand está disponível
        try:
            if hasattr(state, 'get_brand'):
                brand = state.get_brand()
                return brand is not None
            return True  # Se não tem método, assume OK
        except Exception:
            return False
    
    def _select_palette(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa seleção de paleta.
        
        Args:
            input_data: Deve conter "platform", "tone", "persona"
            
        Returns:
            Dict com palette selecionada
        """
        platform = input_data.get("platform")
        tone = input_data.get("tone")
        persona = input_data.get("persona")
        theme_preference = input_data.get("theme_preference", "auto")
        
        if not platform or not tone:
            raise ValueError("platform and tone are required")
        
        # Importa BrandLibrary
        try:
            from ..state_management.models.brand.library import BrandLibrary
            palette = BrandLibrary.select_palette(
                platform=platform,
                tone=tone,
                persona=persona,
                theme_preference=theme_preference,
            )
            
            # Converte para dict se necessário
            if hasattr(palette, 'to_dict'):
                return palette.to_dict()
            elif hasattr(palette, '__dict__'):
                return palette.__dict__
            else:
                # Fallback: usa dataclass asdict
                from dataclasses import asdict
                return asdict(palette)
        except ImportError:
            raise RuntimeError("BrandLibrary not available")
    
    def _validate_palette(self, input_data: Any, output: Any, state: Any) -> bool:
        """Postcondition: Palette deve ter campos essenciais"""
        if not isinstance(output, dict):
            return False
        required_fields = ["id", "primary", "accent", "background", "text"]
        return all(field in output for field in required_fields)
