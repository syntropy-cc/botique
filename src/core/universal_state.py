"""
Universal State module

Encapsulates the universal state Ω of the framework, which includes:
- Contextual memory: CoherenceBrief objects (active memory per post)
- Persistent memory: SQLite database (historical traces, events, prompts)

According to the framework definition:
Ω^(t) = ⟨M^(t), I^(t), G^(t), T^(t), A^(t), O^(t), H^(t), Ξ^(t)⟩

In this implementation:
- M^(t): CoherenceBrief objects stored in state
- H^(t): Historical traces/events via SQLite
- I^(t): Instructions (prompts) via prompt_registry (queried via SQLite)

Location: src/core/universal_state.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import CoherenceBrief (no breaking changes to coherence/brief.py)
try:
    from ..coherence.brief import CoherenceBrief
except ImportError:
    # Fallback if import fails
    CoherenceBrief = None

from .llm_log_db import get_db_path
from .llm_log_queries import list_traces, get_trace_with_events
from .prompt_registry import list_prompt_versions


@dataclass
class UniversalState:
    """
    Universal state Ω that encompasses all system components.
    
    This class provides a formal wrapper around:
    1. CoherenceBrief objects (contextual memory - M)
    2. SQLite database (persistent memory - H)
    3. Prompt registry (instructions - I)
    
    Framework correspondence:
    - coherence_briefs: Represents M^(t) - aggregate memory content
    - db_path: Connection to H^(t) - execution history
    - query_history(): Accesses H^(t) via SQLite
    - get_prompt_history(): Accesses I^(t) via prompt_registry
    
    The projection function π_g(Ω) is implemented in memory_strategies.py.
    This class provides the base state that strategies project from.
    """
    
    # Contextual memory: Active CoherenceBrief objects
    # Represents M^(t) - memory content accessible to agents
    coherence_briefs: Dict[str, Any] = field(default_factory=dict)
    
    # Persistent memory: SQLite database path
    # Represents H^(t) - execution history stored persistently
    db_path: Path = field(default_factory=get_db_path)
    
    # Context metadata
    article_slug: Optional[str] = None
    current_trace_id: Optional[str] = None
    
    def get_brief(self, post_id: str) -> Optional[Any]:
        """
        Retrieve coherence brief by post_id.
        
        This is the read operation ρ(q, M_view) where q = post_id.
        Returns the brief from contextual memory M.
        
        Args:
            post_id: Unique post identifier
            
        Returns:
            CoherenceBrief object if found, None otherwise
        """
        return self.coherence_briefs.get(post_id)
    
    def store_brief(self, brief: Any) -> None:
        """
        Store coherence brief in state.
        
        This is the write operation ω(k, v, Ω) that modifies universal state.
        Updates M^(t) by adding/updating a brief.
        
        Args:
            brief: CoherenceBrief object to store (must have post_id attribute)
        """
        if hasattr(brief, 'post_id'):
            self.coherence_briefs[brief.post_id] = brief
        else:
            raise ValueError("Brief must have post_id attribute")
    
    def query_history(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query historical traces/events from SQLite.
        
        Accesses H^(t) - the execution history stored in the database.
        This enables agents to access historical execution data for:
        - Learning from past executions
        - Finding similar past cases
        - Analyzing performance patterns
        
        Args:
            filters: Optional filters for traces (name, user_id, etc.)
            limit: Maximum number of traces to return
            
        Returns:
            List of trace dictionaries with metadata
        """
        return list_traces(limit=limit, filters=filters, db_path=self.db_path)
    
    def get_trace_details(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed trace with all events.
        
        Retrieves complete execution trace including all events in the trace tree.
        Useful for deep analysis of past executions.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            Dictionary with trace info and events list, or None if not found
        """
        return get_trace_with_events(trace_id, db_path=self.db_path)
    
    def get_prompt_history(self, prompt_key: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a prompt by key.
        
        Accesses I^(t) - the set of all instructions (prompts) in the system.
        Returns all versions of a specific prompt, enabling version tracking
        and prompt evolution analysis.
        
        Args:
            prompt_key: Logical identifier of the prompt (e.g., "post_ideator")
            
        Returns:
            List of prompt dictionaries with version, template, metadata, etc.
        """
        return list_prompt_versions(prompt_key, db_path=self.db_path)
    
    def get_all_briefs(self, article_slug: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all coherence briefs, optionally filtered by article_slug.
        
        Returns all briefs in contextual memory M^(t), optionally filtered
        to only briefs from a specific article.
        
        Args:
            article_slug: Optional article identifier to filter briefs
            
        Returns:
            Dictionary mapping post_id to CoherenceBrief objects
        """
        if article_slug is None:
            return self.coherence_briefs.copy()
        
        # Filter by article_slug (assuming post_id contains article_slug)
        return {
            post_id: brief
            for post_id, brief in self.coherence_briefs.items()
            if article_slug in post_id
        }
    
    def clear_context(self) -> None:
        """
        Clear contextual memory (but not persistent history).
        
        Resets M^(t) to empty but preserves H^(t) in SQLite.
        Useful for starting a new execution session.
        """
        self.coherence_briefs.clear()
        self.article_slug = None
        self.current_trace_id = None
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        briefs_count = len(self.coherence_briefs)
        return (
            f"UniversalState("
            f"briefs={briefs_count}, "
            f"article_slug={self.article_slug}, "
            f"trace_id={self.current_trace_id}"
            f")"
        )

