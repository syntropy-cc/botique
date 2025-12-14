"""
Prompt helpers for integrating prompt versioning with LLM calls.

Provides utilities to register prompts from templates and use them in LLM calls.

Location: src/core/prompt_helpers.py
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .prompt_registry import register_prompt
from .llm_log_db import get_db_path


def register_prompt_from_template(
    prompt_key: str,
    template_path: Path,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> tuple[str, str]:
    """
    Register a prompt version from a template file.
    
    Convenience function that reads a template file and registers it as a prompt version.
    Version is automatically assigned (v1, v2, v3...) based on timestamp.
    
    Args:
        prompt_key: Logical identifier of the prompt
        template_path: Path to the template file
        description: Optional description
        metadata: Optional metadata dictionary
        db_path: Path to database (uses default if None)
        
    Returns:
        Tuple of (prompt_id, version) where:
        - prompt_id: UUID string for the registered prompt version
        - version: Version string (e.g., "v1", "v2", "v3")
        
    Example:
        prompt_id, version = register_prompt_from_template(
            prompt_key="post_ideator",
            template_path=Path("prompts/post_ideator.md")
        )
    """
    template = template_path.read_text(encoding="utf-8")
    
    return register_prompt(
        prompt_key=prompt_key,
        template=template,
        description=description,
        metadata=metadata,
        db_path=db_path,
    )


def get_or_register_prompt(
    prompt_key: str,
    template: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> tuple[str, str]:
    """
    Get or register a prompt version.
    
    This is a convenience wrapper around register_prompt that makes the
    idempotent behavior explicit in the function name.
    Version is automatically assigned (v1, v2, v3...) based on timestamp.
    
    Args:
        prompt_key: Logical identifier of the prompt
        template: Raw prompt template
        description: Optional description
        metadata: Optional metadata dictionary
        db_path: Path to database (uses default if None)
        
    Returns:
        Tuple of (prompt_id, version) where:
        - prompt_id: UUID string for the registered prompt version
        - version: Version string (e.g., "v1", "v2", "v3")
    """
    return register_prompt(
        prompt_key=prompt_key,
        template=template,
        description=description,
        metadata=metadata,
        db_path=db_path,
    )

