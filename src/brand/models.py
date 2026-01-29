"""
Brand identity models

Dataclasses for brand assets: colors, typography, canvas configurations.

Location: src/brand/models.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import json


# =============================================================================
# ENUMS
# =============================================================================

class Platform(Enum):
    """Supported social media platforms aligned with brand strategy"""
    LINKEDIN = "linkedin"      # C-Level: Authority & B2B Leads (75M profiles)
    INSTAGRAM = "instagram"    # Founders: Community & Awareness (141M accounts)
    TWITTER = "twitter"        # Founders: Viral reach (144M users)
    GITHUB = "github"          # Developers: OSS Credibility (3M users)
    YOUTUBE = "youtube"        # All: Deep education (22.9M users)
    DISCORD = "discord"        # Developers: Deep interaction


class Audience(Enum):
    """Target audiences from Plano de Branding 360º"""
    C_LEVEL = "c_level"           # C-Level de PMEs (R$10-100Mi)
    FOUNDER = "founder"           # Fundadores Visionários (Seed-Series B)
    DEVELOPER = "developer"       # DEVs Forjadores (Independent developers)


class BrandValue(Enum):
    """Core brand values"""
    GO_DEEP = "go_deep_or_go_home"              # Profundidade sobre superficialidade
    OPEN_SOURCE = "open_source"                  # Cultura Open Source
    COMMUNITY = "community_collaboration"        # Comunidade & Colaboração
    PIONEER = "pioneer_new_world"                # Desbravar o Novo Mundo


# =============================================================================
# COLOR PALETTE
# =============================================================================

@dataclass
class ColorPalette:
    """
    Color palette definition aligned with brand guidelines.
    
    Based on Plano de Branding 360º visual identity.
    """
    
    id: str
    name: str
    description: str
    
    # Core colors
    primary: str              # Main background or primary element
    secondary: str            # Secondary background or element
    accent: str               # Accent color for emphasis
    background: str           # Main background
    text: str                 # Primary text color
    text_secondary: str       # Secondary text color
    cta: str                  # Call-to-action color
    details_1: str            # Detail/highlight color 1
    details_2: str            # Detail/highlight color 2
    
    # Metadata
    theme: str                # "light" or "dark"
    best_for: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, str]:
        """Export colors as dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "text": self.text,
            "text_secondary": self.text_secondary,
            "cta": self.cta,
            "details_1": self.details_1,
            "details_2": self.details_2,
            "theme": self.theme,
        }
    
    def get_css_variables(self) -> str:
        """Generate CSS custom properties"""
        return f"""
:root {{
    --color-primary: {self.primary};
    --color-secondary: {self.secondary};
    --color-accent: {self.accent};
    --color-background: {self.background};
    --color-text: {self.text};
    --color-text-secondary: {self.text_secondary};
    --color-cta: {self.cta};
    --color-details-1: {self.details_1};
    --color-details-2: {self.details_2};
}}
""".strip()


# =============================================================================
# TYPOGRAPHY
# =============================================================================

@dataclass
class TypographyConfig:
    """
    Typography configuration from brand identity.
    
    Brand standard: Poppins Bold + Inter Regular
    """
    
    id: str
    name: str
    heading_font: str         # Font for headings/titles
    body_font: str            # Font for body text
    character: str            # Character description (e.g., "modern_bold")
    weights: Dict[str, str] = field(default_factory=dict)  # Font weights
    best_for: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, str]:
        """Export typography as dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "heading_font": self.heading_font,
            "body_font": self.body_font,
            "character": self.character,
            "weights": self.weights,
        }
    
    def get_css_font_stack(self) -> str:
        """Generate CSS font stack"""
        return f"""
:root {{
    --font-heading: '{self.heading_font}', sans-serif;
    --font-body: '{self.body_font}', sans-serif;
    --weight-heading: {self.weights.get('heading', '700')};
    --weight-body: {self.weights.get('body', '400')};
    --weight-emphasis: {self.weights.get('emphasis', '600')};
}}
""".strip()


# =============================================================================
# CANVAS CONFIGURATION
# =============================================================================

@dataclass
class CanvasConfig:
    """
    Canvas dimensions for platform/format combinations.
    
    Defines optimal image dimensions for each social media platform.
    """
    
    width: int
    height: int
    aspect_ratio: str
    platform: str
    format: str
    
    def to_dict(self) -> Dict[str, any]:
        """Export as dictionary"""
        return {
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "platform": self.platform,
            "format": self.format,
        }
    
    @property
    def dimensions(self) -> tuple[int, int]:
        """Get dimensions as tuple"""
        return (self.width, self.height)
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"CanvasConfig({self.platform}/{self.format}: "
            f"{self.width}x{self.height} {self.aspect_ratio})"
        )


# =============================================================================
# VISUAL STYLE
# =============================================================================

@dataclass
class VisualStyle:
    """
    Visual style definition for content.
    
    Describes the overall aesthetic and mood of visual content.
    """
    
    id: str
    name: str
    description: str
    characteristics: List[str] = field(default_factory=list)
    best_for_audiences: List[str] = field(default_factory=list)
    mood_keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, any]:
        """Export as dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "characteristics": self.characteristics,
            "best_for_audiences": self.best_for_audiences,
            "mood_keywords": self.mood_keywords,
        }


# =============================================================================
# AUDIENCE PROFILE
# =============================================================================

@dataclass
class AudienceProfile:
    """
    Audience profile model for database-backed profiles.
    
    Represents a complete audience persona profile stored in the database.
    The profile_data field contains the full profile structure as a dict.
    """
    
    id: str
    persona_type: str
    name: str
    description: Optional[str] = None
    profile_data: Dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    version: int = 1
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        """Export profile as dictionary."""
        return {
            "id": self.id,
            "persona_type": self.persona_type,
            "name": self.name,
            "description": self.description,
            "profile_data": self.profile_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AudienceProfile":
        """Create profile from dictionary."""
        return cls(
            id=data.get("id", ""),
            persona_type=data.get("persona_type", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            profile_data=data.get("profile_data", {}),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            version=data.get("version", 1),
            is_active=data.get("is_active", True),
        )
    
    def to_json(self) -> str:
        """Export profile as JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "AudienceProfile":
        """Create profile from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)