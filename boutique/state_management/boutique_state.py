"""
Boutique State

Estado específico do boutique que estende UniversalState.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from framework.core.universal_state import UniversalState
from framework.storage.manager import StorageManager

from .storage.brand_storage import BrandStorage
from .storage.coherence_brief_storage import CoherenceBriefStorage


class BoutiqueState(UniversalState):
    """
    Estado específico do boutique.
    
    Estende UniversalState com:
    - Métodos específicos para briefs
    - Integração com storages específicos
    - Estratégias específicas de projeção
    """
    
    def __init__(self, storage_base_path: Optional[Path] = None):
        """
        Inicializa estado do boutique.
        
        Args:
            storage_base_path: Diretório base para storages (usa padrão se None)
        """
        super().__init__()
        
        # Cria storages específicos
        if storage_base_path is None:
            # Default: output/storage
            root_dir = Path(__file__).resolve().parents[3]
            storage_base_path = root_dir / "output" / "storage"
        
        self.brief_storage = CoherenceBriefStorage(storage_base_path)
        self.brand_storage = BrandStorage()
        
        # Integra storages específicos com StorageManager
        # Atualiza routing do storage manager para usar storages específicos
        self.storage.json_backend = self.brief_storage
        self.storage.memory_backend = self.brand_storage
    
    def store_brief(self, brief: Any) -> str:
        """
        Armazena brief usando JSON backend.
        
        Args:
            brief: CoherenceBrief object
            
        Returns:
            post_id do brief armazenado
        """
        return self.brief_storage.store_brief(brief)
    
    def get_brief(self, post_id: str) -> Optional[Any]:
        """
        Recupera brief usando JSON backend.
        
        Args:
            post_id: Identificador do post
            
        Returns:
            CoherenceBrief object ou None
        """
        return self.brief_storage.retrieve_brief(post_id)
    
    def get_all_briefs(self, article_slug: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém todos os briefs, opcionalmente filtrados por article_slug.
        
        Args:
            article_slug: Slug do artigo para filtrar
            
        Returns:
            Dict mapeando post_id para CoherenceBrief
        """
        if article_slug:
            # Query briefs por article_slug
            briefs = self.brief_storage.query({"article_slug": article_slug})
        else:
            # Lista todas as chaves e recupera briefs
            keys = self.brief_storage.list_keys()
            briefs = {}
            for key in keys:
                brief = self.get_brief(key)
                if brief:
                    briefs[key] = brief
            return briefs
        
        # Converte lista para dict
        result = {}
        for brief in briefs:
            if hasattr(brief, 'post_id'):
                result[brief.post_id] = brief
            elif isinstance(brief, dict) and 'post_id' in brief:
                result[brief['post_id']] = brief
        
        return result
    
    def get_brand(self) -> Any:
        """
        Recupera brand usando memory backend.
        
        Returns:
            BrandLibrary class ou instância
        """
        return self.brand_storage.get_brand_library()
    
    def get_brand_library(self) -> Any:
        """Alias para get_brand()"""
        return self.get_brand()
