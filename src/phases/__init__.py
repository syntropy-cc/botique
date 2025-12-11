"""
Phase wrappers module

Thin wrappers around core components for pipeline phases.

Exports:
    - phase1_ideation.run: Phase 1 wrapper
    - phase2_selection.run: Phase 2 wrapper
    - phase3_coherence.run: Phase 3 wrapper
"""

from .phase1_ideation import run as run_phase1
from .phase2_selection import run as run_phase2
from .phase3_coherence import run as run_phase3

__all__ = [
    "run_phase1",
    "run_phase2",
    "run_phase3",
]

