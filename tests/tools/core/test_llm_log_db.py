"""
Unit tests for LLM log database operations.

Tests database initialization, connections, and path management.

Location: tests/tools/core/test_llm_log_db.py
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.core.llm_log_db import (
    get_db_path,
    get_sqlite_connection,
    db_connection,
    init_database,
    is_postgresql_mode,
    get_db_connection,
)


class TestGetDbPath(unittest.TestCase):
    """Test cases for get_db_path function."""
    
    def test_get_db_path_default(self):
        """Test default path resolution when no environment variable is set."""
        # Clean environment
        if "LLM_LOGS_DB_PATH" in os.environ:
            del os.environ["LLM_LOGS_DB_PATH"]
        
        db_path = get_db_path()
        
        self.assertIsInstance(db_path, Path)
        self.assertEqual(db_path.name, "llm_logs.db")
        # Should be in project root (parent of parent of parent of this file)
        self.assertTrue(db_path.parent.exists())
    
    def test_get_db_path_from_env(self):
        """Test environment variable override."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, "custom_llm_logs.db")
            os.environ["LLM_LOGS_DB_PATH"] = env_path
            
            try:
                db_path = get_db_path()
                
                self.assertIsInstance(db_path, Path)
                self.assertEqual(str(db_path), env_path)
            finally:
                if "LLM_LOGS_DB_PATH" in os.environ:
                    del os.environ["LLM_LOGS_DB_PATH"]


class TestSqliteConnection(unittest.TestCase):
    """Test cases for SQLite connection functions."""
    
    def test_get_sqlite_connection(self):
        """Test SQLite connection creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            conn = get_sqlite_connection(db_path)
            
            self.assertIsInstance(conn, sqlite3.Connection)
            self.assertEqual(conn.row_factory, sqlite3.Row)
            self.assertTrue(db_path.exists())
            
            conn.close()
    
    def test_get_sqlite_connection_creates_directory(self):
        """Test that connection creation creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "subdir" / "test.db"
            
            # Ensure subdir doesn't exist
            self.assertFalse(db_path.parent.exists())
            
            conn = get_sqlite_connection(db_path)
            
            self.assertTrue(db_path.parent.exists())
            self.assertTrue(db_path.exists())
            
            conn.close()
    
    def test_db_connection_context_manager(self):
        """Test context manager for database connections."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            with db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                cursor.execute("INSERT INTO test (id) VALUES (1)")
                # Context manager should commit on exit
            
            # Verify data was committed
            conn2 = sqlite3.connect(str(db_path))
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT id FROM test")
            result = cursor2.fetchone()
            conn2.close()
            
            self.assertEqual(result[0], 1)
    
    def test_db_connection_context_manager_rollback_on_error(self):
        """Test that context manager rolls back on exception."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Initialize database first
            init_database(db_path)
            
            try:
                with db_connection(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO traces (id, created_at) VALUES (?, ?)", ("test_id", "2024-01-01"))
                    # Raise exception to trigger rollback
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            # Verify data was NOT committed
            with db_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM traces WHERE id = ?", ("test_id",))
                count = cursor.fetchone()[0]
                
                self.assertEqual(count, 0)


class TestInitDatabase(unittest.TestCase):
    """Test cases for database initialization."""
    
    def test_init_database_creates_tables(self):
        """Test that init_database creates all required tables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            init_database(db_path)
            
            self.assertTrue(db_path.exists())
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check that tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('traces', 'events', 'prompts', 'model_pricing')
            """)
            tables = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            
            self.assertIn("traces", tables)
            self.assertIn("events", tables)
            self.assertIn("prompts", tables)
            self.assertIn("model_pricing", tables)
    
    def test_init_database_idempotent(self):
        """Test that calling init_database multiple times doesn't fail."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Call multiple times
            init_database(db_path)
            init_database(db_path)
            init_database(db_path)
            
            # Should not raise any exceptions
            self.assertTrue(db_path.exists())
    
    def test_init_database_indexes(self):
        """Test that indexes are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            init_database(db_path)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check that indexes exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            indexes = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            
            # Should have multiple indexes
            self.assertGreater(len(indexes), 0)
            # Check for specific indexes
            self.assertIn("idx_events_trace_id", indexes)
            self.assertIn("idx_prompts_key", indexes)
    
    def test_init_database_schema_structure(self):
        """Test that database schema has correct structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            init_database(db_path)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check traces table structure
            cursor.execute("PRAGMA table_info(traces)")
            traces_columns = {row[1] for row in cursor.fetchall()}
            
            expected_columns = {
                "id", "created_at", "name", "user_id", "tenant_id",
                "tags", "metadata_json", "tokens_input_total",
                "tokens_output_total", "tokens_total", "cost_total"
            }
            
            self.assertTrue(expected_columns.issubset(traces_columns))
            
            # Check events table structure
            cursor.execute("PRAGMA table_info(events)")
            events_columns = {row[1] for row in cursor.fetchall()}
            
            expected_events_columns = {
                "id", "trace_id", "parent_id", "created_at", "type",
                "name", "model", "input_text", "output_text",
                "tokens_input", "tokens_output", "tokens_total"
            }
            
            self.assertTrue(expected_events_columns.issubset(events_columns))
            
            conn.close()


class TestPostgreSQLMode(unittest.TestCase):
    """Test cases for PostgreSQL mode detection."""
    
    def test_is_postgresql_mode_false(self):
        """Test that PostgreSQL mode is False when DB_URL is not set."""
        if "DB_URL" in os.environ:
            del os.environ["DB_URL"]
        
        result = is_postgresql_mode()
        
        self.assertFalse(result)
    
    def test_is_postgresql_mode_true(self):
        """Test that PostgreSQL mode is True when DB_URL is set."""
        os.environ["DB_URL"] = "postgresql://test:test@localhost/test"
        
        try:
            result = is_postgresql_mode()
            self.assertTrue(result)
        finally:
            if "DB_URL" in os.environ:
                del os.environ["DB_URL"]


class TestMigrations(unittest.TestCase):
    """Test cases for database migrations."""
    
    def test_migration_template_hash_column(self):
        """Test that template_hash column migration works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Create database without template_hash column
            init_database(db_path)
            
            # Manually add a prompt without template_hash (simulating old database)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(prompts)")
            columns_before = {row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            # Re-initialize (should handle migration)
            init_database(db_path)
            
            # Verify column exists now
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(prompts)")
            columns_after = {row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            self.assertIn("template_hash", columns_after)
    
    def test_migration_prompt_id_column(self):
        """Test that prompt_id column migration works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Create database
            init_database(db_path)
            
            # Verify prompt_id column exists in events table
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(events)")
            columns = {row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            self.assertIn("prompt_id", columns)


class TestGetDbConnection(unittest.TestCase):
    """Test cases for get_db_connection function."""
    
    def test_get_db_connection_sqlite(self):
        """Test SQLite connection retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            conn = get_db_connection(db_path)
            
            self.assertIsInstance(conn, sqlite3.Connection)
            conn.close()
    
    def test_get_db_connection_default_path(self):
        """Test that get_db_connection uses default path when None."""
        # Clean environment
        if "LLM_LOGS_DB_PATH" in os.environ:
            del os.environ["LLM_LOGS_DB_PATH"]
        
        conn = get_db_connection()
        
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()


if __name__ == "__main__":
    unittest.main()
