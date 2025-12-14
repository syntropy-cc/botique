"""
CLI argument parsing and command handlers.

Builds argument parser with subcommands (full, ideas, briefs, prompts)
and handler functions for each command.

Location: src/cli/commands.py
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from ..core.config import (
    IdeationConfig,
    SelectionConfig,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    PROMPTS_DIR,
    ROOT_DIR,
)
from ..core.llm_client import HttpLLMClient
from ..orchestrator import Orchestrator


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build CLI argument parser with subcommands.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Social Media Post Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Global options
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--llm-base-url",
        default=DEFAULT_BASE_URL,
        help=f"LLM API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--llm-model",
        default=DEFAULT_MODEL,
        help=f"LLM model name (default: {DEFAULT_MODEL})",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )
    
    # Command: full
    p_full = subparsers.add_parser(
        "full",
        help="Run complete pipeline: Article → Ideas → Briefs",
    )
    p_full.add_argument(
        "--article",
        "-a",
        type=Path,
        required=True,
        help="Article file path",
    )
    p_full.add_argument(
        "--min-ideas",
        type=int,
        default=3,
        help="Minimum ideas to generate (default: 3)",
    )
    p_full.add_argument(
        "--max-ideas",
        type=int,
        default=5,
        help="Maximum ideas to generate (default: 5)",
    )
    p_full.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence threshold (default: 0.7)",
    )
    p_full.add_argument(
        "--max-posts",
        type=int,
        default=3,
        help="Maximum posts to generate (default: 3)",
    )
    p_full.add_argument(
        "--strategy",
        choices=["diverse", "top"],
        default="diverse",
        help="Selection strategy: diverse (variety) or top (highest confidence)",
    )
    
    # Command: ideas
    p_ideas = subparsers.add_parser(
        "ideas",
        help="Run Phase 1 only: Generate ideas from article",
    )
    p_ideas.add_argument(
        "--article",
        "-a",
        type=Path,
        required=True,
        help="Article file path",
    )
    p_ideas.add_argument(
        "--min-ideas",
        type=int,
        default=3,
        help="Minimum ideas to generate (default: 3)",
    )
    p_ideas.add_argument(
        "--max-ideas",
        type=int,
        default=5,
        help="Maximum ideas to generate (default: 5)",
    )
    
    # Command: briefs
    p_briefs = subparsers.add_parser(
        "briefs",
        help="Run Phase 2 + 3: Generate briefs from ideas JSON",
    )
    p_briefs.add_argument(
        "--ideas-json",
        type=Path,
        required=True,
        help="Path to phase1_ideas.json",
    )
    p_briefs.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence threshold (default: 0.7)",
    )
    p_briefs.add_argument(
        "--max-posts",
        type=int,
        default=3,
        help="Maximum posts to generate (default: 3)",
    )
    p_briefs.add_argument(
        "--strategy",
        choices=["diverse", "top"],
        default="diverse",
        help="Selection strategy: diverse (variety) or top (highest confidence)",
    )
    
    # Command: prompts
    p_prompts = subparsers.add_parser(
        "prompts",
        help="Register/update prompts from directory in database",
    )
    p_prompts.add_argument(
        "--prompts-dir",
        type=Path,
        default=PROMPTS_DIR,
        help=f"Directory containing .md prompt files (default: {PROMPTS_DIR})",
    )
    p_prompts.add_argument(
        "--update-metadata",
        action="store_true",
        help="Update metadata of existing prompts (without creating new versions)",
    )
    p_prompts.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode (less output)",
    )
    
    return parser


def handle_full_command(args: argparse.Namespace) -> int:
    """
    Handle 'full' command: Run complete pipeline.
    
    Args:
        args: Parsed arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize orchestrator
        llm_client = HttpLLMClient(
            base_url=args.llm_base_url,
            model=args.llm_model,
        )
        
        orchestrator = Orchestrator(
            llm_client=llm_client,
            output_dir=args.output_dir,
        )
        
        # Build configs
        ideation_config = IdeationConfig(
            min_ideas=args.min_ideas,
            max_ideas=args.max_ideas,
        )
        
        selection_config = SelectionConfig(
            min_confidence=args.min_confidence,
            max_selected=args.max_posts,
            strategy=args.strategy,
        )
        
        # Run pipeline
        result = orchestrator.run_full_pipeline(
            article_path=args.article,
            ideation_config=ideation_config,
            selection_config=selection_config,
        )
        
        print(f"\n✓ Pipeline completed successfully")
        print(f"  Output: {result['output_dir']}")
        
        return 0
    
    except Exception as exc:
        print(f"\n✗ Error: {exc}", file=sys.stderr)
        return 1


def handle_ideas_command(args: argparse.Namespace) -> int:
    """
    Handle 'ideas' command: Run Phase 1 only.
    
    Args:
        args: Parsed arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize orchestrator
        llm_client = HttpLLMClient(
            base_url=args.llm_base_url,
            model=args.llm_model,
        )
        
        orchestrator = Orchestrator(
            llm_client=llm_client,
            output_dir=args.output_dir,
        )
        
        # Build config
        ideation_config = IdeationConfig(
            min_ideas=args.min_ideas,
            max_ideas=args.max_ideas,
        )
        
        # Run phase 1
        result = orchestrator.run_ideas_phase(
            article_path=args.article,
            config=ideation_config,
        )
        
        print(f"\n✓ Phase 1 completed successfully")
        print(f"  Generated {result['ideas_count']} ideas")
        
        # Show filtering info if enabled
        if result.get('filtered_count') != result.get('ideas_count'):
            print(f"  Filtered to {result.get('filtered_count', 0)} ideas")
        
        # Show coherence briefs info
        briefs_count = result.get('briefs_count', 0)
        if briefs_count > 0:
            print(f"  Generated {briefs_count} coherence brief(s)")
            output_dir = Path(result.get('output_dir', ''))
            if output_dir.exists():
                consolidated_path = output_dir / "coherence_briefs.json"
                if consolidated_path.exists():
                    print(f"  Consolidated briefs: {consolidated_path}")
                # Show individual brief paths
                for brief in result.get('briefs', [])[:3]:  # Show first 3
                    brief_path = output_dir / brief.post_id / "coherence_brief.json"
                    if brief_path.exists():
                        print(f"    - {brief.post_id}: {brief_path}")
                if briefs_count > 3:
                    print(f"    ... and {briefs_count - 3} more")
        
        print(f"  Output: {result['output_path']}")
        
        return 0
    
    except Exception as exc:
        print(f"\n✗ Error: {exc}", file=sys.stderr)
        return 1


def handle_briefs_command(args: argparse.Namespace) -> int:
    """
    Handle 'briefs' command: Run Phase 2 + 3 from ideas JSON.
    
    Args:
        args: Parsed arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Load ideas JSON
        if not args.ideas_json.exists():
            raise FileNotFoundError(f"Ideas file not found: {args.ideas_json}")
        
        ideas_payload = json.loads(args.ideas_json.read_text(encoding="utf-8"))
        
        # Extract article slug from path
        # Assumes structure: output/<slug>/phase1_ideas.json
        article_slug = args.ideas_json.parent.name
        
        # Initialize orchestrator
        llm_client = HttpLLMClient(
            base_url=args.llm_base_url,
            model=args.llm_model,
        )
        
        orchestrator = Orchestrator(
            llm_client=llm_client,
            output_dir=args.output_dir,
        )
        
        # Build selection config
        selection_config = SelectionConfig(
            min_confidence=args.min_confidence,
            max_selected=args.max_posts,
            strategy=args.strategy,
        )
        
        # Run phase 2
        print("\n" + "="*70)
        print("PHASE 2: SELECTION")
        print("="*70)
        
        phase2_result = orchestrator.run_selection_phase(
            ideas_payload=ideas_payload,
            config=selection_config,
            article_slug=article_slug,
        )
        
        print(f"Selected {phase2_result['selection_count']} ideas")
        
        # Run phase 3
        print("\n" + "="*70)
        print("PHASE 3: COHERENCE")
        print("="*70)
        
        phase3_result = orchestrator.run_coherence_phase(
            selected_ideas=phase2_result["selected_ideas"],
            article_summary=ideas_payload["article_summary"],
            article_slug=article_slug,
        )
        
        print(f"Generated {phase3_result['briefs_count']} coherence briefs")
        
        print(f"\n✓ Phases 2-3 completed successfully")
        print(f"  Output: {phase3_result['output_dir']}")
        
        return 0
    
    except Exception as exc:
        print(f"\n✗ Error: {exc}", file=sys.stderr)
        return 1


def handle_prompts_command(args: argparse.Namespace) -> int:
    """
    Handle 'prompts' command: Register/update prompts from directory.
    
    Args:
        args: Parsed arguments
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Import register functions directly
        # Add scripts directory to path temporarily
        scripts_dir = ROOT_DIR / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        
        # Import from the script module
        import importlib.util
        script_path = ROOT_DIR / "scripts" / "register_prompts_from_directory.py"
        
        if not script_path.exists():
            raise FileNotFoundError(
                f"Script not found: {script_path}\n"
                "Make sure scripts/register_prompts_from_directory.py exists"
            )
        
        spec = importlib.util.spec_from_file_location(
            "register_prompts_from_directory", script_path
        )
        register_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(register_module)
        
        # Check if prompts directory exists
        if not args.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory not found: {args.prompts_dir}\n"
                f"Please create the directory or specify a different path with --prompts-dir"
            )
        
        # Call register function
        result = register_module.register_all_prompts(
            prompts_dir=args.prompts_dir,
            db_path=None,  # Use default
            verbose=not args.quiet,
            update_metadata=args.update_metadata,
        )
        
        if result["total_files"] == 0:
            print("\n⚠️  No prompt files found")
            return 1
        
        if not args.quiet:
            print("\n✓ Prompts registration completed successfully")
        return 0
    
    except Exception as exc:
        print(f"\n✗ Error: {exc}", file=sys.stderr)
        import traceback
        if not args.quiet:
            traceback.print_exc()
        return 1


def main() -> int:
    """
    Main entrypoint for CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = build_arg_parser()
    args = parser.parse_args()
    
    # Route to appropriate handler
    if args.command == "full":
        return handle_full_command(args)
    elif args.command == "ideas":
        return handle_ideas_command(args)
    elif args.command == "briefs":
        return handle_briefs_command(args)
    elif args.command == "prompts":
        return handle_prompts_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

