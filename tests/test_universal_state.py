"""
Unit tests for UniversalState.

Tests the universal state Ω implementation that encapsulates
CoherenceBrief + SQLite as formal state.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.universal_state import UniversalState
from src.coherence.brief import CoherenceBrief


class TestUniversalState(unittest.TestCase):
    """Test cases for UniversalState."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = UniversalState()
        self.test_post_id = "post_test_001"
        self.test_article_slug = "test_article"
        
        # Create a mock CoherenceBrief for testing
        self.mock_brief = Mock(spec=CoherenceBrief)
        self.mock_brief.post_id = self.test_post_id
    
    def test_initialization(self):
        """Test UniversalState initialization."""
        state = UniversalState()
        self.assertEqual(len(state.coherence_briefs), 0)
        self.assertIsNone(state.article_slug)
        self.assertIsNone(state.current_trace_id)
    
    def test_store_and_get_brief(self):
        """Test storing and retrieving briefs."""
        # Store brief
        self.state.store_brief(self.mock_brief)
        
        # Retrieve brief
        retrieved = self.state.get_brief(self.test_post_id)
        self.assertEqual(retrieved, self.mock_brief)
        
        # Non-existent brief
        self.assertIsNone(self.state.get_brief("nonexistent"))
    
    def test_store_brief_validates_post_id(self):
        """Test that store_brief validates post_id attribute."""
        invalid_brief = Mock()  # No post_id attribute
        with self.assertRaises(ValueError):
            self.state.store_brief(invalid_brief)
    
    def test_get_all_briefs(self):
        """Test getting all briefs."""
        # Store multiple briefs
        brief1 = Mock(spec=CoherenceBrief)
        brief1.post_id = "post_article_001"
        brief2 = Mock(spec=CoherenceBrief)
        brief2.post_id = "post_article_002"
        
        self.state.store_brief(brief1)
        self.state.store_brief(brief2)
        
        # Get all briefs
        all_briefs = self.state.get_all_briefs()
        self.assertEqual(len(all_briefs), 2)
        self.assertIn("post_article_001", all_briefs)
        self.assertIn("post_article_002", all_briefs)
    
    def test_get_all_briefs_filtered(self):
        """Test getting all briefs filtered by article_slug."""
        # Store briefs from different articles
        brief1 = Mock(spec=CoherenceBrief)
        brief1.post_id = "post_article_a_001"
        brief2 = Mock(spec=CoherenceBrief)
        brief2.post_id = "post_article_b_001"
        
        self.state.store_brief(brief1)
        self.state.store_brief(brief2)
        
        # Get filtered briefs
        filtered = self.state.get_all_briefs(article_slug="article_a")
        self.assertEqual(len(filtered), 1)
        self.assertIn("post_article_a_001", filtered)
    
    def test_clear_context(self):
        """Test clearing contextual memory."""
        # Store some briefs
        self.state.store_brief(self.mock_brief)
        self.state.article_slug = self.test_article_slug
        self.state.current_trace_id = "trace_123"
        
        # Clear context
        self.state.clear_context()
        
        # Verify cleared
        self.assertEqual(len(self.state.coherence_briefs), 0)
        self.assertIsNone(self.state.article_slug)
        self.assertIsNone(self.state.current_trace_id)
    
    @patch('src.core.universal_state.list_traces')
    def test_query_history(self, mock_list_traces):
        """Test querying historical traces."""
        # Mock return value
        mock_list_traces.return_value = [
            {"id": "trace_1", "name": "test_trace"},
            {"id": "trace_2", "name": "another_trace"},
        ]
        
        # Query history
        history = self.state.query_history()
        
        # Verify
        self.assertEqual(len(history), 2)
        mock_list_traces.assert_called_once()
    
    @patch('src.core.universal_state.list_prompt_versions')
    def test_get_prompt_history(self, mock_list_versions):
        """Test getting prompt history."""
        # Mock return value
        mock_list_versions.return_value = [
            {"id": "prompt_1", "version": "v1"},
            {"id": "prompt_2", "version": "v2"},
        ]
        
        # Get prompt history
        history = self.state.get_prompt_history("post_ideator")
        
        # Verify
        self.assertEqual(len(history), 2)
        mock_list_versions.assert_called_once_with(
            "post_ideator",
            db_path=self.state.db_path
        )
    
    def test_repr(self):
        """Test string representation."""
        self.state.store_brief(self.mock_brief)
        self.state.article_slug = self.test_article_slug
        
        repr_str = repr(self.state)
        self.assertIn("UniversalState", repr_str)
        self.assertIn("briefs=1", repr_str)
        self.assertIn(self.test_article_slug, repr_str)


if __name__ == '__main__':
    unittest.main()

