"""
Core utilities module

Helper functions for file I/O, JSON processing, and template rendering.

Location: src/core/utils.py
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Union


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
# PROMPT BUILDING
# =============================================================================

def build_prompt_from_template(
    template_path: Path,
    context: Dict[str, Any],
) -> str:
    """
    Build prompt from template file and context dictionary.
    
    Generic function to fill in a prompt template with context values.
    Uses render_template internally to replace placeholders.
    
    Args:
        template_path: Path to the template file
        context: Dictionary mapping placeholder names to values
    
    Returns:
        Complete prompt string with placeholders filled
    
    Example:
        template.md contains: "Config: {config_json}\nArticle: {article}"
        context = {"config_json": '{"key": "value"}', "article": "Hello world"}
        result = "Config: {\"key\": \"value\"}\nArticle: Hello world"
    """
    return render_template(template_path, context)


# =============================================================================
# LLM RESPONSE VALIDATION
# =============================================================================

def validate_llm_json_response(
    raw_response: str,
    top_level_keys: list[str],
    nested_validations: Union[Dict[str, list[str]], None] = None,
    list_validations: Union[Dict[str, Union[list[str], Callable]], None] = None,
) -> Dict[str, Any]:
    """
    Parse and validate LLM JSON response structure.
    
    Uses parse_json_safely to handle common LLM output issues, then validates
    the structure according to provided requirements.
    
    Args:
        raw_response: Raw string response from LLM
        top_level_keys: Required top-level keys in the JSON response
        nested_validations: Dict mapping nested keys to their required sub-keys
                           (e.g., {"article_summary": ["title", "main_thesis"]})
        list_validations: Dict mapping list keys to validation requirements.
                         Values can be:
                         - list[str]: Required keys for each item in the list
                         - callable: Custom validation function(item, index) -> None
    
    Returns:
        Parsed and validated JSON as dictionary
    
    Raises:
        ValueError: If JSON is invalid or structure doesn't match requirements
    
    Example:
        # Simple validation
        payload = validate_llm_json_response(
            raw_response,
            top_level_keys=["summary", "items"]
        )
        
        # With nested validation
        payload = validate_llm_json_response(
            raw_response,
            top_level_keys=["summary", "items"],
            nested_validations={"summary": ["title", "content"]}
        )
        
        # With list validation
        payload = validate_llm_json_response(
            raw_response,
            top_level_keys=["items"],
            list_validations={"items": ["id", "name", "value"]}
        )
    """
    # Parse JSON safely
    payload = parse_json_safely(raw_response)
    
    # Validate top-level structure
    validate_json_structure(payload, top_level_keys)
    
    # Validate nested structures
    if nested_validations:
        for key, required_sub_keys in nested_validations.items():
            if key not in payload:
                continue  # Already validated by top-level check
            
            nested_data = payload[key]
            if not isinstance(nested_data, dict):
                raise ValueError(f"'{key}' must be a dictionary")
            
            validate_json_structure(nested_data, required_sub_keys)
    
    # Validate list structures
    if list_validations:
        for key, validation in list_validations.items():
            # Support nested paths like "article_summary.key_insights"
            if "." in key:
                parts = key.split(".")
                nested_obj = payload
                for part in parts[:-1]:
                    if part not in nested_obj:
                        continue  # Skip if parent doesn't exist
                    nested_obj = nested_obj[part]
                    if not isinstance(nested_obj, dict):
                        continue  # Skip if parent is not a dict
                
                list_key = parts[-1]
                if list_key not in nested_obj:
                    continue  # Skip if list doesn't exist
                
                list_data = nested_obj[list_key]
            else:
                # Top-level list
                if key not in payload:
                    continue  # Already validated by top-level check
                list_data = payload[key]
            
            if not isinstance(list_data, list):
                raise ValueError(f"'{key}' must be a list")
            
            # Allow empty lists (some fields like avoid_topics, risks can be empty)
            # Only validate structure if list is not empty
            if len(list_data) == 0:
                continue
            
            # If validation is a list of required keys
            if isinstance(validation, list):
                required_item_keys = validation
                for idx, item in enumerate(list_data):
                    if not isinstance(item, dict):
                        raise ValueError(f"'{key}[{idx}]' must be a dictionary")
                    try:
                        validate_json_structure(item, required_item_keys)
                    except ValueError as exc:
                        raise ValueError(f"Invalid item at '{key}[{idx}]': {exc}") from exc
            
            # If validation is a callable function
            elif callable(validation):
                for idx, item in enumerate(list_data):
                    try:
                        validation(item, idx)
                    except ValueError as exc:
                        raise ValueError(f"Invalid item at '{key}[{idx}]': {exc}") from exc
            else:
                raise TypeError(f"Invalid validation type for '{key}': expected list or callable")
    
    return payload


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