"""
Database module for LLM logging.

Handles database initialization, connection management, and schema creation.
Supports both SQLite (default) and PostgreSQL (via DB_URL environment variable).

Location: src/core/llm_log_db.py
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to import psycopg2 for PostgreSQL support (optional)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def get_db_path() -> Path:
    """
    Get database path from environment variable or default location.
    
    Returns:
        Path to SQLite database file
    """
    env_path = os.getenv("LLM_LOGS_DB_PATH")
    if env_path:
        return Path(env_path)
    
    # Default to project root
    root_dir = Path(__file__).resolve().parents[2]
    return root_dir / "llm_logs.db"


def is_postgresql_mode() -> bool:
    """
    Check if PostgreSQL mode is enabled via DB_URL environment variable.
    
    Returns:
        True if DB_URL is set, False otherwise
    """
    return bool(os.getenv("DB_URL"))


def get_postgresql_connection():
    """
    Get PostgreSQL connection from DB_URL environment variable.
    
    Returns:
        psycopg2 connection object
        
    Raises:
        RuntimeError: If psycopg2 is not available or DB_URL is invalid
    """
    if not PSYCOPG2_AVAILABLE:
        raise RuntimeError(
            "PostgreSQL support requires psycopg2. "
            "Install it with: pip install psycopg2-binary"
        )
    
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise RuntimeError("DB_URL environment variable not set")
    
    return psycopg2.connect(db_url)


def get_sqlite_connection(db_path: Path) -> sqlite3.Connection:
    """
    Get SQLite connection.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        sqlite3.Connection object
    """
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn


def get_db_connection(db_path: Optional[Path] = None):
    """
    Get database connection (SQLite or PostgreSQL).
    
    Args:
        db_path: Path to SQLite database (ignored if PostgreSQL mode)
        
    Returns:
        Database connection object (sqlite3.Connection or psycopg2 connection)
    """
    if is_postgresql_mode():
        return get_postgresql_connection()
    
    if db_path is None:
        db_path = get_db_path()
    
    return get_sqlite_connection(db_path)


@contextmanager
def db_connection(db_path: Optional[Path] = None):
    """
    Context manager for database connections.
    
    Ensures proper cleanup (commit/rollback) of database transactions.
    
    Args:
        db_path: Path to SQLite database (ignored if PostgreSQL mode)
        
    Yields:
        Database connection object
        
    Example:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM traces")
    """
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize database schema.
    
    Creates all tables and indexes if they don't exist.
    Idempotent: safe to call multiple times.
    
    Args:
        db_path: Path to SQLite database (ignored if PostgreSQL mode)
    """
    if db_path is None:
        db_path = get_db_path()
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Create traces table
        if is_postgresql_mode():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    name TEXT,
                    user_id TEXT,
                    tenant_id TEXT,
                    tags TEXT,
                    metadata_json TEXT,
                    tokens_input_total INTEGER,
                    tokens_output_total INTEGER,
                    tokens_total INTEGER,
                    cost_total REAL
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    name TEXT,
                    user_id TEXT,
                    tenant_id TEXT,
                    tags TEXT,
                    metadata_json TEXT,
                    tokens_input_total INTEGER,
                    tokens_output_total INTEGER,
                    tokens_total INTEGER,
                    cost_total REAL
                )
            """)
        
        # Create events table
        if is_postgresql_mode():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    parent_id TEXT,
                    created_at TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT,
                    model TEXT,
                    role TEXT,
                    input_text TEXT,
                    input_json TEXT,
                    output_text TEXT,
                    output_json TEXT,
                    error TEXT,
                    duration_ms INTEGER,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    tokens_total INTEGER,
                    cost_input REAL,
                    cost_output REAL,
                    cost_total REAL,
                    quality_score REAL,
                    quality_label TEXT,
                    quality_metadata_json TEXT,
                    metadata_json TEXT,
                    FOREIGN KEY (trace_id) REFERENCES traces(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES events(id) ON DELETE SET NULL
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    parent_id TEXT,
                    created_at TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT,
                    model TEXT,
                    role TEXT,
                    input_text TEXT,
                    input_json TEXT,
                    output_text TEXT,
                    output_json TEXT,
                    error TEXT,
                    duration_ms INTEGER,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    tokens_total INTEGER,
                    cost_input REAL,
                    cost_output REAL,
                    cost_total REAL,
                    quality_score REAL,
                    quality_label TEXT,
                    quality_metadata_json TEXT,
                    metadata_json TEXT,
                    FOREIGN KEY (trace_id) REFERENCES traces(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES events(id) ON DELETE SET NULL
                )
            """)
        
        # Create model_pricing table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_pricing (
                model_name TEXT PRIMARY KEY,
                price_per_1k_input REAL NOT NULL,
                price_per_1k_output REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_events_trace_id ON events(trace_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_parent_id ON events(parent_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)",
            "CREATE INDEX IF NOT EXISTS idx_events_model ON events(model)",
            "CREATE INDEX IF NOT EXISTS idx_events_name ON events(name)",
            "CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_traces_user_id ON traces(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_traces_tenant_id ON traces(tenant_id)",
            "CREATE INDEX IF NOT EXISTS idx_traces_created_at ON traces(created_at)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()

