"""
Caption Writer Agent

Agente de escrita de caption.
"""

from framework.core.agent import Agent, VertexType
from boutique.instructions.caption_writer import CaptionWriterInstruction


class CaptionWriterAgent(Agent):
    """
    Agente de escrita de caption.
    
    Grafo:
    - Vértice 1: CaptionWriterInstruction
    """
    
    def __init__(self):
        instruction = CaptionWriterInstruction()
        
        super().__init__(
            name="caption_writer",
            entry_vertex="instruction",
            vertices={
                "instruction": VertexType.INSTRUCTION,
            },
            edges={},
        )
        
        self._instruction = instruction
    
    def execute(
        self,
        input_data: dict,
        state,
        state_strategy=None,
    ) -> dict:
        """
        Executa agente: gera caption.
        
        Args:
            input_data: Deve conter "brief" e "all_slide_contents"
            state: UniversalState
            state_strategy: Opcional state strategy
            
        Returns:
            Dict com caption
        """
        from framework.llm.http_client import HttpLLMClient
        llm_client = input_data.get("llm_client")
        if not llm_client:
            llm_client = HttpLLMClient()
        
        instruction_input = {
            "brief": input_data.get("brief"),
            "all_slide_contents": input_data.get("all_slide_contents", []),
        }
        
        caption = self._instruction.execute(
            input_data=instruction_input,
            llm_client=llm_client,
            memory_context=state_strategy.project(state) if state_strategy else None,
        )
        
        return caption
