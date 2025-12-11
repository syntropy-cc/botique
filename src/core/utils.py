"""
Core utilities module

Helper functions for template rendering, JSON parsing, and validation.

Location: src/core/utils.py
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List


def render_template(template_path: Path, context: Dict[str, Any]) -> str:
    """
    Render template file with context variables.
    
    Supports simple {{variable}} substitution.
    
    Args:
        template_path: Path to template file
        context: Dictionary of variables to substitute
    
    Returns:
        Rendered template string
    
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    template_content = template_path.read_text(encoding="utf-8")
    
    # Simple {{variable}} substitution
    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        template_content = template_content.replace(placeholder, str(value))
    
    return template_content


def parse_json_safely(text: str) -> Dict[str, Any]:
    """
    Safely parse JSON from text, handling markdown code blocks.
    
    Attempts to extract JSON from:
    - Plain JSON text
    - Markdown code blocks (```json ... ```)
    - Text with JSON embedded
    
    Args:
        text: Text containing JSON
    
    Returns:
        Parsed JSON dictionary
    
    Raises:
        ValueError: If JSON cannot be parsed
    """
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from markdown code blocks
    json_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try finding JSON object/array in text
    json_object_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    matches = re.findall(json_object_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Last resort: try parsing entire text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Could not parse JSON from text. Text preview: {text[:200]}..."
        ) from exc


def validate_json_structure(
    data: Dict[str, Any],
    required_keys: List[str],
) -> None:
    """
    Validate that dictionary contains all required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
    
    Raises:
        ValueError: If any required keys are missing
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data).__name__}")
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise ValueError(
            f"Missing required keys: {', '.join(missing_keys)}. "
            f"Found keys: {', '.join(data.keys())}"
        )
