"""
Testes para UniversalState.
"""

import pytest
from framework.core.universal_state import UniversalState
from framework.storage.manager import StorageManager


def test_universal_state_initialization():
    """Testa inicialização do UniversalState."""
    state = UniversalState()
    assert state.article_slug is None
    assert state.current_trace_id is None
    assert isinstance(state.storage, StorageManager)


def test_universal_state_store_retrieve():
    """Testa armazenamento e recuperação de entidades."""
    state = UniversalState()
    
    # Armazenar
    key = state.store("test_entity", "test_key", {"data": "test_value"})
    assert key == "test_key"
    
    # Recuperar
    value = state.retrieve("test_entity", "test_key")
    assert value is not None
    assert value.get("data") == "test_value"


def test_universal_state_clear_context():
    """Testa limpeza de contexto."""
    state = UniversalState()
    state.article_slug = "test_article"
    state.current_trace_id = "test_trace"
    
    state.clear_context()
    
    assert state.article_slug is None
    assert state.current_trace_id is None
