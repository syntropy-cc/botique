"""
Agent module

Formalizes agents as directed graphs over the three pillars according to the framework:
A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩

Where:
- V ⊆ I ∪ S ∪ T: Vertex set (instructions, state management, tools)
- E ⊆ V × V: Directed edge set
- λ_V: V → {instruction, state_mgmt, tool}: Vertex labeling function
- λ_E: E → {data, control, conditional}: Edge labeling function
- v_0 ∈ V: Entry vertex
- Σ_A ⊆ Ω: Agent's local state (beliefs, working memory)

For MVP: Agents are lightweight wrappers over existing phase functions.
The graph structure is simple (linear) but extensible for future complexity.

Location: framework/core/agent.py
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .universal_state import UniversalState
from .state_management import StateManagementStrategy


class VertexType(Enum):
    """
    Vertex type labels λ_V(v).
    
    Framework correspondence:
    - INSTRUCTION: Vertex is an instruction i ∈ I
    - STATE_MGMT: Vertex is a state management strategy s ∈ S
    - TOOL: Vertex is a tool t ∈ T
    """
    INSTRUCTION = "instruction"
    STATE_MGMT = "state_mgmt"
    TOOL = "tool"


class EdgeType(Enum):
    """
    Edge type labels λ_E(e).
    
    Framework correspondence:
    - DATA: Data edge - propagates information
    - CONTROL: Control edge - enforces execution ordering
    - CONDITIONAL: Conditional edge - enables branching
    """
    DATA = "data"
    CONTROL = "control"
    CONDITIONAL = "conditional"


@dataclass
class Agent:
    """
    Agent definition A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩.
    
    Framework correspondence:
    - name: Agent identifier
    - entry_vertex: v_0 (designated entry vertex)
    - vertices: V ⊆ I ∪ S ∪ T (vertex set with labels)
    - edges: E ⊆ V × V (directed edges)
    - local_state: Σ_A (agent's local state/beliefs)
    - execute_fn: Wrapper function for existing phase implementation
    
    For MVP: Simple wrapper over existing phase functions.
    Graph structure is linear (one vertex, no edges) but extensible.
    Future: Can add complex graphs with multiple vertices and conditional edges.
    """
    
    # Agent identity
    name: str  # Agent identifier (e.g., "ideation", "selection", "coherence")
    
    # Graph structure
    entry_vertex: str  # v_0: Designated entry vertex
    vertices: Dict[str, VertexType] = field(default_factory=dict)  # V with labels λ_V
    edges: Dict[str, List[str]] = field(default_factory=dict)  # E: from -> [to]
    
    # Local state (beliefs/working memory)
    local_state: Dict[str, Any] = field(default_factory=dict)  # Σ_A
    
    # Execution function (wraps existing phase)
    execute_fn: Optional[Callable] = None
    
    def execute(
        self,
        input_data: Dict[str, Any],
        state: UniversalState,
        state_strategy: Optional[StateManagementStrategy] = None,
    ) -> Dict[str, Any]:
        """
        Execute agent: eval(v, d, Ω) where v is the entry vertex.
        
        Framework correspondence:
        - Executes the agent starting from v_0
        - Projects memory via π_s(Ω) if strategy provided
        - Calls execute_fn with input data and memory view
        - Updates universal state ω(k, v, Ω) if results contain entities
        
        Args:
            input_data: Input data dictionary d
            state: Universal state Ω
            state_strategy: Optional state management strategy s for projection π_s(Ω)
        
        Returns:
            Result dictionary from execute_fn
        """
        # Project state if strategy provided (π_s(Ω))
        state_view = {}
        if state_strategy:
            state_view = state_strategy.project(state)
        
        # Execute wrapped function with input data and state view
        if self.execute_fn:
            # Execute (this calls the existing phase function)
            # Note: Existing phase functions don't expect state_view parameter
            # State view is available but not automatically injected to maintain
            # backward compatibility with existing phase functions
            result = self.execute_fn(**input_data)
            
            # Update universal state if result contains entities (ω operation)
            if isinstance(result, dict):
                # Extract and store entities if present
                # This is generic - specific implementations can override
                if "briefs" in result:
                    for brief in result["briefs"]:
                        if hasattr(brief, 'post_id'):
                            state.store("brief", brief.post_id, brief)
                
                # Store individual brief if present
                if "brief" in result and hasattr(result["brief"], 'post_id'):
                    state.store("brief", result["brief"].post_id, result["brief"])
            
            return result
        
        raise NotImplementedError(f"Agent {self.name} has no execute_fn")
    
    def get_local_state(self, key: str, default: Any = None) -> Any:
        """
        Get value from local state Σ_A.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            Value from local state or default
        """
        return self.local_state.get(key, default)
    
    def set_local_state(self, key: str, value: Any) -> None:
        """
        Set value in local state Σ_A.
        
        Args:
            key: State key
            value: Value to store
        """
        self.local_state[key] = value
    
    def clear_local_state(self) -> None:
        """Clear local state Σ_A."""
        self.local_state.clear()
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        vertices_count = len(self.vertices)
        edges_count = sum(len(targets) for targets in self.edges.values())
        return (
            f"Agent("
            f"name='{self.name}', "
            f"vertices={vertices_count}, "
            f"edges={edges_count}, "
            f"entry='{self.entry_vertex}'"
            f")"
        )
