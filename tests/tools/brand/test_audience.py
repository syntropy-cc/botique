"""
Unit tests for audience profile functions.

Tests audience profile matching and idea enrichment.

Location: tests/tools/brand/test_audience.py
"""

import unittest

from src.brand.audience import get_audience_profile, enrich_idea_with_audience


class TestGetAudienceProfile(unittest.TestCase):
    """Test cases for get_audience_profile function."""
    
    def test_get_audience_profile_c_level(self):
        """Test C-Level profile matching."""
        profile = get_audience_profile("C-Level executives")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "Decisor C-Level")
    
    def test_get_audience_profile_founder(self):
        """Test Founder profile matching."""
        profile = get_audience_profile("Founders and entrepreneurs")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "Fundador Visionário")
    
    def test_get_audience_profile_developer(self):
        """Test Developer profile matching."""
        profile = get_audience_profile("Developers and programmers")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "DEV Forjador")
    
    def test_get_audience_profile_not_found(self):
        """Test unknown persona returns None."""
        profile = get_audience_profile("Unknown persona")
        
        self.assertIsNone(profile)
    
    def test_get_audience_profile_case_insensitive(self):
        """Test that profile matching is case insensitive."""
        profile1 = get_audience_profile("C-LEVEL EXECUTIVE")
        profile2 = get_audience_profile("c-level executive")
        
        self.assertIsNotNone(profile1)
        self.assertIsNotNone(profile2)
        self.assertEqual(profile1["name"], profile2["name"])
    
    def test_get_audience_profile_partial_match(self):
        """Test partial keyword matching."""
        # Test various C-Level keywords
        for keyword in ["C-Level", "executive", "CEO", "CTO", "CFO", "CMO", "decisor"]:
            profile = get_audience_profile(f"Person is {keyword}")
            self.assertIsNotNone(profile, f"Should match for keyword: {keyword}")
            self.assertEqual(profile["name"], "Decisor C-Level")
        
        # Test various Founder keywords
        for keyword in ["founder", "fundador", "startup", "empreendedor"]:
            profile = get_audience_profile(f"Person is {keyword}")
            self.assertIsNotNone(profile, f"Should match for keyword: {keyword}")
            self.assertEqual(profile["name"], "Fundador Visionário")
        
        # Test Developer keywords
        profile = get_audience_profile("Professional programmer")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], "DEV Forjador")


class TestEnrichIdeaWithAudience(unittest.TestCase):
    """Test cases for enrich_idea_with_audience function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.idea = {
            "id": "idea_001",
            "platform": "linkedin",
            "tone": "professional",
            "personality_traits": ["authoritative"],
            "pain_points": ["operational_inefficiency"],
            "desires": ["efficiency"],
            "vocabulary_level": "sophisticated",
            "formality": "formal",
        }
        
        self.audience_profile = {
            "name": "C-Level Executive",
            "personality_traits": ["strategic", "data_driven"],
            "pain_points": ["wasted_budgets", "operational_inefficiency"],
            "desires": ["roi_rapido", "efficiency"],
            "communication_style": {
                "vocabulary": "sophisticated",
                "formality": "formal",
            },
            "brand_values": ["go_deep_or_go_home"],
        }
    
    def test_enrich_idea_with_audience(self):
        """Test basic idea enrichment."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        self.assertIsNotNone(enriched)
        self.assertEqual(enriched["id"], self.idea["id"])
        # Should have merged traits
        self.assertIn("authoritative", enriched["personality_traits"])
        self.assertIn("strategic", enriched["personality_traits"])
    
    def test_enrich_idea_merges_traits(self):
        """Test that personality traits are merged."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        # Should contain both original and profile traits
        traits = enriched["personality_traits"]
        self.assertIn("authoritative", traits)
        self.assertIn("strategic", traits)
        self.assertIn("data_driven", traits)
        # Should limit to 5 traits
        self.assertLessEqual(len(traits), 5)
    
    def test_enrich_idea_merges_pain_points(self):
        """Test that pain points are merged."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        pain_points = enriched["pain_points"]
        self.assertIn("operational_inefficiency", pain_points)
        self.assertIn("wasted_budgets", pain_points)
        # Should limit to 5
        self.assertLessEqual(len(pain_points), 5)
    
    def test_enrich_idea_merges_desires(self):
        """Test that desires are merged."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        desires = enriched["desires"]
        self.assertIn("efficiency", desires)
        self.assertIn("roi_rapido", desires)
        # Should limit to 5
        self.assertLessEqual(len(desires), 5)
    
    def test_enrich_idea_vocabulary_override(self):
        """Test that vocabulary defaults are applied when missing."""
        idea_no_vocab = self.idea.copy()
        del idea_no_vocab["vocabulary_level"]
        
        enriched = enrich_idea_with_audience(idea_no_vocab, self.audience_profile)
        
        self.assertEqual(enriched["vocabulary_level"], "sophisticated")
        
        # Should not override if already present
        enriched2 = enrich_idea_with_audience(self.idea, self.audience_profile)
        self.assertEqual(enriched2["vocabulary_level"], "sophisticated")
    
    def test_enrich_idea_brand_values(self):
        """Test that brand values are added."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        self.assertIn("brand_values", enriched)
        self.assertIn("go_deep_or_go_home", enriched["brand_values"])
    
    def test_enrich_idea_preserves_original_fields(self):
        """Test that original idea fields are preserved."""
        enriched = enrich_idea_with_audience(self.idea, self.audience_profile)
        
        # Original fields should be preserved
        self.assertEqual(enriched["id"], self.idea["id"])
        self.assertEqual(enriched["platform"], self.idea["platform"])
        self.assertEqual(enriched["tone"], self.idea["tone"])
    
    def test_enrich_idea_with_nested_pain_points(self):
        """Test enrichment with nested pain points structure."""
        profile_nested = self.audience_profile.copy()
        profile_nested["pain_points"] = {
            "operational": ["operational_inefficiency"],
            "financial": ["wasted_budgets"],
        }
        
        enriched = enrich_idea_with_audience(self.idea, profile_nested)
        
        # Should flatten nested structure
        pain_points = enriched["pain_points"]
        self.assertIn("operational_inefficiency", pain_points)
        self.assertIn("wasted_budgets", pain_points)
    
    def test_enrich_idea_with_nested_desires(self):
        """Test enrichment with nested desires structure."""
        profile_nested = self.audience_profile.copy()
        profile_nested["desires"] = {
            "efficiency": ["efficiency"],
            "roi": ["roi_rapido"],
        }
        
        enriched = enrich_idea_with_audience(self.idea, profile_nested)
        
        # Should flatten nested structure
        desires = enriched["desires"]
        self.assertIn("efficiency", desires)
        self.assertIn("roi_rapido", desires)


class TestAudienceProfilesComplete(unittest.TestCase):
    """Test cases for audience profile completeness."""
    
    def test_audience_profiles_complete(self):
        """Test that all audience profiles have required fields."""
        profiles = ["C-Level executives", "Founders", "Developers"]
        
        for persona in profiles:
            profile = get_audience_profile(persona)
            self.assertIsNotNone(profile, f"Profile should exist for: {persona}")
            
            # Check required fields
            self.assertIn("name", profile)
            self.assertIn("personality_traits", profile)
            self.assertIn("pain_points", profile)
            self.assertIn("desires", profile)
            self.assertIn("communication_style", profile)
            
            # Check communication style
            comm_style = profile["communication_style"]
            self.assertIn("vocabulary", comm_style)
            self.assertIn("formality", comm_style)
    
    def test_audience_profiles_have_brand_values(self):
        """Test that audience profiles have brand values."""
        profiles = ["C-Level executives", "Founders", "Developers"]
        
        for persona in profiles:
            profile = get_audience_profile(persona)
            self.assertIsNotNone(profile)
            
            # Should have brand_values
            self.assertIn("brand_values", profile)
            self.assertIsInstance(profile["brand_values"], list)
            self.assertGreater(len(profile["brand_values"]), 0)


if __name__ == "__main__":
    unittest.main()
