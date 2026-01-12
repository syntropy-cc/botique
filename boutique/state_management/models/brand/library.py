"""
Brand library module

Centralized repository of brand assets based on Plano de Branding 360º.

Contains:
- Color palettes (6 palettes aligned with brand guidelines)
- Typography configurations
- Canvas dimensions
- Selection logic

Location: src/brand/library.py
"""

from typing import Optional

from .models import ColorPalette, TypographyConfig, CanvasConfig


class BrandLibrary:
    """
    Centralized brand identity library.
    
    All visual assets based on Plano de Branding 360º:
    - Fonts: Poppins Bold, Inter Regular
    - Colors: Electric Blue (#0060FF), Burnt Orange (#FF6B00), Graphite (#222831)
    - Audiences: C-Levels, Founders, Developers
    """
    
    # =========================================================================
    # COLOR PALETTES
    # =========================================================================
    
    PALETTES = {
        # Light Theme - Professional (C-Level)
        "brand_light_professional": ColorPalette(
            id="brand_light_professional",
            name="Brand Light - Professional",
            description="Clean professional palette for C-Level decision makers",
            primary="#F6F8FA",           # Neutro Claro (background)
            secondary="#E0EFFF",         # Azul Claro
            accent="#0060FF",            # Azul Elétrico (CTA)
            background="#F6F8FA",        # Neutro Claro
            text="#222831",              # Grafite Escuro
            text_secondary="#6B7280",    # Cinza Médio
            cta="#0060FF",               # Azul Elétrico
            details_1="#FF6B00",         # Laranja Queimado
            details_2="#D1D5DB",         # Cinza Claro
            theme="light",
            best_for=["c_level", "professional", "linkedin", "roi_focused"]
        ),
        
        # Dark Theme - Professional (C-Level)
        "brand_dark_professional": ColorPalette(
            id="brand_dark_professional",
            name="Brand Dark - Professional",
            description="Authoritative dark palette for executive content",
            primary="#000000",           # Preto Absoluto (background)
            secondary="#222831",         # Grafite Escuro
            accent="#0060FF",            # Azul Elétrico (CTA)
            background="#000000",        # Preto Absoluto
            text="#F9FAFB",              # Branco Neve
            text_secondary="#9CA3AF",    # Cinza Aço
            cta="#0060FF",               # Azul Elétrico
            details_1="#E0EFFF",         # Azul Neon
            details_2="#E0EFFF",         # Azul Claro
            theme="dark",
            best_for=["c_level", "authority", "linkedin", "premium"]
        ),
        
        # Light Theme - Founder Visionary
        "brand_light_founder": ColorPalette(
            id="brand_light_founder",
            name="Brand Light - Founder",
            description="Inspiring palette for visionary founders",
            primary="#F6F8FA",           # Neutro Claro
            secondary="#E0EFFF",         # Azul Claro
            accent="#FF6B00",            # Laranja Queimado (energy)
            background="#F6F8FA",
            text="#222831",              # Grafite Escuro
            text_secondary="#6B7280",    # Cinza Médio
            cta="#0060FF",               # Azul Elétrico
            details_1="#FF6B00",         # Laranja Queimado
            details_2="#0060FF",         # Azul Elétrico
            theme="light",
            best_for=["founder", "visionary", "instagram", "growth"]
        ),
        
        # Dark Theme - Founder Builder
        "brand_dark_founder": ColorPalette(
            id="brand_dark_founder",
            name="Brand Dark - Founder",
            description="Bold dark palette for builder culture",
            primary="#000000",           # Preto Absoluto
            secondary="#222831",         # Grafite Escuro
            accent="#FF6B00",            # Laranja Queimado
            background="#000000",
            text="#F9FAFB",              # Branco Neve
            text_secondary="#9CA3AF",    # Cinza Aço
            cta="#FF6B00",               # Laranja Queimado (action)
            details_1="#0060FF",         # Azul Elétrico
            details_2="#E0EFFF",         # Azul Neon
            theme="dark",
            best_for=["founder", "builder", "instagram", "exponential"]
        ),
        
        # Dark Theme - Developer Code Deep
        "brand_dark_developer": ColorPalette(
            id="brand_dark_developer",
            name="Brand Dark - Developer",
            description="Technical dark palette for code-focused content",
            primary="#000000",           # Preto Absoluto
            secondary="#222831",         # Grafite Escuro
            accent="#0060FF",            # Azul Elétrico (tech)
            background="#000000",
            text="#E0EFFF",              # Azul Neon (code aesthetic)
            text_secondary="#9CA3AF",    # Cinza Aço
            cta="#FF6B00",               # Laranja Queimado (action)
            details_1="#0060FF",         # Azul Elétrico
            details_2="#D1D5DB",         # Cinza Claro
            theme="dark",
            best_for=["developer", "technical", "github", "code_deep_dive"]
        ),
        
        # Light Theme - Community & Collaboration
        "brand_light_community": ColorPalette(
            id="brand_light_community",
            name="Brand Light - Community",
            description="Welcoming palette for community content",
            primary="#F9FAFB",           # Branco Neve
            secondary="#E0EFFF",         # Azul Claro
            accent="#0060FF",            # Azul Elétrico
            background="#F9FAFB",
            text="#222831",              # Grafite Escuro
            text_secondary="#6B7280",    # Cinza Médio
            cta="#FF6B00",               # Laranja Queimado
            details_1="#0060FF",         # Azul Elétrico
            details_2="#E0EFFF",         # Azul Claro
            theme="light",
            best_for=["community", "collaboration", "discord", "inclusive"]
        ),
    }
    
    # =========================================================================
    # TYPOGRAPHY
    # =========================================================================
    
    TYPOGRAPHY = {
        "brand_primary": TypographyConfig(
            id="brand_primary",
            name="Brand Primary - Poppins + Inter",
            heading_font="Poppins",
            body_font="Inter",
            character="modern_bold",
            weights={
                "heading": "700",  # Poppins Bold
                "body": "400",     # Inter Regular
                "emphasis": "600"  # Inter Semibold
            },
            best_for=["all_audiences", "brand_consistency", "primary"]
        ),
        
        "brand_professional": TypographyConfig(
            id="brand_professional",
            name="Brand Professional - Inter Only",
            heading_font="Inter",
            body_font="Inter",
            character="clean_professional",
            weights={
                "heading": "700",  # Inter Bold
                "body": "400",     # Inter Regular
                "emphasis": "600"  # Inter Semibold
            },
            best_for=["c_level", "professional", "linkedin"]
        ),
        
        "brand_bold": TypographyConfig(
            id="brand_bold",
            name="Brand Bold - Poppins Heavy",
            heading_font="Poppins",
            body_font="Poppins",
            character="bold_impactful",
            weights={
                "heading": "800",  # Poppins Extra Bold
                "body": "600",     # Poppins Semibold
                "emphasis": "700"  # Poppins Bold
            },
            best_for=["founder", "builder", "impact", "cta"]
        ),
    }
    
    # =========================================================================
    # CANVAS CONFIGURATIONS
    # =========================================================================
    
    CANVAS_CONFIGS = {
        # LinkedIn - Professional networking (75M profiles)
        ("linkedin", "carousel"): CanvasConfig(1080, 1350, "4:5", "linkedin", "carousel"),
        ("linkedin", "single_image"): CanvasConfig(1200, 627, "1.91:1", "linkedin", "single_image"),
        
        # Instagram - Visual storytelling (141M accounts)
        ("instagram", "carousel"): CanvasConfig(1080, 1080, "1:1", "instagram", "carousel"),
        ("instagram", "single_image"): CanvasConfig(1080, 1080, "1:1", "instagram", "single_image"),
        ("instagram", "story"): CanvasConfig(1080, 1920, "9:16", "instagram", "story"),
        ("instagram", "reel"): CanvasConfig(1080, 1920, "9:16", "instagram", "reel"),
        
        # Twitter/X - Quick engagement (144M users)
        ("twitter", "single_image"): CanvasConfig(1200, 675, "16:9", "twitter", "single_image"),
        ("twitter", "carousel"): CanvasConfig(1200, 675, "16:9", "twitter", "carousel"),
        
        # YouTube - Video thumbnails (22.9M users)
        ("youtube", "thumbnail"): CanvasConfig(1280, 720, "16:9", "youtube", "thumbnail"),
        
        # GitHub - Repository visuals (3M users)
        ("github", "readme_banner"): CanvasConfig(1280, 640, "2:1", "github", "readme_banner"),
    }
    
    # =========================================================================
    # SELECTION LOGIC
    # =========================================================================
    
    @classmethod
    def select_palette(
        cls,
        platform: str,
        tone: str,
        persona: Optional[str] = None,
        theme_preference: str = "auto"
    ) -> ColorPalette:
        """
        Select brand-aligned color palette.
        
        Selection logic follows brand strategy:
        - C-Level: Professional palettes
        - Founders: Founder palettes (emphasize action/growth)
        - Developers: Technical dark palette
        - Default: Community palette
        
        Args:
            platform: Social media platform
            tone: Content tone (professional, empowering, urgent, etc.)
            persona: Target persona description
            theme_preference: "light", "dark", or "auto"
        
        Returns:
            Selected ColorPalette
        """
        platform_lower = platform.lower()
        tone_lower = tone.lower()
        persona_lower = (persona or "").lower()
        
        # Detect audience type
        audience_type = cls._detect_audience_type(platform_lower, persona_lower)
        
        # Determine theme
        use_dark = cls._should_use_dark_theme(tone_lower, theme_preference)
        
        # Select palette
        if audience_type == "c_level":
            palette_id = "brand_dark_professional" if use_dark else "brand_light_professional"
        elif audience_type == "founder":
            palette_id = "brand_dark_founder" if use_dark else "brand_light_founder"
        elif audience_type == "developer":
            palette_id = "brand_dark_developer"  # Always dark for devs
        else:
            palette_id = "brand_light_community"  # Default
        
        return cls.PALETTES[palette_id]
    
    @classmethod
    def select_typography(
        cls,
        platform: str,
        audience: Optional[str] = None,
    ) -> TypographyConfig:
        """
        Select typography based on platform and audience.
        
        Args:
            platform: Social media platform
            audience: Target audience type
        
        Returns:
            Selected TypographyConfig
        """
        platform_lower = platform.lower()
        audience_lower = (audience or "").lower()
        
        # Professional contexts → Inter clean
        if platform_lower == "linkedin" or "c-level" in audience_lower:
            return cls.TYPOGRAPHY["brand_professional"]
        
        # High-impact contexts → Poppins bold
        elif "founder" in audience_lower or "cta" in audience_lower:
            return cls.TYPOGRAPHY["brand_bold"]
        
        # Default → Brand primary
        else:
            return cls.TYPOGRAPHY["brand_primary"]
    
    @classmethod
    def get_canvas_config(cls, platform: str, format: str) -> CanvasConfig:
        """
        Get canvas dimensions for platform/format combination.
        
        Args:
            platform: Social media platform
            format: Content format (carousel, single_image, etc.)
        
        Returns:
            CanvasConfig with dimensions
        """
        key = (platform.lower(), format.lower())
        return cls.CANVAS_CONFIGS.get(
            key,
            CanvasConfig(1080, 1080, "1:1", platform, format)  # Default square
        )
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    @staticmethod
    def _detect_audience_type(platform: str, persona: str) -> str:
        """Detect audience type from platform and persona"""
        # Check persona keywords
        if any(x in persona for x in ["c-level", "executive", "ceo", "cto", "decisor"]):
            return "c_level"
        elif any(x in persona for x in ["founder", "startup", "visionário", "empreendedor"]):
            return "founder"
        elif any(x in persona for x in ["developer", "dev", "engineer", "forjador"]):
            return "developer"
        
        # Fallback to platform defaults
        if platform == "linkedin":
            return "c_level"
        elif platform in ["instagram", "twitter"]:
            return "founder"
        elif platform in ["github", "discord"]:
            return "developer"
        
        return "community"
    
    @staticmethod
    def _should_use_dark_theme(tone: str, theme_preference: str) -> bool:
        """Determine if dark theme should be used"""
        if theme_preference == "dark":
            return True
        elif theme_preference == "light":
            return False
        else:  # auto
            # Dark for: urgent, technical, authority, dramatic tones
            return any(x in tone for x in [
                "urgent", "critical", "technical", "authority", "dramatic", "bold"
            ])