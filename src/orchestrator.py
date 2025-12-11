"""
Main orchestrator for the social media post generation pipeline.

Thin coordinator that initializes LLM client and phase handlers,
then orchestrates the execution of phases in sequence.

Location: src/orchestrator.py
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .core.config import (
    IdeationConfig,
    SelectionConfig,
    OUTPUT_DIR,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_API_ENV_VAR,
)
from .core.llm_client import HttpLLMClient
from .phases.phase1_ideation import run as run_phase1
from .phases.phase2_selection import run as run_phase2
from .phases.phase3_coherence import run as run_phase3


class Orchestrator:
    """
    Main coordinator for the pipeline.
    
    Thin coordinator that:
    - Initializes LLM client and phase handlers
    - run_full_pipeline() calls phases in sequence
    - run_ideas_phase(), run_selection_phase(), run_coherence_phase()
    - Returns results
    """
    
    def __init__(
        self,
        llm_client: Optional[HttpLLMClient] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize orchestrator.
        
        Args:
            llm_client: LLM client instance (creates default if None)
            output_dir: Output directory (defaults to OUTPUT_DIR)
        """
        if llm_client is None:
            llm_client = HttpLLMClient(
                base_url=DEFAULT_BASE_URL,
                model=DEFAULT_MODEL,
            )
        
        self.llm_client = llm_client
        self.output_dir = output_dir or OUTPUT_DIR
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_ideas_phase(
        self,
        article_path: Path,
        config: IdeationConfig,
    ) -> Dict[str, Any]:
        """
        Run Phase 1: Ideation.
        
        Args:
            article_path: Path to article file
            config: Ideation configuration
        
        Returns:
            Phase 1 output payload
        """
        return run_phase1(
            article_path=article_path,
            config=config,
            llm_client=self.llm_client,
            output_dir=self.output_dir,
        )
    
    def run_selection_phase(
        self,
        ideas_payload: Dict[str, Any],
        config: SelectionConfig,
        article_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run Phase 2: Selection.
        
        Args:
            ideas_payload: Output from phase 1
            config: Selection configuration
            article_slug: Article identifier (extracted from payload if None)
        
        Returns:
            Phase 2 output payload
        """
        if article_slug is None:
            article_slug = ideas_payload.get("article_slug", "unknown")
        
        return run_phase2(
            ideas_payload=ideas_payload,
            config=config,
            article_slug=article_slug,
            output_dir=self.output_dir,
        )
    
    def run_coherence_phase(
        self,
        selected_ideas: list,
        article_summary: Dict[str, Any],
        article_slug: str,
    ) -> Dict[str, Any]:
        """
        Run Phase 3: Coherence.
        
        Args:
            selected_ideas: List of selected idea dicts
            article_summary: Article summary from phase 1
            article_slug: Article identifier
        
        Returns:
            Phase 3 output payload
        """
        return run_phase3(
            selected_ideas=selected_ideas,
            article_summary=article_summary,
            article_slug=article_slug,
            output_dir=self.output_dir,
        )
    
    def run_full_pipeline(
        self,
        article_path: Path,
        ideation_config: Optional[IdeationConfig] = None,
        selection_config: Optional[SelectionConfig] = None,
    ) -> Dict[str, Any]:
        """
        Run full pipeline: Phase 1 → Phase 2 → Phase 3.
        
        Args:
            article_path: Path to article file
            ideation_config: Ideation configuration (defaults if None)
            selection_config: Selection configuration (defaults if None)
        
        Returns:
            Complete pipeline results with all phase outputs
        """
        # Default configs
        if ideation_config is None:
            ideation_config = IdeationConfig()
        
        if selection_config is None:
            selection_config = SelectionConfig()
        
        # Phase 1: Ideation
        print("\n" + "="*70)
        print("PHASE 1: IDEATION")
        print("="*70)
        
        phase1_result = self.run_ideas_phase(article_path, ideation_config)
        article_slug = phase1_result["article_slug"]
        
        print(f"Generated {phase1_result['ideas_count']} ideas")
        print(f"Output: {phase1_result['output_path']}")
        
        # Phase 2: Selection
        print("\n" + "="*70)
        print("PHASE 2: SELECTION")
        print("="*70)
        
        phase2_result = self.run_selection_phase(
            ideas_payload=phase1_result,
            config=selection_config,
            article_slug=article_slug,
        )
        
        print(f"Selected {phase2_result['selection_count']} ideas")
        print(f"Output: {phase2_result['output_path']}")
        
        # Phase 3: Coherence
        print("\n" + "="*70)
        print("PHASE 3: COHERENCE")
        print("="*70)
        
        phase3_result = self.run_coherence_phase(
            selected_ideas=phase2_result["selected_ideas"],
            article_summary=phase1_result["article_summary"],
            article_slug=article_slug,
        )
        
        print(f"Generated {phase3_result['briefs_count']} coherence briefs")
        print(f"Output: {phase3_result['output_path']}")
        
        # Summary
        print("\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)
        print(f"Article: {article_slug}")
        print(f"Ideas generated: {phase1_result['ideas_count']}")
        print(f"Ideas selected: {phase2_result['selection_count']}")
        print(f"Briefs created: {phase3_result['briefs_count']}")
        print(f"Output directory: {phase3_result['output_dir']}")
        
        return {
            "article_slug": article_slug,
            "phase1": phase1_result,
            "phase2": phase2_result,
            "phase3": phase3_result,
            "output_dir": phase3_result["output_dir"],
        }

