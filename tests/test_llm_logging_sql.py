"""
Tests for SQL-based LLM logging system.

Tests trace/event creation, cost calculation, quality metrics, queries, and migration.

Location: tests/test_llm_logging_sql.py
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.llm_log_db import db_connection, init_database
from core.llm_logger import LLMLogger
from core.llm_pricing import calculate_cost, load_pricing_config, update_pricing
from core.llm_log_queries import (
    get_cost_summary,
    get_event_tree,
    get_events_by_trace,
    get_trace_with_events,
    list_traces,
    search_events_by_text,
)


class TestLLMLoggingSQL(unittest.TestCase):
    """Test suite for SQL-based LLM logging."""
    
    def setUp(self):
        """Set up test database in memory."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.db_path_obj = Path(self.db_path)
        
        # Initialize database
        init_database(self.db_path_obj)
        
        # Create logger with test database
        self.logger = LLMLogger(
            db_path=self.db_path_obj,
            use_sql=True,
        )
    
    def tearDown(self):
        """Clean up test database."""
        import os
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_trace_creation(self):
        """Test creating a trace."""
        trace_id = self.logger.create_trace(
            name="test_trace",
            user_id="user123",
            tenant_id="tenant456",
            tags="test,debug",
            metadata={"test": True},
        )
        
        self.assertIsNotNone(trace_id)
        
        # Verify trace in database
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM traces WHERE id = ?", (trace_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row["name"], "test_trace")
            self.assertEqual(row["user_id"], "user123")
            self.assertEqual(row["tenant_id"], "tenant456")
            self.assertEqual(row["tags"], "test,debug")
            
            metadata = json.loads(row["metadata_json"])
            self.assertTrue(metadata["test"])
    
    def test_llm_event_creation(self):
        """Test creating an LLM event."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        event_id = self.logger.log_llm_event(
            trace_id=trace_id,
            name="test_llm_call",
            model="deepseek-chat",
            input_text="Test prompt",
            input_obj={"prompt": "Test prompt", "temperature": 0.2},
            output_text="Test response",
            output_obj={"content": "Test response"},
            duration_ms=1000.5,
            tokens_input=100,
            tokens_output=50,
            tokens_total=150,
        )
        
        self.assertIsNotNone(event_id)
        
        # Verify event in database
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row["trace_id"], trace_id)
            self.assertEqual(row["type"], "llm")
            self.assertEqual(row["name"], "test_llm_call")
            self.assertEqual(row["model"], "deepseek-chat")
            self.assertEqual(row["input_text"], "Test prompt")
            self.assertEqual(row["output_text"], "Test response")
            self.assertEqual(row["tokens_input"], 100)
            self.assertEqual(row["tokens_output"], 50)
            self.assertEqual(row["tokens_total"], 150)
            self.assertEqual(row["duration_ms"], 1000)
            self.assertIsNotNone(row["cost_total"])  # Should be calculated
    
    def test_step_event_creation(self):
        """Test creating a non-LLM step event."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        event_id = self.logger.log_step_event(
            trace_id=trace_id,
            name="test_step",
            input_text="Input data",
            output_text="Output data",
            duration_ms=500.0,
            type="preprocess",
            metadata={"step": "validation"},
        )
        
        self.assertIsNotNone(event_id)
        
        # Verify event in database
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row["trace_id"], trace_id)
            self.assertEqual(row["type"], "preprocess")
            self.assertEqual(row["name"], "test_step")
            self.assertIsNone(row["model"])  # Non-LLM events have no model
            self.assertEqual(row["input_text"], "Input data")
            self.assertEqual(row["output_text"], "Output data")
            self.assertEqual(row["duration_ms"], 500)
    
    def test_event_hierarchy(self):
        """Test parent-child relationships between events."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        # Create parent event
        parent_id = self.logger.log_step_event(
            trace_id=trace_id,
            name="parent_step",
            type="system",
        )
        
        # Create child event
        child_id = self.logger.log_step_event(
            trace_id=trace_id,
            name="child_step",
            parent_id=parent_id,
            type="step",
        )
        
        # Verify relationship
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT parent_id FROM events WHERE id = ?", (child_id,))
            row = cursor.fetchone()
            self.assertEqual(row["parent_id"], parent_id)
    
    def test_cost_calculation(self):
        """Test cost calculation."""
        # Test with known model
        cost_input, cost_output, cost_total = calculate_cost(
            "deepseek-chat", 1000, 500, self.db_path_obj
        )
        
        self.assertIsNotNone(cost_input)
        self.assertIsNotNone(cost_output)
        self.assertIsNotNone(cost_total)
        self.assertGreater(cost_total, 0)
        
        # Test with unknown model
        cost_input, cost_output, cost_total = calculate_cost(
            "unknown-model", 1000, 500, self.db_path_obj
        )
        
        self.assertIsNone(cost_input)
        self.assertIsNone(cost_output)
        self.assertIsNone(cost_total)
    
    def test_quality_metrics(self):
        """Test setting quality metrics on events."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        event_id = self.logger.log_llm_event(
            trace_id=trace_id,
            name="test_llm",
            model="deepseek-chat",
            input_text="Test",
            input_obj={},
            output_text="Response",
            output_obj={},
            duration_ms=100,
            tokens_input=10,
            tokens_output=5,
        )
        
        # Set quality metrics
        self.logger.set_event_quality(
            event_id=event_id,
            score=0.85,
            label="good",
            metadata={"rated_by": "test", "criteria": "relevance"},
        )
        
        # Verify quality metrics
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quality_score, quality_label, quality_metadata_json FROM events WHERE id = ?",
                (event_id,)
            )
            row = cursor.fetchone()
            
            self.assertEqual(row["quality_score"], 0.85)
            self.assertEqual(row["quality_label"], "good")
            
            metadata = json.loads(row["quality_metadata_json"])
            self.assertEqual(metadata["rated_by"], "test")
    
    def test_list_traces(self):
        """Test listing traces with filters."""
        # Create multiple traces
        trace1 = self.logger.create_trace(name="trace1", user_id="user1")
        trace2 = self.logger.create_trace(name="trace2", user_id="user2")
        trace3 = self.logger.create_trace(name="trace3", user_id="user1")
        
        # List all traces
        traces = list_traces(limit=10, db_path=self.db_path_obj)
        self.assertGreaterEqual(len(traces), 3)
        
        # Filter by user_id
        traces = list_traces(
            limit=10,
            filters={"user_id": "user1"},
            db_path=self.db_path_obj,
        )
        self.assertEqual(len(traces), 2)
        for trace in traces:
            self.assertEqual(trace["user_id"], "user1")
    
    def test_get_trace_with_events(self):
        """Test getting trace with events."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        # Create events
        event1 = self.logger.log_llm_event(
            trace_id=trace_id,
            name="event1",
            model="deepseek-chat",
            input_text="Input1",
            input_obj={},
            output_text="Output1",
            output_obj={},
            duration_ms=100,
        )
        
        event2 = self.logger.log_step_event(
            trace_id=trace_id,
            name="event2",
        )
        
        # Get trace with events
        trace = get_trace_with_events(trace_id, self.db_path_obj)
        
        self.assertIsNotNone(trace)
        self.assertEqual(trace["id"], trace_id)
        self.assertEqual(len(trace["events"]), 2)
    
    def test_search_events_by_text(self):
        """Test searching events by text."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        # Create event with specific text
        self.logger.log_llm_event(
            trace_id=trace_id,
            name="test_event",
            model="deepseek-chat",
            input_text="Search for this text",
            input_obj={},
            output_text="Response text",
            output_obj={},
            duration_ms=100,
        )
        
        # Search for text
        results = search_events_by_text("Search for", db_path=self.db_path_obj)
        
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("Search for this text", results[0]["input_text"])
    
    def test_get_cost_summary(self):
        """Test cost summary aggregation."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        # Create multiple LLM events with costs
        for i in range(3):
            self.logger.log_llm_event(
                trace_id=trace_id,
                name=f"event_{i}",
                model="deepseek-chat",
                input_text="Test",
                input_obj={},
                output_text="Response",
                output_obj={},
                duration_ms=100,
                tokens_input=100,
                tokens_output=50,
            )
        
        # Get cost summary
        summary = get_cost_summary(db_path=self.db_path_obj)
        
        self.assertIsNotNone(summary)
        self.assertIn("summary", summary)
        self.assertGreater(summary["summary"]["total_cost"], 0)
        self.assertEqual(summary["summary"]["total_events"], 3)
    
    def test_get_event_tree(self):
        """Test getting event tree with children."""
        trace_id = self.logger.create_trace(name="test_trace")
        
        # Create parent and child events
        parent_id = self.logger.log_step_event(
            trace_id=trace_id,
            name="parent",
        )
        
        child_id = self.logger.log_step_event(
            trace_id=trace_id,
            name="child",
            parent_id=parent_id,
        )
        
        # Get event tree
        tree = get_event_tree(parent_id, self.db_path_obj)
        
        self.assertIsNotNone(tree)
        self.assertEqual(tree["id"], parent_id)
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(tree["children"][0]["id"], child_id)
    
    def test_pricing_config(self):
        """Test pricing configuration management."""
        # Load default pricing
        pricing = load_pricing_config(self.db_path_obj)
        self.assertIn("deepseek-chat", pricing)
        
        # Update pricing
        update_pricing(
            "test-model",
            price_input=0.001,
            price_output=0.002,
            db_path=self.db_path_obj,
        )
        
        # Verify update
        pricing = load_pricing_config(self.db_path_obj)
        self.assertIn("test-model", pricing)
        self.assertEqual(pricing["test-model"]["input"], 0.001)
        self.assertEqual(pricing["test-model"]["output"], 0.002)
    
    def test_logger_compatibility(self):
        """Test that old log_call() API still works."""
        trace_id = self.logger.create_trace(name="test_trace")
        self.logger.current_trace_id = trace_id
        
        # Use old API
        self.logger.log_call(
            prompt="Test prompt",
            response="Test response",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.2,
            duration_ms=1000,
            tokens_input=100,
            tokens_output=50,
            tokens_total=150,
        )
        
        # Verify event was created
        with db_connection(self.db_path_obj) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM events WHERE trace_id = ?", (trace_id,))
            row = cursor.fetchone()
            self.assertEqual(row["count"], 1)


if __name__ == "__main__":
    unittest.main()

