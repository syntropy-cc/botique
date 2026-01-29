"""
Test Result Logger.

Captures structured results from pipeline test executions, including:
- Test run metadata (timestamp, test name, category, status)
- Phase-by-phase results (outputs, validation, artifacts)
- Performance metrics (duration, tokens, API calls)
- Coherence brief evolution tracking
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.llm_log_db import db_connection, get_db_path, init_database, is_postgresql_mode


def init_test_results_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize database schema for test results.
    
    Creates tables for test_runs, test_phases, and test_artifacts.
    Idempotent: safe to call multiple times.
    
    Args:
        db_path: Path to SQLite database (ignored if PostgreSQL mode)
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure main database is initialized
    init_database(db_path)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Create test_runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                test_run_id TEXT PRIMARY KEY,
                test_name TEXT NOT NULL,
                test_category TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create test_phases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_phases (
                phase_id TEXT PRIMARY KEY,
                test_run_id TEXT NOT NULL,
                phase_name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms INTEGER,
                output_json TEXT,
                artifacts_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_run_id) REFERENCES test_runs(test_run_id) ON DELETE CASCADE
            )
        """)
        
        # Create test_artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_artifacts (
                artifact_id TEXT PRIMARY KEY,
                test_run_id TEXT NOT NULL,
                phase_name TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                artifact_path TEXT NOT NULL,
                artifact_metadata_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_run_id) REFERENCES test_runs(test_run_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_runs_category 
            ON test_runs(test_category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_runs_timestamp 
            ON test_runs(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_phases_run_id 
            ON test_phases(test_run_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_test_artifacts_run_id 
            ON test_artifacts(test_run_id)
        """)
        
        conn.commit()


class TestResultLogger:
    """
    Logger for test execution results.
    
    Captures structured results from pipeline tests, including phase outputs,
    validation results, performance metrics, and artifact references.
    """
    
    def __init__(
        self,
        test_name: str,
        test_category: str = "unit",
        db_path: Optional[Path] = None,
    ):
        """
        Initialize test result logger.
        
        Args:
            test_name: Name of the test function
            test_category: Category of test (unit, integration, e2e)
            db_path: Path to database (uses default if None)
        """
        self.test_name = test_name
        self.test_category = test_category
        self.db_path = db_path or get_db_path()
        
        # Initialize database schema
        init_test_results_db(self.db_path)
        
        # Test run state
        self.test_run_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.phases: Dict[str, Dict[str, Any]] = {}
        self.coherence_brief_evolution: Dict[str, List[str]] = {}
        self.performance: Dict[str, Any] = {
            "total_duration_ms": 0,
            "llm_calls": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0,
        }
        self.validation_summary: Dict[str, Any] = {
            "all_gates_passed": True,
            "failed_gates": [],
            "quality_score": 0.0,
        }
        self.status: str = "running"
        self.error: Optional[str] = None
    
    def start_test_run(self) -> str:
        """
        Start a new test run.
        
        Returns:
            Test run ID (UUID)
        """
        self.test_run_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.status = "running"
        return self.test_run_id
    
    def log_phase_result(
        self,
        phase: str,
        status: str,
        output: Dict[str, Any],
        artifacts: Optional[Dict[str, str]] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """
        Log results for a phase.
        
        Args:
            phase: Phase name (phase1, phase2, etc.)
            status: Phase status (passed, failed, skipped)
            output: Phase output dictionary
            artifacts: Dictionary mapping artifact names to file paths
            duration_ms: Phase duration in milliseconds
        """
        if self.test_run_id is None:
            raise RuntimeError("Test run not started. Call start_test_run() first.")
        
        phase_data = {
            "status": status,
            "duration_ms": duration_ms,
            "output": output,
            "artifacts": artifacts or {},
        }
        
        self.phases[phase] = phase_data
        
        # Update performance metrics
        if duration_ms:
            self.performance["total_duration_ms"] += duration_ms
        
        # Track coherence brief evolution if present
        if "brief_enrichment" in output:
            enrichment = output["brief_enrichment"]
            fields_added = enrichment.get("fields_added", [])
            if fields_added:
                self.coherence_brief_evolution[f"after_{phase}"] = fields_added
    
    def get_phase_output(self, phase: str) -> Optional[Dict[str, Any]]:
        """
        Get output for a specific phase.
        
        Args:
            phase: Phase name
            
        Returns:
            Phase output dictionary or None if phase not logged
        """
        if phase not in self.phases:
            return None
        return self.phases[phase]["output"]
    
    def has_phase(self, phase: str) -> bool:
        """
        Check if a phase has been logged.
        
        Args:
            phase: Phase name
            
        Returns:
            True if phase exists, False otherwise
        """
        return phase in self.phases
    
    def update_performance(
        self,
        llm_calls: Optional[int] = None,
        total_tokens: Optional[int] = None,
        estimated_cost: Optional[float] = None,
    ) -> None:
        """
        Update performance metrics.
        
        Args:
            llm_calls: Number of LLM API calls
            total_tokens: Total tokens used
            estimated_cost: Estimated cost in USD
        """
        if llm_calls is not None:
            self.performance["llm_calls"] += llm_calls
        if total_tokens is not None:
            self.performance["total_tokens"] += total_tokens
        if estimated_cost is not None:
            self.performance["estimated_cost"] += estimated_cost
    
    def update_validation_summary(
        self,
        all_gates_passed: Optional[bool] = None,
        failed_gates: Optional[List[str]] = None,
        quality_score: Optional[float] = None,
    ) -> None:
        """
        Update validation summary.
        
        Args:
            all_gates_passed: Whether all validation gates passed
            failed_gates: List of failed gate names
            quality_score: Overall quality score (0.0-1.0)
        """
        if all_gates_passed is not None:
            self.validation_summary["all_gates_passed"] = all_gates_passed
        if failed_gates is not None:
            self.validation_summary["failed_gates"] = failed_gates
        if quality_score is not None:
            self.validation_summary["quality_score"] = quality_score
    
    def end_test_run(
        self,
        status: str = "passed",
        error: Optional[str] = None,
    ) -> None:
        """
        End test run and finalize data.
        
        Args:
            status: Final test status (passed, failed, skipped)
            error: Error message if test failed
        """
        self.status = status
        self.error = error
        
        # Calculate total duration
        if self.start_time:
            end_time = datetime.utcnow()
            total_duration = (end_time - self.start_time).total_seconds() * 1000
            self.performance["total_duration_ms"] = total_duration
    
    def save_to_db(self) -> str:
        """
        Save test run to database.
        
        Returns:
            Test run ID
        """
        if self.test_run_id is None:
            raise RuntimeError("Test run not started. Call start_test_run() first.")
        
        timestamp = self.start_time.isoformat() + "Z" if self.start_time else datetime.utcnow().isoformat() + "Z"
        
        metadata = {
            "performance": self.performance,
            "validation_summary": self.validation_summary,
            "coherence_brief_evolution": self.coherence_brief_evolution,
        }
        if self.error:
            metadata["error"] = self.error
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert test run
            cursor.execute("""
                INSERT OR REPLACE INTO test_runs 
                (test_run_id, test_name, test_category, timestamp, status, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.test_run_id,
                self.test_name,
                self.test_category,
                timestamp,
                self.status,
                json.dumps(metadata),
            ))
            
            # Insert phases
            for phase_name, phase_data in self.phases.items():
                phase_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT OR REPLACE INTO test_phases
                    (phase_id, test_run_id, phase_name, status, duration_ms, output_json, artifacts_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    phase_id,
                    self.test_run_id,
                    phase_name,
                    phase_data["status"],
                    phase_data.get("duration_ms"),
                    json.dumps(phase_data["output"]),
                    json.dumps(phase_data.get("artifacts", {})),
                ))
            
            conn.commit()
        
        return self.test_run_id
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert test run to dictionary.
        
        Returns:
            Dictionary representation of test run
        """
        return {
            "test_run_id": self.test_run_id,
            "test_name": self.test_name,
            "test_category": self.test_category,
            "timestamp": self.start_time.isoformat() + "Z" if self.start_time else None,
            "status": self.status,
            "phases": self.phases,
            "coherence_brief_evolution": self.coherence_brief_evolution,
            "performance": self.performance,
            "validation_summary": self.validation_summary,
            "error": self.error,
        }
