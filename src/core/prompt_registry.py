"""
Prompt Registry module

Manages prompt versioning and registration in the database.
Ensures prompts are treated as first-class, versioned artifacts.

Versioning is automatic: each time a prompt_key is registered with a different
template, a new version (v1, v2, v3...) is created automatically based on timestamp.

Location: src/core/prompt_registry.py
"""

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .llm_log_db import db_connection, get_db_path


def _compute_template_hash(template: str) -> str:
    """
    Compute SHA256 hash of template for comparison.
    
    Args:
        template: Prompt template string
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(template.encode('utf-8')).hexdigest()


def find_existing_prompt(
    prompt_key: str,
    template: str,
    db_path: Optional[Path] = None,
) -> Optional[tuple[str, str]]:
    """
    Check if a prompt with the same key and template already exists.
    
    This function performs a two-step check:
    1. First checks by hash for fast comparison
    2. Then verifies exact template match to avoid hash collisions
    
    Args:
        prompt_key: Logical identifier of the prompt
        template: Raw prompt template
        db_path: Path to SQLite database (uses default if None)
        
    Returns:
        Tuple of (prompt_id, version) if found, None otherwise
    """
    if db_path is None:
        db_path = get_db_path()
    
    template_hash = _compute_template_hash(template)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # First check by hash (fast, indexed lookup)
        cursor.execute("""
            SELECT id, version, template FROM prompts 
            WHERE prompt_key = ? AND template_hash = ?
        """, (prompt_key, template_hash))
        candidates = cursor.fetchall()
        
        # Verify exact template match (handles hash collisions)
        for candidate in candidates:
            if candidate["template"] == template:
                return candidate["id"], candidate["version"]
        
        return None


def register_prompt(
    prompt_key: str,
    template: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> tuple[str, str]:
    """
    Register a prompt with automatic versioning and duplicate prevention.
    
    The system automatically creates versions (v1, v2, v3...) based on timestamp.
    
    **Duplicate Prevention:**
    - First checks if an identical template already exists for this prompt_key
    - Uses hash-based comparison for efficiency, then verifies exact match
    - If template is identical, returns existing prompt_id (no duplicate created)
    - If template is different, creates a new version automatically
    
    This function is idempotent: safe to call multiple times with the same
    template. It ensures no duplicate prompt versions are created for identical templates.
    
    Args:
        prompt_key: Logical identifier of the prompt (e.g., "summarize", "classify_intent")
        template: Raw prompt template (before variable injection)
        description: Optional explanation of intent or changes
        metadata: Optional JSON metadata (author, experiment name, git commit, etc.)
        db_path: Path to SQLite database (uses default if None)
        
    Returns:
        Tuple of (prompt_id, version) where:
        - prompt_id: UUID string for the registered prompt version
        - version: Version string (e.g., "v1", "v2", "v3")
        
    Example:
        prompt_id, version = register_prompt(
            prompt_key="post_ideator",
            template="Analyze the article: {article}",
            description="Post ideator prompt"
        )
        # First call: returns (uuid, "v1")
        # Second call with same template: returns (same_uuid, "v1") - no duplicate
        # Third call with different template: returns (new_uuid, "v2")
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Normalize template (remove trailing whitespace, normalize line endings)
    template = template.rstrip()
    
    # Check if identical template already exists
    existing = find_existing_prompt(prompt_key, template, db_path)
    if existing:
        # Identical template exists, return existing prompt_id (no duplicate)
        return existing
    
    template_hash = _compute_template_hash(template)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Count existing versions to determine next version number
        cursor.execute("""
            SELECT COUNT(*) as count FROM prompts 
            WHERE prompt_key = ?
        """, (prompt_key,))
        count_row = cursor.fetchone()
        version_number = (count_row["count"] or 0) + 1
        version = f"v{version_number}"
        
        # Create new prompt version
        prompt_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        # Store template hash in metadata for easier comparison
        if metadata is None:
            metadata = {}
        metadata["template_hash"] = template_hash
        metadata_json = json.dumps(metadata)
        
        cursor.execute("""
            INSERT INTO prompts 
            (id, prompt_key, version, template, template_hash, description, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prompt_id,
            prompt_key,
            version,
            template,
            template_hash,
            description,
            now,
            metadata_json,
        ))
        conn.commit()
    
    return prompt_id, version


def get_prompt(
    prompt_id: str,
    db_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a prompt by ID.
    
    Args:
        prompt_id: Prompt ID (UUID string)
        db_path: Path to SQLite database (uses default if None)
        
    Returns:
        Dictionary with prompt data, or None if not found
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prompt_key, version, template, description, 
                   created_at, metadata_json
            FROM prompts 
            WHERE id = ?
        """, (prompt_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        result = {
            "id": row["id"],
            "prompt_key": row["prompt_key"],
            "version": row["version"],
            "template": row["template"],
            "description": row["description"],
            "created_at": row["created_at"],
        }
        
        if row["metadata_json"]:
            try:
                result["metadata"] = json.loads(row["metadata_json"])
            except json.JSONDecodeError:
                result["metadata"] = None
        else:
            result["metadata"] = None
        
        return result


def list_prompt_versions(
    prompt_key: str,
    db_path: Optional[Path] = None,
) -> list[Dict[str, Any]]:
    """
    List all versions of a prompt key.
    
    Args:
        prompt_key: Logical identifier of the prompt
        db_path: Path to SQLite database (uses default if None)
        
    Returns:
        List of dictionaries with prompt version data, sorted by created_at
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, prompt_key, version, template, description, 
                   created_at, metadata_json
            FROM prompts 
            WHERE prompt_key = ?
            ORDER BY created_at ASC
        """, (prompt_key,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = {
                "id": row["id"],
                "prompt_key": row["prompt_key"],
                "version": row["version"],
                "template": row["template"],
                "description": row["description"],
                "created_at": row["created_at"],
            }
            
            if row["metadata_json"]:
                try:
                    result["metadata"] = json.loads(row["metadata_json"])
                except json.JSONDecodeError:
                    result["metadata"] = None
            else:
                result["metadata"] = None
            
            results.append(result)
        
        return results

