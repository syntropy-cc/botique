# Event Logging System

## Overview

The event logging system tracks all workflow events in the pipeline, including both LLM API calls and non-LLM workflow steps (preprocessing, postprocessing, tool calls, system events). All events are stored in a database (SQLite by default, PostgreSQL optional) for efficient querying, analysis, and cost tracking.

The system provides:
- Complete traceability of all pipeline executions
- Cost tracking and analysis for LLM calls
- Performance metrics (duration, tokens, costs)
- Quality tracking and evaluation
- Prompt versioning integration

## Architecture

The logging system uses a database-centric architecture:

```
Workflow → LLMLogger → Database (SQLite/PostgreSQL)
```

### Database Schema

The system uses four main tables:

- **`traces`**: High-level execution traces (e.g., "generate_ideas", "full_pipeline")
- **`events`**: Individual events within a trace (LLM calls, workflow steps)
- **`prompts`**: Prompt templates with versioning
- **`model_pricing`**: Model pricing information for cost calculation

### Event Types

Events are distinguished by the `type` field in the `events` table:

- **`'llm'`**: LLM API calls (via `log_llm_event` or `log_call`)
- **`'step'`**: General workflow steps (default for `log_step_event`)
- **`'preprocess'`**: Preprocessing steps
- **`'postprocess'`**: Postprocessing steps
- **`'tool'`**: Tool/function calls
- **`'system'`**: System-level events

## Usage in Code

### Basic Setup

```python
from src.core.llm_logger import LLMLogger

# Create logger (uses default SQLite database)
logger = LLMLogger()

# Or specify custom database path
logger = LLMLogger(db_path=Path("/custom/path/llm_logs.db"))
```

### Creating a Trace

A trace represents a high-level execution (e.g., a full pipeline run):

```python
trace_id = logger.create_trace(
    name="generate_ideas",
    user_id="user123",  # Optional
    tenant_id="tenant456",  # Optional
    tags="production,ideas",  # Optional comma-separated tags
    metadata={"article_slug": "my-article"}  # Optional metadata
)

# Set as current trace for automatic use
logger.current_trace_id = trace_id
```

### Logging LLM Events

LLM events are automatically logged when using `HttpLLMClient` with a logger:

```python
from src.core.llm_client import HttpLLMClient

client = HttpLLMClient(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    logger=logger,  # Logger is automatically used
)

# This call is automatically logged
response = client.generate(prompt="Hello", max_tokens=100)
```

You can also log LLM events manually:

```python
event_id = logger.log_llm_event(
    trace_id=trace_id,
    name="phase1_ideation.generate_ideas",
    model="deepseek-chat",
    input_text=prompt,
    input_obj={"prompt": prompt, "temperature": 0.2},
    output_text=response,
    output_obj={"content": response},
    duration_ms=1500.5,
    tokens_input=100,
    tokens_output=50,
    tokens_total=150,
    prompt_id=prompt_id,  # Link to prompt version
)
```

### Logging Non-LLM Workflow Events

Log workflow steps that are not LLM calls:

```python
# Log a preprocessing step
event_id = logger.log_step_event(
    trace_id=trace_id,
    name="preprocess_article",
    input_text="Processing article.md",
    input_obj={"file_path": "articles/article.md"},
    output_text="Article processed",
    output_obj={"word_count": 1500},
    duration_ms=250.0,
    type="preprocess",
    status="success",
)

# Log a validation step
event_id = logger.log_step_event(
    trace_id=trace_id,
    name="validate_json",
    input_obj={"json_data": data},
    output_obj={"valid": True, "errors": []},
    type="step",
    status="success",
)

# Log an error
event_id = logger.log_step_event(
    trace_id=trace_id,
    name="file_processing",
    input_text="Processing file",
    error="File not found",
    type="step",
    status="error",
)
```

### Setting Context

Set context information that will be included in subsequent events:

```python
logger.set_context(
    article_slug="my-article",
    post_id="post_001",
    slide_number=1,
)
```

## Database Configuration

### SQLite (Default)

By default, the system uses SQLite. The database file is created at:
- `llm_logs.db` in the project root, or
- Path specified by `LLM_LOGS_DB_PATH` environment variable

```bash
export LLM_LOGS_DB_PATH="/custom/path/llm_logs.db"
```

### PostgreSQL

To use PostgreSQL instead of SQLite, set the `DB_URL` environment variable:

```bash
export DB_URL="postgresql://user:password@localhost:5432/dbname"
```

The system automatically detects PostgreSQL mode and uses the appropriate connection.

## Querying Events

Use the query helpers in `src/core/llm_log_queries.py`:

```python
from src.core.llm_log_queries import (
    list_traces,
    get_trace_events,
    get_cost_summary,
    search_events_by_text,
)

# List recent traces
traces = list_traces(limit=10)

# Get all events for a trace
events = get_trace_events(trace_id)

# Get cost summary
summary = get_cost_summary(trace_id)

# Search events by text
results = search_events_by_text("error", limit=20)
```

### Filtering by Event Type

```python
from src.core.llm_log_db import db_connection, get_db_path

db_path = get_db_path()
with db_connection(db_path) as conn:
    cursor = conn.cursor()
    # Get only LLM events
    cursor.execute("SELECT * FROM events WHERE type = 'llm' AND trace_id = ?", (trace_id,))
    llm_events = cursor.fetchall()
    
    # Get only workflow steps
    cursor.execute("SELECT * FROM events WHERE type IN ('step', 'preprocess', 'postprocess') AND trace_id = ?", (trace_id,))
    workflow_events = cursor.fetchall()
```

## Migrating Old Logs

If you have old JSON log files from the previous directory-based logging system, you can import them using the migration script:

```bash
python scripts/migrate_logs_from_filesystem.py
```

This script searches for JSON files in:
- `output/**/llm_logs/*.json`
- `logs/llm_calls/**/*.json`

And imports them into the database. Note that the current system no longer writes these JSON files - all events are stored directly in the database.

## Best Practices

1. **Create traces for high-level operations**: Use `create_trace()` for each major pipeline execution
2. **Set context early**: Call `set_context()` at the start of processing to tag all subsequent events
3. **Use descriptive event names**: Use names like `"phase1_ideation.generate_ideas"` instead of generic names
4. **Link prompts**: Always provide `prompt_id` when logging LLM events to enable prompt version tracking
5. **Log errors**: Use `log_step_event()` with `status="error"` to track failures
6. **Use metadata**: Include relevant metadata in events for easier querying later

## Troubleshooting

### Database not found

The database is automatically created on first use. If you encounter issues:
- Check file permissions for SQLite
- Verify `LLM_LOGS_DB_PATH` points to a writable location
- For PostgreSQL, verify `DB_URL` is correct and the database exists

### Events not appearing

- Ensure `logger.enabled` is `True` (default)
- Verify `use_sql=True` (default)
- Check that `create_trace()` was called and `trace_id` is set
- Verify database connection (check logs for errors)

### High database size

SQLite databases can grow large. Consider:
- Archiving old traces periodically
- Using PostgreSQL for production deployments
- Implementing data retention policies

