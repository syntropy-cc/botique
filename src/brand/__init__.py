"""
Brand domain module

Provides brand identity management, audience profiling, and visual asset libraries.

Exports:
    - BrandLibrary: Visual asset selection
    - get_audience_profile: Get audience profile (database-backed with fallback)
    - AudienceRepository: Database repository for profiles
    - init_audience_database: Initialize database schema
"""

from .library import BrandLibrary
from .models import (
    Audience,
    AudienceProfile,
    BrandValue,
    CanvasConfig,
    ColorPalette,
    Platform,
    TypographyConfig,
    VisualStyle,
)
from .audience import (
    enrich_idea_with_audience,
    get_audience_from_platform,
    get_audience_profile,
    get_content_focus_keywords,
    get_recommended_platforms,
)
from .audience_repo import (
    AudienceRepository,
    get_repository,
    init_audience_database,
)

__all__ = [
    # Library
    "BrandLibrary",
    # Models
    "Platform",
    "Audience",
    "BrandValue",
    "ColorPalette",
    "TypographyConfig",
    "CanvasConfig",
    "VisualStyle",
    "AudienceProfile",
    # Audience functions
    "get_audience_profile",
    "enrich_idea_with_audience",
    "get_audience_from_platform",
    "get_content_focus_keywords",
    "get_recommended_platforms",
    # Repository
    "AudienceRepository",
    "get_repository",
    "init_audience_database",
]
