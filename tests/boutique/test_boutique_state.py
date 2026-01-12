"""
Testes para BoutiqueState.
"""

import pytest
from boutique.state_management.boutique_state import BoutiqueState
from boutique.state_management.models.coherence_brief import CoherenceBrief


def test_boutique_state_initialization():
    """Testa inicialização do BoutiqueState."""
    state = BoutiqueState()
    assert state.brief_storage is not None
    assert state.brand_storage is not None


def test_boutique_state_store_brief():
    """Testa armazenamento de brief."""
    state = BoutiqueState()
    
    # Criar brief mínimo
    brief = CoherenceBrief(
        post_id="test_post",
        idea_id="test_idea",
        platform="instagram",
        format="carousel",
        tone="professional",
    )
    
    # Armazenar
    post_id = state.store_brief(brief)
    assert post_id == "test_post"
    
    # Recuperar
    retrieved_brief = state.get_brief("test_post")
    assert retrieved_brief is not None
    assert retrieved_brief.post_id == "test_post"
