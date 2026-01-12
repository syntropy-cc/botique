"""
Query helpers for LLM logging database.

Provides programmatic access to traces, events, and cost summaries.

Location: src/core/llm_log_queries.py
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .llm_log_db import db_connection, get_db_path


def _row_to_dict(row) -> Dict[str, Any]:
    """
    Convert database row to dictionary.
    
    Works with both sqlite3.Row and psycopg2 RealDictCursor.
    """
    if hasattr(row, "keys"):
        # sqlite3.Row or psycopg2 RealDictCursor
        return dict(row)
    elif isinstance(row, tuple):
        # Fallback for tuple rows - need cursor description
        # This shouldn't happen with our setup, but handle it gracefully
        return {f"col_{i}": val for i, val in enumerate(row)}
    else:
        # Try to convert to dict anyway
        try:
            return dict(row)
        except (TypeError, ValueError):
            return {"value": row}


def list_traces(
    limit: int = 50,
    filters: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    List traces with optional filters.
    
    Args:
        limit: Maximum number of traces to return
        filters: Optional filters dict with keys:
            - user_id: Filter by user_id
            - tenant_id: Filter by tenant_id
            - name: Filter by trace name (partial match)
            - created_after: ISO8601 datetime string
            - created_before: ISO8601 datetime string
        db_path: Path to database (uses default if None)
        
    Returns:
        List of trace dictionaries
    """
    if db_path is None:
        db_path = get_db_path()
    
    filters = filters or {}
    
    query = "SELECT * FROM traces WHERE 1=1"
    params = []
    
    if "user_id" in filters:
        query += " AND user_id = ?"
        params.append(filters["user_id"])
    
    if "tenant_id" in filters:
        query += " AND tenant_id = ?"
        params.append(filters["tenant_id"])
    
    if "name" in filters:
        query += " AND name LIKE ?"
        params.append(f"%{filters['name']}%")
    
    if "created_after" in filters:
        query += " AND created_at >= ?"
        params.append(filters["created_after"])
    
    if "created_before" in filters:
        query += " AND created_at <= ?"
        params.append(filters["created_before"])
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        traces = []
        for row in rows:
            trace = _row_to_dict(row)
            # Parse JSON fields
            if trace.get("metadata_json"):
                try:
                    trace["metadata"] = json.loads(trace["metadata_json"])
                except (json.JSONDecodeError, TypeError):
                    trace["metadata"] = None
            else:
                trace["metadata"] = None
            traces.append(trace)
        
        return traces


def get_trace_with_events(trace_id: str, db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get trace with all events organized as a tree.
    
    Args:
        trace_id: Trace ID
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary with trace info and events list (flat, with parent_id relationships)
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get trace
        cursor.execute("SELECT * FROM traces WHERE id = ?", (trace_id,))
        trace_row = cursor.fetchone()
        
        if not trace_row:
            return None
        
        trace = _row_to_dict(trace_row)
        
        # Parse metadata JSON
        if trace.get("metadata_json"):
            try:
                trace["metadata"] = json.loads(trace["metadata_json"])
            except (json.JSONDecodeError, TypeError):
                trace["metadata"] = None
        else:
            trace["metadata"] = None
        
        # Get events
        cursor.execute("""
            SELECT * FROM events 
            WHERE trace_id = ? 
            ORDER BY created_at ASC
        """, (trace_id,))
        event_rows = cursor.fetchall()
        
        events = []
        for row in event_rows:
            event = _row_to_dict(row)
            
            # Parse JSON fields
            for json_field in ["input_json", "output_json", "metadata_json", "quality_metadata_json"]:
                if event.get(json_field):
                    try:
                        event[json_field.replace("_json", "")] = json.loads(event[json_field])
                    except (json.JSONDecodeError, TypeError):
                        event[json_field.replace("_json", "")] = None
                else:
                    event[json_field.replace("_json", "")] = None
            
            events.append(event)
        
        trace["events"] = events
        return trace


def get_events_by_trace(trace_id: str, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Get all events for a trace (flat list).
    
    Args:
        trace_id: Trace ID
        db_path: Path to database (uses default if None)
        
    Returns:
        List of event dictionaries
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events 
            WHERE trace_id = ? 
            ORDER BY created_at ASC
        """, (trace_id,))
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = _row_to_dict(row)
            
            # Parse JSON fields
            for json_field in ["input_json", "output_json", "metadata_json", "quality_metadata_json"]:
                if event.get(json_field):
                    try:
                        event[json_field.replace("_json", "")] = json.loads(event[json_field])
                    except (json.JSONDecodeError, TypeError):
                        event[json_field.replace("_json", "")] = None
                else:
                    event[json_field.replace("_json", "")] = None
            
            events.append(event)
        
        return events


def get_event_tree(event_id: str, db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get event with all children recursively.
    
    Args:
        event_id: Event ID
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary with event info and children list
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get event
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event_row = cursor.fetchone()
        
        if not event_row:
            return None
        
        event = _row_to_dict(event_row)
        
        # Parse JSON fields
        for json_field in ["input_json", "output_json", "metadata_json", "quality_metadata_json"]:
            if event.get(json_field):
                try:
                    event[json_field.replace("_json", "")] = json.loads(event[json_field])
                except (json.JSONDecodeError, TypeError):
                    event[json_field.replace("_json", "")] = None
            else:
                event[json_field.replace("_json", "")] = None
        
        # Get children
        cursor.execute("SELECT * FROM events WHERE parent_id = ? ORDER BY created_at ASC", (event_id,))
        child_rows = cursor.fetchall()
        
        children = []
        for row in child_rows:
            child = _row_to_dict(row)
            # Recursively get children
            child_tree = get_event_tree(child["id"], db_path)
            if child_tree:
                children.append(child_tree)
            else:
                # Parse JSON for leaf nodes
                for json_field in ["input_json", "output_json", "metadata_json", "quality_metadata_json"]:
                    if child.get(json_field):
                        try:
                            child[json_field.replace("_json", "")] = json.loads(child[json_field])
                        except (json.JSONDecodeError, TypeError):
                            child[json_field.replace("_json", "")] = None
                    else:
                        child[json_field.replace("_json", "")] = None
                children.append(child)
        
        event["children"] = children
        return event


def search_events_by_text(
    query: str,
    limit: int = 100,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Search events by text in input_text or output_text.
    
    Args:
        query: Search query (partial match)
        limit: Maximum number of results
        db_path: Path to database (uses default if None)
        
    Returns:
        List of matching event dictionaries
    """
    if db_path is None:
        db_path = get_db_path()
    
    search_pattern = f"%{query}%"
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events 
            WHERE input_text LIKE ? OR output_text LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, limit))
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = _row_to_dict(row)
            
            # Parse JSON fields
            for json_field in ["input_json", "output_json", "metadata_json", "quality_metadata_json"]:
                if event.get(json_field):
                    try:
                        event[json_field.replace("_json", "")] = json.loads(event[json_field])
                    except (json.JSONDecodeError, TypeError):
                        event[json_field.replace("_json", "")] = None
                else:
                    event[json_field.replace("_json", "")] = None
            
            events.append(event)
        
        return events


def get_cost_summary(
    filters: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Get cost summary with aggregations.
    
    Args:
        filters: Optional filters dict with keys:
            - trace_id: Filter by trace_id
            - model: Filter by model name
            - type: Filter by event type
            - created_after: ISO8601 datetime string
            - created_before: ISO8601 datetime string
            - user_id: Filter by user_id (via trace)
            - tenant_id: Filter by tenant_id (via trace)
            - group_by: List of grouping fields: ['day', 'model', 'tenant', 'user']
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary with cost summary and aggregations
    """
    if db_path is None:
        db_path = get_db_path()
    
    filters = filters or {}
    group_by = filters.get("group_by", [])
    
    # Build WHERE clause
    where_clauses = ["1=1"]
    params = []
    
    if "trace_id" in filters:
        where_clauses.append("e.trace_id = ?")
        params.append(filters["trace_id"])
    
    if "model" in filters:
        where_clauses.append("e.model = ?")
        params.append(filters["model"])
    
    if "type" in filters:
        where_clauses.append("e.type = ?")
        params.append(filters["type"])
    
    if "created_after" in filters:
        where_clauses.append("e.created_at >= ?")
        params.append(filters["created_after"])
    
    if "created_before" in filters:
        where_clauses.append("e.created_at <= ?")
        params.append(filters["created_before"])
    
    if "user_id" in filters:
        where_clauses.append("t.user_id = ?")
        params.append(filters["user_id"])
    
    if "tenant_id" in filters:
        where_clauses.append("t.tenant_id = ?")
        params.append(filters["tenant_id"])
    
    where_sql = " AND ".join(where_clauses)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Overall summary
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_events,
                SUM(e.tokens_input) as total_tokens_input,
                SUM(e.tokens_output) as total_tokens_output,
                SUM(e.tokens_total) as total_tokens,
                SUM(e.cost_total) as total_cost,
                AVG(e.cost_total) as avg_cost_per_event
            FROM events e
            LEFT JOIN traces t ON e.trace_id = t.id
            WHERE {where_sql}
        """, params)
        
        summary_row = cursor.fetchone()
        summary = _row_to_dict(summary_row) if summary_row else {}
        
        # Grouped aggregations
        aggregations = {}
        
        if "day" in group_by:
            # Use SUBSTR for SQLite compatibility (extracts YYYY-MM-DD from ISO8601)
            # Works with both SQLite and PostgreSQL
            cursor.execute(f"""
                SELECT 
                    SUBSTR(e.created_at, 1, 10) as day,
                    COUNT(*) as event_count,
                    SUM(e.cost_total) as total_cost,
                    SUM(e.tokens_total) as total_tokens
                FROM events e
                LEFT JOIN traces t ON e.trace_id = t.id
                WHERE {where_sql}
                GROUP BY SUBSTR(e.created_at, 1, 10)
                ORDER BY day DESC
            """, params)
            rows = cursor.fetchall()
            aggregations["by_day"] = [_row_to_dict(row) for row in rows]
        
        if "model" in group_by:
            cursor.execute(f"""
                SELECT 
                    e.model,
                    COUNT(*) as event_count,
                    SUM(e.cost_total) as total_cost,
                    SUM(e.tokens_total) as total_tokens
                FROM events e
                LEFT JOIN traces t ON e.trace_id = t.id
                WHERE {where_sql} AND e.model IS NOT NULL
                GROUP BY e.model
                ORDER BY total_cost DESC
            """, params)
            rows = cursor.fetchall()
            aggregations["by_model"] = [_row_to_dict(row) for row in rows]
        
        if "tenant" in group_by:
            cursor.execute(f"""
                SELECT 
                    t.tenant_id,
                    COUNT(*) as event_count,
                    SUM(e.cost_total) as total_cost,
                    SUM(e.tokens_total) as total_tokens
                FROM events e
                LEFT JOIN traces t ON e.trace_id = t.id
                WHERE {where_sql} AND t.tenant_id IS NOT NULL
                GROUP BY t.tenant_id
                ORDER BY total_cost DESC
            """, params)
            rows = cursor.fetchall()
            aggregations["by_tenant"] = [_row_to_dict(row) for row in rows]
        
        if "user" in group_by:
            cursor.execute(f"""
                SELECT 
                    t.user_id,
                    COUNT(*) as event_count,
                    SUM(e.cost_total) as total_cost,
                    SUM(e.tokens_total) as total_tokens
                FROM events e
                LEFT JOIN traces t ON e.trace_id = t.id
                WHERE {where_sql} AND t.user_id IS NOT NULL
                GROUP BY t.user_id
                ORDER BY total_cost DESC
            """, params)
            rows = cursor.fetchall()
            aggregations["by_user"] = [_row_to_dict(row) for row in rows]
        
        return {
            "summary": summary,
            "aggregations": aggregations,
        }


def get_prompt_versions_with_usage(
    prompt_key: str,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Get all versions of a prompt with their usage count.
    
    Args:
        prompt_key: Logical identifier of the prompt
        db_path: Path to database (uses default if None)
        
    Returns:
        List of dictionaries with prompt version data and usage statistics
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.id,
                p.prompt_key,
                p.version,
                p.template,
                p.description,
                p.created_at,
                p.metadata_json,
                COUNT(e.id) as usage_count
            FROM prompts p
            LEFT JOIN events e ON p.id = e.prompt_id
            WHERE p.prompt_key = ?
            GROUP BY p.id, p.prompt_key, p.version, p.template, p.description, p.created_at, p.metadata_json
            ORDER BY p.created_at ASC
        """, (prompt_key,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = {
                "id": row["id"],
                "prompt_key": row["prompt_key"],
                "version": row["version"],
                "template": row["template"],
                "description": row["description"],
                "created_at": row["created_at"],
                "usage_count": row["usage_count"] or 0,
            }
            
            if row["metadata_json"]:
                try:
                    result["metadata"] = json.loads(row["metadata_json"])
                except (json.JSONDecodeError, TypeError):
                    result["metadata"] = None
            else:
                result["metadata"] = None
            
            results.append(result)
        
        return results


def compare_prompt_versions(
    prompt_key: str,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Compare different versions of a prompt by cost, tokens, and quality.
    
    Args:
        prompt_key: Logical identifier of the prompt
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary with comparison data per version
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.id,
                p.version,
                COUNT(e.id) as event_count,
                SUM(e.tokens_input) as total_tokens_input,
                SUM(e.tokens_output) as total_tokens_output,
                SUM(e.tokens_total) as total_tokens,
                SUM(e.cost_total) as total_cost,
                AVG(e.cost_total) as avg_cost_per_event,
                AVG(e.duration_ms) as avg_duration_ms,
                AVG(e.quality_score) as avg_quality_score,
                MIN(e.created_at) as first_used,
                MAX(e.created_at) as last_used
            FROM prompts p
            LEFT JOIN events e ON p.id = e.prompt_id AND e.type = 'llm'
            WHERE p.prompt_key = ?
            GROUP BY p.id, p.version
            ORDER BY p.created_at ASC
        """, (prompt_key,))
        rows = cursor.fetchall()
        
        versions = []
        for row in rows:
            version_data = {
                "prompt_id": row["id"],
                "version": row["version"],
                "event_count": row["event_count"] or 0,
                "total_tokens_input": row["total_tokens_input"] or 0,
                "total_tokens_output": row["total_tokens_output"] or 0,
                "total_tokens": row["total_tokens"] or 0,
                "total_cost": float(row["total_cost"]) if row["total_cost"] else 0.0,
                "avg_cost_per_event": float(row["avg_cost_per_event"]) if row["avg_cost_per_event"] else 0.0,
                "avg_duration_ms": float(row["avg_duration_ms"]) if row["avg_duration_ms"] else None,
                "avg_quality_score": float(row["avg_quality_score"]) if row["avg_quality_score"] else None,
                "first_used": row["first_used"],
                "last_used": row["last_used"],
            }
            versions.append(version_data)
        
        return {
            "prompt_key": prompt_key,
            "versions": versions,
        }


def get_prompt_quality_stats(
    prompt_id: Optional[str] = None,
    prompt_key: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Get quality statistics for a prompt version or all versions of a prompt key.
    
    Args:
        prompt_id: Specific prompt ID (if provided, prompt_key is ignored)
        prompt_key: Logical identifier of the prompt (used if prompt_id not provided)
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary with quality statistics
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        if prompt_id:
            # Get stats for specific prompt version
            cursor.execute("""
                SELECT 
                    p.id,
                    p.prompt_key,
                    p.version,
                    COUNT(e.id) as event_count,
                    AVG(e.quality_score) as avg_quality_score,
                    MIN(e.quality_score) as min_quality_score,
                    MAX(e.quality_score) as max_quality_score,
                    COUNT(CASE WHEN e.quality_score >= 0.8 THEN 1 END) as high_quality_count,
                    COUNT(CASE WHEN e.quality_score < 0.5 THEN 1 END) as low_quality_count
                FROM prompts p
                LEFT JOIN events e ON p.id = e.prompt_id AND e.type = 'llm'
                WHERE p.id = ?
                GROUP BY p.id, p.prompt_key, p.version
            """, (prompt_id,))
        elif prompt_key:
            # Get stats for all versions of a prompt key
            cursor.execute("""
                SELECT 
                    p.id,
                    p.prompt_key,
                    p.version,
                    COUNT(e.id) as event_count,
                    AVG(e.quality_score) as avg_quality_score,
                    MIN(e.quality_score) as min_quality_score,
                    MAX(e.quality_score) as max_quality_score,
                    COUNT(CASE WHEN e.quality_score >= 0.8 THEN 1 END) as high_quality_count,
                    COUNT(CASE WHEN e.quality_score < 0.5 THEN 1 END) as low_quality_count
                FROM prompts p
                LEFT JOIN events e ON p.id = e.prompt_id AND e.type = 'llm'
                WHERE p.prompt_key = ?
                GROUP BY p.id, p.prompt_key, p.version
                ORDER BY p.created_at ASC
            """, (prompt_key,))
        else:
            return {"error": "Either prompt_id or prompt_key must be provided"}
        
        rows = cursor.fetchall()
        
        if prompt_id and len(rows) == 1:
            # Single version result
            row = rows[0]
            return {
                "prompt_id": row["id"],
                "prompt_key": row["prompt_key"],
                "version": row["version"],
                "event_count": row["event_count"] or 0,
                "avg_quality_score": float(row["avg_quality_score"]) if row["avg_quality_score"] else None,
                "min_quality_score": float(row["min_quality_score"]) if row["min_quality_score"] else None,
                "max_quality_score": float(row["max_quality_score"]) if row["max_quality_score"] else None,
                "high_quality_count": row["high_quality_count"] or 0,
                "low_quality_count": row["low_quality_count"] or 0,
            }
        else:
            # Multiple versions result
            versions = []
            for row in rows:
                versions.append({
                    "prompt_id": row["id"],
                    "version": row["version"],
                    "event_count": row["event_count"] or 0,
                    "avg_quality_score": float(row["avg_quality_score"]) if row["avg_quality_score"] else None,
                    "min_quality_score": float(row["min_quality_score"]) if row["min_quality_score"] else None,
                    "max_quality_score": float(row["max_quality_score"]) if row["max_quality_score"] else None,
                    "high_quality_count": row["high_quality_count"] or 0,
                    "low_quality_count": row["low_quality_count"] or 0,
                })
            
            return {
                "prompt_key": prompt_key,
                "versions": versions,
            }

