"""
Idea filtering and selection module

Strategies for filtering and selecting ideas based on various criteria.

Location: src/ideas/filter.py
"""

from typing import Any, Dict, List, Optional


class IdeaFilter:
    """
    Filter and rank ideas based on various criteria.
    
    Provides multiple selection strategies:
    - Confidence-based filtering
    - Diversity maximization
    - Platform-specific filtering
    - Custom ID selection
    """
    
    @staticmethod
    def filter_by_confidence(
        ideas: List[Dict[str, Any]],
        min_confidence: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Filter ideas by minimum confidence threshold.
        
        Args:
            ideas: List of idea dicts
            min_confidence: Minimum confidence score (0.0-1.0)
        
        Returns:
            Filtered list of ideas meeting threshold
        """
        return [
            idea for idea in ideas
            if idea.get("confidence", 0.0) >= min_confidence
        ]
    
    @staticmethod
    def rank_by_confidence(
        ideas: List[Dict[str, Any]],
        descending: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Sort ideas by confidence score.
        
        Args:
            ideas: List of idea dicts
            descending: Sort descending (highest first) if True
        
        Returns:
            Sorted list of ideas
        """
        return sorted(
            ideas,
            key=lambda x: x.get("confidence", 0.0),
            reverse=descending,
        )
    
    @staticmethod
    def select_diverse(
        ideas: List[Dict[str, Any]],
        max_count: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Select diverse ideas to maximize variety.
        
        Strategy:
        1. Start with highest confidence idea
        2. Add ideas that differ in platform, tone, or objective
        3. Fill remaining slots with highest confidence
        
        This ensures variety across:
        - Platforms (LinkedIn, Instagram, etc.)
        - Tones (professional, empowering, etc.)
        - Objectives (awareness, engagement, conversion)
        - Audiences (C-Level, Founder, Developer)
        
        Args:
            ideas: List of idea dicts
            max_count: Maximum number of ideas to select
        
        Returns:
            Diverse selection of ideas
        """
        if not ideas:
            return []
        
        # Start with highest confidence
        ranked = IdeaFilter.rank_by_confidence(ideas)
        selected = [ranked[0]]
        
        # Add diverse ideas
        for idea in ranked[1:]:
            if len(selected) >= max_count:
                break
            
            # Check if this idea adds diversity
            is_diverse = IdeaFilter._is_diverse_from(idea, selected)
            
            if is_diverse:
                selected.append(idea)
        
        # Fill remaining slots with highest confidence
        while len(selected) < max_count and len(selected) < len(ranked):
            next_idea = ranked[len(selected)]
            if next_idea not in selected:
                selected.append(next_idea)
        
        return selected
    
    @staticmethod
    def select_by_platform(
        ideas: List[Dict[str, Any]],
        platforms: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Filter ideas by platform.
        
        Args:
            ideas: List of idea dicts
            platforms: List of platform names to include
        
        Returns:
            Filtered ideas matching specified platforms
        """
        platforms_lower = [p.lower() for p in platforms]
        return [
            idea for idea in ideas
            if idea.get("platform", "").lower() in platforms_lower
        ]
    
    @staticmethod
    def select_by_ids(
        ideas: List[Dict[str, Any]],
        ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Select ideas by specific IDs.
        
        Maintains order of provided IDs.
        
        Args:
            ideas: List of idea dicts
            ids: List of idea IDs to select
        
        Returns:
            Selected ideas in specified order
        """
        id_set = set(ids)
        id_to_idea = {idea["id"]: idea for idea in ideas if idea.get("id") in id_set}
        
        # Return in order of provided IDs
        return [id_to_idea[id_] for id_ in ids if id_ in id_to_idea]
    
    @staticmethod
    def select_by_objective(
        ideas: List[Dict[str, Any]],
        objectives: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Filter ideas by objective.
        
        Args:
            ideas: List of idea dicts
            objectives: List of objectives (awareness, engagement, conversion)
        
        Returns:
            Filtered ideas matching specified objectives
        """
        objectives_lower = [o.lower() for o in objectives]
        return [
            idea for idea in ideas
            if idea.get("objective", "").lower() in objectives_lower
        ]
    
    @staticmethod
    def select_top_n(
        ideas: List[Dict[str, Any]],
        n: int,
    ) -> List[Dict[str, Any]]:
        """
        Select top N ideas by confidence.
        
        Args:
            ideas: List of idea dicts
            n: Number of ideas to select
        
        Returns:
            Top N ideas by confidence
        """
        ranked = IdeaFilter.rank_by_confidence(ideas)
        return ranked[:n]
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    @staticmethod
    def _is_diverse_from(
        idea: Dict[str, Any],
        existing: List[Dict[str, Any]],
    ) -> bool:
        """
        Check if idea is diverse compared to existing selection.
        
        An idea is considered diverse if it differs from all existing ideas
        in at least one of: platform, tone, or objective.
        
        Args:
            idea: Idea to check
            existing: List of already selected ideas
        
        Returns:
            True if idea adds diversity
        """
        for existing_idea in existing:
            # If all three match, not diverse
            if (idea["platform"] == existing_idea["platform"] and
                idea["tone"] == existing_idea["tone"] and
                idea["objective"] == existing_idea["objective"]):
                return False
        
        return True
    
    @staticmethod
    def get_statistics(ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about a set of ideas.
        
        Useful for debugging and analysis.
        
        Args:
            ideas: List of idea dicts
        
        Returns:
            Statistics dict
        """
        if not ideas:
            return {"count": 0}
        
        platforms = {}
        tones = {}
        objectives = {}
        confidences = []
        
        for idea in ideas:
            platform = idea.get("platform", "unknown")
            tone = idea.get("tone", "unknown")
            objective = idea.get("objective", "unknown")
            confidence = idea.get("confidence", 0.0)
            
            platforms[platform] = platforms.get(platform, 0) + 1
            tones[tone] = tones.get(tone, 0) + 1
            objectives[objective] = objectives.get(objective, 0) + 1
            confidences.append(confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        min_confidence = min(confidences) if confidences else 0.0
        max_confidence = max(confidences) if confidences else 0.0
        
        return {
            "count": len(ideas),
            "platforms": platforms,
            "tones": tones,
            "objectives": objectives,
            "confidence": {
                "min": min_confidence,
                "max": max_confidence,
                "avg": avg_confidence,
            }
        }


class SelectionStrategy:
    """
    Named selection strategies for common use cases.
    
    Provides pre-configured selection logic for typical scenarios.
    """
    
    @staticmethod
    def diverse_multi_platform(
        ideas: List[Dict[str, Any]],
        max_count: int = 3,
        min_confidence: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Select diverse ideas across multiple platforms.
        
        Good for: Multi-platform campaigns
        
        Args:
            ideas: List of idea dicts
            max_count: Maximum ideas to select
            min_confidence: Minimum confidence threshold
        
        Returns:
            Diverse selection of high-confidence ideas
        """
        filtered = IdeaFilter.filter_by_confidence(ideas, min_confidence)
        return IdeaFilter.select_diverse(filtered, max_count)
    
    @staticmethod
    def linkedin_only_professional(
        ideas: List[Dict[str, Any]],
        max_count: int = 2,
        min_confidence: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Select LinkedIn-focused professional content.
        
        Good for: B2B campaigns targeting C-Level
        
        Args:
            ideas: List of idea dicts
            max_count: Maximum ideas to select
            min_confidence: Minimum confidence threshold
        
        Returns:
            Top LinkedIn ideas with professional tone
        """
        linkedin_ideas = IdeaFilter.select_by_platform(ideas, ["linkedin"])
        filtered = IdeaFilter.filter_by_confidence(linkedin_ideas, min_confidence)
        return IdeaFilter.select_top_n(filtered, max_count)
    
    @staticmethod
    def founder_multi_channel(
        ideas: List[Dict[str, Any]],
        max_count: int = 3,
        min_confidence: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Select ideas for founder audience across channels.
        
        Good for: Startup ecosystem campaigns
        
        Args:
            ideas: List of idea dicts
            max_count: Maximum ideas to select
            min_confidence: Minimum confidence threshold
        
        Returns:
            Instagram/Twitter ideas with empowering tone
        """
        founder_platforms = IdeaFilter.select_by_platform(
            ideas, ["instagram", "twitter"]
        )
        filtered = IdeaFilter.filter_by_confidence(founder_platforms, min_confidence)
        return IdeaFilter.select_diverse(filtered, max_count)