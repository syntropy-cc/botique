"""
Event Logger module

Logging system for tracking all workflow events (LLM calls and non-LLM workflow steps)
with inputs, outputs, and metrics. All events are stored in a database (SQLite or PostgreSQL).

Location: src/core/llm_logger.py
"""

import json
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .llm_log_db import db_connection, get_db_path, init_database
from .pricing import calculate_cost


class LLMLogger:
    """
    Logger for all workflow events (LLM calls and non-LLM workflow steps).
    
    Captures:
    - LLM events: Input prompts, output responses, performance metrics (tokens, duration, costs)
    - Non-LLM workflow events: Process steps, preprocessing, postprocessing, tool calls, system events
    - Context: Phase, function, article, post, slide information
    - Error information and status
    
    All events are stored in a database (SQLite by default, PostgreSQL via DB_URL).
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
        enabled: bool = True,
        db_path: Optional[Path] = None,
        use_sql: bool = True,
    ):
        """
        Initialize event logger.
        
        Args:
            enabled: Whether logging is enabled (default: True)
            db_path: Path to SQL database (uses default if None)
            use_sql: Whether to write to SQL database (default: True)
        """
        self.enabled = enabled
        self.db_path = db_path or get_db_path()
        self.use_sql = use_sql
        
        # Initialize database if using SQL
        if self.use_sql:
            init_database(self.db_path)
        
        # Session tracking (for trace_id and in-memory debugging)
        self.session_id = str(uuid.uuid4())
        self.pipeline_start = datetime.utcnow().isoformat() + "Z"
        self.calls: List[Dict[str, Any]] = []
        
        # Current trace ID (for SQL logging)
        self.current_trace_id: Optional[str] = None
        
        # Context tracking
        self.current_article_slug: Optional[str] = None
        self.current_post_id: Optional[str] = None
        self.current_slide_number: Optional[int] = None
    
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
        
        Uses database pricing if available, falls back to MODEL_COSTS.
        
        Args:
            model: Model identifier
            tokens_input: Input tokens
            tokens_output: Output tokens
        
        Returns:
            Estimated cost in USD, or None if cannot calculate
        """
        if tokens_input is None or tokens_output is None:
            return None
        
        # Try database pricing first
        if self.use_sql:
            try:
                cost_input, cost_output, cost_total = calculate_cost(
                    model, tokens_input, tokens_output, self.db_path
                )
                if cost_total is not None:
                    return cost_total
            except Exception:
                pass  # Fall back to MODEL_COSTS
        
        # Fall back to MODEL_COSTS
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
        prompt_id: Optional[str] = None,
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
            prompt_id: Optional prompt ID for version tracking
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
        
        # Write to SQL database
        if self.use_sql:
            self._write_llm_event_to_sql(
                trace_id=self.current_trace_id or self.session_id,
                name=f"{phase}.{function}",
                model=model,
                input_text=prompt,
                input_obj={
                    "prompt": prompt,
                    "prompt_length": len(prompt),
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "base_url": base_url,
                },
                output_text=response,
                output_obj={
                    "content": response if response else None,
                    "content_length": len(response) if response else 0,
                    "truncated": False,
                },
                duration_ms=duration_ms,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_total,
                prompt_id=prompt_id,
                status=status,
                error=error,
                metadata={
                    "phase": phase,
                    "function": function,
                    "base_url": base_url,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "prompt_length": len(prompt),
                    "context": {
                        "article_slug": self.current_article_slug,
                        "post_id": self.current_post_id,
                        "slide_number": self.current_slide_number,
                    },
                },
            )
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_id
    
    def reset_session(self):
        """Reset session for new pipeline run"""
        self.session_id = str(uuid.uuid4())
        self.pipeline_start = datetime.utcnow().isoformat() + "Z"
        self.calls = []
        self.current_trace_id = None
        self.current_article_slug = None
        self.current_post_id = None
        self.current_slide_number = None
    
    # =============================================================================
    # SQL Backend Methods
    # =============================================================================
    
    def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new trace (high-level execution).
        
        Args:
            name: Human-readable trace name (e.g., "generate_ideas", "full_pipeline")
            user_id: Optional user identifier
            tenant_id: Optional tenant identifier
            tags: Optional comma-separated tags
            metadata: Optional metadata dictionary (will be JSON-serialized)
            
        Returns:
            Trace ID (UUID string)
        """
        if not self.enabled or not self.use_sql:
            # Return session_id for compatibility
            return self.session_id
        
        trace_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO traces 
                (id, created_at, name, user_id, tenant_id, tags, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                trace_id,
                now,
                name,
                user_id,
                tenant_id,
                tags,
                metadata_json,
            ))
            conn.commit()
        
        self.current_trace_id = trace_id
        return trace_id
    
    def log_llm_event(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_text: Optional[str],
        input_obj: Optional[Dict[str, Any]],
        output_text: Optional[str],
        output_obj: Optional[Dict[str, Any]],
        duration_ms: float,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        tokens_total: Optional[int] = None,
        parent_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an LLM event to SQL database.
        
        Args:
            trace_id: Trace ID (from create_trace)
            name: Event name (e.g., "deepseek-chat", "phase1_ideation.generate_ideas")
            model: Model identifier
            input_text: Main prompt or textual input
            input_obj: Full input object (will be JSON-serialized)
            output_text: Main response or textual output
            output_obj: Full output object (will be JSON-serialized)
            duration_ms: Duration in milliseconds
            tokens_input: Input tokens
            tokens_output: Output tokens
            tokens_total: Total tokens
            parent_id: Optional parent event ID (for hierarchical relationships)
            prompt_id: Optional prompt ID (required for LLM events to track prompt version)
            metadata: Optional metadata dictionary
            
        Returns:
            Event ID (UUID string)
        """
        # Extract important fields from input_obj to include in metadata if not already present
        if metadata is None:
            metadata = {}
        
        # Add important fields from input_obj to metadata if available
        if input_obj:
            if "base_url" in input_obj and "base_url" not in metadata:
                metadata["base_url"] = input_obj["base_url"]
            if "max_tokens" in input_obj and "max_tokens" not in metadata:
                metadata["max_tokens"] = input_obj["max_tokens"]
            if "temperature" in input_obj and "temperature" not in metadata:
                metadata["temperature"] = input_obj["temperature"]
            if "prompt_length" in input_obj and "prompt_length" not in metadata:
                metadata["prompt_length"] = input_obj["prompt_length"]
        
        return self._write_llm_event_to_sql(
            trace_id=trace_id,
            name=name,
            model=model,
            input_text=input_text,
            input_obj=input_obj,
            output_text=output_text,
            output_obj=output_obj,
            duration_ms=duration_ms,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            parent_id=parent_id,
            prompt_id=prompt_id,
            metadata=metadata,
        )
    
    def _write_llm_event_to_sql(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_text: Optional[str],
        input_obj: Optional[Dict[str, Any]],
        output_text: Optional[str],
        output_obj: Optional[Dict[str, Any]],
        duration_ms: float,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        tokens_total: Optional[int] = None,
        parent_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        status: str = "success",
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Internal method to write LLM event to SQL."""
        if not self.enabled or not self.use_sql:
            return str(uuid.uuid4())  # Return dummy ID
        
        event_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        # Calculate costs
        cost_input, cost_output, cost_total = calculate_cost(
            model, tokens_input, tokens_output, self.db_path
        )
        
        # Serialize JSON fields
        input_json = json.dumps(input_obj) if input_obj else None
        output_json = json.dumps(output_obj) if output_obj else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events 
                (id, trace_id, parent_id, prompt_id, created_at, type, name, model, role,
                 input_text, input_json, output_text, output_json, error, duration_ms,
                 tokens_input, tokens_output, tokens_total,
                 cost_input, cost_output, cost_total, metadata_json)
                VALUES (?, ?, ?, ?, ?, 'llm', ?, ?, 'user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                trace_id,
                parent_id,
                prompt_id,
                now,
                name,
                model,
                input_text,
                input_json,
                output_text,
                output_json,
                error,
                int(round(duration_ms)),
                tokens_input,
                tokens_output,
                tokens_total,
                cost_input,
                cost_output,
                cost_total,
                metadata_json,
            ))
            conn.commit()
        
        return event_id
    
    def log_step_event(
        self,
        trace_id: str,
        name: str,
        input_text: Optional[str] = None,
        input_obj: Optional[Dict[str, Any]] = None,
        output_text: Optional[str] = None,
        output_obj: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        type: str = "step",
        error: Optional[str] = None,
        status: str = "success",
    ) -> str:
        """
        Log a non-LLM workflow step event to SQL database.
        
        Args:
            trace_id: Trace ID (from create_trace)
            name: Event name (e.g., "preprocess_prompt", "validate_json", "phase1_start")
            input_text: Optional textual input
            input_obj: Optional input object (will be JSON-serialized)
            output_text: Optional textual output
            output_obj: Optional output object (will be JSON-serialized)
            duration_ms: Optional duration in milliseconds
            parent_id: Optional parent event ID (for hierarchical relationships)
            metadata: Optional metadata dictionary
            type: Event type (default: "step", can be "tool", "preprocess", "postprocess", "system")
            error: Optional error message if the step failed
            status: Step status (default: "success", can be "error", "timeout", etc.)
            
        Returns:
            Event ID (UUID string)
        """
        if not self.enabled or not self.use_sql:
            return str(uuid.uuid4())  # Return dummy ID
        
        event_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        # Enhance metadata with status and other process-specific information
        if metadata is None:
            metadata = {}
        
        # Add status to metadata if not already present
        if "status" not in metadata:
            metadata["status"] = status
        
        # Add process-specific information to metadata
        if input_obj:
            # Extract key fields from input_obj to metadata for easier querying
            if "file_path" in input_obj and "file_path" not in metadata:
                metadata["file_path"] = input_obj["file_path"]
            if "idea_id" in input_obj and "idea_id" not in metadata:
                metadata["idea_id"] = input_obj["idea_id"]
            if "post_id" in input_obj and "post_id" not in metadata:
                metadata["post_id"] = input_obj["post_id"]
        
        if output_obj:
            # Extract key fields from output_obj to metadata
            if "ideas_count" in output_obj and "ideas_count" not in metadata:
                metadata["ideas_count"] = output_obj["ideas_count"]
            if "platform" in output_obj and "platform" not in metadata:
                metadata["platform"] = output_obj["platform"]
            if "format" in output_obj and "format" not in metadata:
                metadata["format"] = output_obj["format"]
        
        # Serialize JSON fields
        input_json = json.dumps(input_obj) if input_obj else None
        output_json = json.dumps(output_obj) if output_obj else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Ensure we have at least input_text or input_json
        # If only input_obj is provided, extract a summary for input_text
        if not input_text and input_obj:
            # Try to create a readable summary
            if isinstance(input_obj, dict):
                if "file_path" in input_obj:
                    input_text = f"Processing file: {input_obj['file_path']}"
                elif "idea_id" in input_obj:
                    input_text = f"Processing idea: {input_obj['idea_id']}"
                elif "post_id" in input_obj:
                    input_text = f"Processing post: {input_obj['post_id']}"
                else:
                    # Create a summary from first few keys
                    keys = list(input_obj.keys())[:3]
                    input_text = f"Processing: {', '.join(keys)}"
        
        # For output, ensure we have at least output_text or output_json
        # Events with status 'success' or 'complete' should have output
        if status in ["success", "complete"] and not output_text and not output_json:
            # If we have output_obj, create output_text from it
            if output_obj:
                if isinstance(output_obj, dict):
                    if "ideas_count" in output_obj:
                        output_text = f"Loaded {output_obj['ideas_count']} ideas"
                    elif "post_id" in output_obj:
                        output_text = f"Generated brief for {output_obj['post_id']}"
                    elif "platform" in output_obj and "format" in output_obj:
                        output_text = f"Generated {output_obj['platform']}/{output_obj['format']} brief"
                    else:
                        # Create a summary from first few keys
                        keys = list(output_obj.keys())[:3]
                        output_text = f"Completed: {', '.join(keys)}"
        
        # For events with error status, ensure error field is set
        if status == "error" and not error:
            error = "Process failed (no error message provided)"
        
        # Ensure metadata always has at least basic information
        if not metadata_json and not metadata:
            metadata = {"status": status}
            metadata_json = json.dumps(metadata)
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events 
                (id, trace_id, parent_id, created_at, type, name, model, role,
                 input_text, input_json, output_text, output_json, error, duration_ms,
                 tokens_input, tokens_output, tokens_total,
                 cost_input, cost_output, cost_total, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, ?)
            """, (
                event_id,
                trace_id,
                parent_id,
                now,
                type,
                name,
                input_text,
                input_json,
                output_text,
                output_json,
                error,
                int(round(duration_ms)) if duration_ms is not None else None,
                metadata_json,
            ))
            conn.commit()
        
        return event_id
    
    def set_event_quality(
        self,
        event_id: str,
        score: Optional[float] = None,
        label: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Set quality metrics for an event.
        
        Args:
            event_id: Event ID
            score: Optional quality score (0-1 or 0-5)
            label: Optional quality label (e.g., "good", "bad", "needs_review")
            metadata: Optional quality metadata (who rated, criteria, etc.)
        """
        if not self.enabled or not self.use_sql:
            return
        
        quality_metadata_json = json.dumps(metadata) if metadata else None
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events 
                SET quality_score = ?, quality_label = ?, quality_metadata_json = ?
                WHERE id = ?
            """, (score, label, quality_metadata_json, event_id))
            conn.commit()

