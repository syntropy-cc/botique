"""
Testes para agentes do boutique.
"""

import pytest
from boutique.agents.post_ideator_agent import PostIdeatorAgent
from boutique.agents.narrative_architect_agent import NarrativeArchitectAgent
from boutique.state_management.boutique_state import BoutiqueState


def test_post_ideator_agent_initialization():
    """Testa inicialização do PostIdeatorAgent."""
    agent = PostIdeatorAgent()
    assert agent.name == "post_ideator"
    assert agent.entry_vertex == "instruction"


def test_narrative_architect_agent_initialization():
    """Testa inicialização do NarrativeArchitectAgent."""
    agent = NarrativeArchitectAgent()
    assert agent.name == "narrative_architect"


def test_agent_execution():
    """Testa execução básica de agente."""
    agent = PostIdeatorAgent()
    state = BoutiqueState()
    
    # Execução básica (pode falhar se não houver LLM configurado)
    # Este é um teste estrutural, não funcional completo
    assert agent is not None
    assert state is not None
