"""
Unit tests for BrandLibrary.

Tests brand asset selection logic (palettes, typography, canvas).

Location: tests/tools/brand/test_library.py
"""

import unittest

from src.brand.library import BrandLibrary
from src.brand.models import ColorPalette, TypographyConfig, CanvasConfig


class TestSelectPalette(unittest.TestCase):
    """Test cases for palette selection."""
    
    def test_select_palette_c_level(self):
        """Test C-Level palette selection."""
        palette = BrandLibrary.select_palette(
            platform="linkedin",
            tone="professional",
            persona="C-Level executives",
        )
        
        self.assertIsInstance(palette, ColorPalette)
        self.assertIn("professional", palette.id.lower())
        # Should default to light for professional tone
        self.assertIn("light", palette.id.lower())
    
    def test_select_palette_c_level_dark(self):
        """Test C-Level dark palette selection."""
        palette = BrandLibrary.select_palette(
            platform="linkedin",
            tone="professional",
            persona="C-Level executives",
            theme_preference="dark",
        )
        
        self.assertIsInstance(palette, ColorPalette)
        self.assertIn("professional", palette.id.lower())
        self.assertIn("dark", palette.id.lower())
    
    def test_select_palette_founder(self):
        """Test Founder palette selection."""
        palette = BrandLibrary.select_palette(
            platform="instagram",
            tone="empowering",
            persona="Founders and entrepreneurs",
        )
        
        self.assertIsInstance(palette, ColorPalette)
        self.assertIn("founder", palette.id.lower())
    
    def test_select_palette_developer(self):
        """Test Developer palette selection (always dark)."""
        palette = BrandLibrary.select_palette(
            platform="github",
            tone="technical",
            persona="Developers and programmers",
        )
        
        self.assertIsInstance(palette, ColorPalette)
        self.assertIn("developer", palette.id.lower())
        self.assertIn("dark", palette.id.lower())
        
        # Should be dark even with light preference
        palette2 = BrandLibrary.select_palette(
            platform="github",
            tone="technical",
            persona="Developers",
            theme_preference="light",
        )
        
        self.assertIn("dark", palette2.id.lower())
    
    def test_select_palette_default(self):
        """Test default/community palette selection."""
        # Use a platform that doesn't map to any specific audience
        # and a persona that doesn't match any keywords
        palette = BrandLibrary.select_palette(
            platform="unknown_platform",
            tone="casual",
            persona="General audience with no specific keywords",
        )
        
        self.assertIsInstance(palette, ColorPalette)
        self.assertIn("community", palette.id.lower())
    
    def test_select_palette_theme_preference(self):
        """Test theme preference override."""
        # Light preference
        palette_light = BrandLibrary.select_palette(
            platform="linkedin",
            tone="professional",
            persona="Founders",
            theme_preference="light",
        )
        
        # Dark preference
        palette_dark = BrandLibrary.select_palette(
            platform="linkedin",
            tone="professional",
            persona="Founders",
            theme_preference="dark",
        )
        
        self.assertIn("light", palette_light.id.lower())
        self.assertIn("dark", palette_dark.id.lower())
    
    def test_select_palette_case_insensitive(self):
        """Test that palette selection is case insensitive."""
        palette1 = BrandLibrary.select_palette(
            platform="LINKEDIN",
            tone="PROFESSIONAL",
            persona="C-LEVEL",
        )
        
        palette2 = BrandLibrary.select_palette(
            platform="linkedin",
            tone="professional",
            persona="c-level",
        )
        
        self.assertEqual(palette1.id, palette2.id)


class TestSelectTypography(unittest.TestCase):
    """Test cases for typography selection."""
    
    def test_select_typography_by_platform(self):
        """Test typography selection by platform."""
        # LinkedIn should use professional
        typography = BrandLibrary.select_typography(
            platform="linkedin",
        )
        
        self.assertIsInstance(typography, TypographyConfig)
        self.assertIn("professional", typography.id.lower())
    
    def test_select_typography_by_audience(self):
        """Test typography selection by audience."""
        # C-Level should use professional
        typography = BrandLibrary.select_typography(
            platform="instagram",
            audience="C-Level executives",
        )
        
        self.assertIsInstance(typography, TypographyConfig)
        self.assertIn("professional", typography.id.lower())
        
        # Founder should use bold
        typography2 = BrandLibrary.select_typography(
            platform="twitter",
            audience="Founders",
        )
        
        self.assertIsInstance(typography2, TypographyConfig)
        self.assertIn("bold", typography2.id.lower())
    
    def test_select_typography_default(self):
        """Test default typography selection."""
        typography = BrandLibrary.select_typography(
            platform="discord",
            audience="General",
        )
        
        self.assertIsInstance(typography, TypographyConfig)
        # Should have default primary typography
        self.assertIsNotNone(typography.id)


class TestGetCanvasConfig(unittest.TestCase):
    """Test cases for canvas configuration."""
    
    def test_get_canvas_config_linkedin(self):
        """Test LinkedIn canvas configuration."""
        canvas = BrandLibrary.get_canvas_config(
            platform="linkedin",
            format="carousel",
        )
        
        self.assertIsInstance(canvas, CanvasConfig)
        self.assertEqual(canvas.platform, "linkedin")
        self.assertEqual(canvas.format, "carousel")
        # LinkedIn carousel should be 1080x1350 (4:5 aspect ratio)
        self.assertEqual(canvas.width, 1080)
        self.assertEqual(canvas.height, 1350)
        self.assertEqual(canvas.aspect_ratio, "4:5")
    
    def test_get_canvas_config_instagram(self):
        """Test Instagram canvas configuration."""
        canvas = BrandLibrary.get_canvas_config(
            platform="instagram",
            format="single_image",
        )
        
        self.assertIsInstance(canvas, CanvasConfig)
        self.assertEqual(canvas.platform, "instagram")
    
    def test_get_canvas_config_carousel(self):
        """Test carousel format configuration."""
        canvas = BrandLibrary.get_canvas_config(
            platform="linkedin",
            format="carousel",
        )
        
        self.assertIsInstance(canvas, CanvasConfig)
        self.assertEqual(canvas.format, "carousel")
    
    def test_get_canvas_config_video(self):
        """Test video format configuration."""
        canvas = BrandLibrary.get_canvas_config(
            platform="youtube",
            format="video_short",
        )
        
        self.assertIsInstance(canvas, CanvasConfig)
        self.assertEqual(canvas.format, "video_short")
    
    def test_get_canvas_config_default(self):
        """Test default canvas configuration for unknown combinations."""
        canvas = BrandLibrary.get_canvas_config(
            platform="unknown",
            format="unknown_format",
        )
        
        self.assertIsInstance(canvas, CanvasConfig)
        # Should default to 1080x1080 square
        self.assertEqual(canvas.width, 1080)
        self.assertEqual(canvas.height, 1080)
        self.assertEqual(canvas.aspect_ratio, "1:1")


class TestPaletteValidation(unittest.TestCase):
    """Test cases for palette validation."""
    
    def test_all_palettes_valid(self):
        """Test that all palettes in library are valid."""
        for palette_id, palette in BrandLibrary.PALETTES.items():
            self.assertIsInstance(palette, ColorPalette)
            self.assertEqual(palette.id, palette_id)
            self.assertIsNotNone(palette.name)
            self.assertIsNotNone(palette.description)
            self.assertIsNotNone(palette.primary)
            self.assertIsNotNone(palette.secondary)
            self.assertIsNotNone(palette.accent)
            self.assertIsNotNone(palette.background)
            self.assertIsNotNone(palette.text)
            self.assertIsNotNone(palette.text_secondary)
            self.assertIsNotNone(palette.cta)
            self.assertIn(palette.theme, ["light", "dark"])
    
    def test_palette_to_dict(self):
        """Test palette serialization."""
        palette = BrandLibrary.PALETTES[list(BrandLibrary.PALETTES.keys())[0]]
        palette_dict = palette.to_dict()
        
        self.assertIsInstance(palette_dict, dict)
        self.assertEqual(palette_dict["id"], palette.id)
        self.assertIn("primary", palette_dict)
        self.assertIn("theme", palette_dict)


class TestTypographyValidation(unittest.TestCase):
    """Test cases for typography validation."""
    
    def test_all_typography_valid(self):
        """Test that all typography configs are valid."""
        for typography_id, typography in BrandLibrary.TYPOGRAPHY.items():
            self.assertIsInstance(typography, TypographyConfig)
            self.assertEqual(typography.id, typography_id)
            self.assertIsNotNone(typography.heading_font)
            self.assertIsNotNone(typography.body_font)
            self.assertIsNotNone(typography.weights)
            self.assertIn("heading", typography.weights)
            self.assertIn("body", typography.weights)


class TestCanvasConfigsValidation(unittest.TestCase):
    """Test cases for canvas configs validation."""
    
    def test_all_canvas_configs_valid(self):
        """Test that all canvas configs are valid."""
        for (platform, format_type), canvas in BrandLibrary.CANVAS_CONFIGS.items():
            self.assertIsInstance(canvas, CanvasConfig)
            self.assertEqual(canvas.platform, platform)
            self.assertEqual(canvas.format, format_type)
            self.assertGreater(canvas.width, 0)
            self.assertGreater(canvas.height, 0)
            self.assertIsNotNone(canvas.aspect_ratio)
    
    def test_canvas_config_common_formats(self):
        """Test common platform/format combinations."""
        common_combinations = [
            ("linkedin", "carousel"),
            ("instagram", "single_image"),
            ("twitter", "single_image"),
            ("youtube", "video_short"),
        ]
        
        for platform, format_type in common_combinations:
            canvas = BrandLibrary.get_canvas_config(platform, format_type)
            self.assertIsInstance(canvas, CanvasConfig)
            self.assertEqual(canvas.platform, platform)
            self.assertEqual(canvas.format, format_type)


if __name__ == "__main__":
    unittest.main()
