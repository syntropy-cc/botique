"""
Unit tests for TemplateLibrary.

Tests the TemplateLibrary class that manages textual/narrative templates
and provides access methods.

Location: tests/tools/test_template_library.py
"""

import unittest
from unittest.mock import patch

from src.templates.library import TemplateLibrary
from src.templates.textual_templates import (
    TextualTemplate,
    HOOK_TEMPLATES,
    VALUE_DATA_TEMPLATES,
    VALUE_INSIGHT_TEMPLATES,
    VALUE_SOLUTION_TEMPLATES,
    VALUE_EXAMPLE_TEMPLATES,
    CTA_TEMPLATES,
)


class TestTemplateLibrary(unittest.TestCase):
    """Test cases for TemplateLibrary."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.library = TemplateLibrary()
        
        # Get all expected templates
        self.all_expected_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
    
    def test_library_initialization(self):
        """Test TemplateLibrary initialization."""
        library = TemplateLibrary()
        
        self.assertIsNotNone(library.templates)
        self.assertIsInstance(library.templates, dict)
        self.assertGreater(len(library.templates), 0)
    
    def test_all_templates_loaded(self):
        """Test that all templates are loaded into the library."""
        expected_count = len(self.all_expected_templates)
        actual_count = len(self.library.templates)
        
        self.assertEqual(actual_count, expected_count,
                        f"Expected {expected_count} templates, got {actual_count}")
    
    def test_templates_are_indexed_by_id(self):
        """Test that templates are indexed by their ID."""
        for expected_template in self.all_expected_templates:
            template_id = expected_template.id
            self.assertIn(template_id, self.library.templates,
                         f"Template {template_id} not found in library")
            
            retrieved_template = self.library.templates[template_id]
            self.assertEqual(retrieved_template.id, expected_template.id)
            self.assertEqual(retrieved_template.module_type, expected_template.module_type)
    
    def test_get_template_existing(self):
        """Test getting an existing template by ID."""
        # Get first hook template as test case
        test_template = HOOK_TEMPLATES[0]
        template_id = test_template.id
        
        retrieved = self.library.get_template(template_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, test_template.id)
        self.assertEqual(retrieved.module_type, test_template.module_type)
        self.assertEqual(retrieved.function, test_template.function)
    
    def test_get_template_nonexistent(self):
        """Test getting a non-existent template returns None."""
        retrieved = self.library.get_template("NONEXISTENT_TEMPLATE_ID")
        
        self.assertIsNone(retrieved)
    
    def test_get_template_empty_string(self):
        """Test getting template with empty string ID."""
        retrieved = self.library.get_template("")
        
        self.assertIsNone(retrieved)
    
    def test_get_templates_by_module_type_hook(self):
        """Test getting templates by module type: hook."""
        hook_templates = self.library.get_templates_by_module_type("hook")
        
        self.assertIsInstance(hook_templates, list)
        self.assertGreater(len(hook_templates), 0)
        
        # All returned templates should be hook type
        for template in hook_templates:
            self.assertEqual(template.module_type, "hook")
        
        # Should match expected count
        expected_hook_count = len(HOOK_TEMPLATES)
        self.assertEqual(len(hook_templates), expected_hook_count)
    
    def test_get_templates_by_module_type_insight(self):
        """Test getting templates by module type: insight."""
        insight_templates = self.library.get_templates_by_module_type("insight")
        
        self.assertIsInstance(insight_templates, list)
        self.assertGreater(len(insight_templates), 0)
        
        # All returned templates should be insight type
        for template in insight_templates:
            self.assertEqual(template.module_type, "insight")
        
        # Should include both VALUE_DATA and VALUE_INSIGHT (both map to insight)
        expected_insight_count = len(VALUE_DATA_TEMPLATES) + len(VALUE_INSIGHT_TEMPLATES)
        self.assertEqual(len(insight_templates), expected_insight_count)
    
    def test_get_templates_by_module_type_solution(self):
        """Test getting templates by module type: solution."""
        solution_templates = self.library.get_templates_by_module_type("solution")
        
        self.assertIsInstance(solution_templates, list)
        self.assertGreater(len(solution_templates), 0)
        
        for template in solution_templates:
            self.assertEqual(template.module_type, "solution")
        
        expected_solution_count = len(VALUE_SOLUTION_TEMPLATES)
        self.assertEqual(len(solution_templates), expected_solution_count)
    
    def test_get_templates_by_module_type_example(self):
        """Test getting templates by module type: example."""
        example_templates = self.library.get_templates_by_module_type("example")
        
        self.assertIsInstance(example_templates, list)
        self.assertGreater(len(example_templates), 0)
        
        for template in example_templates:
            self.assertEqual(template.module_type, "example")
        
        expected_example_count = len(VALUE_EXAMPLE_TEMPLATES)
        self.assertEqual(len(example_templates), expected_example_count)
    
    def test_get_templates_by_module_type_cta(self):
        """Test getting templates by module type: cta."""
        cta_templates = self.library.get_templates_by_module_type("cta")
        
        self.assertIsInstance(cta_templates, list)
        self.assertGreater(len(cta_templates), 0)
        
        for template in cta_templates:
            self.assertEqual(template.module_type, "cta")
        
        expected_cta_count = len(CTA_TEMPLATES)
        self.assertEqual(len(cta_templates), expected_cta_count)
    
    def test_get_templates_by_module_type_nonexistent(self):
        """Test getting templates by non-existent module type."""
        templates = self.library.get_templates_by_module_type("nonexistent_type")
        
        self.assertIsInstance(templates, list)
        self.assertEqual(len(templates), 0)
    
    def test_get_templates_for_ids_single(self):
        """Test getting templates for a single ID."""
        test_id = HOOK_TEMPLATES[0].id
        
        templates = self.library.get_templates_for_ids([test_id])
        
        self.assertIsInstance(templates, list)
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, test_id)
    
    def test_get_templates_for_ids_multiple(self):
        """Test getting templates for multiple IDs."""
        test_ids = [
            HOOK_TEMPLATES[0].id,
            VALUE_INSIGHT_TEMPLATES[0].id,
            CTA_TEMPLATES[0].id,
        ]
        
        templates = self.library.get_templates_for_ids(test_ids)
        
        self.assertIsInstance(templates, list)
        self.assertEqual(len(templates), 3)
        
        # Verify all requested IDs are present
        retrieved_ids = [t.id for t in templates]
        for test_id in test_ids:
            self.assertIn(test_id, retrieved_ids)
    
    def test_get_templates_for_ids_preserves_order(self):
        """Test that get_templates_for_ids preserves order of input IDs."""
        test_ids = [
            CTA_TEMPLATES[0].id,
            HOOK_TEMPLATES[0].id,
            VALUE_INSIGHT_TEMPLATES[0].id,
        ]
        
        templates = self.library.get_templates_for_ids(test_ids)
        
        # Verify order is preserved
        for i, test_id in enumerate(test_ids):
            self.assertEqual(templates[i].id, test_id)
    
    def test_get_templates_for_ids_with_nonexistent(self):
        """Test getting templates when some IDs don't exist."""
        test_ids = [
            HOOK_TEMPLATES[0].id,
            "NONEXISTENT_ID",
            CTA_TEMPLATES[0].id,
        ]
        
        templates = self.library.get_templates_for_ids(test_ids)
        
        # Should only return templates that exist
        self.assertEqual(len(templates), 2)
        retrieved_ids = [t.id for t in templates]
        self.assertIn(HOOK_TEMPLATES[0].id, retrieved_ids)
        self.assertIn(CTA_TEMPLATES[0].id, retrieved_ids)
        self.assertNotIn("NONEXISTENT_ID", retrieved_ids)
    
    def test_get_templates_for_ids_empty_list(self):
        """Test getting templates for empty list."""
        templates = self.library.get_templates_for_ids([])
        
        self.assertIsInstance(templates, list)
        self.assertEqual(len(templates), 0)
    
    def test_get_templates_for_ids_all_nonexistent(self):
        """Test getting templates when all IDs are nonexistent."""
        templates = self.library.get_templates_for_ids(["ID1", "ID2", "ID3"])
        
        self.assertIsInstance(templates, list)
        self.assertEqual(len(templates), 0)
    
    def test_to_detailed_reference_single_template(self):
        """Test generating detailed reference for single template."""
        test_id = HOOK_TEMPLATES[0].id
        
        reference = self.library.to_detailed_reference([test_id])
        
        self.assertIsInstance(reference, str)
        self.assertIn("SELECTED TEXTUAL TEMPLATES", reference)
        self.assertIn(test_id, reference)
    
    def test_to_detailed_reference_multiple_templates(self):
        """Test generating detailed reference for multiple templates."""
        test_ids = [
            HOOK_TEMPLATES[0].id,
            VALUE_INSIGHT_TEMPLATES[0].id,
            CTA_TEMPLATES[0].id,
        ]
        
        reference = self.library.to_detailed_reference(test_ids)
        
        self.assertIsInstance(reference, str)
        self.assertIn("SELECTED TEXTUAL TEMPLATES", reference)
        
        # Should contain all template IDs
        for test_id in test_ids:
            self.assertIn(test_id, reference)
    
    def test_to_detailed_reference_includes_structure(self):
        """Test that detailed reference includes structure information."""
        test_id = HOOK_TEMPLATES[0].id
        template = self.library.get_template(test_id)
        
        reference = self.library.to_detailed_reference([test_id])
        
        self.assertIn("Structure:", reference)
        self.assertIn(template.structure, reference)
    
    def test_to_detailed_reference_includes_length_range(self):
        """Test that detailed reference includes length range."""
        test_id = HOOK_TEMPLATES[0].id
        template = self.library.get_template(test_id)
        
        reference = self.library.to_detailed_reference([test_id])
        
        self.assertIn("Length:", reference)
        self.assertIn(str(template.length_range[0]), reference)
        self.assertIn(str(template.length_range[1]), reference)
    
    def test_to_detailed_reference_includes_tone(self):
        """Test that detailed reference includes tone."""
        test_id = HOOK_TEMPLATES[0].id
        template = self.library.get_template(test_id)
        
        reference = self.library.to_detailed_reference([test_id])
        
        self.assertIn("Tone:", reference)
        # Tone text should be present (may be substring of template.tone)
        self.assertTrue(any(word in reference.lower() for word in template.tone.lower().split()))
    
    def test_to_detailed_reference_includes_example(self):
        """Test that detailed reference includes example."""
        test_id = HOOK_TEMPLATES[0].id
        template = self.library.get_template(test_id)
        
        reference = self.library.to_detailed_reference([test_id])
        
        self.assertIn("Example:", reference)
        self.assertIn(template.example, reference)
    
    def test_to_detailed_reference_groups_by_type(self):
        """Test that detailed reference groups templates by module type."""
        test_ids = [
            HOOK_TEMPLATES[0].id,
            HOOK_TEMPLATES[1].id,
            CTA_TEMPLATES[0].id,
            VALUE_INSIGHT_TEMPLATES[0].id,
        ]
        
        reference = self.library.to_detailed_reference(test_ids)
        
        # Should have section headers for different types
        self.assertIn("HOOK", reference)
        self.assertIn("CTA", reference)
        # Insight section might be labeled differently
        self.assertIn("VALUE: Insight/Data", reference)
    
    def test_to_detailed_reference_empty_list(self):
        """Test generating detailed reference for empty list."""
        reference = self.library.to_detailed_reference([])
        
        self.assertIsInstance(reference, str)
        self.assertIn("(no templates selected)", reference)
    
    def test_to_detailed_reference_all_nonexistent(self):
        """Test generating detailed reference when all IDs are nonexistent."""
        reference = self.library.to_detailed_reference(["ID1", "ID2"])
        
        self.assertIsInstance(reference, str)
        self.assertIn("(no templates selected)", reference)
    
    def test_to_detailed_reference_markdown_format(self):
        """Test that detailed reference is in markdown format."""
        test_id = HOOK_TEMPLATES[0].id
        
        reference = self.library.to_detailed_reference([test_id])
        
        # Should have markdown headers
        self.assertIn("##", reference)
        # Should have markdown list items
        self.assertIn("- **", reference)
        # Should have markdown sub-items
        self.assertIn("  -", reference)
    
    def test_library_is_singleton_behavior(self):
        """Test that library loads templates consistently across instances."""
        library1 = TemplateLibrary()
        library2 = TemplateLibrary()
        
        # Both should have same number of templates
        self.assertEqual(len(library1.templates), len(library2.templates))
        
        # Same template should be retrievable from both
        test_id = HOOK_TEMPLATES[0].id
        template1 = library1.get_template(test_id)
        template2 = library2.get_template(test_id)
        
        self.assertEqual(template1.id, template2.id)
        self.assertEqual(template1.function, template2.function)
    
    def test_templates_dictionary_mutability(self):
        """Test that templates dictionary can be accessed and is properly structured."""
        # Should be able to iterate over templates
        template_count = 0
        for template_id, template in self.library.templates.items():
            template_count += 1
            self.assertIsInstance(template_id, str)
            self.assertIsInstance(template, TextualTemplate)
            self.assertEqual(template.id, template_id)
        
        self.assertGreater(template_count, 0)


if __name__ == "__main__":
    unittest.main()
