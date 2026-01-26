# Pipeline Test Suite

Comprehensive test suite for the social media post generation pipeline, testing integrations between agents and tools across all 5 phases.

## Structure

```
tests/pipeline/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_phase1_ideation.py       # Phase 1 unit tests
├── test_phase2_selection.py      # Phase 2 selection tests
├── test_phase2_configuration.py  # Phase 2 configuration tests
├── test_phase3_post_creation.py  # Phase 3 tests
├── test_phase4_slide_generation.py # Phase 4 tests
├── test_phase5_finalization.py   # Phase 5 tests
├── test_phase_integrations.py    # Multi-phase integration tests
├── test_full_pipeline.py         # End-to-end tests
├── test_coherence_brief_evolution.py # Brief evolution tests
├── test_pipeline_validation.py   # Validation gates tests
├── test_error_handling.py        # Error scenarios tests
├── result_logging/               # Test result logging system
│   ├── test_result_logger.py    # Result logger
│   ├── test_artifact_storage.py # Artifact storage
│   ├── test_analysis.py         # Analysis tools
│   └── test_report_generator.py # Report generation
└── fixtures/                     # Test data
    └── articles/                 # Sample articles
```

## Running Tests

### Run all pipeline tests
```bash
pytest tests/pipeline/
```

### Run specific test category
```bash
# Unit tests only
pytest tests/pipeline/test_phase*.py -m "not integration and not e2e"

# Integration tests
pytest tests/pipeline/ -m integration

# End-to-end tests
pytest tests/pipeline/ -m e2e
```

### Run with coverage
```bash
pytest tests/pipeline/ --cov=src --cov-report=html
```

## Test Result Logging

The test suite includes a comprehensive result logging system that captures:
- Generated ideas, narrative structures, copies, visuals
- Performance metrics (duration, tokens, costs)
- Validation results and gate status
- Artifacts (JSON files, images)

### Using Result Logging in Tests

Tests automatically use result logging via fixtures:

```python
def test_example(test_result_logger, test_artifact_storage):
    # Test execution...
    
    # Log phase results
    test_result_logger.log_phase_result(
        phase="phase1",
        status="passed",
        output={"ideas": [...]},
        artifacts={"ideas_json": "path/to/file.json"},
        duration_ms=1250,
    )
    
    # Store artifacts
    test_artifact_storage.save_artifact("phase1", "ideas.json", ideas_data)
```

### Analyzing Test Results

After tests run, analyze results:

```python
from tests.pipeline.result_logging import TestAnalysis, TestReportGenerator

# Get test runs
analyzer = TestAnalysis()
runs = analyzer.get_test_runs(date_range=("2026-01-20", "2026-01-20"))

# Analyze template selection
template_analysis = analyzer.analyze_template_selection([r["test_run_id"] for r in runs])

# Generate report
report_generator = TestReportGenerator()
report_path = report_generator.generate_report(
    test_run_id=runs[0]["test_run_id"],
    output_path="test_report.html",
)
```

### Generating Reports

```bash
# Generate report for specific test run
python -m tests.pipeline.result_logging.test_report_generator \
    --test-run-id abc123 \
    --output report.html

# Generate comparison report
python -m tests.pipeline.result_logging.test_report_generator \
    --compare run1 run2 \
    --output comparison.html

# Generate summary report
python -m tests.pipeline.result_logging.test_report_generator \
    --date-range 2026-01-01 2026-01-31 \
    --output summary.json
```

## Test Categories

### Unit Tests
- Individual phase execution with mocked dependencies
- Fast execution (< 1 second per test)
- Run on every commit

### Integration Tests
- Multi-phase workflows with real tool integration
- Medium execution time (< 5 seconds per test)
- Run on PR, before merge

### End-to-End Tests
- Full pipeline execution
- Slower execution (< 30 seconds per test)
- Run nightly, before release

## Test Data

Sample articles are available in `fixtures/articles/`:
- `minimal_article.txt`: Minimal valid article
- `full_article.txt`: Complete article
- `short_article.txt`: Short article (edge case)
- `long_article.txt`: Long article (edge case)

## Result Storage

Test results and artifacts are stored in:
```
tests/pipeline/test_results/
├── runs/
│   └── YYYY-MM-DD/
│       └── test_run_<id>/
│           ├── phase1/
│           ├── phase2/
│           └── ...
└── reports/
```

## Database

Test results are stored in the same database as LLM logs (`llm_logs.db` by default), with additional tables:
- `test_runs`: Test run metadata
- `test_phases`: Phase-by-phase results
- `test_artifacts`: Artifact metadata

## Coverage Goals

- Phase functions: 90%+
- Validation logic: 95%+
- Error handling: 80%+
- Integration paths: 70%+
