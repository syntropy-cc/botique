"""
SQLite storage adapter.

Backend para armazenar histórico, eventos e prompts em SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import StorageBackend


class SQLiteStorageBackend(StorageBackend):
    """
    Backend SQLite para histórico e eventos.
    
    Armazena:
    - Traces de execução
    - Eventos LLM
    - Versões de prompts
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa adapter SQLite.
        
        Args:
            db_path: Caminho para o banco SQLite (usa padrão se None)
        """
        if db_path is None:
            # Default location
            import os
            env_path = os.getenv("LLM_LOGS_DB_PATH")
            if env_path:
                db_path = Path(env_path)
            else:
                # Default to project root
                db_path = Path(__file__).resolve().parents[4] / "llm_logs.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão SQLite."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_schema(self):
        """Garante que o schema do banco existe."""
        # Schema básico - pode ser estendido conforme necessário
        with self._get_connection() as conn:
            # Tabela genérica para armazenamento key-value
            conn.execute("""
                CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Armazena valor no SQLite."""
        import json
        
        # Serializa valor para JSON
        value_json = json.dumps(value) if not isinstance(value, str) else value
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO storage (key, value, metadata, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value_json, metadata_json))
            conn.commit()
        
        return key
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Recupera valor do SQLite."""
        import json
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM storage WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            value_json = row[0]
            try:
                return json.loads(value_json)
            except json.JSONDecodeError:
                # Se não for JSON válido, retorna como string
                return value_json
    
    def query(self, query: Dict[str, Any]) -> List[Any]:
        """Consulta valores com filtros."""
        import json
        
        # Construção básica de query - pode ser melhorada
        conditions = []
        params = []
        
        # Query por metadata
        if "metadata" in query:
            metadata_json = json.dumps(query["metadata"])
            conditions.append("metadata LIKE ?")
            params.append(f"%{metadata_json}%")
        
        # Query por prefixo de chave
        if "key_prefix" in query:
            conditions.append("key LIKE ?")
            params.append(f"{query['key_prefix']}%")
        
        sql = "SELECT value FROM storage"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                try:
                    results.append(json.loads(row[0]))
                except json.JSONDecodeError:
                    results.append(row[0])
            
            return results
    
    def delete(self, key: str) -> bool:
        """Remove valor do SQLite."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM storage WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista todas as chaves."""
        sql = "SELECT key FROM storage"
        params = []
        
        if prefix:
            sql += " WHERE key LIKE ?"
            params.append(f"{prefix}%")
        
        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [row[0] for row in cursor.fetchall()]
