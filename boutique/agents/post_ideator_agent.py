"""
Post Ideator Agent

Agente de geração de ideias de posts.
"""

from framework.core.agent import Agent, VertexType
from boutique.instructions.post_ideator import PostIdeatorInstruction
from boutique.tools.parameter_resolver import ParameterResolverTool


class PostIdeatorAgent(Agent):
    """
    Agente de geração de ideias.
    
    Grafo:
    - Vértice 1: PostIdeatorInstruction
    - Vértice 2: ParameterResolverTool (opcional)
    - Aresta: data (propaga resultado)
    """
    
    def __init__(self):
        instruction = PostIdeatorInstruction()
        tool = ParameterResolverTool()
        
        super().__init__(
            name="post_ideator",
            entry_vertex="instruction",
            vertices={
                "instruction": VertexType.INSTRUCTION,
                "tool": VertexType.TOOL,
            },
            edges={
                "instruction": ["tool"],  # Opcional: pode ir direto para saída
            },
        )
        
        # Armazena instruction e tool para uso em execute
        self._instruction = instruction
        self._tool = tool
    
    def execute(
        self,
        input_data: dict,
        state,
        state_strategy=None,
    ) -> dict:
        """
        Executa agente: gera ideias e opcionalmente resolve parâmetros.
        
        Args:
            input_data: Deve conter "article" e "config"
            state: UniversalState
            state_strategy: Opcional state strategy
            
        Returns:
            Dict com "article_summary" e "ideas"
        """
        # Executa instruction
        from framework.llm.http_client import HttpLLMClient
        llm_client = input_data.get("llm_client")
        if not llm_client:
            llm_client = HttpLLMClient()
        
        # Prepara input para instruction
        instruction_input = {
            "article": input_data.get("article", ""),
            "config": input_data.get("config"),
        }
        
        # Executa instruction
        ideas_result = self._instruction.execute(
            input_data=instruction_input,
            llm_client=llm_client,
            memory_context=state_strategy.project(state) if state_strategy else None,
        )
        
        # Opcionalmente resolve parâmetros para cada idea
        if input_data.get("resolve_parameters", False):
            ideas = ideas_result.get("ideas", [])
            for idea in ideas:
                post_id = f"post_{input_data.get('article_slug', 'unknown')}_{idea.get('id', 'unknown')}"
                params = self._tool.execute({
                    "idea": idea,
                    "article_summary": ideas_result.get("article_summary", {}),
                    "post_id": post_id,
                })
                idea["post_config"] = params
        
        return ideas_result
