"""
Core utilities module

Helper functions for file I/O, JSON processing, and template rendering.

Location: src/core/utils.py
"""

import json
from pathlib import Path
from typing import Any, Dict


# =============================================================================
# TEMPLATE RENDERING
# =============================================================================

def render_template(template_path: Path, context: Dict[str, str]) -> str:
    """
    Render a template by replacing placeholders with context values.
    
    Uses simple string replacement to avoid issues with braces in content.
    Each placeholder {key} in the template is replaced with context[key].
    
    Args:
        template_path: Path to the template file
        context: Dictionary mapping placeholder names to values
    
    Returns:
        Rendered template string
    
    Example:
        template.md contains: "Article: {article}"
        context = {"article": "Hello world"}
        result = "Article: Hello world"
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    text = template_path.read_text(encoding="utf-8")
    
    for key, value in context.items():
        placeholder = "{" + key + "}"
        text = text.replace(placeholder, str(value))
    
    return text


# =============================================================================
# JSON PROCESSING
# =============================================================================

def parse_json_safely(raw: str) -> Dict[str, Any]:
    """
    Parse JSON string, handling common LLM output issues.
    
    Strips markdown code fences (```json ... ```) if present.
    
    Args:
        raw: Raw string that should contain JSON
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        ValueError: If the string is not valid JSON after cleaning
    """
    cleaned = raw.strip()
    
    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        
        # Remove opening fence (```json or ```)
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        
        # Remove closing fence (```)
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        
        cleaned = "\n".join(lines).strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON after cleaning. First 200 chars: {cleaned[:200]}"
        ) from exc


def save_json(data: Any, path: Path, indent: int = 2) -> None:
    """
    Save data as JSON to file.
    
    Creates parent directories if they don't exist.
    
    Args:
        data: Data to serialize (must be JSON-serializable)
        path: Output file path
        indent: JSON indentation level (default: 2)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False),
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    """
    Load JSON from file.
    
    Args:
        path: Path to JSON file
    
    Returns:
        Parsed JSON data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


# =============================================================================
# PATH UTILITIES
# =============================================================================

def resolve_article_path(article_arg: str, articles_dir: Path) -> Path:
    """
    Resolve article path from CLI argument.
    
    If the path is relative, resolves it relative to articles_dir.
    If absolute, uses it as-is.
    
    Args:
        article_arg: Article path from CLI (relative or absolute)
        articles_dir: Base directory for articles
    
    Returns:
        Resolved absolute path
    
    Raises:
        FileNotFoundError: If the resolved path doesn't exist
    """
    article_path = Path(article_arg)
    
    if not article_path.is_absolute():
        article_path = (articles_dir / article_path).resolve()
    
    if not article_path.exists():
        raise FileNotFoundError(f"Article not found: {article_path}")
    
    return article_path


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    
    Returns:
        The same path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# =============================================================================
# STRING UTILITIES
# =============================================================================

def parse_list_arg(value: str | None) -> list[str] | None:
    """
    Parse comma-separated CLI argument into list.
    
    Args:
        value: Comma-separated string (e.g., "linkedin,instagram")
    
    Returns:
        List of stripped values, or None if input is None/empty
    
    Example:
        parse_list_arg("a, b,c ") → ["a", "b", "c"]
        parse_list_arg(None) → None
    """
    if not value:
        return None
    
    return [v.strip() for v in value.split(",") if v.strip()]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: String to append if truncated (default: "...")
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_json_structure(data: Dict[str, Any], required_keys: list[str]) -> None:
    """
    Validate that a JSON structure contains required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
    
    Raises:
        ValueError: If any required key is missing
    """
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise ValueError(
            f"Missing required keys in JSON: {', '.join(missing_keys)}"
        )


def validate_confidence(confidence: float) -> None:
    """
    Validate confidence score is in valid range.
    
    Args:
        confidence: Confidence value to validate
    
    Raises:
        ValueError: If confidence is not between 0.0 and 1.0
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            f"Confidence must be between 0.0 and 1.0, got: {confidence}"
        )