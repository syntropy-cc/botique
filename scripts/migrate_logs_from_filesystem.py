#!/usr/bin/env python3
"""
Migration script for converting filesystem-based JSON logs to SQL database.

Traverses existing log directories and imports all logs into the SQL database.

Location: scripts/migrate_logs_from_filesystem.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
src_path = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(src_path))

from core.llm_log_db import db_connection, get_db_path, init_database
from core.llm_logger import LLMLogger


def find_log_files(root_dir: Path) -> List[Path]:
    """
    Find all JSON log files in the filesystem.
    
    Searches in:
    - output/**/llm_logs/*.json
    - logs/llm_calls/**/*.json
    
    Args:
        root_dir: Root directory to search from
        
    Returns:
        List of log file paths
    """
    log_files = []
    
    # Search in output/**/llm_logs/*.json
    output_dir = root_dir / "output"
    if output_dir.exists():
        for log_file in output_dir.rglob("llm_logs/*.json"):
            log_files.append(log_file)
    
    # Search in logs/llm_calls/**/*.json
    logs_dir = root_dir / "logs" / "llm_calls"
    if logs_dir.exists():
        for log_file in logs_dir.rglob("*.json"):
            log_files.append(log_file)
    
    return log_files


def load_log_file(log_path: Path) -> Optional[Dict]:
    """
    Load and parse a JSON log file.
    
    Args:
        log_path: Path to JSON log file
        
    Returns:
        Parsed JSON dictionary, or None if invalid
    """
    try:
        content = log_path.read_text(encoding="utf-8")
        return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  ⚠️  Error reading {log_path}: {e}")
        return None


def check_trace_exists(trace_id: str, db_path: Path) -> bool:
    """
    Check if a trace already exists in the database.
    
    Args:
        trace_id: Trace ID (session_id)
        db_path: Path to database
        
    Returns:
        True if trace exists, False otherwise
    """
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM traces WHERE id = ?", (trace_id,))
        return cursor.fetchone() is not None


def check_event_exists(event_id: str, db_path: Path) -> bool:
    """
    Check if an event already exists in the database.
    
    Args:
        event_id: Event ID (call_id)
        db_path: Path to database
        
    Returns:
        True if event exists, False otherwise
    """
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM events WHERE id = ?", (event_id,))
        return cursor.fetchone() is not None


def migrate_log_file(log_path: Path, db_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Migrate a single log file to the database.
    
    Args:
        log_path: Path to JSON log file
        db_path: Path to database
        dry_run: If True, don't actually insert data
        
    Returns:
        Dictionary with counts: {"traces_created": 0, "events_created": 0, "traces_skipped": 0, "events_skipped": 0}
    """
    counts = {
        "traces_created": 0,
        "events_created": 0,
        "traces_skipped": 0,
        "events_skipped": 0,
    }
    
    log_data = load_log_file(log_path)
    if not log_data:
        return counts
    
    session_id = log_data.get("session_id")
    if not session_id:
        print(f"  ⚠️  No session_id in {log_path}")
        return counts
    
    # Check if trace already exists
    if check_trace_exists(session_id, db_path):
        print(f"  ⏭️  Trace {session_id[:8]}... already exists, skipping")
        counts["traces_skipped"] = 1
        # Still check events
        calls = log_data.get("calls", [])
        for call in calls:
            call_id = call.get("call_id")
            if call_id and check_event_exists(call_id, db_path):
                counts["events_skipped"] += 1
        return counts
    
    if dry_run:
        print(f"  🔍 Would migrate {log_path.name} (trace: {session_id[:8]}...)")
        counts["traces_created"] = 1
        counts["events_created"] = len(log_data.get("calls", []))
        return counts
    
    # Create trace
    article_slug = log_data.get("article_slug", "unknown")
    pipeline_start = log_data.get("pipeline_start")
    pipeline_end = log_data.get("pipeline_end")
    
    metadata = {
        "article_slug": article_slug,
        "pipeline_start": pipeline_start,
        "pipeline_end": pipeline_end,
        "source_file": str(log_path),
    }
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traces 
            (id, created_at, name, user_id, tenant_id, tags, metadata_json,
             tokens_input_total, tokens_output_total, tokens_total, cost_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            pipeline_start or pipeline_end or "1970-01-01T00:00:00Z",
            f"migrated_{article_slug}",
            None,  # user_id
            None,  # tenant_id
            None,  # tags
            json.dumps(metadata),
            log_data.get("total_tokens"),  # tokens_input_total (simplified)
            None,  # tokens_output_total
            log_data.get("total_tokens"),  # tokens_total
            log_data.get("total_cost_estimate"),  # cost_total
        ))
        conn.commit()
    
    counts["traces_created"] = 1
    
    # Create events for each call
    calls = log_data.get("calls", [])
    for call in calls:
        call_id = call.get("call_id")
        if not call_id:
            continue
        
        # Check if event already exists
        if check_event_exists(call_id, db_path):
            counts["events_skipped"] += 1
            continue
        
        # Extract data from call
        timestamp = call.get("timestamp")
        phase = call.get("phase", "unknown")
        function = call.get("function", "unknown")
        model = call.get("model")
        base_url = call.get("base_url")
        
        input_data = call.get("input", {})
        output_data = call.get("output", {})
        metrics = call.get("metrics", {})
        context = call.get("context", {})
        
        prompt = input_data.get("prompt", "")
        response = output_data.get("content")
        
        tokens_input = metrics.get("tokens_input")
        tokens_output = metrics.get("tokens_output")
        tokens_total = metrics.get("tokens_total")
        duration_ms = metrics.get("duration_ms", 0)
        cost_estimate = metrics.get("cost_estimate")
        
        status = call.get("status", "success")
        error = call.get("error")
        
        # Build input/output objects
        input_obj = {
            "prompt": prompt,
            "prompt_length": input_data.get("prompt_length"),
            "max_tokens": input_data.get("max_tokens"),
            "temperature": input_data.get("temperature"),
            "base_url": base_url,
        }
        
        output_obj = {
            "content": response,
            "content_length": output_data.get("content_length"),
            "truncated": output_data.get("truncated", False),
        }
        
        metadata_event = {
            "phase": phase,
            "function": function,
            "context": context,
        }
        
        # Calculate costs (if not already calculated)
        cost_input = None
        cost_output = None
        cost_total = cost_estimate
        
        if model and tokens_input is not None and tokens_output is not None:
            from core.llm_pricing import calculate_cost
            cost_input, cost_output, cost_total_calc = calculate_cost(
                model, tokens_input, tokens_output, db_path
            )
            if cost_total is None:
                cost_total = cost_total_calc
        
        # Insert event
        with db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events 
                (id, trace_id, parent_id, created_at, type, name, model, role,
                 input_text, input_json, output_text, output_json, error, duration_ms,
                 tokens_input, tokens_output, tokens_total,
                 cost_input, cost_output, cost_total, metadata_json)
                VALUES (?, ?, ?, ?, 'llm', ?, ?, 'user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_id,
                session_id,
                None,  # parent_id
                timestamp or "1970-01-01T00:00:00Z",
                f"{phase}.{function}",
                model,
                prompt,
                json.dumps(input_obj),
                response,
                json.dumps(output_obj),
                error,
                int(round(duration_ms)) if duration_ms else None,
                tokens_input,
                tokens_output,
                tokens_total,
                cost_input,
                cost_output,
                cost_total,
                json.dumps(metadata_event),
            ))
            conn.commit()
        
        counts["events_created"] += 1
    
    return counts


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate filesystem-based JSON logs to SQL database"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Root directory to search for log files (default: project root)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Path to SQL database (default: uses LLM_LOGS_DB_PATH or llm_logs.db)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run: don't actually insert data, just report what would be done",
    )
    
    args = parser.parse_args()
    
    root_dir = args.root_dir
    db_path = args.db_path or get_db_path()
    dry_run = args.dry_run
    
    print("=" * 70)
    print("MIGRATE LOGS FROM FILESYSTEM TO SQL")
    print("=" * 70)
    print(f"Root directory: {root_dir}")
    print(f"Database path: {db_path}")
    print(f"Dry run: {dry_run}")
    print()
    
    # Initialize database
    print("Initializing database...")
    init_database(db_path)
    print("✓ Database initialized")
    print()
    
    # Find log files
    print("Searching for log files...")
    log_files = find_log_files(root_dir)
    print(f"✓ Found {len(log_files)} log file(s)")
    print()
    
    if not log_files:
        print("No log files found. Nothing to migrate.")
        return 0
    
    # Migrate each file
    total_counts = {
        "traces_created": 0,
        "events_created": 0,
        "traces_skipped": 0,
        "events_skipped": 0,
    }
    
    print("Migrating log files...")
    for i, log_file in enumerate(log_files, 1):
        print(f"[{i}/{len(log_files)}] {log_file.relative_to(root_dir)}")
        counts = migrate_log_file(log_file, db_path, dry_run=dry_run)
        
        for key in total_counts:
            total_counts[key] += counts[key]
    
    print()
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Traces created: {total_counts['traces_created']}")
    print(f"Traces skipped (already exist): {total_counts['traces_skipped']}")
    print(f"Events created: {total_counts['events_created']}")
    print(f"Events skipped (already exist): {total_counts['events_skipped']}")
    print()
    
    if dry_run:
        print("⚠️  This was a dry run. No data was actually inserted.")
        print("   Run without --dry-run to perform the migration.")
    else:
        print("✓ Migration complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

