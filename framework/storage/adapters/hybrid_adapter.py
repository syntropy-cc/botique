"""
Hybrid storage adapter.

Backend híbrido que roteia para múltiplos adaptadores baseado em tipo ou prefixo.
"""

from typing import Any, Dict, List, Optional

from ..base import StorageBackend


class HybridStorageBackend(StorageBackend):
    """
    Backend híbrido que usa múltiplos adaptadores.
    
    Roteia operações para o adaptador apropriado baseado em:
    - Tipo de entidade
    - Prefixo da chave
    - Configuração customizada
    """
    
    def __init__(self, adapters: Dict[str, StorageBackend], routing: Optional[Dict[str, str]] = None):
        """
        Inicializa adapter híbrido.
        
        Args:
            adapters: Dicionário mapeando nomes de adaptadores para instâncias
            routing: Dicionário mapeando tipos de entidade para nomes de adaptadores
                    Exemplo: {"brief": "json", "trace": "sqlite", "brand": "memory"}
        """
        self.adapters = adapters
        self.routing = routing or {}
    
    def _get_adapter(self, entity_type: Optional[str] = None, key: Optional[str] = None) -> StorageBackend:
        """
        Determina qual adaptador usar baseado em tipo ou chave.
        
        Args:
            entity_type: Tipo de entidade (ex: "brief", "trace")
            key: Chave completa (pode conter prefixo)
            
        Returns:
            Adaptador apropriado
        """
        # Tenta determinar por tipo primeiro
        if entity_type and entity_type in self.routing:
            adapter_name = self.routing[entity_type]
            if adapter_name in self.adapters:
                return self.adapters[adapter_name]
        
        # Tenta determinar por prefixo da chave
        if key:
            for prefix, adapter_name in self.routing.items():
                if key.startswith(prefix):
                    if adapter_name in self.adapters:
                        return self.adapters[adapter_name]
        
        # Default: usa primeiro adaptador disponível
        if self.adapters:
            return list(self.adapters.values())[0]
        
        raise ValueError("No adapters available")
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Armazena valor usando adaptador apropriado."""
        # Tenta extrair tipo de metadata ou key
        entity_type = None
        if metadata and "entity_type" in metadata:
            entity_type = metadata["entity_type"]
        
        adapter = self._get_adapter(entity_type=entity_type, key=key)
        return adapter.store(key, value, metadata)
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Recupera valor usando adaptador apropriado."""
        adapter = self._get_adapter(key=key)
        return adapter.retrieve(key)
    
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """Consulta valores em todos os adaptadores relevantes."""
        entity_type = query.get("entity_type")
        
        if entity_type and entity_type in self.routing:
            # Query apenas no adaptador específico
            adapter_name = self.routing[entity_type]
            if adapter_name in self.adapters:
                return self.adapters[adapter_name].query(query)
        
        # Query em todos os adaptadores e combina resultados
        all_results = []
        for adapter in self.adapters.values():
            try:
                results = adapter.query(query)
                all_results.extend(results)
            except Exception:
                # Ignora erros de adaptadores que não suportam a query
                continue
        
        return all_results
    
    def delete(self, key: str) -> bool:
        """Remove valor usando adaptador apropriado."""
        adapter = self._get_adapter(key=key)
        return adapter.delete(key)
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista todas as chaves de todos os adaptadores."""
        all_keys = []
        for adapter in self.adapters.values():
            try:
                keys = adapter.list_keys(prefix)
                all_keys.extend(keys)
            except Exception:
                continue
        
        return all_keys
