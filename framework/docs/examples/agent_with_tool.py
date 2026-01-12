"""
Exemplo de agente com instrução e tool.

Este exemplo demonstra como criar um agente que usa uma instrução
seguida de uma tool para processar o resultado.
"""

from framework.core.agent import Agent, VertexType
from framework.core.instruction import Instruction
from framework.core.tool import Tool
from framework.core.universal_state import UniversalState


def process_result(data):
    """Tool function que processa o resultado da instrução."""
    if isinstance(data, dict):
        return {"processed": True, **data}
    return {"processed": True, "data": data}


def main():
    # Criar instrução
    instruction = Instruction(
        prompt_key="analyze",
        prompt_template="Analyze the following: {input}",
        model="deepseek-chat",
    )
    
    # Criar tool
    tool = Tool(
        sig=("input", "output"),
        f=process_result,
        name="result_processor",
        description="Processa resultado da análise",
    )
    
    # Criar agente com instrução e tool
    agent = Agent(
        name="analyze_and_process",
        entry_vertex="instruction",
        vertices={
            "instruction": VertexType.INSTRUCTION,
            "tool": VertexType.TOOL,
        },
        edges=[
            ("instruction", "tool", "data"),
        ],
        vertex_objects={
            "instruction": instruction,
            "tool": tool,
        },
    )
    
    # Criar estado
    state = UniversalState()
    
    # Executar agente
    result = agent.execute(
        input_data={"input": "Sample data"},
        state=state,
    )
    
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
