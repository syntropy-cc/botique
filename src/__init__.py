"""
Social Media Post Generation Pipeline

Main package exports for easy imports.

Exports:
    - Orchestrator: Main pipeline coordinator (compatibility wrapper)
    - IdeationConfig, SelectionConfig: Configuration classes
    - HttpLLMClient: LLM client

NOTE: This module provides backward compatibility aliases.
The new architecture uses:
    - framework/ for reusable components
    - boutique/ for project-specific components
"""

from .orchestrator import Orchestrator
from .core.config import IdeationConfig, SelectionConfig

# Import from new locations with fallback
try:
    from framework.llm.http_client import HttpLLMClient
except ImportError:
    # Fallback to old location for compatibility
    from .core.llm_client import HttpLLMClient

# Export boutique components
try:
    from boutique.orchestrator.boutique_orchestrator import BoutiqueOrchestrator
    from boutique.state_management.boutique_state import BoutiqueState
    from boutique.state_management.models.coherence_brief import CoherenceBrief
except ImportError:
    # Not available yet
    BoutiqueOrchestrator = None
    BoutiqueState = None
    CoherenceBrief = None

__all__ = [
    "Orchestrator",
    "IdeationConfig",
    "SelectionConfig",
    "HttpLLMClient",
    # New components (if available)
    "BoutiqueOrchestrator",
    "BoutiqueState",
    "CoherenceBrief",
]

