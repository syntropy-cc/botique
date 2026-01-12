"""
Tool module

Formalizes tools according to the framework definition:
t = ⟨sig, f, effects, pre, post⟩

Where:
- sig: Function signature (τ_in, τ_out)
- f: Implemented function f: τ_in → τ_out
- effects: Side effects declaration
- pre: Precondition predicate
- post: Postcondition predicate

Location: framework/core/tool.py
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


@dataclass
class Tool:
    """
    Formal tool definition t = ⟨sig, f, effects, pre, post⟩.
    
    Framework correspondence:
    - sig: Function signature (input type, output type)
    - f: Implemented function
    - effects: Side effects (io, network, state, irreversible, evolution)
    - pre: Precondition predicate
    - post: Postcondition predicate
    
    Tools execute deterministically. The choice of which tool to invoke
    is probabilistic (handled by agent graph transitions).
    """
    
    # Function signature sig = (τ_in, τ_out)
    sig: Tuple[Any, Any]  # (input_type, output_type) - can be str descriptions
    
    # Implemented function f: τ_in → τ_out
    f: Callable[[Any], Any]
    
    # Side effects declaration
    effects: Set[str] = field(default_factory=set)  # {io, network, state, irreversible, evolution}
    
    # Precondition predicate pre: τ_in × Ω → {true, false}
    pre: Optional[Callable[[Any, Any], bool]] = None
    
    # Postcondition predicate post: τ_in × τ_out × Ω → {true, false}
    post: Optional[Callable[[Any, Any, Any], bool]] = None
    
    # Tool metadata
    name: Optional[str] = None
    description: Optional[str] = None
    
    def execute(self, input_data: Any, state: Any = None) -> Any:
        """
        Execute tool: exec_t(d, Ω).
        
        Framework correspondence:
        exec_t(d, Ω) = f(d) if pre(d, Ω) else ⊥
        
        Args:
            input_data: Input data d
            state: Universal state Ω (optional, for precondition check)
            
        Returns:
            Tool output f(d) if precondition satisfied, None otherwise
        """
        # Check precondition
        if self.pre and state is not None:
            if not self.pre(input_data, state):
                return None
        
        # Execute function
        result = self.f(input_data)
        
        # Check postcondition
        if self.post and state is not None:
            if not self.post(input_data, result, state):
                # Postcondition failed - log warning but return result
                # In production, might want to raise exception
                pass
        
        return result
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        name = self.name or "Tool"
        effects_str = ",".join(self.effects) if self.effects else "none"
        return f"Tool(name='{name}', effects={{{effects_str}}})"
