"""
Testes para sistema de storage.
"""

import pytest
from pathlib import Path
from framework.storage.manager import StorageManager
from framework.storage.adapters.memory_adapter import MemoryStorageBackend


def test_storage_manager_initialization():
    """Testa inicialização do StorageManager."""
    manager = StorageManager()
    assert manager.sqlite_backend is not None
    assert manager.json_backend is not None
    assert manager.memory_backend is not None


def test_storage_manager_routing():
    """Testa roteamento automático de entidades."""
    manager = StorageManager()
    
    # Trace deve ir para SQLite
    # Brief deve ir para JSON
    # Brand deve ir para Memory
    
    # Teste básico de armazenamento
    manager.store("test_entity", "test_key", {"data": "value"})


def test_memory_backend():
    """Testa MemoryStorageBackend."""
    backend = MemoryStorageBackend()
    
    # Store
    key = backend.store("test_key", {"data": "value"})
    assert key == "test_key"
    
    # Retrieve
    value = backend.retrieve("test_key")
    assert value == {"data": "value"}
    
    # Delete
    deleted = backend.delete("test_key")
    assert deleted is True
    
    # Retrieve after delete
    value = backend.retrieve("test_key")
    assert value is None
