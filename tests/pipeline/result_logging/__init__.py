"""
Test result logging and analysis system.

Provides:
- TestResultLogger: Captures structured test execution results
- TestArtifactStorage: Manages storage of test artifacts (JSON, images)
- TestAnalysis: Analyzes and compares test results
- TestReportGenerator: Generates HTML/JSON reports
"""

from .test_result_logger import TestResultLogger, init_test_results_db
from .test_artifact_storage import TestArtifactStorage, get_test_results_dir
from .test_analysis import TestAnalysis
from .test_report_generator import TestReportGenerator

__all__ = [
    "TestResultLogger",
    "TestArtifactStorage",
    "TestAnalysis",
    "TestReportGenerator",
    "init_test_results_db",
    "get_test_results_dir",
]
