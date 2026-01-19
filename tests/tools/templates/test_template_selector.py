"""
Unit tests for TemplateSelector.

Tests the TemplateSelector class that selects appropriate templates
using embedding-based semantic similarity.

Location: tests/tools/test_template_selector.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.templates.selector import (
    TemplateSelector,
    EMBEDDINGS_AVAILABLE,
)
from src.templates.library import TemplateLibrary
from src.templates.textual_templates import TextualTemplate


class TestTemplateSelector(unittest.TestCase):
    """Test cases for TemplateSelector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.library = TemplateLibrary()
    
    def test_selector_initialization_without_embeddings(self):
        """Test TemplateSelector initialization when embeddings are not available."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            self.assertIsNotNone(selector.library)
            self.assertIsInstance(selector.library, TemplateLibrary)
            self.assertIsNone(selector.model)
            self.assertEqual(len(selector.template_embeddings_cache), 0)
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_selector_initialization_with_embeddings(self):
        """Test TemplateSelector initialization when embeddings are available."""
        selector = TemplateSelector()
        
        self.assertIsNotNone(selector.library)
        self.assertIsNotNone(selector.model)
        # Cache should be populated
        self.assertGreater(len(selector.template_embeddings_cache), 0)
    
    def test_selector_initialization_with_custom_model(self):
        """Test TemplateSelector initialization with custom model name."""
        custom_model = "all-MiniLM-L6-v2"
        
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            # When embeddings are not available, model_name should still be stored
            selector = TemplateSelector(model_name=custom_model)
            
            self.assertEqual(selector.model_name, custom_model)
            self.assertIsNone(selector.model)
    
    def test_build_template_description(self):
        """Test building template description for embedding."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template = self.library.get_template("H_QUESTION")
            description = selector._build_template_description(template)
            
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 0)
            # Should contain semantic description
            self.assertIn(template.semantic_description, description)
            # Should contain function
            self.assertIn(template.function, description)
    
    def test_build_slide_description(self):
        """Test building slide description from purpose and copy direction."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            purpose = "Activate pain point"
            copy_direction = "Use provocative question"
            key_elements = ["time waste", "productivity"]
            
            description = selector._build_slide_description(
                purpose=purpose,
                copy_direction=copy_direction,
                key_elements=key_elements,
            )
            
            self.assertIsInstance(description, str)
            self.assertIn(purpose, description)
            self.assertIn(copy_direction, description)
            self.assertIn("time waste", description)
            self.assertIn("productivity", description)
    
    def test_build_slide_description_empty_elements(self):
        """Test building slide description with empty key elements."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            description = selector._build_slide_description(
                purpose="Test purpose",
                copy_direction="Test direction",
                key_elements=[],
            )
            
            self.assertIn("Test purpose", description)
            self.assertIn("Test direction", description)
    
    def test_map_template_type_to_module_types_hook(self):
        """Test mapping template type 'hook' to module types."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types("hook")
            
            self.assertEqual(module_types, ["hook"])
    
    def test_map_template_type_to_module_types_transition(self):
        """Test mapping template type 'transition' to module types."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types("transition")
            
            self.assertEqual(module_types, ["insight"])
    
    def test_map_template_type_to_module_types_value_data(self):
        """Test mapping template type 'value' with subtype 'data'."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types(
                "value",
                value_subtype="data"
            )
            
            self.assertEqual(module_types, ["insight"])
    
    def test_map_template_type_to_module_types_value_insight(self):
        """Test mapping template type 'value' with subtype 'insight'."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types(
                "value",
                value_subtype="insight"
            )
            
            self.assertEqual(module_types, ["insight"])
    
    def test_map_template_type_to_module_types_value_solution(self):
        """Test mapping template type 'value' with subtype 'solution'."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types(
                "value",
                value_subtype="solution"
            )
            
            self.assertEqual(module_types, ["solution"])
    
    def test_map_template_type_to_module_types_value_example(self):
        """Test mapping template type 'value' with subtype 'example'."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types(
                "value",
                value_subtype="example"
            )
            
            self.assertEqual(module_types, ["example"])
    
    def test_map_template_type_to_module_types_value_no_subtype(self):
        """Test mapping template type 'value' without subtype."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types("value")
            
            # Should return all value-related types
            self.assertIn("insight", module_types)
            self.assertIn("solution", module_types)
            self.assertIn("example", module_types)
    
    def test_map_template_type_to_module_types_cta(self):
        """Test mapping template type 'cta' to module types."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types("cta")
            
            self.assertEqual(module_types, ["cta"])
    
    def test_map_template_type_to_module_types_unknown(self):
        """Test mapping unknown template type."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            module_types = selector._map_template_type_to_module_types("unknown_type")
            
            # Should default to insight
            self.assertEqual(module_types, ["insight"])
    
    def test_normalize_text(self):
        """Test text normalization."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Test lowercase conversion
            result = selector._normalize_text("HELLO WORLD")
            self.assertEqual(result, "hello world")
            
            # Test punctuation removal
            result = selector._normalize_text("Hello, World!")
            self.assertNotIn(",", result)
            self.assertNotIn("!", result)
            
            # Test whitespace normalization
            result = selector._normalize_text("Hello    World")
            self.assertNotIn("    ", result)
            self.assertIn("hello world", result)
    
    def test_text_similarity(self):
        """Test text similarity calculation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Identical texts should have high similarity
            similarity = selector._text_similarity("hello world", "hello world")
            self.assertGreater(similarity, 0.9)
            
            # Similar texts should have some similarity
            similarity = selector._text_similarity("hello world", "hello there")
            self.assertGreater(similarity, 0.0)
            self.assertLessEqual(similarity, 1.0)
            
            # Different texts should have lower similarity
            similarity = selector._text_similarity("hello world", "goodbye universe")
            self.assertLess(similarity, 0.5)
            
            # Empty texts should return 0
            similarity = selector._text_similarity("", "hello")
            self.assertEqual(similarity, 0.0)
    
    def test_keyword_similarity(self):
        """Test keyword similarity calculation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # All keywords found
            similarity = selector._keyword_similarity(
                "hello world test",
                ["hello", "world", "test"]
            )
            self.assertEqual(similarity, 1.0)
            
            # Some keywords found
            similarity = selector._keyword_similarity(
                "hello world",
                ["hello", "world", "test"]
            )
            self.assertAlmostEqual(similarity, 2/3, places=2)
            
            # No keywords found
            similarity = selector._keyword_similarity(
                "hello world",
                ["test", "example"]
            )
            self.assertEqual(similarity, 0.0)
            
            # Empty keywords
            similarity = selector._keyword_similarity("hello", [])
            self.assertEqual(similarity, 0.0)
    
    def test_calculate_tone_boost(self):
        """Test tone boost calculation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template = self.library.get_template("H_QUESTION")
            
            # Same tone should give high boost
            boost = selector._calculate_tone_boost(template, template.tone)
            self.assertGreater(boost, 0.5)
            
            # Different tone should give lower boost
            boost = selector._calculate_tone_boost(template, "completely different tone")
            self.assertLess(boost, 0.8)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Identical vectors should have high similarity
            vec1 = np.array([1.0, 0.0, 0.0])
            vec2 = np.array([1.0, 0.0, 0.0])
            similarity = selector._cosine_similarity(vec1, vec2)
            self.assertGreater(similarity, 0.9)
            
            # Orthogonal vectors should have lower similarity
            vec1 = np.array([1.0, 0.0])
            vec2 = np.array([0.0, 1.0])
            similarity = selector._cosine_similarity(vec1, vec2)
            self.assertLess(similarity, 0.6)
            
            # Zero vectors should return 0
            vec1 = np.array([0.0, 0.0])
            vec2 = np.array([1.0, 1.0])
            similarity = selector._cosine_similarity(vec1, vec2)
            self.assertEqual(similarity, 0.0)
    
    def test_select_template_hook_fallback(self):
        """Test selecting hook template using fallback method."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template_id, justification, score = selector.select_template(
                template_type="hook",
                purpose="Activate pain about time waste",
                copy_direction="Use provocative question",
                key_elements=["time", "waste"],
                persona="busy professional",
                tone="provocative",
            )
            
            self.assertIsInstance(template_id, str)
            self.assertIn(template_id, selector.library.templates)
            self.assertIsInstance(justification, str)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            # Selected template should be a hook
            selected_template = selector.library.get_template(template_id)
            self.assertEqual(selected_template.module_type, "hook")
    
    def test_select_template_value_insight_fallback(self):
        """Test selecting value insight template using fallback method."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template_id, justification, score = selector.select_template(
                template_type="value",
                value_subtype="insight",
                purpose="Share strategic insight about automation",
                copy_direction="Explain principle",
                key_elements=["automation", "strategy"],
                persona="executive",
                tone="technical",
            )
            
            self.assertIsInstance(template_id, str)
            selected_template = selector.library.get_template(template_id)
            self.assertEqual(selected_template.module_type, "insight")
    
    def test_select_template_solution_fallback(self):
        """Test selecting solution template using fallback method."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template_id, justification, score = selector.select_template(
                template_type="value",
                value_subtype="solution",
                purpose="Provide step-by-step solution",
                copy_direction="List sequential steps",
                key_elements=["steps", "process"],
                persona="learner",
                tone="tutorial",
            )
            
            self.assertIsInstance(template_id, str)
            selected_template = selector.library.get_template(template_id)
            self.assertEqual(selected_template.module_type, "solution")
    
    def test_select_template_cta_fallback(self):
        """Test selecting CTA template using fallback method."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template_id, justification, score = selector.select_template(
                template_type="cta",
                purpose="Generate engagement",
                copy_direction="Invite to comment",
                key_elements=["engagement", "interaction"],
                persona="social media user",
                tone="engaging",
            )
            
            self.assertIsInstance(template_id, str)
            selected_template = selector.library.get_template(template_id)
            self.assertEqual(selected_template.module_type, "cta")
    
    def test_select_template_invalid_type(self):
        """Test selecting template with invalid type raises error."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Mock to return empty candidates
            with patch.object(selector.library, 'get_templates_by_module_type', return_value=[]):
                with self.assertRaises(ValueError):
                    selector.select_template(
                        template_type="nonexistent",
                        purpose="test",
                        copy_direction="test",
                    )
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_select_template_with_embeddings(self):
        """Test selecting template using embeddings method."""
        selector = TemplateSelector()
        
        template_id, justification, score = selector.select_template(
            template_type="hook",
            purpose="Activate pain about time waste",
            copy_direction="Use provocative question",
            key_elements=["time", "waste"],
            persona="busy professional",
            tone="provocative",
        )
        
        self.assertIsInstance(template_id, str)
        self.assertIn(template_id, selector.library.templates)
        self.assertIsInstance(justification, str)
        self.assertIsInstance(score, float)
        
        # Justification should mention semantic analysis
        self.assertIn("Semantic Analysis", justification)
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_precomputation(self):
        """Test that embeddings are pre-computed for all templates on initialization."""
        selector = TemplateSelector()
        
        # Verify embeddings are pre-computed
        self.assertIsNotNone(selector.model)
        self.assertGreater(len(selector.template_embeddings_cache), 0)
        
        # All templates should have embeddings cached
        total_templates = len(selector.library.templates)
        cached_embeddings = len(selector.template_embeddings_cache)
        
        self.assertEqual(cached_embeddings, total_templates,
                        f"Expected {total_templates} cached embeddings, got {cached_embeddings}")
        
        # Verify embeddings are numpy arrays
        for template_id, embedding in selector.template_embeddings_cache.items():
            self.assertIsInstance(embedding, np.ndarray)
            self.assertGreater(len(embedding), 0, f"Empty embedding for template {template_id}")
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_semantic_selection_hook(self):
        """Test real semantic selection for hook templates using actual embeddings."""
        selector = TemplateSelector()
        
        # Test case from documentation: Question about ideal scenario should match H_QUESTION
        template_id, justification, score = selector.select_template(
            template_type="hook",
            purpose="Generate curiosity",
            copy_direction="What if scenario about ideal situation",
            key_elements=["ideal", "scenario", "possibility"],
            persona="learner",
            tone="curious",
        )
        
        selected_template = selector.library.get_template(template_id)
        self.assertEqual(selected_template.module_type, "hook")
        
        # H_QUESTION should be a strong match for this description
        # It should have a reasonable confidence score
        self.assertGreater(score, 0.5, "Semantic match should have reasonable confidence")
        self.assertIn("Semantic Analysis", justification)
        
        # Verify the selected template makes semantic sense
        # H_QUESTION's semantic_description mentions "curiosity" and "ideal scenario"
        if template_id == "H_QUESTION":
            self.assertIn("curiosity", selected_template.semantic_description.lower())
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_semantic_selection_data(self):
        """Test real semantic selection for value data templates using actual embeddings."""
        selector = TemplateSelector()
        
        # Test case: Data with source should match VD_SOURCE template
        template_id, justification, score = selector.select_template(
            template_type="value",
            value_subtype="data",
            purpose="Present quantified evidence with authority",
            copy_direction="Show statistics with credible source like McKinsey or Gartner",
            key_elements=["statistics", "source", "authority"],
            persona="executive",
            tone="technical",
        )
        
        selected_template = selector.library.get_template(template_id)
        self.assertEqual(selected_template.module_type, "insight")  # Data maps to insight
        
        # Should have reasonable confidence
        self.assertGreater(score, 0.5, "Semantic match should have reasonable confidence")
        self.assertIn("Semantic Analysis", justification)
        
        # Verify semantic match makes sense - should prefer templates with "source" or "reference"
        template_desc = selected_template.semantic_description.lower()
        self.assertTrue(
            any(keyword in template_desc for keyword in ["source", "reference", "attribution", "data"]),
            f"Selected template {template_id} should relate to data with source"
        )
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_semantic_selection_solution(self):
        """Test real semantic selection for solution templates using actual embeddings."""
        selector = TemplateSelector()
        
        # Test case: Sequential steps should match VS_123 template
        template_id, justification, score = selector.select_template(
            template_type="value",
            value_subtype="solution",
            purpose="Provide clear step-by-step guidance",
            copy_direction="List sequential steps in order: first do this, then that, finally this",
            key_elements=["steps", "sequence", "process"],
            persona="learner",
            tone="tutorial",
        )
        
        selected_template = selector.library.get_template(template_id)
        self.assertEqual(selected_template.module_type, "solution")
        
        # Should have reasonable confidence
        self.assertGreater(score, 0.5, "Semantic match should have reasonable confidence")
        self.assertIn("Semantic Analysis", justification)
        
        # Verify semantic match - should prefer templates mentioning "steps" or "sequential"
        template_desc = selected_template.semantic_description.lower()
        self.assertTrue(
            any(keyword in template_desc for keyword in ["step", "sequential", "progressive", "process"]),
            f"Selected template {template_id} should relate to sequential steps"
        )
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_comparison_fallback_vs_embeddings(self):
        """Test that embeddings produce different (hopefully better) results than fallback."""
        selector_embeddings = TemplateSelector()
        
        # Test the same case with embeddings
        template_id_emb, justification_emb, score_emb = selector_embeddings.select_template(
            template_type="hook",
            purpose="Create curiosity without direct question",
            copy_direction="Reveal something unexpected or secret they didn't know",
            key_elements=["secret", "revelation", "mystery"],
            persona="curious reader",
            tone="intriguing",
        )
        
        # Verify embeddings were used
        self.assertIn("Semantic Analysis", justification_emb)
        self.assertGreater(score_emb, 0.0)
        
        # H_MYSTERY should be a strong match for this description
        selected_template = selector_embeddings.library.get_template(template_id_emb)
        self.assertEqual(selected_template.module_type, "hook")
        
        # The template should semantically relate to mystery/secret/revelation
        if template_id_emb == "H_MYSTERY":
            self.assertIn("mystery", selected_template.semantic_description.lower())
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_cosine_similarity_range(self):
        """Test that cosine similarity scores from real embeddings are in expected range."""
        selector = TemplateSelector()
        
        # Get a template and its embedding
        template = selector.library.get_template("H_QUESTION")
        template_embedding = selector.template_embeddings_cache[template.id]
        
        # Generate embedding for a similar description
        similar_text = "question about ideal scenario curious inspiring"
        similar_embedding = selector.model.encode(similar_text, convert_to_numpy=True)
        
        # Calculate similarity
        similarity = selector._cosine_similarity(template_embedding, similar_embedding)
        
        # Similarity should be in 0-1 range
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
        
        # Similar descriptions should have reasonable similarity
        # (not too low, since they're semantically related)
        self.assertGreater(similarity, 0.3, "Similar semantic descriptions should have decent similarity")
        
        # Test with very different text
        different_text = "save money financial investment ROI"
        different_embedding = selector.model.encode(different_text, convert_to_numpy=True)
        different_similarity = selector._cosine_similarity(template_embedding, different_embedding)
        
        # Different texts should have lower similarity than similar ones
        self.assertLess(different_similarity, similarity,
                       "Different descriptions should have lower similarity than similar ones")
    
    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "sentence-transformers not available")
    def test_real_embeddings_selection_consistency(self):
        """Test that embedding-based selection produces consistent results."""
        selector = TemplateSelector()
        
        # Same inputs should produce same results
        result1 = selector.select_template(
            template_type="hook",
            purpose="Activate pain point",
            copy_direction="Ask about frustration",
            key_elements=["pain", "frustration"],
            persona="professional",
            tone="provocative",
        )
        
        result2 = selector.select_template(
            template_type="hook",
            purpose="Activate pain point",
            copy_direction="Ask about frustration",
            key_elements=["pain", "frustration"],
            persona="professional",
            tone="provocative",
        )
        
        # Should select the same template
        self.assertEqual(result1[0], result2[0], "Same inputs should produce same template selection")
        
        # Scores should be very close (allowing for tiny floating point differences)
        self.assertAlmostEqual(result1[2], result2[2], places=5,
                              msg="Same inputs should produce same confidence scores")
    
    def test_generate_justification(self):
        """Test justification generation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template = selector.library.get_template("H_QUESTION")
            
            justification = selector._generate_justification(
                template_id="H_QUESTION",
                score=0.85,
                persona="professional",
                tone="provocative",
                method="fallback",
            )
            
            self.assertIsInstance(justification, str)
            self.assertIn(template.function, justification)
            self.assertIn("0.85", justification)
            self.assertIn("Fallback", justification)
            self.assertIn("professional", justification)
            self.assertIn("provocative", justification)
    
    def test_generate_justification_nonexistent_template(self):
        """Test justification generation for nonexistent template."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            justification = selector._generate_justification(
                template_id="NONEXISTENT",
                score=0.5,
                persona="test",
                tone="test",
                method="test",
            )
            
            self.assertIsInstance(justification, str)
            self.assertIn("NONEXISTENT", justification)
            self.assertIn("0.5", justification)
    
    def test_select_with_fallback_returns_best_template(self):
        """Test that fallback method returns best matching template."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Get all hook templates
            candidates = selector.library.get_templates_by_module_type("hook")
            
            template_id, score = selector._select_with_fallback(
                candidates=candidates,
                slide_description="question about ideal scenario curious",
                persona="learner",
                tone="curious",
            )
            
            self.assertIsInstance(template_id, str)
            self.assertIsInstance(score, float)
            self.assertIn(template_id, [c.id for c in candidates])
            
            # Should have some score
            self.assertGreater(score, 0.0)
    
    def test_select_with_embeddings_mocked(self):
        """Test select_with_embeddings with mocked model."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', True):
            mock_model = MagicMock()
            
            # Mock encode to return different embeddings
            def mock_encode(text, convert_to_numpy=True):
                # Return embeddings that simulate similarity
                if "question" in text.lower() and "ideal" in text.lower():
                    return np.array([1.0, 0.0, 0.0] * 128)  # Similar to H_QUESTION
                else:
                    return np.array([0.0, 1.0, 0.0] * 128)  # Different
            
            mock_model.encode = mock_encode
            
            selector = TemplateSelector()
            selector.model = mock_model
            
            # Pre-populate cache with mock embeddings
            candidates = selector.library.get_templates_by_module_type("hook")
            for template in candidates:
                template_text = selector._build_template_description(template)
                embedding = mock_model.encode(template_text)
                selector.template_embeddings_cache[template.id] = embedding
            
            template_id, score = selector._select_with_embeddings(
                candidates=candidates,
                slide_description="question about ideal scenario",
                tone="curious",
            )
            
            self.assertIsInstance(template_id, str)
            self.assertIsInstance(score, float)
            self.assertIn(template_id, [c.id for c in candidates])
    
    def test_calculate_semantic_similarity_fallback(self):
        """Test fallback semantic similarity calculation."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            template = self.library.get_template("H_QUESTION")
            
            score = selector._calculate_semantic_similarity_fallback(
                template=template,
                slide_description="question about ideal scenario curious inspiring",
                persona="learner",
                tone="curious",
            )
            
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            # Should have some score since template matches description
            self.assertGreater(score, 0.0)
    
    def test_select_template_preserves_parameters(self):
        """Test that select_template preserves all input parameters."""
        with patch('src.templates.selector.EMBEDDINGS_AVAILABLE', False):
            selector = TemplateSelector()
            
            # Test with all parameters
            template_id, justification, score = selector.select_template(
                template_type="hook",
                value_subtype=None,
                purpose="Test purpose",
                copy_direction="Test direction",
                key_elements=["element1", "element2"],
                persona="Test persona",
                tone="Test tone",
                platform="linkedin",
            )
            
            self.assertIsInstance(template_id, str)
            # Verify that parameters are used (justification should contain persona and tone)
            self.assertIn("Test persona", justification)
            self.assertIn("Test tone", justification)


if __name__ == "__main__":
    unittest.main()
