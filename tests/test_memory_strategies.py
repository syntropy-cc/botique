"""
Unit tests for Memory Strategies.

Tests the memory projection functions π that define how agents
view the universal state Ω.
"""

import unittest
from unittest.mock import Mock

from src.core.memory_strategies import (
    MemoryStrategy,
    EpisodicStrategy,
    HierarchicalStrategy,
    SemanticStrategy,
    create_strategy,
)
from src.core.universal_state import UniversalState


class TestMemoryStrategies(unittest.TestCase):
    """Test cases for Memory Strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = UniversalState()
        self.post_id = "post_test_001"
        self.article_slug = "test_article"
        
        # Create mock brief
        self.mock_brief = Mock()
        self.mock_brief.post_id = self.post_id
        self.mock_brief.to_prompt_context = Mock(return_value="Mock context")
    
    def test_episodic_strategy_with_brief(self):
        """Test EpisodicStrategy when brief exists."""
        # Store brief
        self.state.store_brief(self.mock_brief)
        
        # Create strategy
        strategy = EpisodicStrategy(post_id=self.post_id)
        
        # Project state
        view = strategy.project(self.state)
        
        # Verify projection
        self.assertEqual(view["brief"], self.mock_brief)
        self.assertEqual(view["post_id"], self.post_id)
        self.assertIn("context", view)
    
    def test_episodic_strategy_without_brief(self):
        """Test EpisodicStrategy when brief doesn't exist."""
        # No brief stored
        strategy = EpisodicStrategy(post_id=self.post_id)
        
        # Project state
        view = strategy.project(self.state)
        
        # Verify projection
        self.assertIsNone(view["brief"])
        self.assertEqual(view["post_id"], self.post_id)
        self.assertEqual(view["context"], "")
    
    def test_hierarchical_strategy(self):
        """Test HierarchicalStrategy."""
        # Store multiple briefs from same article
        brief1 = Mock()
        brief1.post_id = f"post_{self.article_slug}_001"
        brief2 = Mock()
        brief2.post_id = f"post_{self.article_slug}_002"
        
        self.state.store_brief(brief1)
        self.state.store_brief(brief2)
        
        # Create strategy
        strategy = HierarchicalStrategy(article_slug=self.article_slug)
        
        # Project state
        view = strategy.project(self.state)
        
        # Verify projection
        self.assertEqual(view["count"], 2)
        self.assertEqual(view["article_slug"], self.article_slug)
        self.assertIn("briefs", view)
        self.assertEqual(len(view["briefs"]), 2)
    
    @patch('src.core.memory_strategies.UniversalState.query_history')
    def test_semantic_strategy(self, mock_query):
        """Test SemanticStrategy (skeleton implementation)."""
        # Mock query history
        mock_query.return_value = [
            {"id": "trace_1", "name": "test"},
            {"id": "trace_2", "name": "another"},
        ]
        
        # Create strategy
        strategy = SemanticStrategy(similarity_threshold=0.7, top_k=10)
        
        # Project state
        view = strategy.project(self.state, query="test query")
        
        # Verify projection (currently returns recent traces)
        self.assertIn("history", view)
        self.assertEqual(view["count"], 2)
        self.assertEqual(view["query"], "test query")
        self.assertIn("note", view)  # Skeleton note
    
    def test_create_strategy_episodic(self):
        """Test factory function for episodic strategy."""
        strategy = create_strategy("episodic", "post_123")
        self.assertIsInstance(strategy, EpisodicStrategy)
        self.assertEqual(strategy.post_id, "post_123")
    
    def test_create_strategy_hierarchical(self):
        """Test factory function for hierarchical strategy."""
        strategy = create_strategy("hierarchical", "article_slug")
        self.assertIsInstance(strategy, HierarchicalStrategy)
        self.assertEqual(strategy.article_slug, "article_slug")
    
    def test_create_strategy_semantic(self):
        """Test factory function for semantic strategy."""
        strategy = create_strategy(
            "semantic",
            "",
            similarity_threshold=0.8,
            top_k=5
        )
        self.assertIsInstance(strategy, SemanticStrategy)
        self.assertEqual(strategy.threshold, 0.8)
        self.assertEqual(strategy.top_k, 5)
    
    def test_create_strategy_invalid(self):
        """Test factory function with invalid strategy type."""
        with self.assertRaises(ValueError):
            create_strategy("invalid_type", "identifier")


if __name__ == '__main__':
    unittest.main()

