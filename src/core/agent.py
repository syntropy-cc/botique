"""
Agent module

Formalizes agents as directed graphs over the three pillars according to the framework:
A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩

Where:
- V ⊆ I ∪ G ∪ T: Vertex set (instructions, memory management, tools)
- E ⊆ V × V: Directed edge set
- λ_V: V → {instruction, memory_mgmt, tool}: Vertex labeling function
- λ_E: E → {data, control, conditional}: Edge labeling function
- v_0 ∈ V: Entry vertex
- Σ_A ⊆ Ω: Agent's local state (beliefs, working memory)

For MVP: Agents are lightweight wrappers over existing phase functions.
The graph structure is simple (linear) but extensible for future complexity.

Location: src/core/agent.py
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .universal_state import UniversalState
from .memory_strategies import MemoryStrategy, EpisodicStrategy


class VertexType(Enum):
    """
    Vertex type labels λ_V(v).
    
    Framework correspondence:
    - INSTRUCTION: Vertex is an instruction i ∈ I
    - MEMORY_MGMT: Vertex is a memory strategy g ∈ G
    - TOOL: Vertex is a tool t ∈ T
    """
    INSTRUCTION = "instruction"
    MEMORY_MGMT = "memory_mgmt"
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
    - vertices: V ⊆ I ∪ G ∪ T (vertex set with labels)
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
        memory_strategy: Optional[MemoryStrategy] = None,
    ) -> Dict[str, Any]:
        """
        Execute agent: eval(v, d, Ω) where v is the entry vertex.
        
        Framework correspondence:
        - Executes the agent starting from v_0
        - Projects memory via π_g(Ω) if strategy provided
        - Calls execute_fn with input data and memory view
        - Updates universal state ω(k, v, Ω) if results contain briefs
        
        Args:
            input_data: Input data dictionary d
            state: Universal state Ω
            memory_strategy: Optional memory strategy g for projection π_g(Ω)
        
        Returns:
            Result dictionary from execute_fn
        """
        # Project memory if strategy provided (π_g(Ω))
        memory_view = {}
        if memory_strategy:
            memory_view = memory_strategy.project(state)
        
        # Execute wrapped function with input data and memory view
        if self.execute_fn:
            # Execute (this calls the existing phase function)
            # Note: Existing phase functions don't expect memory_view parameter
            # Memory view is available but not automatically injected to maintain
            # backward compatibility with existing phase functions
            result = self.execute_fn(**input_data)
            
            # Update universal state if result contains briefs (ω operation)
            if isinstance(result, dict):
                # Extract briefs if present
                if "briefs" in result:
                    for brief in result["briefs"]:
                        if hasattr(brief, 'post_id'):
                            state.store_brief(brief)
                
                # Store individual brief if present
                if "brief" in result and hasattr(result["brief"], 'post_id'):
                    state.store_brief(result["brief"])
            
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


# Factory functions for creating agents from existing phases

def create_ideation_agent(phase1_fn: Callable) -> Agent:
    """
    Create ideation agent from phase 1 function.
    
    Args:
        phase1_fn: Function from phases.phase1_ideation.run
    
    Returns:
        Agent instance wrapping the ideation phase
    """
    return Agent(
        name="ideation",
        entry_vertex="generate_ideas",
        vertices={"generate_ideas": VertexType.INSTRUCTION},
        edges={},  # Linear: no edges for MVP
        execute_fn=phase1_fn,
    )


def create_selection_agent(phase2_fn: Callable) -> Agent:
    """
    Create selection agent from phase 2 function.
    
    Args:
        phase2_fn: Function from phases.phase2_selection.run
    
    Returns:
        Agent instance wrapping the selection phase
    """
    return Agent(
        name="selection",
        entry_vertex="select_ideas",
        vertices={"select_ideas": VertexType.TOOL},
        edges={},  # Linear: no edges for MVP
        execute_fn=phase2_fn,
    )


def create_coherence_agent(phase3_fn: Callable) -> Agent:
    """
    Create coherence agent from phase 3 function.
    
    Args:
        phase3_fn: Function from phases.phase3_coherence.run
    
    Returns:
        Agent instance wrapping the coherence phase
    """
    return Agent(
        name="coherence",
        entry_vertex="build_briefs",
        vertices={"build_briefs": VertexType.MEMORY_MGMT},
        edges={},  # Linear: no edges for MVP
        execute_fn=phase3_fn,
    )

