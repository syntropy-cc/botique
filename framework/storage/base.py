"""
Interface base para backends de armazenamento.

Define a interface StorageBackend que todos os adaptadores devem implementar.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """
    Interface base para backends de armazenamento.
    
    Todos os adaptadores (SQLite, JSON, Memory, etc.) devem implementar
    esta interface para garantir compatibilidade com o StorageManager.
    """
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Armazena valor com chave.
        
        Args:
            key: Chave única para identificar o valor
            value: Valor a ser armazenado (pode ser qualquer tipo)
            metadata: Metadados opcionais (timestamps, tags, etc.)
            
        Returns:
            ID ou chave do valor armazenado
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Recupera valor por chave.
        
        Args:
            key: Chave do valor a recuperar
            
        Returns:
            Valor recuperado ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """
        Consulta valores com filtros.
        
        Args:
            query: Dicionário com critérios de busca
                  Exemplo: {"type": "brief", "post_id": "post_001"}
                  
        Returns:
            Lista de valores que correspondem aos critérios
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Remove valor por chave.
        
        Args:
            key: Chave do valor a remover
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        Lista todas as chaves disponíveis.
        
        Args:
            prefix: Prefixo opcional para filtrar chaves
            
        Returns:
            Lista de chaves
        """
        pass
