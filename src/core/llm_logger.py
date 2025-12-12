"""
LLM Logger module

Logging system for tracking LLM API calls with inputs, outputs, and metrics.

Location: src/core/llm_logger.py
"""

import json
import os
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class LLMLogger:
    """
    Logger for LLM API calls.
    
    Captures all LLM calls with:
    - Input prompts and parameters
    - Output responses
    - Performance metrics (tokens, duration, costs)
    - Context (phase, function, article)
    - Error information
    
    Logs are saved in JSON format for easy analysis and auditing.
    """
    
    # Cost estimates per 1K tokens (input/output) by model
    # These are approximate and should be updated based on actual pricing
    MODEL_COSTS = {
        "deepseek-chat": {"input": 0.00014, "output": 0.00028},  # per 1K tokens
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        central_logs_dir: Optional[Path] = None,
        enabled: bool = True,
    ):
        """
        Initialize LLM logger.
        
        Args:
            output_dir: Base output directory (defaults to OUTPUT_DIR)
            central_logs_dir: Centralized logs directory (optional)
            enabled: Whether logging is enabled (default: True)
        """
        from .config import OUTPUT_DIR
        
        self.enabled = enabled
        self.output_dir = output_dir or OUTPUT_DIR
        self.central_logs_dir = central_logs_dir or self._get_central_logs_dir()
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.pipeline_start = datetime.utcnow().isoformat() + "Z"
        self.calls: List[Dict[str, Any]] = []
        
        # Context tracking
        self.current_article_slug: Optional[str] = None
        self.current_post_id: Optional[str] = None
        self.current_slide_number: Optional[int] = None
    
    def _get_central_logs_dir(self) -> Optional[Path]:
        """Get central logs directory from env var or default location"""
        env_dir = os.getenv("LLM_LOGS_DIR")
        if env_dir:
            return Path(env_dir)
        
        # Default to logs/llm_calls/ in project root
        root_dir = Path(__file__).resolve().parents[2]
        return root_dir / "logs" / "llm_calls"
    
    def set_context(
        self,
        article_slug: Optional[str] = None,
        post_id: Optional[str] = None,
        slide_number: Optional[int] = None,
    ):
        """
        Set context for subsequent log entries.
        
        Args:
            article_slug: Article identifier
            post_id: Post identifier
            slide_number: Slide number
        """
        if article_slug is not None:
            self.current_article_slug = article_slug
        if post_id is not None:
            self.current_post_id = post_id
        if slide_number is not None:
            self.current_slide_number = slide_number
    
    def _detect_phase_and_function(self) -> tuple[str, str]:
        """
        Detect phase and function from stack trace.
        
        Skips internal frames (llm_client, llm_logger) to find the actual caller.
        
        Returns:
            Tuple of (phase, function) identifiers
        """
        stack = traceback.extract_stack()
        
        # Skip internal frames: current frame, log_call, generate, etc.
        skip_patterns = ["llm_client.py", "llm_logger.py"]
        
        # Look for phase functions or generator methods
        for frame in reversed(stack[:-1]):  # Exclude current frame
            filename = frame.filename
            func_name = frame.name
            
            # Skip internal frames
            if any(pattern in filename for pattern in skip_patterns):
                continue
            
            # Detect phase based on filename or function name
            if "phase1_ideation" in filename or "IdeaGenerator" in func_name or "generate_ideas" in func_name:
                return ("phase1_ideation", func_name)
            elif "phase2_selection" in filename:
                return ("phase2_selection", func_name)
            elif "phase3_coherence" in filename or "CoherenceBriefBuilder" in func_name:
                return ("phase3_coherence", func_name)
            elif "phase4" in filename or "NarrativeArchitect" in func_name:
                return ("phase4_post_creation", func_name)
            elif "phase5" in filename or "Copywriter" in func_name or "VisualComposer" in func_name:
                return ("phase5_slide_generation", func_name)
            elif "phase6" in filename or "CaptionWriter" in func_name:
                return ("phase6_finalization", func_name)
        
        # Fallback: use the first non-internal frame
        for frame in reversed(stack[:-1]):
            filename = frame.filename
            if not any(pattern in filename for pattern in skip_patterns):
                return ("unknown", frame.name)
        
        # Last resort
        return ("unknown", "unknown")
    
    def _calculate_cost(
        self,
        model: str,
        tokens_input: Optional[int],
        tokens_output: Optional[int],
    ) -> Optional[float]:
        """
        Calculate estimated cost based on model and tokens.
        
        Args:
            model: Model identifier
            tokens_input: Input tokens
            tokens_output: Output tokens
        
        Returns:
            Estimated cost in USD, or None if cannot calculate
        """
        if tokens_input is None or tokens_output is None:
            return None
        
        costs = self.MODEL_COSTS.get(model)
        if not costs:
            return None
        
        input_cost = (tokens_input / 1000) * costs["input"]
        output_cost = (tokens_output / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def log_call(
        self,
        prompt: str,
        response: Optional[str],
        model: str,
        base_url: str,
        max_tokens: int,
        temperature: float,
        duration_ms: float,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        tokens_total: Optional[int] = None,
        status: str = "success",
        error: Optional[str] = None,
        phase: Optional[str] = None,
        function: Optional[str] = None,
    ):
        """
        Log an LLM API call.
        
        Args:
            prompt: Input prompt text
            response: Output response text (None if error)
            model: Model identifier
            base_url: API base URL
            max_tokens: Maximum tokens requested
            temperature: Temperature setting
            duration_ms: Duration in milliseconds
            tokens_input: Input tokens (if available)
            tokens_output: Output tokens (if available)
            tokens_total: Total tokens (if available)
            status: Call status ("success", "error", "timeout")
            error: Error message if status is "error"
            phase: Phase identifier (auto-detected if None)
            function: Function name (auto-detected if None)
        """
        if not self.enabled:
            return
        
        # Auto-detect phase and function if not provided
        if phase is None or function is None:
            detected_phase, detected_function = self._detect_phase_and_function()
            phase = phase or detected_phase
            function = function or detected_function
        
        # Calculate cost
        cost_estimate = self._calculate_cost(model, tokens_input, tokens_output)
        
        # Build log entry
        call_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        log_entry: Dict[str, Any] = {
            "call_id": call_id,
            "timestamp": timestamp,
            "phase": phase,
            "function": function,
            "model": model,
            "base_url": base_url,
            "input": {
                "prompt": prompt,
                "prompt_length": len(prompt),
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            "output": {
                "content": response if response else None,
                "content_length": len(response) if response else 0,
                "truncated": False,  # Could be enhanced to detect truncation
            },
            "metrics": {
                "duration_ms": round(duration_ms, 2),
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "tokens_total": tokens_total,
                "cost_estimate": round(cost_estimate, 6) if cost_estimate else None,
            },
            "status": status,
            "error": error,
            "context": {
                "article_slug": self.current_article_slug,
                "post_id": self.current_post_id,
                "slide_number": self.current_slide_number,
            },
        }
        
        self.calls.append(log_entry)
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_id
    
    def get_logs_path(self, article_slug: Optional[str] = None) -> Path:
        """
        Get path for log file.
        
        Args:
            article_slug: Article slug for local logs (uses current if None)
        
        Returns:
            Path to log file
        """
        article_slug = article_slug or self.current_article_slug or "unknown"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        log_dir = self.output_dir / article_slug / "llm_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir / f"session_{timestamp}_{self.session_id[:8]}.json"
    
    def get_central_logs_path(self, article_slug: Optional[str] = None) -> Optional[Path]:
        """
        Get path for centralized log file.
        
        Args:
            article_slug: Article slug (uses current if None)
        
        Returns:
            Path to centralized log file, or None if central logging disabled
        """
        if not self.central_logs_dir:
            return None
        
        article_slug = article_slug or self.current_article_slug or "unknown"
        now = datetime.utcnow()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Create date-based directory structure
        log_dir = (
            self.central_logs_dir
            / str(now.year)
            / f"{now.month:02d}"
            / f"{now.day:02d}"
        )
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir / f"{article_slug}_{self.session_id[:8]}_{timestamp}.json"
    
    def save_logs(self, article_slug: Optional[str] = None) -> Dict[str, str]:
        """
        Save all logged calls to file(s).
        
        Saves to both local and central locations if configured.
        
        Args:
            article_slug: Article slug (uses current if None)
        
        Returns:
            Dict with paths to saved log files
        """
        if not self.enabled or not self.calls:
            return {}
        
        article_slug = article_slug or self.current_article_slug or "unknown"
        pipeline_end = datetime.utcnow().isoformat() + "Z"
        
        # Calculate totals
        total_tokens = sum(
            call["metrics"]["tokens_total"]
            for call in self.calls
            if call["metrics"]["tokens_total"] is not None
        )
        total_cost = sum(
            call["metrics"]["cost_estimate"]
            for call in self.calls
            if call["metrics"]["cost_estimate"] is not None
        )
        
        # Build log document
        log_document = {
            "session_id": self.session_id,
            "article_slug": article_slug,
            "pipeline_start": self.pipeline_start,
            "pipeline_end": pipeline_end,
            "total_calls": len(self.calls),
            "total_tokens": total_tokens if total_tokens > 0 else None,
            "total_cost_estimate": round(total_cost, 6) if total_cost > 0 else None,
            "calls": self.calls,
        }
        
        saved_paths = {}
        
        # Save local log
        local_path = self.get_logs_path(article_slug)
        local_path.write_text(
            json.dumps(log_document, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        saved_paths["local"] = str(local_path)
        
        # Save central log if configured
        central_path = self.get_central_logs_path(article_slug)
        if central_path:
            central_path.write_text(
                json.dumps(log_document, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            saved_paths["central"] = str(central_path)
        
        return saved_paths
    
    def reset_session(self):
        """Reset session for new pipeline run"""
        self.session_id = str(uuid.uuid4())
        self.pipeline_start = datetime.utcnow().isoformat() + "Z"
        self.calls = []
        self.current_article_slug = None
        self.current_post_id = None
        self.current_slide_number = None

