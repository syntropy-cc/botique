"""
Registry de backends de armazenamento disponíveis.

Mantém registro de todos os adaptadores disponíveis e facilita sua criação.
"""

from pathlib import Path
from typing import Dict, Optional, Type

from .adapters.hybrid_adapter import HybridStorageBackend
from .adapters.json_adapter import JSONStorageBackend
from .adapters.memory_adapter import MemoryStorageBackend
from .adapters.sqlite_adapter import SQLiteStorageBackend
from .base import StorageBackend


class StorageRegistry:
    """
    Registry de backends de armazenamento.
    
    Facilita criação e gerenciamento de adaptadores.
    """
    
    _adapters: Dict[str, Type[StorageBackend]] = {
        "sqlite": SQLiteStorageBackend,
        "json": JSONStorageBackend,
        "memory": MemoryStorageBackend,
        "hybrid": HybridStorageBackend,
    }
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[StorageBackend]):
        """
        Registra um novo adaptador.
        
        Args:
            name: Nome do adaptador
            adapter_class: Classe do adaptador
        """
        cls._adapters[name] = adapter_class
    
    @classmethod
    def get_adapter_class(cls, name: str) -> Optional[Type[StorageBackend]]:
        """
        Obtém classe de adaptador por nome.
        
        Args:
            name: Nome do adaptador
            
        Returns:
            Classe do adaptador ou None se não encontrado
        """
        return cls._adapters.get(name)
    
    @classmethod
    def list_adapters(cls) -> list[str]:
        """
        Lista todos os adaptadores registrados.
        
        Returns:
            Lista de nomes de adaptadores
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def create_adapter(cls, name: str, **kwargs) -> StorageBackend:
        """
        Cria instância de adaptador.
        
        Args:
            name: Nome do adaptador
            **kwargs: Argumentos para construtor do adaptador
            
        Returns:
            Instância do adaptador
            
        Raises:
            ValueError: Se adaptador não encontrado
        """
        adapter_class = cls.get_adapter_class(name)
        if adapter_class is None:
            raise ValueError(f"Adapter '{name}' not found. Available: {cls.list_adapters()}")
        
        return adapter_class(**kwargs)
