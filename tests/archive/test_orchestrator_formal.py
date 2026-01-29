"""
Unit tests for FormalOrchestrator.

Tests the formal orchestrator O = ⟨R, π, dispatch, aggregate, Γ⟩
that coordinates multi-agent execution.
"""

import unittest
from unittest.mock import Mock

from src.core.orchestrator_formal import FormalOrchestrator
from src.core.agent import Agent, VertexType
from src.core.universal_state import UniversalState
from src.core.memory_strategies import EpisodicStrategy


class TestFormalOrchestrator(unittest.TestCase):
    """Test cases for FormalOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = FormalOrchestrator()
        
        # Create mock agents
        self.agent1 = Agent(
            name="ideation",
            entry_vertex="generate_ideas",
            vertices={"generate_ideas": VertexType.INSTRUCTION},
            execute_fn=Mock(return_value={"ideas": [1, 2, 3]}),
        )
        
        self.agent2 = Agent(
            name="selection",
            entry_vertex="select_ideas",
            vertices={"select_ideas": VertexType.TOOL},
            execute_fn=Mock(return_value={"selected": [1, 2]}),
        )
        
        self.agent3 = Agent(
            name="coherence",
            entry_vertex="build_briefs",
            vertices={"build_briefs": VertexType.MEMORY_MGMT},
            execute_fn=Mock(return_value={"briefs": []}),
        )
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = FormalOrchestrator()
        self.assertEqual(len(orch.registry), 0)
        self.assertEqual(orch.internal_state["execution_count"], 0)
    
    def test_register_agent(self):
        """Test registering agents in registry."""
        self.orchestrator.register_agent(self.agent1)
        
        self.assertIn("ideation", self.orchestrator.registry)
        self.assertEqual(self.orchestrator.registry["ideation"], self.agent1)
        self.assertEqual(self.orchestrator.internal_state["total_agents"], 1)
    
    def test_register_agent_with_description(self):
        """Test registering agent with description."""
        self.orchestrator.register_agent(
            self.agent1,
            description="Generates ideas from articles"
        )
        
        descriptions = self.orchestrator.internal_state.get("agent_descriptions", {})
        self.assertEqual(descriptions["ideation"], "Generates ideas from articles")
    
    def test_select_agents_ideation(self):
        """Test agent selection for ideation query."""
        self.orchestrator.register_agent(self.agent1)
        
        state = UniversalState()
        selected = self.orchestrator.select_agents("generate ideas", state)
        
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].name, "ideation")
    
    def test_select_agents_full_pipeline(self):
        """Test agent selection for full pipeline query."""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        self.orchestrator.register_agent(self.agent3)
        
        state = UniversalState()
        selected = self.orchestrator.select_agents("full pipeline", state)
        
        # Should return all three agents in order
        self.assertEqual(len(selected), 3)
        self.assertEqual(selected[0].name, "ideation")
        self.assertEqual(selected[1].name, "selection")
        self.assertEqual(selected[2].name, "coherence")
    
    def test_select_agents_no_match(self):
        """Test agent selection with no matching query."""
        self.orchestrator.register_agent(self.agent1)
        
        state = UniversalState()
        selected = self.orchestrator.select_agents("unknown query", state)
        
        self.assertEqual(len(selected), 0)
    
    def test_dispatch(self):
        """Test dispatching task to agent."""
        self.orchestrator.register_agent(self.agent1)
        
        state = UniversalState()
        task = {"article_path": "test.md"}
        
        result = self.orchestrator.dispatch(
            agent=self.agent1,
            task=task,
            state=state,
        )
        
        # Verify agent was executed
        self.agent1.execute_fn.assert_called_once()
        self.assertEqual(result, {"ideas": [1, 2, 3]})
        self.assertEqual(self.orchestrator.internal_state["execution_count"], 1)
    
    def test_dispatch_with_strategy(self):
        """Test dispatching with memory strategy."""
        self.orchestrator.register_agent(self.agent1)
        
        state = UniversalState()
        task = {"post_id": "post_001"}
        strategy = EpisodicStrategy(post_id="post_001")
        
        result = self.orchestrator.dispatch(
            agent=self.agent1,
            task=task,
            state=state,
            memory_strategy=strategy,
        )
        
        # Verify execution
        self.agent1.execute_fn.assert_called_once()
        self.assertEqual(result, {"ideas": [1, 2, 3]})
    
    def test_aggregate_single(self):
        """Test aggregating single result."""
        results = [{"key": "value"}]
        aggregated = self.orchestrator.aggregate(results)
        self.assertEqual(aggregated, {"key": "value"})
    
    def test_aggregate_multiple(self):
        """Test aggregating multiple results."""
        results = [
            {"key1": "value1"},
            {"key2": "value2"},
            {"key3": "value3"},
        ]
        aggregated = self.orchestrator.aggregate(results)
        
        # Should merge all dictionaries
        self.assertIn("key1", aggregated)
        self.assertIn("key2", aggregated)
        self.assertIn("key3", aggregated)
    
    def test_aggregate_empty(self):
        """Test aggregating empty results."""
        aggregated = self.orchestrator.aggregate([])
        self.assertEqual(aggregated, {})
    
    def test_orchestrate_sequential(self):
        """Test orchestrating sequential pipeline."""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        
        initial_data = {"article_path": "test.md"}
        
        result = self.orchestrator.orchestrate(
            query="full pipeline",
            initial_data=initial_data,
        )
        
        # Verify both agents were executed
        self.agent1.execute_fn.assert_called_once()
        self.agent2.execute_fn.assert_called_once()
        
        # Verify result is aggregated
        self.assertIn("ideas", result)
        self.assertIn("selected", result)
    
    def test_orchestrate_no_agents(self):
        """Test orchestrating with no selected agents."""
        with self.assertRaises(ValueError) as context:
            self.orchestrator.orchestrate(
                query="unknown query",
                initial_data={},
            )
        
        self.assertIn("No agents selected", str(context.exception))
    
    def test_get_registry(self):
        """Test getting registry copy."""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        
        registry = self.orchestrator.get_registry()
        
        # Should be a copy
        self.assertIsNot(registry, self.orchestrator.registry)
        self.assertEqual(len(registry), 2)
        self.assertIn("ideation", registry)
        self.assertIn("selection", registry)
    
    def test_get_internal_state(self):
        """Test getting internal state copy."""
        self.orchestrator.register_agent(self.agent1)
        
        state = self.orchestrator.get_internal_state()
        
        # Should be a copy
        self.assertIsNot(state, self.orchestrator.internal_state)
        self.assertEqual(state["total_agents"], 1)
    
    def test_repr(self):
        """Test string representation."""
        self.orchestrator.register_agent(self.agent1)
        
        repr_str = repr(self.orchestrator)
        self.assertIn("FormalOrchestrator", repr_str)
        self.assertIn("ideation", repr_str)


if __name__ == '__main__':
    unittest.main()

