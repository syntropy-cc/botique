"""
Slide Generation Pipeline

Pipeline para geração de slides (copy + visual + composição).
"""

from typing import Any, Dict, List, Optional

from boutique.agents.copywriter_agent import CopywriterAgent
from boutique.agents.visual_composer_agent import VisualComposerAgent
from boutique.state_management.boutique_state import BoutiqueState
from boutique.state_management.models.coherence_brief import CoherenceBrief
from boutique.tools.image_compositor import ImageCompositorTool


def run_slide_generation_pipeline(
    brief: CoherenceBrief,
    slide_info: Dict[str, Any],
    article_text: str,
    layout: Optional[Dict[str, Any]] = None,
    llm_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executa pipeline de geração de slide.
    
    Args:
        brief: CoherenceBrief
        slide_info: Informações do slide do narrative_structure
        article_text: Texto do artigo
        layout: Layout do slide (opcional)
        llm_client: Cliente LLM
        
    Returns:
        Resultado com slide_content, visual_specs e final_slide_path
    """
    state = BoutiqueState()
    state.store_brief(brief)
    
    # Gera copy
    copywriter = CopywriterAgent()
    slide_content = copywriter.execute(
        input_data={
            "brief": brief,
            "slide_info": slide_info,
            "article_text": article_text,
            "llm_client": llm_client,
        },
        state=state,
    )
    
    # Enriquece brief com copy guidelines
    if hasattr(brief, 'enrich_from_copywriting'):
        copy_guidelines = slide_content.get("copy_guidelines", {})
        if copy_guidelines:
            brief.enrich_from_copywriting(copy_guidelines)
    
    # Gera visual specs
    visual_composer = VisualComposerAgent()
    visual_specs = visual_composer.execute(
        input_data={
            "brief": brief,
            "slide_info": slide_info,
            "layout": layout,
            "llm_client": llm_client,
        },
        state=state,
    )
    
    # Enriquece brief com visual preferences
    if hasattr(brief, 'enrich_from_visual_composition'):
        visual_preferences = visual_specs.get("visual_preferences", {})
        if visual_preferences:
            brief.enrich_from_visual_composition(visual_preferences)
    
    # Compõe imagem final (se necessário)
    final_slide_path = None
    if slide_content.get("texts") and visual_specs.get("background"):
        compositor = ImageCompositorTool()
        final_slide_path = compositor.execute({
            "background_path": visual_specs.get("background", {}).get("path"),
            "text_overlay": {
                "texts": slide_content.get("texts", {}),
                "canvas_width": brief.canvas.get("width", 1080),
                "canvas_height": brief.canvas.get("height", 1350),
            },
            "output_path": f"output/{brief.post_id}/slide_{slide_info.get('number', 1)}.png",
        })
    
    return {
        "slide_number": slide_info.get("number", 1),
        "slide_content": slide_content,
        "visual_specs": visual_specs,
        "final_slide_path": final_slide_path.get("output_path") if final_slide_path else None,
    }
