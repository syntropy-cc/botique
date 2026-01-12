"""
Universal State module

Encapsulates the universal state Ω of the framework, which includes:
- Contextual memory: Generic objects stored in state
- Persistent memory: Via StorageManager (SQLite, JSON, Memory)

According to the framework definition:
Ω^(t) = ⟨M^(t), I^(t), S^(t), T^(t), A^(t), O^(t), H^(t), Ξ^(t)⟩

In this implementation:
- M^(t): Generic objects stored via StorageManager
- H^(t): Historical traces/events via SQLite (via StorageManager)
- I^(t): Instructions (prompts) via prompt_registry (queried via SQLite)

Location: framework/core/universal_state.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..storage.manager import StorageManager


@dataclass
class UniversalState:
    """
    Universal state Ω that encompasses all system components.
    
    This class provides a formal wrapper around:
    1. Generic objects stored via StorageManager (contextual memory - M)
    2. StorageManager for persistent memory (H)
    3. Prompt registry (instructions - I) - accessed via StorageManager
    
    Framework correspondence:
    - storage: Represents access to M^(t) and H^(t) via StorageManager
    - query_history(): Accesses H^(t) via StorageManager
    - get_prompt_history(): Accesses I^(t) via StorageManager
    
    The projection function π_s(Ω) is implemented in state_management.py.
    This class provides the base state that strategies project from.
    """
    
    # Storage manager for all state operations
    storage: StorageManager = field(default_factory=StorageManager)
    
    # Context metadata
    article_slug: Optional[str] = None
    current_trace_id: Optional[str] = None
    
    # In-memory cache for frequently accessed objects
    _cache: Dict[str, Any] = field(default_factory=dict, init=False)
    
    def store(self, entity_type: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store entity in state.
        
        This is the write operation ω(k, v, Ω) that modifies universal state.
        Uses StorageManager to route to appropriate backend.
        
        Args:
            entity_type: Type of entity (ex: "brief", "trace", "brand")
            key: Unique identifier
            value: Value to store
            metadata: Optional metadata
            
        Returns:
            Key of stored value
        """
        stored_key = self.storage.store(entity_type, key, value, metadata)
        # Update cache
        self._cache[f"{entity_type}:{key}"] = value
        return stored_key
    
    def retrieve(self, entity_type: str, key: str) -> Optional[Any]:
        """
        Retrieve entity from state.
        
        This is the read operation ρ(q, M_view) where q = key.
        Uses StorageManager to route to appropriate backend.
        
        Args:
            entity_type: Type of entity
            key: Unique identifier
            
        Returns:
            Retrieved value or None if not found
        """
        # Check cache first
        cache_key = f"{entity_type}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Retrieve from storage
        value = self.storage.retrieve(entity_type, key)
        if value is not None:
            # Update cache
            self._cache[cache_key] = value
        
        return value
    
    def query(self, entity_type: str, query: Dict[str, Any]) -> List[Any]:
        """
        Query entities with filters.
        
        Args:
            entity_type: Type of entity
            query: Query criteria
            
        Returns:
            List of matching entities
        """
        return self.storage.query(entity_type, query)
    
    def delete(self, entity_type: str, key: str) -> bool:
        """
        Delete entity from state.
        
        Args:
            entity_type: Type of entity
            key: Unique identifier
            
        Returns:
            True if deleted successfully
        """
        deleted = self.storage.delete(entity_type, key)
        # Remove from cache
        cache_key = f"{entity_type}:{key}"
        self._cache.pop(cache_key, None)
        return deleted
    
    def query_history(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query historical traces/events.
        
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
        # Query traces from SQLite backend
        query = filters or {}
        if limit:
            query["_limit"] = limit
        
        return self.storage.query("trace", query)
    
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
        # Query trace by ID
        traces = self.storage.query("trace", {"id": trace_id})
        if not traces:
            return None
        
        trace = traces[0]
        
        # Query events for this trace
        events = self.storage.query("event", {"trace_id": trace_id})
        trace["events"] = events
        
        return trace
    
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
        return self.storage.query("prompt", {"prompt_key": prompt_key})
    
    def clear_context(self) -> None:
        """
        Clear contextual memory cache (but not persistent storage).
        
        Resets in-memory cache but preserves persistent storage.
        Useful for starting a new execution session.
        """
        self._cache.clear()
        self.article_slug = None
        self.current_trace_id = None
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        cache_count = len(self._cache)
        return (
            f"UniversalState("
            f"cache={cache_count}, "
            f"article_slug={self.article_slug}, "
            f"trace_id={self.current_trace_id}"
            f")"
        )
