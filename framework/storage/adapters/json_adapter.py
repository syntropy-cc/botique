"""
JSON storage adapter.

Backend para armazenar objetos complexos em arquivos JSON.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import StorageBackend


class JSONStorageBackend(StorageBackend):
    """
    Backend JSON para objetos complexos.
    
    Armazena:
    - CoherenceBrief
    - PostIdea
    - NarrativeStructure
    - Outros objetos serializáveis em JSON
    """
    
    def __init__(self, base_path: Path):
        """
        Inicializa adapter JSON.
        
        Args:
            base_path: Diretório base para armazenar arquivos JSON
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        """Obtém caminho do arquivo para uma chave."""
        # Sanitiza chave para nome de arquivo seguro
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_key}.json"
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Armazena valor em arquivo JSON."""
        file_path = self._get_file_path(key)
        
        # Se value já for dict, usa diretamente; senão, tenta serializar
        if isinstance(value, dict):
            data = value.copy()
        else:
            # Tenta converter para dict se tiver método to_dict
            if hasattr(value, "to_dict"):
                data = value.to_dict()
            else:
                # Serializa como JSON string
                data = {"_value": value}
        
        # Adiciona metadata se fornecido
        if metadata:
            data["_metadata"] = metadata
        
        # Adiciona timestamp
        from datetime import datetime
        data["_stored_at"] = datetime.now().isoformat()
        
        # Escreve arquivo
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return key
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Recupera valor de arquivo JSON."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Remove campos internos
            if "_value" in data:
                return data["_value"]
            
            # Remove metadata e timestamp
            data.pop("_metadata", None)
            data.pop("_stored_at", None)
            
            return data
        except (json.JSONDecodeError, IOError):
            return None
    
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """Consulta valores com filtros."""
        results = []
        
        # Busca em todos os arquivos JSON
        for json_file in self.base_path.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Remove campos internos para comparação
                check_data = {k: v for k, v in data.items() 
                            if not k.startswith("_")}
                
                # Verifica se corresponde aos critérios
                matches = True
                for query_key, query_value in query.items():
                    if query_key not in check_data or check_data[query_key] != query_value:
                        matches = False
                        break
                
                if matches:
                    # Remove campos internos do resultado
                    result = {k: v for k, v in data.items() 
                            if not k.startswith("_")}
                    results.append(result)
            except (json.JSONDecodeError, IOError):
                continue
        
        return results
    
    def delete(self, key: str) -> bool:
        """Remove arquivo JSON."""
        file_path = self._get_file_path(key)
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista todas as chaves (nomes de arquivos sem extensão)."""
        keys = []
        
        for json_file in self.base_path.glob("*.json"):
            key = json_file.stem.replace("_", "/")  # Restaura separadores
            if prefix is None or key.startswith(prefix):
                keys.append(key)
        
        return keys
