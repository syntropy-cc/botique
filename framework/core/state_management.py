"""
State Management Strategies module

Implements state management strategies s = ⟨π, ρ, ω, γ⟩ according to the framework.

The projection function π is the core concept:
π: Ω → V_view

Where:
- π: Projection function defining the accessible view of universal state
- Ω: Universal state (from universal_state.py)
- V_view: State view accessible to an agent/phase

Different strategies enable different access patterns:
- Episodic: Focus on current entity (temporal focus)
- Hierarchical: All entities from current context (abstraction levels)
- Semantic: Historical traces by similarity (semantic search - skeleton)

Framework correspondence:
- StateManagementStrategy: Base class for s (state management strategy)
- project(): Implements π: Ω → V_view
- EpisodicStrategy: π_episodic(Ω^(t)) = {entity ∈ M^(t) : entity_id = current}
- HierarchicalStrategy: π_hierarchical(Ω^(t)) = {entity ∈ M^(t) : context = current}
- SemanticStrategy: π_semantic(Ω^(t), q) = top_k{similar traces} (skeleton)

Location: framework/core/state_management.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .universal_state import UniversalState


class StateManagementStrategy(ABC):
    """
    Base class for state management strategies s = ⟨π, ρ, ω, γ⟩.
    
    Framework correspondence:
    - This class represents s (state management strategy)
    - project() implements π: Ω → V_view (projection function)
    - The strategy determines which portions of Ω are visible to an agent
    
    Each strategy defines how an agent views the universal state, enabling
    different patterns:
    - Temporal focus (EpisodicStrategy)
    - Hierarchical abstraction (HierarchicalStrategy)
    - Semantic similarity (SemanticStrategy)
    """
    
    @abstractmethod
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project universal state to a state view.
        
        Implements π: Ω → V_view
        Defines which portions of the universal state are accessible.
        
        Framework correspondence:
        π_s(Ω^(t)) = {m ∈ M^(t) : filter_s(m, t) ∧ scope_s(m) ∧ relevance_s(m)}
        
        Args:
            state: Universal state Ω
            query: Optional query string for context-dependent projection
            
        Returns:
            Dictionary representing the state view V_view
        """
        pass


class EpisodicStrategy(StateManagementStrategy):
    """
    Episodic state strategy: focuses on the current entity.
    
    Framework correspondence:
    π_episodic(Ω^(t)) = {m ∈ M^(t) : entity_id = current_entity_id}
    
    Temporal focus: Only the entity currently being processed.
    Use case: Phases that need only the entity being processed.
    
    This is the most common strategy for per-entity processing phases.
    """
    
    def __init__(self, entity_type: str, entity_id: str):
        """
        Initialize episodic strategy for a specific entity.
        
        Args:
            entity_type: Type of entity (e.g., "brief", "idea")
            entity_id: Unique entity identifier (e.g., "post_article_slug_001")
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project state to episodic view: only the current entity.
        
        Returns:
            Dictionary with:
            - entity: Entity object for current entity (if found)
            - context: Formatted context string from entity (if available)
            - entity_id: Current entity identifier
        """
        entity = state.retrieve(self.entity_type, self.entity_id)
        
        if entity:
            # Use entity's context formatting method if available
            if hasattr(entity, 'to_prompt_context'):
                context = entity.to_prompt_context()
            elif hasattr(entity, 'to_dict'):
                import json
                context = json.dumps(entity.to_dict(), indent=2)
            else:
                context = str(entity)
            return {
                "entity": entity,
                "context": context,
                "entity_id": self.entity_id,
                "entity_type": self.entity_type,
            }
        
        # No entity found yet
        return {
            "entity": None,
            "context": "",
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
        }


class HierarchicalStrategy(StateManagementStrategy):
    """
    Hierarchical state strategy: all entities from the current context.
    
    Framework correspondence:
    π_hierarchical(Ω^(t)) = ∪_{l=0}^L abstract_l(M^(t))
    
    Hierarchical abstraction: All entities from the same context.
    Use case: Phases that need to see all entities from a context to ensure
    coherence across entities or to reuse patterns.
    
    Enables cross-entity analysis and consistency checking.
    """
    
    def __init__(self, entity_type: str, context_key: str, context_value: str):
        """
        Initialize hierarchical strategy for a specific context.
        
        Args:
            entity_type: Type of entity (e.g., "brief")
            context_key: Context key to filter by (e.g., "article_slug")
            context_value: Context value (e.g., "why-traditional-learning-fails")
        """
        self.entity_type = entity_type
        self.context_key = context_key
        self.context_value = context_value
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project state to hierarchical view: all entities from current context.
        
        Returns:
            Dictionary with:
            - entities: Dict mapping entity_id to entity objects
            - count: Number of entities found
            - context_key: Context key used
            - context_value: Context value used
        """
        # Query entities by context
        entities = state.query(self.entity_type, {self.context_key: self.context_value})
        
        # Convert to dict if needed
        if isinstance(entities, list):
            entities_dict = {}
            for entity in entities:
                # Try to get ID from entity
                if hasattr(entity, 'post_id'):
                    entities_dict[entity.post_id] = entity
                elif isinstance(entity, dict) and 'post_id' in entity:
                    entities_dict[entity['post_id']] = entity
                else:
                    # Use index as key
                    entities_dict[str(len(entities_dict))] = entity
            entities = entities_dict
        
        return {
            "entities": entities,
            "count": len(entities),
            "context_key": self.context_key,
            "context_value": self.context_value,
            "entity_type": self.entity_type,
        }


class SemanticStrategy(StateManagementStrategy):
    """
    Semantic state strategy: historical traces by similarity (skeleton).
    
    Framework correspondence:
    π_semantic(Ω^(t), q) = top_k{m ∈ M^(t) : sim(embed(m), embed(q)) > ε}
    
    Semantic similarity: Historical traces similar to current query.
    Use case: Phases that need to learn from similar past executions.
    
    This is a skeleton implementation - actual semantic search requires
    embeddings and similarity computation (future extension).
    """
    
    def __init__(self, similarity_threshold: float = 0.7, top_k: int = 10):
        """
        Initialize semantic strategy.
        
        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0)
            top_k: Maximum number of similar traces to return
        """
        self.threshold = similarity_threshold
        self.top_k = top_k
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project state to semantic view: similar historical traces.
        
        TODO: Implement actual semantic search with embeddings.
        For now, returns recent traces as a placeholder.
        
        Returns:
            Dictionary with:
            - history: List of similar traces (currently recent traces)
            - count: Number of traces found
            - query: Original query string
        """
        # Skeleton: For now, just return recent traces
        # Future: Implement embedding-based similarity search
        history = state.query_history(limit=self.top_k)
        
        return {
            "history": history,
            "count": len(history),
            "query": query,
            "note": "Semantic search not yet implemented - returning recent traces",
        }


# Factory function for creating strategies
def create_strategy(
    strategy_type: str,
    entity_type: str,
    identifier: str,
    **kwargs,
) -> StateManagementStrategy:
    """
    Factory function to create state management strategies.
    
    Args:
        strategy_type: Type of strategy ("episodic", "hierarchical", "semantic")
        entity_type: Type of entity (e.g., "brief", "idea")
        identifier: Entity ID (for episodic) or context value (for hierarchical)
        **kwargs: Additional strategy-specific parameters
    
    Returns:
        StateManagementStrategy instance
    
    Example:
        strategy = create_strategy("episodic", "brief", "post_article_001")
        strategy = create_strategy("hierarchical", "brief", "article_slug", context_key="article_slug")
        strategy = create_strategy("semantic", "", "", similarity_threshold=0.8)
    """
    if strategy_type == "episodic":
        return EpisodicStrategy(entity_type=entity_type, entity_id=identifier)
    elif strategy_type == "hierarchical":
        context_key = kwargs.get("context_key", "article_slug")
        return HierarchicalStrategy(
            entity_type=entity_type,
            context_key=context_key,
            context_value=identifier
        )
    elif strategy_type == "semantic":
        threshold = kwargs.get("similarity_threshold", 0.7)
        top_k = kwargs.get("top_k", 10)
        return SemanticStrategy(similarity_threshold=threshold, top_k=top_k)
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
