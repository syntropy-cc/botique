"""
Gerenciador unificado de storage.

Organiza diferentes backends e roteia operações para o adaptador apropriado.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .adapters.hybrid_adapter import HybridStorageBackend
from .adapters.json_adapter import JSONStorageBackend
from .adapters.memory_adapter import MemoryStorageBackend
from .adapters.sqlite_adapter import SQLiteStorageBackend
from .base import StorageBackend
from .registry import StorageRegistry


class StorageManager:
    """
    Gerenciador unificado de storage.
    
    Organiza diferentes backends e roteia operações:
    - SQLite: histórico, eventos, prompts
    - JSON: briefs, ideias, estruturas narrativas
    - Memory: brand, palettes, typography (classes)
    """
    
    def __init__(
        self,
        sqlite_path: Optional[Path] = None,
        json_base_path: Optional[Path] = None,
        routing: Optional[Dict[str, str]] = None
    ):
        """
        Inicializa gerenciador de storage.
        
        Args:
            sqlite_path: Caminho para banco SQLite (usa padrão se None)
            json_base_path: Diretório base para arquivos JSON (usa padrão se None)
            routing: Mapeamento customizado de tipos para backends
        """
        # Cria backends
        self.sqlite_backend = SQLiteStorageBackend(sqlite_path)
        
        if json_base_path is None:
            # Default: output/storage/json
            root_dir = Path(__file__).resolve().parents[3]
            json_base_path = root_dir / "output" / "storage" / "json"
        
        self.json_backend = JSONStorageBackend(json_base_path)
        self.memory_backend = MemoryStorageBackend()
        
        # Routing padrão
        default_routing = {
            "trace": "sqlite",
            "event": "sqlite",
            "prompt": "sqlite",
            "brief": "json",
            "idea": "json",
            "narrative": "json",
            "brand": "memory",
            "palette": "memory",
            "typography": "memory",
        }
        
        # Merge com routing customizado
        self.routing = {**default_routing, **(routing or {})}
        
        # Cria backend híbrido
        self.hybrid_backend = HybridStorageBackend(
            adapters={
                "sqlite": self.sqlite_backend,
                "json": self.json_backend,
                "memory": self.memory_backend,
            },
            routing=self.routing
        )
    
    def store(self, entity_type: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Armazena entidade usando backend apropriado.
        
        Args:
            entity_type: Tipo de entidade (ex: "brief", "trace")
            key: Chave única
            value: Valor a armazenar
            metadata: Metadados opcionais
            
        Returns:
            Chave do valor armazenado
        """
        if metadata is None:
            metadata = {}
        metadata["entity_type"] = entity_type
        
        return self.hybrid_backend.store(key, value, metadata)
    
    def retrieve(self, entity_type: str, key: str) -> Optional[Any]:
        """
        Recupera entidade usando backend apropriado.
        
        Args:
            entity_type: Tipo de entidade
            key: Chave do valor
            
        Returns:
            Valor recuperado ou None
        """
        # Usa routing para determinar backend
        backend_name = self.routing.get(entity_type)
        if backend_name == "sqlite":
            return self.sqlite_backend.retrieve(key)
        elif backend_name == "json":
            return self.json_backend.retrieve(key)
        elif backend_name == "memory":
            return self.memory_backend.retrieve(key)
        else:
            # Fallback: tenta todos
            for backend in [self.sqlite_backend, self.json_backend, self.memory_backend]:
                result = backend.retrieve(key)
                if result is not None:
                    return result
            return None
    
    def query(self, entity_type: str, query: Dict[str, Any]) -> List[Any]:
        """
        Consulta entidades usando backend apropriado.
        
        Args:
            entity_type: Tipo de entidade
            query: Critérios de busca
            
        Returns:
            Lista de valores que correspondem aos critérios
        """
        query["entity_type"] = entity_type
        return self.hybrid_backend.query(query)
    
    def delete(self, entity_type: str, key: str) -> bool:
        """
        Remove entidade usando backend apropriado.
        
        Args:
            entity_type: Tipo de entidade
            key: Chave do valor
            
        Returns:
            True se removido com sucesso
        """
        backend_name = self.routing.get(entity_type)
        if backend_name == "sqlite":
            return self.sqlite_backend.delete(key)
        elif backend_name == "json":
            return self.json_backend.delete(key)
        elif backend_name == "memory":
            return self.memory_backend.delete(key)
        else:
            # Tenta todos
            for backend in [self.sqlite_backend, self.json_backend, self.memory_backend]:
                if backend.delete(key):
                    return True
            return False
    
    def list_keys(self, entity_type: Optional[str] = None, prefix: Optional[str] = None) -> List[str]:
        """
        Lista chaves de entidades.
        
        Args:
            entity_type: Tipo de entidade (opcional)
            prefix: Prefixo para filtrar (opcional)
            
        Returns:
            Lista de chaves
        """
        if entity_type:
            backend_name = self.routing.get(entity_type)
            if backend_name == "sqlite":
                return self.sqlite_backend.list_keys(prefix)
            elif backend_name == "json":
                return self.json_backend.list_keys(prefix)
            elif backend_name == "memory":
                return self.memory_backend.list_keys(prefix)
        
        # Lista de todos os backends
        all_keys = []
        for backend in [self.sqlite_backend, self.json_backend, self.memory_backend]:
            all_keys.extend(backend.list_keys(prefix))
        
        return list(set(all_keys))  # Remove duplicatas
