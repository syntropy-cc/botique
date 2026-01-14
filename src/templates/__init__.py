"""
Textual templates module

Provides template structures for textual/narrative content modules.

This module is specifically for textual/narrative templates that guide
text structure and content. Design templates (for visual composition)
will be implemented separately in the future.

Location: src/templates/
"""

from .textual_templates import TextualTemplate
from .library import TemplateLibrary
from .selector import TemplateSelector

__all__ = [
    "TextualTemplate",
    "TemplateLibrary",
    "TemplateSelector",
]
