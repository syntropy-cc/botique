"""
Parameter Resolver Tool

Tool para resolução de parâmetros de post (palette, typography, canvas, etc.).
"""

from typing import Any, Dict

from framework.core.tool import Tool


class ParameterResolverTool(Tool):
    """Tool para resolução de parâmetros de post"""
    
    def __init__(self):
        super().__init__(
            sig=("idea", "article_summary", "post_id"),
            f=self._resolve_parameters,
            effects={"state"},  # Modifica estado
            name="parameter_resolver",
            description="Resolves post parameters (palette, typography, canvas) from idea",
        )
    
    def _resolve_parameters(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve parâmetros de post a partir de idea.
        
        Args:
            input_data: Deve conter "idea", "article_summary", "post_id"
            
        Returns:
            Dict com post_config completo
        """
        idea = input_data.get("idea", {})
        article_summary = input_data.get("article_summary", {})
        post_id = input_data.get("post_id", "")
        
        if not idea:
            raise ValueError("idea is required")
        
        platform = idea.get("platform", "")
        tone = idea.get("tone", "")
        persona = idea.get("persona", "")
        format_type = idea.get("format", "carousel")
        
        # Resolve palette
        try:
            from .palette_selector import PaletteSelectorTool
            palette_tool = PaletteSelectorTool()
            palette = palette_tool.execute({
                "platform": platform,
                "tone": tone,
                "persona": persona,
            })
        except Exception:
            palette = {}
        
        # Resolve typography
        try:
            from ..state_management.models.brand.library import BrandLibrary
            typography = BrandLibrary.select_typography(platform, persona)
            if hasattr(typography, 'to_dict'):
                typography_dict = typography.to_dict()
            else:
                from dataclasses import asdict
                typography_dict = asdict(typography)
        except Exception:
            typography_dict = {}
        
        # Resolve canvas
        try:
            from ..state_management.models.brand.library import BrandLibrary
            canvas = BrandLibrary.get_canvas_config(platform, format_type)
            if hasattr(canvas, 'to_dict'):
                canvas_dict = canvas.to_dict()
            else:
                from dataclasses import asdict
                canvas_dict = asdict(canvas)
        except Exception:
            canvas_dict = {}
        
        return {
            "post_id": post_id,
            "idea_ref": idea.get("id", ""),
            "platform": platform,
            "tone": tone,
            "persona": persona,
            "palette_id": palette.get("id", ""),
            "palette": palette,
            "typography_id": typography_dict.get("id", ""),
            "typography": typography_dict,
            "canvas": canvas_dict,
            "format": format_type,
        }
