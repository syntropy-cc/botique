"""
Unit tests for Agent.

Tests the Agent wrapper A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩
that wraps existing phase functions.
"""

import unittest
from unittest.mock import Mock

from src.core.agent import (
    Agent,
    VertexType,
    EdgeType,
    create_ideation_agent,
    create_selection_agent,
    create_coherence_agent,
)
from src.core.universal_state import UniversalState
from src.core.memory_strategies import EpisodicStrategy


class TestAgent(unittest.TestCase):
    """Test cases for Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state = UniversalState()
        
        # Mock execute function
        self.mock_execute_fn = Mock(return_value={"result": "success"})
        
        # Create test agent
        self.agent = Agent(
            name="test_agent",
            entry_vertex="test_vertex",
            vertices={"test_vertex": VertexType.INSTRUCTION},
            execute_fn=self.mock_execute_fn,
        )
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = Agent(
            name="test",
            entry_vertex="entry",
            vertices={"entry": VertexType.INSTRUCTION},
        )
        self.assertEqual(agent.name, "test")
        self.assertEqual(agent.entry_vertex, "entry")
        self.assertEqual(len(agent.vertices), 1)
        self.assertEqual(len(agent.local_state), 0)
    
    def test_execute_without_strategy(self):
        """Test agent execution without memory strategy."""
        input_data = {"key": "value"}
        
        result = self.agent.execute(
            input_data=input_data,
            state=self.state,
        )
        
        # Verify execute_fn was called
        self.mock_execute_fn.assert_called_once_with(**input_data)
        self.assertEqual(result, {"result": "success"})
    
    def test_execute_with_strategy(self):
        """Test agent execution with memory strategy."""
        # Set up memory strategy
        post_id = "post_001"
        brief = Mock()
        brief.post_id = post_id
        self.state.store_brief(brief)
        strategy = EpisodicStrategy(post_id=post_id)
        
        input_data = {"key": "value"}
        
        result = self.agent.execute(
            input_data=input_data,
            state=self.state,
            memory_strategy=strategy,
        )
        
        # Verify execute_fn was called (strategy is used internally)
        self.mock_execute_fn.assert_called_once_with(**input_data)
        self.assertEqual(result, {"result": "success"})
    
    def test_execute_updates_state_with_briefs(self):
        """Test that execute updates state when result contains briefs."""
        # Mock brief
        brief = Mock()
        brief.post_id = "post_001"
        
        # Mock execute function returning briefs
        self.mock_execute_fn.return_value = {"briefs": [brief]}
        
        input_data = {"key": "value"}
        self.agent.execute(input_data=input_data, state=self.state)
        
        # Verify brief was stored
        stored = self.state.get_brief("post_001")
        self.assertEqual(stored, brief)
    
    def test_local_state_operations(self):
        """Test local state get/set/clear operations."""
        # Set state
        self.agent.set_local_state("key1", "value1")
        self.agent.set_local_state("key2", "value2")
        
        # Get state
        self.assertEqual(self.agent.get_local_state("key1"), "value1")
        self.assertEqual(self.agent.get_local_state("key2"), "value2")
        self.assertEqual(self.agent.get_local_state("nonexistent", "default"), "default")
        
        # Clear state
        self.agent.clear_local_state()
        self.assertEqual(len(self.agent.local_state), 0)
    
    def test_execute_without_execute_fn(self):
        """Test that execute raises NotImplementedError if no execute_fn."""
        agent = Agent(
            name="no_fn",
            entry_vertex="entry",
            vertices={"entry": VertexType.INSTRUCTION},
        )
        
        with self.assertRaises(NotImplementedError):
            agent.execute({}, self.state)
    
    def test_create_ideation_agent(self):
        """Test factory function for ideation agent."""
        mock_fn = Mock()
        agent = create_ideation_agent(mock_fn)
        
        self.assertEqual(agent.name, "ideation")
        self.assertEqual(agent.entry_vertex, "generate_ideas")
        self.assertEqual(agent.vertices["generate_ideas"], VertexType.INSTRUCTION)
        self.assertEqual(agent.execute_fn, mock_fn)
    
    def test_create_selection_agent(self):
        """Test factory function for selection agent."""
        mock_fn = Mock()
        agent = create_selection_agent(mock_fn)
        
        self.assertEqual(agent.name, "selection")
        self.assertEqual(agent.entry_vertex, "select_ideas")
        self.assertEqual(agent.vertices["select_ideas"], VertexType.TOOL)
        self.assertEqual(agent.execute_fn, mock_fn)
    
    def test_create_coherence_agent(self):
        """Test factory function for coherence agent."""
        mock_fn = Mock()
        agent = create_coherence_agent(mock_fn)
        
        self.assertEqual(agent.name, "coherence")
        self.assertEqual(agent.entry_vertex, "build_briefs")
        self.assertEqual(agent.vertices["build_briefs"], VertexType.MEMORY_MGMT)
        self.assertEqual(agent.execute_fn, mock_fn)
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.agent)
        self.assertIn("Agent", repr_str)
        self.assertIn("test_agent", repr_str)
        self.assertIn("test_vertex", repr_str)


if __name__ == '__main__':
    unittest.main()

