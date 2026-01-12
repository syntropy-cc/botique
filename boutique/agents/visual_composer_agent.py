"""
Visual Composer Agent

Agente de composição visual.
"""

from framework.core.agent import Agent, VertexType
from boutique.instructions.visual_composer import VisualComposerInstruction
from boutique.tools.layout_resolver import LayoutResolverTool
from boutique.tools.palette_selector import PaletteSelectorTool


class VisualComposerAgent(Agent):
    """
    Agente de composição visual.
    
    Grafo:
    - Vértice 1: VisualComposerInstruction
    - Vértice 2: LayoutResolverTool (opcional)
    - Vértice 3: PaletteSelectorTool (opcional)
    """
    
    def __init__(self):
        instruction = VisualComposerInstruction()
        layout_tool = LayoutResolverTool()
        palette_tool = PaletteSelectorTool()
        
        super().__init__(
            name="visual_composer",
            entry_vertex="instruction",
            vertices={
                "instruction": VertexType.INSTRUCTION,
                "layout_resolver": VertexType.TOOL,
                "palette_selector": VertexType.TOOL,
            },
            edges={
                "instruction": ["layout_resolver"],  # Opcional
            },
        )
        
        self._instruction = instruction
        self._layout_tool = layout_tool
        self._palette_tool = palette_tool
    
    def execute(
        self,
        input_data: dict,
        state,
        state_strategy=None,
    ) -> dict:
        """
        Executa agente: gera especificações visuais.
        
        Args:
            input_data: Deve conter "brief", "slide_info", "layout"
            state: UniversalState
            state_strategy: Opcional state strategy
            
        Returns:
            Dict com especificações visuais
        """
        from framework.llm.http_client import HttpLLMClient
        llm_client = input_data.get("llm_client")
        if not llm_client:
            llm_client = HttpLLMClient()
        
        instruction_input = {
            "brief": input_data.get("brief"),
            "slide_info": input_data.get("slide_info", {}),
            "layout": input_data.get("layout", {}),
        }
        
        visual_specs = self._instruction.execute(
            input_data=instruction_input,
            llm_client=llm_client,
            memory_context=state_strategy.project(state) if state_strategy else None,
        )
        
        return visual_specs
