"""
Test Report Generator.

Generates human-readable reports from test results.

Location: tests/pipeline/result_logging/test_report_generator.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .test_analysis import TestAnalysis
from src.core.llm_log_db import get_db_path


class TestReportGenerator:
    """
    Generates HTML/JSON reports from test results.
    
    Provides:
    - HTML reports with visualizations
    - JSON reports for programmatic analysis
    - Side-by-side comparison views
    - Artifact browsing
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize report generator.
        
        Args:
            db_path: Path to database (uses default if None)
        """
        self.db_path = db_path or get_db_path()
        self.analysis = TestAnalysis(db_path)
    
    def generate_report(
        self,
        test_run_id: str,
        output_path: Path,
        include_artifacts: bool = True,
    ) -> Path:
        """
        Generate HTML report for a test run.
        
        Args:
            test_run_id: Test run ID to generate report for
            output_path: Path to save report
            include_artifacts: Whether to include artifact links
            
        Returns:
            Path to generated report
        """
        # Get test run data
        run = self.analysis._get_test_run(test_run_id)
        if not run:
            raise ValueError(f"Test run {test_run_id} not found")
        
        # Generate HTML content
        html_content = self._generate_html_content(run, include_artifacts)
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")
        
        return output_path
    
    def generate_comparison_report(
        self,
        run_id_1: str,
        run_id_2: str,
        output_path: Path,
    ) -> Path:
        """
        Generate comparison report for two test runs.
        
        Args:
            run_id_1: First test run ID
            run_id_2: Second test run ID
            output_path: Path to save report
            
        Returns:
            Path to generated report
        """
        comparison = self.analysis.compare_test_runs(run_id_1, run_id_2)
        
        # Generate comparison HTML
        html_content = self._generate_comparison_html(comparison)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding="utf-8")
        
        return output_path
    
    def generate_summary_report(
        self,
        date_range: tuple[str, str],
        output_path: Path,
        test_category: Optional[str] = None,
    ) -> Path:
        """
        Generate summary report for date range.
        
        Args:
            date_range: Tuple of (start_date, end_date)
            output_path: Path to save report (JSON)
            test_category: Optional category filter
            
        Returns:
            Path to generated report
        """
        runs = self.analysis.get_test_runs(date_range=date_range, test_category=test_category)
        
        summary = {
            "date_range": date_range,
            "total_runs": len(runs),
            "test_category": test_category,
            "summary": {
                "passed": sum(1 for r in runs if r.get("status") == "passed"),
                "failed": sum(1 for r in runs if r.get("status") == "failed"),
                "skipped": sum(1 for r in runs if r.get("status") == "skipped"),
            },
        }
        
        # Add analysis if runs available
        if runs:
            run_ids = [r["test_run_id"] for r in runs]
            summary["template_analysis"] = self.analysis.analyze_template_selection(run_ids)
            summary["quality_trends"] = self.analysis.analyze_quality_trends(run_ids)
            summary["ideas_analysis"] = self.analysis.analyze_ideas(run_ids)
        
        # Save as JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        
        return output_path
    
    def _generate_html_content(self, run: Dict[str, Any], include_artifacts: bool) -> str:
        """Generate HTML content for test run report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report: {run.get('test_name', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; }}
        .status {{ padding: 5px 10px; border-radius: 3px; }}
        .status.passed {{ background-color: #d4edda; color: #155724; }}
        .status.failed {{ background-color: #f8d7da; color: #721c24; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Test Report: {run.get('test_name', 'Unknown')}</h1>
    <div class="section">
        <h2>Overview</h2>
        <p><strong>Status:</strong> <span class="status {run.get('status', 'unknown')}">{run.get('status', 'unknown')}</span></p>
        <p><strong>Category:</strong> {run.get('test_category', 'unknown')}</p>
        <p><strong>Timestamp:</strong> {run.get('timestamp', 'unknown')}</p>
    </div>
"""
        
        # Add phase results if available
        html += self._generate_phases_section(run.get("test_run_id", ""))
        
        html += """
</body>
</html>
"""
        return html
    
    def _generate_phases_section(self, test_run_id: str) -> str:
        """Generate phases section HTML."""
        html = '<div class="section"><h2>Phase Results</h2>'
        
        # Get phases from database
        from src.core.llm_log_db import db_connection
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT phase_name, status, duration_ms FROM test_phases WHERE test_run_id = ? ORDER BY phase_name",
                (test_run_id,),
            )
            phases = cursor.fetchall()
            
            if phases:
                html += '<table><tr><th>Phase</th><th>Status</th><th>Duration (ms)</th></tr>'
                for phase in phases:
                    html += f'<tr><td>{phase["phase_name"]}</td><td>{phase["status"]}</td><td>{phase["duration_ms"] or "N/A"}</td></tr>'
                html += '</table>'
            else:
                html += '<p>No phase data available.</p>'
        
        html += '</div>'
        return html
    
    def _generate_comparison_html(self, comparison: Dict[str, Any]) -> str:
        """Generate comparison HTML."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Comparison Report</title>
</head>
<body>
    <h1>Test Comparison Report</h1>
    <p>Comparing {comparison.get('run1_id')} vs {comparison.get('run2_id')}</p>
    <pre>{json.dumps(comparison, indent=2)}</pre>
</body>
</html>
"""
