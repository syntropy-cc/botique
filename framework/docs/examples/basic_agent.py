"""
Exemplo básico de criação e execução de um agente.

Este exemplo demonstra como criar um agente simples com uma instrução.
"""

from framework.core.agent import Agent, VertexType
from framework.core.instruction import Instruction
from framework.core.universal_state import UniversalState


def main():
    # Criar instrução simples
    instruction = Instruction(
        prompt_key="greeting",
        prompt_template="Say hello to {name}",
        model="deepseek-chat",
        temperature=0.7,
    )
    
    # Criar agente com apenas uma instrução
    agent = Agent(
        name="greeting_agent",
        entry_vertex="instruction",
        vertices={
            "instruction": VertexType.INSTRUCTION,
        },
        edges=[],
        vertex_objects={
            "instruction": instruction,
        },
    )
    
    # Criar estado
    state = UniversalState()
    
    # Executar agente
    result = agent.execute(
        input_data={"name": "World"},
        state=state,
    )
    
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
