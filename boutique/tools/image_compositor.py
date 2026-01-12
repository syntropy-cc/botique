"""
Image Compositor Tool

Tool para composição de imagens (background + elementos + texto).
"""

from pathlib import Path
from typing import Any, Dict

from framework.core.tool import Tool


class ImageCompositorTool(Tool):
    """Tool para composição de imagens"""
    
    def __init__(self):
        super().__init__(
            sig=("background_path", "text_overlay", "output_path"),
            f=self._compose_image,
            effects={"io"},  # I/O operations
            pre=self._check_paths,
            name="image_compositor",
            description="Composes final slide image from background, elements, and text",
        )
    
    def _check_paths(self, input_data: Any, state: Any) -> bool:
        """Precondition: Background path deve existir"""
        if not isinstance(input_data, dict):
            return False
        background_path = input_data.get("background_path")
        if background_path:
            return Path(background_path).exists()
        return True  # Se não tem background, pode criar do zero
    
    def _compose_image(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compõe imagem final combinando background, elementos e texto.
        
        Args:
            input_data: Deve conter "background_path", "text_overlay", "output_path"
            
        Returns:
            Dict com path da imagem final
        """
        background_path = input_data.get("background_path")
        text_overlay = input_data.get("text_overlay", {})
        output_path = Path(input_data.get("output_path", "output/slide.png"))
        
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise RuntimeError("PIL (Pillow) is required for image composition")
        
        # Carrega background ou cria canvas
        if background_path and Path(background_path).exists():
            img = Image.open(background_path)
        else:
            # Cria canvas padrão
            width = text_overlay.get("canvas_width", 1080)
            height = text_overlay.get("canvas_height", 1350)
            img = Image.new("RGB", (width, height), color="#000000")
        
        draw = ImageDraw.Draw(img)
        
        # Renderiza textos
        texts = text_overlay.get("texts", {})
        for slot_name, slot_data in texts.items():
            if not isinstance(slot_data, dict):
                continue
            
            content = slot_data.get("content", "")
            if not content:
                continue
            
            x = slot_data.get("x", 540)
            y = slot_data.get("y", 400)
            color = slot_data.get("color", "#FFFFFF")
            font_size = slot_data.get("font_size", 48)
            
            # Tenta carregar fonte
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
            
            # Desenha texto
            draw.text((x, y), content, fill=color, font=font, anchor="mm")
        
        # Salva imagem
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        
        return {
            "output_path": str(output_path),
            "width": img.width,
            "height": img.height,
        }
