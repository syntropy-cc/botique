"""
Memory storage adapter.

Backend in-memory para classes Python (não serializáveis em JSON).
"""

from typing import Any, Dict, List, Optional

from ..base import StorageBackend


class MemoryStorageBackend(StorageBackend):
    """
    Backend in-memory para classes Python.
    
    Armazena:
    - Brand
    - ColorPalette
    - TypographyConfig
    - Outras classes Python que não são facilmente serializáveis
    """
    
    def __init__(self):
        """Inicializa adapter em memória."""
        self._storage: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Armazena valor em memória."""
        self._storage[key] = value
        
        if metadata:
            self._metadata[key] = metadata.copy()
        elif key not in self._metadata:
            self._metadata[key] = {}
        
        # Adiciona timestamp
        from datetime import datetime
        self._metadata[key]["_stored_at"] = datetime.now().isoformat()
        
        return key
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Recupera valor da memória."""
        return self._storage.get(key)
    
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """Consulta valores com filtros."""
        results = []
        
        for key, value in self._storage.items():
            # Verifica metadata
            metadata = self._metadata.get(key, {})
            
            matches = True
            for query_key, query_value in query.items():
                # Busca em metadata primeiro
                if query_key in metadata and metadata[query_key] != query_value:
                    matches = False
                    break
                # Se value for objeto, tenta buscar atributo
                elif hasattr(value, query_key):
                    if getattr(value, query_key) != query_value:
                        matches = False
                        break
                else:
                    matches = False
                    break
            
            if matches:
                results.append(value)
        
        return results
    
    def delete(self, key: str) -> bool:
        """Remove valor da memória."""
        if key in self._storage:
            del self._storage[key]
            if key in self._metadata:
                del self._metadata[key]
            return True
        return False
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista todas as chaves."""
        keys = list(self._storage.keys())
        
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        
        return keys
