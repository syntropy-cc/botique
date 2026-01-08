"""
Memory Strategies module

Implements memory management strategies g = ⟨π, ρ, ω, γ⟩ according to the framework.

The projection function π is the core concept:
π: Ω → M_view

Where:
- π: Projection function defining the accessible view of universal state
- Ω: Universal state (from universal_state.py)
- M_view: Memory view accessible to an agent/phase

Different strategies enable different access patterns:
- Episodic: Focus on current post's brief (temporal focus)
- Hierarchical: All briefs from current article (abstraction levels)
- Semantic: Historical traces by similarity (semantic search - skeleton)

Framework correspondence:
- MemoryStrategy: Base class for g (memory management strategy)
- project(): Implements π: Ω → M_view
- EpisodicStrategy: π_episodic(Ω^(t)) = {brief ∈ M^(t) : post_id = current}
- HierarchicalStrategy: π_hierarchical(Ω^(t)) = {brief ∈ M^(t) : article_slug = current}
- SemanticStrategy: π_semantic(Ω^(t), q) = top_k{similar traces} (skeleton)

Location: src/core/memory_strategies.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .universal_state import UniversalState


class MemoryStrategy(ABC):
    """
    Base class for memory management strategies g = ⟨π, ρ, ω, γ⟩.
    
    Framework correspondence:
    - This class represents g (memory management strategy)
    - project() implements π: Ω → M_view (projection function)
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
        Project universal state to a memory view.
        
        Implements π: Ω → M_view
        Defines which portions of the universal state are accessible.
        
        Framework correspondence:
        π_g(Ω^(t)) = {m ∈ M^(t) : filter_g(m, t) ∧ scope_g(m) ∧ relevance_g(m)}
        
        Args:
            state: Universal state Ω
            query: Optional query string for context-dependent projection
            
        Returns:
            Dictionary representing the memory view M_view
        """
        pass


class EpisodicStrategy(MemoryStrategy):
    """
    Episodic memory strategy: focuses on the current post's brief.
    
    Framework correspondence:
    π_episodic(Ω^(t)) = {m ∈ M^(t) : post_id = current_post_id}
    
    Temporal focus: Only the brief for the post currently being processed.
    Use case: Phases that need only the brief of the post being processed.
    
    This is the most common strategy for per-post processing phases.
    """
    
    def __init__(self, post_id: str):
        """
        Initialize episodic strategy for a specific post.
        
        Args:
            post_id: Unique post identifier (e.g., "post_article_slug_001")
        """
        self.post_id = post_id
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project state to episodic view: only the current post's brief.
        
        Returns:
            Dictionary with:
            - brief: CoherenceBrief object for current post (if found)
            - context: Formatted context string from brief (if available)
            - post_id: Current post identifier
        """
        brief = state.get_brief(self.post_id)
        
        if brief:
            # Use brief's context formatting method if available
            if hasattr(brief, 'to_prompt_context'):
                context = brief.to_prompt_context()
            else:
                context = str(brief)
            return {
                "brief": brief,
                "context": context,
                "post_id": self.post_id,
            }
        
        # No brief found yet
        return {
            "brief": None,
            "context": "",
            "post_id": self.post_id,
        }


class HierarchicalStrategy(MemoryStrategy):
    """
    Hierarchical memory strategy: all briefs from the current article.
    
    Framework correspondence:
    π_hierarchical(Ω^(t)) = ∪_{l=0}^L abstract_l(M^(t))
    
    Hierarchical abstraction: All briefs from the same article.
    Use case: Phases that need to see all posts from an article to ensure
    coherence across posts or to reuse patterns.
    
    Enables cross-post analysis and consistency checking.
    """
    
    def __init__(self, article_slug: str):
        """
        Initialize hierarchical strategy for a specific article.
        
        Args:
            article_slug: Article identifier (e.g., "why-traditional-learning-fails")
        """
        self.article_slug = article_slug
    
    def project(self, state: UniversalState, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Project state to hierarchical view: all briefs from current article.
        
        Returns:
            Dictionary with:
            - briefs: Dict mapping post_id to CoherenceBrief objects
            - count: Number of briefs found
            - article_slug: Current article identifier
        """
        briefs = state.get_all_briefs(article_slug=self.article_slug)
        
        return {
            "briefs": briefs,
            "count": len(briefs),
            "article_slug": self.article_slug,
        }


class SemanticStrategy(MemoryStrategy):
    """
    Semantic memory strategy: historical traces by similarity (skeleton).
    
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
    identifier: str,
    **kwargs,
) -> MemoryStrategy:
    """
    Factory function to create memory strategies.
    
    Args:
        strategy_type: Type of strategy ("episodic", "hierarchical", "semantic")
        identifier: Post ID (for episodic) or article slug (for hierarchical)
        **kwargs: Additional strategy-specific parameters
    
    Returns:
        MemoryStrategy instance
    
    Example:
        strategy = create_strategy("episodic", "post_article_001")
        strategy = create_strategy("hierarchical", "article_slug")
        strategy = create_strategy("semantic", "", similarity_threshold=0.8)
    """
    if strategy_type == "episodic":
        return EpisodicStrategy(post_id=identifier)
    elif strategy_type == "hierarchical":
        return HierarchicalStrategy(article_slug=identifier)
    elif strategy_type == "semantic":
        threshold = kwargs.get("similarity_threshold", 0.7)
        top_k = kwargs.get("top_k", 10)
        return SemanticStrategy(similarity_threshold=threshold, top_k=top_k)
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

