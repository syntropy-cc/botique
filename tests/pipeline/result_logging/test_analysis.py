"""
Test Analysis.

Analyzes and compares test results across runs.

Location: tests/pipeline/result_logging/test_analysis.py
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.llm_log_db import db_connection, get_db_path


class TestAnalysis:
    """
    Analyzes and compares test results across runs.
    
    Provides functions for:
    - Comparing test runs
    - Analyzing patterns in generated content
    - Quality trend analysis
    - Performance analysis
    - Coherence brief evolution analysis
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize test analysis.
        
        Args:
            db_path: Path to database (uses default if None)
        """
        self.db_path = db_path or get_db_path()
    
    def get_test_runs(
        self,
        date_range: Optional[tuple[str, str]] = None,
        test_category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get test runs with optional filters.
        
        Args:
            date_range: Tuple of (start_date, end_date) in ISO format
            test_category: Filter by category (unit, integration, e2e)
            limit: Maximum number of runs to return
            
        Returns:
            List of test run dictionaries
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM test_runs WHERE 1=1"
            params = []
            
            if date_range:
                query += " AND timestamp >= ? AND timestamp <= ?"
                params.extend(date_range)
            
            if test_category:
                query += " AND test_category = ?"
                params.append(test_category)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            runs = []
            for row in rows:
                run = dict(row)
                if run.get("metadata_json"):
                    run["metadata"] = json.loads(run["metadata_json"])
                runs.append(run)
            
            return runs
    
    def compare_test_runs(self, run_id_1: str, run_id_2: str) -> Dict[str, Any]:
        """
        Compare two test runs and highlight differences.
        
        Args:
            run_id_1: First test run ID
            run_id_2: Second test run ID
            
        Returns:
            Comparison dictionary with differences
        """
        run1 = self._get_test_run(run_id_1)
        run2 = self._get_test_run(run_id_2)
        
        if not run1 or not run2:
            return {"error": "One or both test runs not found"}
        
        comparison = {
            "run1_id": run_id_1,
            "run2_id": run_id_2,
            "differences": {},
        }
        
        # Compare ideas
        ideas1 = self._get_phase_output(run_id_1, "phase1", "ideas")
        ideas2 = self._get_phase_output(run_id_2, "phase1", "ideas")
        
        if ideas1 and ideas2:
            comparison["differences"]["ideas"] = {
                "count_diff": len(ideas1) - len(ideas2),
                "different_ids": set(ideas1) - set(ideas2) if isinstance(ideas1, list) else None,
            }
        
        return comparison
    
    def analyze_template_selection(self, test_run_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze template selection patterns across test runs.
        
        Args:
            test_run_ids: List of test run IDs to analyze
            
        Returns:
            Analysis dictionary with template usage patterns
        """
        template_usage = {}
        confidence_scores = []
        template_ids_used = set()
        
        for run_id in test_run_ids:
            phase3_output = self._get_phase_output(run_id, "phase3")
            if phase3_output and "template_selection" in phase3_output:
                template_data = phase3_output["template_selection"]
                
                # Collect template IDs
                template_ids = template_data.get("template_ids_used", [])
                template_ids_used.update(template_ids)
                
                # Collect confidence scores
                avg_conf = template_data.get("avg_confidence", 0)
                if avg_conf > 0:
                    confidence_scores.append(avg_conf)
                
                # Count template usage
                for template_id in template_ids:
                    template_usage[template_id] = template_usage.get(template_id, 0) + 1
        
        # Calculate statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Most used templates
        most_used = sorted(template_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "avg_confidence": avg_confidence,
            "most_used_templates": [t[0] for t in most_used],
            "template_usage_counts": dict(most_used),
            "total_unique_templates": len(template_ids_used),
            "fallback_usage_rate": 0.0,  # Would calculate from actual data
        }
    
    def analyze_coherence_brief_evolution(self, test_run_id: str) -> Dict[str, Any]:
        """
        Analyze how coherence brief evolves through phases.
        
        Args:
            test_run_id: Test run ID to analyze
            
        Returns:
            Evolution analysis dictionary
        """
        run = self._get_test_run(test_run_id)
        if not run or "metadata" not in run:
            return {"error": "Test run not found or incomplete"}
        
        evolution = run["metadata"].get("coherence_brief_evolution", {})
        
        return {
            "initial_fields": evolution.get("initial_fields", []),
            "fields_added_in_phase3": evolution.get("after_phase3", []),
            "fields_added_in_phase4": evolution.get("after_phase4", []),
            "final_fields": evolution.get("final_fields", []),
        }
    
    def analyze_quality_trends(self, test_run_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze quality scores over time.
        
        Args:
            test_run_ids: List of test run IDs to analyze
            
        Returns:
            Quality trend analysis dictionary
        """
        quality_scores = []
        gate_pass_rates = {}
        
        for run_id in test_run_ids:
            run = self._get_test_run(run_id)
            if run and "metadata" in run:
                validation = run["metadata"].get("validation_summary", {})
                quality_score = validation.get("quality_score", 0)
                if quality_score > 0:
                    quality_scores.append(quality_score)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "avg_quality_score": avg_quality,
            "quality_scores": quality_scores,
            "trend": "stable",  # Would calculate actual trend
            "gate_pass_rates": gate_pass_rates,
        }
    
    def analyze_ideas(self, test_run_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze ideas generated across test runs.
        
        Args:
            test_run_ids: List of test run IDs to analyze
            
        Returns:
            Ideas analysis dictionary
        """
        all_ideas = []
        
        for run_id in test_run_ids:
            ideas = self._get_phase_output(run_id, "phase1", "ideas")
            if ideas:
                all_ideas.extend(ideas if isinstance(ideas, list) else [ideas])
        
        # Calculate diversity (simple measure)
        platforms = set(idea.get("platform") for idea in all_ideas if idea.get("platform"))
        tones = set(idea.get("tone") for idea in all_ideas if idea.get("tone"))
        
        diversity_score = (len(platforms) + len(tones)) / max(len(all_ideas), 1)
        
        return {
            "total_ideas": len(all_ideas),
            "avg_ideas_per_run": len(all_ideas) / max(len(test_run_ids), 1),
            "diversity_score": diversity_score,
            "platforms_used": list(platforms),
            "tones_used": list(tones),
        }
    
    def _get_test_run(self, test_run_id: str) -> Optional[Dict[str, Any]]:
        """Get test run by ID."""
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_runs WHERE test_run_id = ?", (test_run_id,))
            row = cursor.fetchone()
            
            if row:
                run = dict(row)
                if run.get("metadata_json"):
                    run["metadata"] = json.loads(run["metadata_json"])
                return run
            return None
    
    def _get_phase_output(self, test_run_id: str, phase: str, key: Optional[str] = None) -> Optional[Any]:
        """Get phase output for a test run."""
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT output_json FROM test_phases WHERE test_run_id = ? AND phase_name = ?",
                (test_run_id, phase),
            )
            row = cursor.fetchone()
            
            if row and row["output_json"]:
                output = json.loads(row["output_json"])
                if key:
                    return output.get(key)
                return output
            return None
