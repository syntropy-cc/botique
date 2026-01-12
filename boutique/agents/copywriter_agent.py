"""
Copywriter Agent

Agente de copywriting.
"""

from framework.core.agent import Agent, VertexType
from boutique.instructions.copywriter import CopywriterInstruction
from boutique.tools.validators import QualityValidatorTool


class CopywriterAgent(Agent):
    """
    Agente de copywriting.
    
    Grafo:
    - Vértice 1: CopywriterInstruction
    - Vértice 2: QualityValidatorTool (opcional)
    """
    
    def __init__(self):
        instruction = CopywriterInstruction()
        validator = QualityValidatorTool()
        
        super().__init__(
            name="copywriter",
            entry_vertex="instruction",
            vertices={
                "instruction": VertexType.INSTRUCTION,
                "validator": VertexType.TOOL,
            },
            edges={
                "instruction": ["validator"],  # Opcional
            },
        )
        
        self._instruction = instruction
        self._validator = validator
    
    def execute(
        self,
        input_data: dict,
        state,
        state_strategy=None,
    ) -> dict:
        """
        Executa agente: gera copy para slide.
        
        Args:
            input_data: Deve conter "brief", "slide_info", "article_text"
            state: UniversalState
            state_strategy: Opcional state strategy
            
        Returns:
            Dict com conteúdo do slide
        """
        from framework.llm.http_client import HttpLLMClient
        llm_client = input_data.get("llm_client")
        if not llm_client:
            llm_client = HttpLLMClient()
        
        instruction_input = {
            "brief": input_data.get("brief"),
            "slide_info": input_data.get("slide_info", {}),
            "article_text": input_data.get("article_text", ""),
        }
        
        slide_content = self._instruction.execute(
            input_data=instruction_input,
            llm_client=llm_client,
            memory_context=state_strategy.project(state) if state_strategy else None,
        )
        
        # Opcionalmente valida qualidade
        if input_data.get("validate", False):
            validation = self._validator.execute({
                "output_data": {"brief": input_data.get("brief"), "slides": [slide_content]},
                "validation_rules": input_data.get("validation_rules", {}),
            })
            slide_content["validation"] = validation
        
        return slide_content
