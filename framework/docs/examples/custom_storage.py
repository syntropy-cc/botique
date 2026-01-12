"""
Exemplo de criação de backend de storage customizado.

Este exemplo demonstra como criar um backend de storage personalizado
e usá-lo com o StorageManager.
"""

from framework.storage.base import StorageBackend
from framework.storage.manager import StorageManager
from framework.storage.registry import StorageRegistry
from typing import Any, Dict, List, Optional


class InMemoryStorageBackend(StorageBackend):
    """Backend de storage simples em memória."""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Armazena valor."""
        self._storage[key] = {"value": value, "metadata": metadata or {}}
        return key
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Recupera valor."""
        if key in self._storage:
            return self._storage[key]["value"]
        return None
    
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """Consulta valores (implementação simples)."""
        results = []
        for key, data in self._storage.items():
            # Match simples por metadata
            if "metadata" in query:
                if data["metadata"] == query["metadata"]:
                    results.append(data["value"])
            else:
                results.append(data["value"])
        return results
    
    def delete(self, key: str) -> bool:
        """Remove valor."""
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista chaves."""
        keys = list(self._storage.keys())
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return keys


def main():
    # Registrar backend customizado
    StorageRegistry.register_adapter("inmemory", InMemoryStorageBackend)
    
    # Criar storage manager com backend customizado
    # (Nota: StorageManager atual usa backends específicos,
    # mas você pode criar um customizado)
    backend = InMemoryStorageBackend()
    
    # Usar backend diretamente
    backend.store("test_key", {"data": "test_value"})
    value = backend.retrieve("test_key")
    print(f"Retrieved: {value}")
    
    # Query
    results = backend.query({})
    print(f"All values: {results}")


if __name__ == "__main__":
    main()
