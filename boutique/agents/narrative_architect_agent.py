"""
Narrative Architect Agent

Agente de arquitetura narrativa.
"""

from framework.core.agent import Agent, VertexType
from boutique.instructions.narrative_architect import NarrativeArchitectInstruction


class NarrativeArchitectAgent(Agent):
    """
    Agente de arquitetura narrativa.
    
    Grafo:
    - Vértice 1: NarrativeArchitectInstruction
    """
    
    def __init__(self):
        instruction = NarrativeArchitectInstruction()
        
        super().__init__(
            name="narrative_architect",
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
        Executa agente: gera estrutura narrativa.
        
        Args:
            input_data: Deve conter "brief" e "article_text"
            state: UniversalState
            state_strategy: Opcional state strategy
            
        Returns:
            Dict com estrutura narrativa
        """
        from framework.llm.http_client import HttpLLMClient
        llm_client = input_data.get("llm_client")
        if not llm_client:
            llm_client = HttpLLMClient()
        
        instruction_input = {
            "brief": input_data.get("brief"),
            "article_text": input_data.get("article_text", ""),
        }
        
        structure = self._instruction.execute(
            input_data=instruction_input,
            llm_client=llm_client,
            memory_context=state_strategy.project(state) if state_strategy else None,
        )
        
        return structure
