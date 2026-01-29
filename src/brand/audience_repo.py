"""
Audience Repository

Database-backed repository for audience profile CRUD operations.

Implements Document Store model per ADR-001: stores complete profiles
as JSON documents in SQLite database.

Location: src/brand/audience_repo.py
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Singleton instance
_repository_instance: Optional["AudienceRepository"] = None


def get_repository(db_path: Optional[Path] = None) -> "AudienceRepository":
    """
    Get singleton repository instance.
    
    Args:
        db_path: Optional path to database file
    
    Returns:
        AudienceRepository instance
    """
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = AudienceRepository(db_path)
    return _repository_instance


def init_audience_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize audience database schema.
    
    Creates tables and indexes if they don't exist.
    Idempotent: safe to call multiple times.
    
    Args:
        db_path: Path to SQLite database file. If None, uses default location.
    """
    if db_path is None:
        db_path = _get_default_db_path()
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    repo = AudienceRepository(db_path)
    repo._init_schema()


class AudienceRepository:
    """
    Repository for audience profile data access.
    
    Implements Document Store model: stores complete profiles as JSON
    documents in SQLite database. Optimized for primary access pattern:
    get complete profile by persona_type.
    
    Per ADR-001: Single source of truth in JSON, no data duplication.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize repository.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = _get_default_db_path()
        
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self) -> None:
        """Initialize database schema (idempotent)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_profiles (
                    id TEXT PRIMARY KEY,
                    persona_type TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    profile_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Create indexes for primary access pattern
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_type 
                ON audience_profiles(persona_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audience_profiles_active 
                ON audience_profiles(is_active)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_active 
                ON audience_profiles(persona_type, is_active)
            """)
            
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_profile(self, persona_type: str) -> Optional[Dict]:
        """
        Get complete profile by persona type.
        
        Args:
            persona_type: Persona type identifier (e.g., "c_level", "founder", "developer")
        
        Returns:
            Complete profile dict with all attributes, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data, id, name, description, created_at, updated_at, version, is_active
                FROM audience_profiles
                WHERE persona_type = ? AND is_active = 1
            """, (persona_type,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            # Parse JSON profile data
            profile_data = json.loads(row["profile_data"])
            
            # Add metadata
            profile_data["_metadata"] = {
                "id": row["id"],
                "persona_type": persona_type,
                "name": row["name"],
                "description": row["description"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "version": row["version"],
                "is_active": bool(row["is_active"]),
            }
            
            return profile_data
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict]:
        """
        Get profile by ID.
        
        Args:
            profile_id: Profile UUID
        
        Returns:
            Complete profile dict, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data, persona_type, name, description, created_at, updated_at, version, is_active
                FROM audience_profiles
                WHERE id = ? AND is_active = 1
            """, (profile_id,))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            profile_data = json.loads(row["profile_data"])
            profile_data["_metadata"] = {
                "id": profile_id,
                "persona_type": row["persona_type"],
                "name": row["name"],
                "description": row["description"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "version": row["version"],
                "is_active": bool(row["is_active"]),
            }
            
            return profile_data
    
    def create_profile(
        self,
        persona_type: str,
        name: str,
        profile_data: Dict,
        description: Optional[str] = None,
    ) -> str:
        """
        Create new audience profile.
        
        Args:
            persona_type: Unique persona type identifier
            name: Profile name
            profile_data: Complete profile data as dict (will be stored as JSON)
            description: Optional description
        
        Returns:
            Profile ID (UUID)
        
        Raises:
            sqlite3.IntegrityError: If persona_type already exists
        """
        profile_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        # Ensure profile_data includes persona_type
        profile_data = profile_data.copy()
        profile_data["persona_type"] = persona_type
        profile_data["name"] = name
        if description:
            profile_data["description"] = description
        
        profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audience_profiles 
                (id, persona_type, name, description, profile_data, created_at, updated_at, version, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
            """, (
                profile_id,
                persona_type,
                name,
                description,
                profile_json,
                now,
                now,
            ))
            conn.commit()
        
        return profile_id
    
    def update_profile(self, persona_type: str, profile_data: Dict) -> bool:
        """
        Update existing profile.
        
        Args:
            persona_type: Persona type identifier
            profile_data: Updated profile data (complete profile as dict)
        
        Returns:
            True if updated, False if profile not found
        """
        now = datetime.utcnow().isoformat() + "Z"
        
        # Ensure profile_data includes persona_type
        profile_data = profile_data.copy()
        profile_data["persona_type"] = persona_type
        
        profile_json = json.dumps(profile_data, ensure_ascii=False, indent=2)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current version
            cursor.execute("""
                SELECT version FROM audience_profiles
                WHERE persona_type = ? AND is_active = 1
            """, (persona_type,))
            row = cursor.fetchone()
            if row is None:
                return False
            
            new_version = row["version"] + 1
            
            # Update profile
            cursor.execute("""
                UPDATE audience_profiles
                SET profile_data = ?,
                    updated_at = ?,
                    version = ?
                WHERE persona_type = ? AND is_active = 1
            """, (profile_json, now, new_version, persona_type))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_profile(self, persona_type: str) -> bool:
        """
        Soft delete profile (sets is_active = 0).
        
        Args:
            persona_type: Persona type identifier
        
        Returns:
            True if deleted, False if profile not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audience_profiles
                SET is_active = 0,
                    updated_at = ?
                WHERE persona_type = ? AND is_active = 1
            """, (datetime.utcnow().isoformat() + "Z", persona_type))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def deactivate_profile(self, persona_type: str) -> bool:
        """
        Deactivate profile without deletion (alias for delete_profile).
        
        Args:
            persona_type: Persona type identifier
        
        Returns:
            True if deactivated, False if profile not found
        """
        return self.delete_profile(persona_type)
    
    def list_profiles(self, active_only: bool = True) -> List[Dict]:
        """
        List all profiles.
        
        Args:
            active_only: If True, only return active profiles
        
        Returns:
            List of profile metadata dicts
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("""
                    SELECT id, persona_type, name, description, created_at, updated_at, version, is_active
                    FROM audience_profiles
                    WHERE is_active = 1
                    ORDER BY persona_type
                """)
            else:
                cursor.execute("""
                    SELECT id, persona_type, name, description, created_at, updated_at, version, is_active
                    FROM audience_profiles
                    ORDER BY persona_type
                """)
            
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "persona_type": row["persona_type"],
                    "name": row["name"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "version": row["version"],
                    "is_active": bool(row["is_active"]),
                }
                for row in rows
            ]
    
    def search_profiles(self, query: str) -> List[Dict]:
        """
        Search profiles by name or description.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching profile metadata dicts
        """
        search_pattern = f"%{query}%"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, persona_type, name, description, created_at, updated_at, version, is_active
                FROM audience_profiles
                WHERE (name LIKE ? OR description LIKE ? OR persona_type LIKE ?)
                  AND is_active = 1
                ORDER BY persona_type
            """, (search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "persona_type": row["persona_type"],
                    "name": row["name"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "version": row["version"],
                    "is_active": bool(row["is_active"]),
                }
                for row in rows
            ]


def _get_default_db_path() -> Path:
    """
    Get default database path.
    
    Uses environment variable BRANDING_DB_PATH if set, otherwise
    defaults to data/branding.db in project root.
    """
    import os
    
    env_path = os.getenv("BRANDING_DB_PATH")
    if env_path:
        return Path(env_path)
    
    # Default to data/branding.db in project root
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "data" / "branding.db"
