"""
Formal Orchestrator module

Implements the formal orchestrator O = ⟨R, π, dispatch, aggregate, Γ⟩ according to the framework.

Where:
- R: A → D_desc: Agent registry mapping agents to capability descriptions
- π: Q × Ω → P(A): Selection policy (determines which agents handle queries)
- dispatch: Q × A × Ω → E: Distributes tasks to agents
- aggregate: P(R) → R: Combines results from multiple agents
- Γ: Orchestrator's internal state

For MVP: Simple rule-based selection policy and sequential execution.
Future: Can add LLM-based selection, parallel execution, etc.

Location: src/core/orchestrator_formal.py
"""

from typing import Any, Dict, List, Optional

from .agent import Agent
from .universal_state import UniversalState
from .memory_strategies import MemoryStrategy, EpisodicStrategy, HierarchicalStrategy


class FormalOrchestrator:
    """
    Formal orchestrator O = ⟨R, π, dispatch, aggregate, Γ⟩.
    
    Framework correspondence:
    - registry: R - Agent registry mapping agents to descriptions
    - select_agents(): π - Selection policy π(q, Ω)
    - dispatch(): dispatch - Task distribution dispatch(q, A, Ω)
    - orchestrate(): Aggregate - Combines results aggregate(P(R))
    - internal_state: Γ - Orchestrator's internal state
    
    For MVP: Simple rule-based selection and sequential pipeline execution.
    Future: Can add LLM-based selection, parallel execution, complex aggregation.
    """
    
    def __init__(self):
        """
        Initialize formal orchestrator.
        
        Creates empty registry R and internal state Γ.
        """
        # Registry R: mapping agent names to Agent objects
        self.registry: Dict[str, Agent] = {}
        
        # Internal state Γ
        self.internal_state: Dict[str, Any] = {
            "execution_count": 0,
            "total_agents": 0,
        }
    
    def register_agent(self, agent: Agent, description: Optional[str] = None) -> None:
        """
        Register agent in registry R.
        
        Framework correspondence: R(A) → D_desc
        Maps agent to its capability description and stores in registry.
        
        Args:
            agent: Agent instance to register
            description: Optional capability description (currently unused but
                        reserved for future LLM-based selection)
        """
        self.registry[agent.name] = agent
        self.internal_state["total_agents"] = len(self.registry)
        
        # Store description in internal state for future use
        if description:
            if "agent_descriptions" not in self.internal_state:
                self.internal_state["agent_descriptions"] = {}
            self.internal_state["agent_descriptions"][agent.name] = description
    
    def select_agents(self, query: str, state: UniversalState) -> List[Agent]:
        """
        Selection policy π(q, Ω).
        
        Framework correspondence: π: Q × Ω → P(A)
        Determines which agents should handle the incoming query.
        
        For MVP: Simple rule-based selection by keyword matching in query string.
        Future: Can implement LLM-based semantic selection or more sophisticated policies.
        
        Args:
            query: Query string (describes the task)
            state: Universal state Ω
            
        Returns:
            List of selected agents
        """
        query_lower = query.lower()
        selected = []
        
        # Rule-based selection by keyword matching
        if any(word in query_lower for word in ["ideation", "ideas", "idea", "generate"]):
            if "ideation" in self.registry:
                selected.append(self.registry["ideation"])
        
        if any(word in query_lower for word in ["selection", "select", "filter", "choose"]):
            if "selection" in self.registry:
                selected.append(self.registry["selection"])
        
        if any(word in query_lower for word in ["coherence", "brief", "briefs", "build"]):
            if "coherence" in self.registry:
                selected.append(self.registry["coherence"])
        
        # Special case: full pipeline
        if any(word in query_lower for word in ["full", "pipeline", "complete", "all"]):
            # Return all agents in sequence
            for agent_name in ["ideation", "selection", "coherence"]:
                if agent_name in self.registry:
                    selected.append(self.registry[agent_name])
            # Remove duplicates while preserving order
            seen = set()
            unique_selected = []
            for agent in selected:
                if agent.name not in seen:
                    seen.add(agent.name)
                    unique_selected.append(agent)
            return unique_selected
        
        return selected
    
    def dispatch(
        self,
        agent: Agent,
        task: Dict[str, Any],
        state: UniversalState,
        memory_strategy: Optional[MemoryStrategy] = None,
    ) -> Dict[str, Any]:
        """
        Dispatch task to agent: dispatch(q, A, Ω).
        
        Framework correspondence: dispatch: Q × A × Ω → E
        Distributes a task to a specific agent with appropriate memory strategy.
        
        For MVP: Uses EpisodicStrategy if no strategy provided (most common case).
        Future: Can implement smarter strategy selection based on task requirements.
        
        Args:
            agent: Agent to dispatch task to
            task: Task data dictionary q
            state: Universal state Ω
            memory_strategy: Optional memory strategy (defaults to EpisodicStrategy
                           if task has post_id)
        
        Returns:
            Result from agent execution
        """
        # Select memory strategy if not provided
        if memory_strategy is None:
            # Try to infer from task data
            if "post_id" in task:
                memory_strategy = EpisodicStrategy(post_id=task["post_id"])
            elif "article_slug" in task:
                memory_strategy = HierarchicalStrategy(article_slug=task["article_slug"])
        
        # Execute agent with memory strategy
        result = agent.execute(
            input_data=task,
            state=state,
            memory_strategy=memory_strategy,
        )
        
        # Update internal state
        self.internal_state["execution_count"] += 1
        
        return result
    
    def aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agents: aggregate(P(R)).
        
        Framework correspondence: aggregate: P(R) → R
        Combines results from multiple agent executions into a single result.
        
        For MVP: Simple merge of result dictionaries.
        Future: Can implement more sophisticated aggregation (conflict resolution,
                priority-based merging, etc.).
        
        Args:
            results: List of result dictionaries from agent executions
            
        Returns:
            Aggregated result dictionary
        """
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Merge all results (last wins for conflicts)
        aggregated = {}
        for result in results:
            if isinstance(result, dict):
                aggregated.update(result)
        
        return aggregated
    
    def orchestrate(
        self,
        query: str,
        initial_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Orchestrate multi-agent execution.
        
        Framework correspondence: Combines π, dispatch, and aggregate
        Complete orchestration workflow:
        1. Select agents via π(q, Ω)
        2. Dispatch tasks to each agent via dispatch(q, A, Ω)
        3. Aggregate results via aggregate(P(R))
        
        For MVP: Sequential pipeline execution (A_n ∘ ... ∘ A_1).
        Future: Can add parallel execution, conditional branching, etc.
        
        Args:
            query: Query string describing the task
            initial_data: Initial data dictionary for the pipeline
            
        Returns:
            Aggregated result from all agent executions
        """
        # Initialize universal state
        state = UniversalState()
        if "article_slug" in initial_data:
            state.article_slug = initial_data["article_slug"]
        
        # Select agents via selection policy π
        agents = self.select_agents(query, state)
        
        if not agents:
            raise ValueError(f"No agents selected for query: {query}")
        
        # Sequential execution (pipeline): A_n ∘ ... ∘ A_1
        results = []
        current_data = initial_data
        
        for agent in agents:
            # Dispatch to agent
            result = self.dispatch(
                agent=agent,
                task=current_data,
                state=state,
            )
            results.append(result)
            
            # Pass result as input to next agent (pipeline pattern)
            if isinstance(result, dict):
                # Update current_data with result for next agent
                current_data = {**current_data, **result}
        
        # Aggregate all results
        aggregated = self.aggregate(results)
        
        return aggregated
    
    def get_registry(self) -> Dict[str, Agent]:
        """
        Get agent registry R.
        
        Returns:
            Dictionary mapping agent names to Agent objects
        """
        return self.registry.copy()
    
    def get_internal_state(self) -> Dict[str, Any]:
        """
        Get orchestrator internal state Γ.
        
        Returns:
            Dictionary with orchestrator state
        """
        return self.internal_state.copy()
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        agent_names = list(self.registry.keys())
        exec_count = self.internal_state.get("execution_count", 0)
        return (
            f"FormalOrchestrator("
            f"agents={agent_names}, "
            f"executions={exec_count}"
            f")"
        )

