"""
Brand Storage

Storage específico para Brand usando Memory backend.
"""

from typing import Any, Optional

from framework.storage.adapters.memory_adapter import MemoryStorageBackend


class BrandStorage(MemoryStorageBackend):
    """
    Storage específico para Brand (classes Python).
    
    Carrega brand da biblioteca e mantém em memória.
    """
    
    def __init__(self):
        """Inicializa storage de brand."""
        super().__init__()
        # Carrega brand da biblioteca
        self._load_brand()
    
    def _load_brand(self):
        """Carrega brand da biblioteca."""
        try:
            from ..models.brand.library import BrandLibrary
            # Armazena BrandLibrary como brand default
            self.store("default", BrandLibrary)
        except ImportError:
            # Se não conseguir importar, cria placeholder
            pass
    
    def get_brand_library(self) -> Any:
        """
        Obtém BrandLibrary.
        
        Returns:
            BrandLibrary class ou instância
        """
        brand = self.retrieve("default")
        if brand:
            return brand
        # Fallback: tenta importar diretamente
        try:
            from ..models.brand.library import BrandLibrary
            return BrandLibrary
        except ImportError:
            return None
