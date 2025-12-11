"""
Brand models module

Data models for brand assets (palettes, typography, canvas).

Location: src/brand/models.py
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ColorPalette:
    """Color palette definition"""
    id: str
    name: str
    description: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    text_secondary: str = ""
    cta: str = ""
    details_1: str = ""
    details_2: str = ""
    theme: str = "light"
    best_for: List[str] = field(default_factory=list)


@dataclass
class TypographyConfig:
    """Typography configuration"""
    id: str
    name: str
    heading_font: str
    body_font: str
    character: str
    weights: Dict[str, str] = field(default_factory=lambda: {"heading": "700", "body": "400"})
    best_for: List[str] = field(default_factory=list)


@dataclass
class CanvasConfig:
    """Canvas dimensions for platform/format"""
    width: int
    height: int
    aspect_ratio: str
    platform: str = ""
    format: str = ""

