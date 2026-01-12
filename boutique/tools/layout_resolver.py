"""
Layout Resolver Tool

Tool para resolução de layouts por slide baseado em narrative structure.
"""

from typing import Any, Dict, List

from framework.core.tool import Tool


class LayoutResolverTool(Tool):
    """Tool para resolução de layouts por slide"""
    
    def __init__(self):
        super().__init__(
            sig=("narrative_structure", "libraries_path"),
            f=self._resolve_layouts,
            effects=set(),  # Não modifica estado, apenas resolve
            name="layout_resolver",
            description="Resolves layouts for each slide based on narrative structure",
        )
    
    def _resolve_layouts(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve layouts para cada slide.
        
        Args:
            input_data: Deve conter "narrative_structure" e opcionalmente "libraries_path"
            
        Returns:
            Dict mapeando slide_number para layout
        """
        narrative_structure = input_data.get("narrative_structure", {})
        libraries_path = input_data.get("libraries_path")
        
        if not narrative_structure:
            raise ValueError("narrative_structure is required")
        
        slides = narrative_structure.get("slides", [])
        layouts = {}
        
        for slide in slides:
            slide_number = slide.get("number", 0)
            module = slide.get("module", "")
            purpose = slide.get("purpose", "")
            
            # Seleciona layout baseado em module e purpose
            # Por enquanto, usa layout padrão - pode ser estendido para usar libraries
            layout = self._select_layout_for_slide(module, purpose, libraries_path)
            layouts[str(slide_number)] = layout
        
        return {
            "layouts": layouts,
            "slide_count": len(slides),
        }
    
    def _select_layout_for_slide(
        self,
        module: str,
        purpose: str,
        libraries_path: Any = None,
    ) -> Dict[str, Any]:
        """
        Seleciona layout para um slide específico.
        
        Por enquanto, retorna layout padrão. Pode ser estendido para
        carregar de libraries/layouts/.
        """
        # Layout padrão baseado em module
        default_layouts = {
            "hook": {
                "type": "centered",
                "text_slots": {
                    "headline": {"x": 540, "y": 400, "max_chars": 60},
                    "subheadline": {"x": 540, "y": 500, "max_chars": 100},
                },
            },
            "transition": {
                "type": "split",
                "text_slots": {
                    "headline": {"x": 270, "y": 400, "max_chars": 50},
                    "body": {"x": 810, "y": 400, "max_chars": 200},
                },
            },
            "cta": {
                "type": "bottom",
                "text_slots": {
                    "headline": {"x": 540, "y": 1000, "max_chars": 60},
                    "cta": {"x": 540, "y": 1150, "max_chars": 40},
                },
            },
        }
        
        # Tenta encontrar layout por module
        if module in default_layouts:
            return default_layouts[module]
        
        # Fallback: layout genérico
        return {
            "type": "centered",
            "text_slots": {
                "headline": {"x": 540, "y": 400, "max_chars": 60},
                "body": {"x": 540, "y": 600, "max_chars": 200},
            },
        }
