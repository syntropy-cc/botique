"""
Unit tests for TextualTemplate dataclass.

Tests the TextualTemplate dataclass that represents textual/narrative templates.

Location: tests/tools/test_textual_templates.py
"""

import unittest
from dataclasses import asdict

from src.templates.textual_templates import (
    TextualTemplate,
    HOOK_TEMPLATES,
    VALUE_DATA_TEMPLATES,
    VALUE_INSIGHT_TEMPLATES,
    VALUE_SOLUTION_TEMPLATES,
    VALUE_EXAMPLE_TEMPLATES,
    CTA_TEMPLATES,
)


class TestTextualTemplate(unittest.TestCase):
    """Test cases for TextualTemplate dataclass."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_template = TextualTemplate(
            id="TEST_001",
            module_type="hook",
            function="Test function",
            structure="Test [variable] structure",
            length_range=(50, 100),
            tone="test tone",
            example="Test example text",
            keywords=["test", "example"],
            semantic_description="Test semantic description",
        )
    
    def test_template_initialization(self):
        """Test TextualTemplate initialization."""
        template = TextualTemplate(
            id="H_TEST",
            module_type="hook",
            function="Test hook",
            structure="[Action] now",
            length_range=(60, 90),
            tone="provocative",
            example="Start now.",
            keywords=["action", "urgency"],
            semantic_description="Urgent call to action",
        )
        
        self.assertEqual(template.id, "H_TEST")
        self.assertEqual(template.module_type, "hook")
        self.assertEqual(template.function, "Test hook")
        self.assertEqual(template.structure, "[Action] now")
        self.assertEqual(template.length_range, (60, 90))
        self.assertEqual(template.tone, "provocative")
        self.assertEqual(template.example, "Start now.")
        self.assertEqual(template.keywords, ["action", "urgency"])
        self.assertEqual(template.semantic_description, "Urgent call to action")
    
    def test_template_equality(self):
        """Test template equality based on id."""
        template1 = TextualTemplate(
            id="TEST_001",
            module_type="hook",
            function="Test",
            structure="[X]",
            length_range=(50, 100),
            tone="test",
            example="Test",
            keywords=[],
            semantic_description="Test",
        )
        
        template2 = TextualTemplate(
            id="TEST_001",
            module_type="insight",
            function="Different",
            structure="[Y]",
            length_range=(100, 200),
            tone="different",
            example="Different",
            keywords=["other"],
            semantic_description="Different",
        )
        
        # Templates with same ID are considered same
        self.assertEqual(template1.id, template2.id)
        # But they are different objects
        self.assertIsNot(template1, template2)
    
    def test_template_as_dict(self):
        """Test converting template to dictionary."""
        template_dict = asdict(self.sample_template)
        
        self.assertIsInstance(template_dict, dict)
        self.assertEqual(template_dict["id"], "TEST_001")
        self.assertEqual(template_dict["module_type"], "hook")
        self.assertEqual(template_dict["length_range"], (50, 100))
        self.assertIsInstance(template_dict["keywords"], list)
    
    def test_template_immutability(self):
        """Test that template fields are accessible but dataclass is frozen-like."""
        # Dataclasses are not frozen by default, but we test access
        self.assertEqual(self.sample_template.id, "TEST_001")
        self.assertEqual(self.sample_template.module_type, "hook")
        
        # Test field access
        self.assertIsNotNone(self.sample_template.function)
        self.assertIsNotNone(self.sample_template.structure)
        self.assertIsNotNone(self.sample_template.length_range)
        self.assertIsNotNone(self.sample_template.tone)
        self.assertIsNotNone(self.sample_template.example)
        self.assertIsNotNone(self.sample_template.keywords)
        self.assertIsNotNone(self.sample_template.semantic_description)
    
    def test_template_with_empty_fields(self):
        """Test template with optional empty fields."""
        template = TextualTemplate(
            id="TEST_EMPTY",
            module_type="cta",
            function="",
            structure="[Action]",
            length_range=(50, 100),
            tone="",
            example="",
            keywords=[],
            semantic_description="",
        )
        
        self.assertEqual(template.id, "TEST_EMPTY")
        self.assertEqual(template.function, "")
        self.assertEqual(template.keywords, [])
        self.assertEqual(template.semantic_description, "")
    
    def test_template_length_range_validation(self):
        """Test that length_range is a tuple of two integers."""
        template = TextualTemplate(
            id="TEST_RANGE",
            module_type="hook",
            function="Test",
            structure="[X]",
            length_range=(60, 120),
            tone="test",
            example="Test example",
            keywords=[],
            semantic_description="Test",
        )
        
        self.assertIsInstance(template.length_range, tuple)
        self.assertEqual(len(template.length_range), 2)
        self.assertIsInstance(template.length_range[0], int)
        self.assertIsInstance(template.length_range[1], int)
        self.assertLess(template.length_range[0], template.length_range[1])


class TestTemplateCollections(unittest.TestCase):
    """Test cases for template collections."""
    
    def test_hook_templates_exist(self):
        """Test that HOOK_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(HOOK_TEMPLATES)
        self.assertIsInstance(HOOK_TEMPLATES, list)
        self.assertGreater(len(HOOK_TEMPLATES), 0)
        
        # Check all are TextualTemplate instances
        for template in HOOK_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "hook")
    
    def test_value_data_templates_exist(self):
        """Test that VALUE_DATA_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(VALUE_DATA_TEMPLATES)
        self.assertIsInstance(VALUE_DATA_TEMPLATES, list)
        self.assertGreater(len(VALUE_DATA_TEMPLATES), 0)
        
        # Check all have insight module_type (data templates map to insight)
        for template in VALUE_DATA_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "insight")
    
    def test_value_insight_templates_exist(self):
        """Test that VALUE_INSIGHT_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(VALUE_INSIGHT_TEMPLATES)
        self.assertIsInstance(VALUE_INSIGHT_TEMPLATES, list)
        self.assertGreater(len(VALUE_INSIGHT_TEMPLATES), 0)
        
        for template in VALUE_INSIGHT_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "insight")
    
    def test_value_solution_templates_exist(self):
        """Test that VALUE_SOLUTION_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(VALUE_SOLUTION_TEMPLATES)
        self.assertIsInstance(VALUE_SOLUTION_TEMPLATES, list)
        self.assertGreater(len(VALUE_SOLUTION_TEMPLATES), 0)
        
        for template in VALUE_SOLUTION_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "solution")
    
    def test_value_example_templates_exist(self):
        """Test that VALUE_EXAMPLE_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(VALUE_EXAMPLE_TEMPLATES)
        self.assertIsInstance(VALUE_EXAMPLE_TEMPLATES, list)
        self.assertGreater(len(VALUE_EXAMPLE_TEMPLATES), 0)
        
        for template in VALUE_EXAMPLE_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "example")
    
    def test_cta_templates_exist(self):
        """Test that CTA_TEMPLATES is defined and non-empty."""
        self.assertIsNotNone(CTA_TEMPLATES)
        self.assertIsInstance(CTA_TEMPLATES, list)
        self.assertGreater(len(CTA_TEMPLATES), 0)
        
        for template in CTA_TEMPLATES:
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.module_type, "cta")
    
    def test_all_templates_have_unique_ids(self):
        """Test that all templates have unique IDs."""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        
        template_ids = [t.id for t in all_templates]
        unique_ids = set(template_ids)
        
        # If all IDs are unique, length should match
        self.assertEqual(len(template_ids), len(unique_ids), 
                        f"Duplicate IDs found: {[id for id in template_ids if template_ids.count(id) > 1]}")
    
    def test_all_templates_have_required_fields(self):
        """Test that all templates have required fields."""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        
        required_fields = [
            "id", "module_type", "function", "structure",
            "length_range", "tone", "example", "keywords",
            "semantic_description"
        ]
        
        for template in all_templates:
            for field in required_fields:
                self.assertTrue(hasattr(template, field), 
                              f"Template {template.id} missing field: {field}")
                # Fields should not be None (empty string/empty list is OK)
                value = getattr(template, field)
                self.assertIsNotNone(value, 
                                    f"Template {template.id} has None value for field: {field}")
    
    def test_template_ids_follow_pattern(self):
        """Test that template IDs follow expected patterns."""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        
        for template in all_templates:
            # IDs should not be empty
            self.assertGreater(len(template.id), 0, 
                             f"Template has empty ID: {template}")
            
            # IDs should contain at least one underscore or alphanumeric
            self.assertTrue(any(c.isalnum() or c == '_' for c in template.id),
                          f"Template ID has invalid characters: {template.id}")
    
    def test_template_length_ranges_are_valid(self):
        """Test that all template length ranges are valid."""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        
        for template in all_templates:
            min_len, max_len = template.length_range
            
            # Min should be positive
            self.assertGreater(min_len, 0, 
                             f"Template {template.id} has non-positive min length")
            
            # Max should be greater than min
            self.assertGreater(max_len, min_len,
                             f"Template {template.id} has max <= min length")
            
            # Reasonable upper bound (templates shouldn't be extremely long)
            self.assertLess(max_len, 1000,
                          f"Template {template.id} has unreasonably large max length")
    
    def test_template_examples_are_strings(self):
        """Test that all template examples are non-empty strings."""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        
        for template in all_templates:
            self.assertIsInstance(template.example, str)
            self.assertGreater(len(template.example), 0,
                             f"Template {template.id} has empty example")


if __name__ == "__main__":
    unittest.main()
