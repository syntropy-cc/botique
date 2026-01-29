"""
Unit tests for LLM log query functions.

Tests trace and event query functionality.

Location: tests/tools/core/test_llm_log_queries.py
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from src.core.llm_log_queries import (
    list_traces,
    get_trace_with_events,
    get_events_by_trace,
    get_event_tree,
    search_events_by_text,
    get_cost_summary,
    get_prompt_versions_with_usage,
    compare_prompt_versions,
    get_prompt_quality_stats,
)
from src.core.llm_log_db import init_database, db_connection
from src.core.prompt_registry import register_prompt


class TestLLMLogQueries(unittest.TestCase):
    """Test cases for LLM log query functions."""
    
    def setUp(self):
        """Set up test database with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        init_database(self.db_path)
        
        # Create sample data
        self.setup_sample_data()
    
    def tearDown(self):
        """Clean up test database."""
        if self.db_path.exists():
            self.db_path.unlink()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_sample_data(self):
        """Create sample traces and events for testing."""
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create trace
            self.trace_id = str(uuid4())
            now = datetime.utcnow().isoformat() + "Z"
            cursor.execute("""
                INSERT INTO traces (id, created_at, name, user_id, tenant_id, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.trace_id,
                now,
                "test_trace",
                "user_123",
                "tenant_456",
                json.dumps({"article_slug": "test-article"}),
            ))
            
            # Create events
            self.event_ids = []
            for i in range(3):
                event_id = str(uuid4())
                self.event_ids.append(event_id)
                cursor.execute("""
                    INSERT INTO events (
                        id, trace_id, created_at, type, name, model,
                        input_text, output_text, tokens_input, tokens_output,
                        tokens_total, cost_total, duration_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    self.trace_id,
                    now,
                    "llm",
                    f"test_event_{i}",
                    "deepseek-chat",
                    f"Input text {i}",
                    f"Output text {i}",
                    100 + i * 10,
                    50 + i * 5,
                    150 + i * 15,
                    0.001 + i * 0.0001,
                    1000 + i * 100,
                ))
            
            # Create child event
            child_event_id = str(uuid4())
            cursor.execute("""
                INSERT INTO events (
                    id, trace_id, parent_id, created_at, type, name
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                child_event_id,
                self.trace_id,
                self.event_ids[0],
                now,
                "step",
                "child_event",
            ))
            self.child_event_id = child_event_id
            
            conn.commit()
    
    def test_list_traces_basic(self):
        """Test basic trace listing."""
        traces = list_traces(limit=10, db_path=self.db_path)
        
        self.assertGreaterEqual(len(traces), 1)
        self.assertIn(self.trace_id, [t["id"] for t in traces])
    
    def test_list_traces_with_filters(self):
        """Test trace filtering."""
        # Filter by user_id
        traces = list_traces(
            limit=10,
            filters={"user_id": "user_123"},
            db_path=self.db_path,
        )
        
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["user_id"], "user_123")
        
        # Filter by tenant_id
        traces = list_traces(
            limit=10,
            filters={"tenant_id": "tenant_456"},
            db_path=self.db_path,
        )
        
        self.assertEqual(len(traces), 1)
        
        # Filter by name
        traces = list_traces(
            limit=10,
            filters={"name": "test"},
            db_path=self.db_path,
        )
        
        self.assertGreaterEqual(len(traces), 1)
    
    def test_list_traces_with_date_filters(self):
        """Test trace filtering by date."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Filter by created_after
        traces = list_traces(
            limit=10,
            filters={"created_after": yesterday.isoformat()},
            db_path=self.db_path,
        )
        
        self.assertGreaterEqual(len(traces), 1)
        
        # Filter by created_before
        traces = list_traces(
            limit=10,
            filters={"created_before": tomorrow.isoformat()},
            db_path=self.db_path,
        )
        
        self.assertGreaterEqual(len(traces), 1)
    
    def test_get_trace_with_events(self):
        """Test retrieving trace with events."""
        trace = get_trace_with_events(self.trace_id, self.db_path)
        
        self.assertIsNotNone(trace)
        self.assertEqual(trace["id"], self.trace_id)
        self.assertIn("events", trace)
        self.assertEqual(len(trace["events"]), 4)  # 3 events + 1 child
        
        # Check metadata parsing
        self.assertIn("metadata", trace)
        self.assertEqual(trace["metadata"]["article_slug"], "test-article")
    
    def test_get_trace_with_events_nonexistent(self):
        """Test retrieving non-existent trace."""
        trace = get_trace_with_events("nonexistent_id", self.db_path)
        
        self.assertIsNone(trace)
    
    def test_get_events_by_trace(self):
        """Test retrieving flat list of events for trace."""
        events = get_events_by_trace(self.trace_id, self.db_path)
        
        self.assertEqual(len(events), 4)  # 3 events + 1 child
        event_ids = [e["id"] for e in events]
        self.assertIn(self.event_ids[0], event_ids)
    
    def test_get_event_tree(self):
        """Test retrieving event tree."""
        tree = get_event_tree(self.event_ids[0], self.db_path)
        
        self.assertIsNotNone(tree)
        self.assertEqual(tree["id"], self.event_ids[0])
        self.assertIn("children", tree)
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(tree["children"][0]["id"], self.child_event_id)
    
    def test_search_events_by_text(self):
        """Test searching events by text."""
        events = search_events_by_text("Input text", limit=10, db_path=self.db_path)
        
        self.assertGreaterEqual(len(events), 1)
        self.assertTrue(any("Input text" in e.get("input_text", "") for e in events))
    
    def test_get_cost_summary(self):
        """Test cost summary calculation."""
        summary = get_cost_summary(
            filters={"trace_id": self.trace_id},
            db_path=self.db_path,
        )
        
        self.assertIn("summary", summary)
        self.assertIn("total_cost", summary["summary"])
        self.assertGreater(summary["summary"]["total_cost"], 0)
    
    def test_get_cost_summary_with_grouping(self):
        """Test cost summary with grouping."""
        summary = get_cost_summary(
            filters={"trace_id": self.trace_id, "group_by": ["model"]},
            db_path=self.db_path,
        )
        
        self.assertIn("aggregations", summary)
        self.assertIn("by_model", summary["aggregations"])
        self.assertGreater(len(summary["aggregations"]["by_model"]), 0)
    
    def test_get_prompt_versions_with_usage(self):
        """Test retrieving prompt versions with usage count."""
        # Register a prompt
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Test template",
            db_path=self.db_path,
        )
        
        # Create event with prompt_id
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            event_id = str(uuid4())
            now = datetime.utcnow().isoformat() + "Z"
            cursor.execute("""
                INSERT INTO events (
                    id, trace_id, created_at, type, prompt_id
                )
                VALUES (?, ?, ?, ?, ?)
            """, (event_id, self.trace_id, now, "llm", prompt_id))
            conn.commit()
        
        versions = get_prompt_versions_with_usage("test_prompt", self.db_path)
        
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["usage_count"], 1)
    
    def test_compare_prompt_versions(self):
        """Test comparing prompt versions."""
        # Register multiple versions
        prompt_id1, version1 = register_prompt(
            prompt_key="test_prompt",
            template="Version 1",
            db_path=self.db_path,
        )
        
        prompt_id2, version2 = register_prompt(
            prompt_key="test_prompt",
            template="Version 2",
            db_path=self.db_path,
        )
        
        # Create events for version 1
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            for i in range(2):
                event_id = str(uuid4())
                now = datetime.utcnow().isoformat() + "Z"
                cursor.execute("""
                    INSERT INTO events (
                        id, trace_id, created_at, type, prompt_id,
                        tokens_total, cost_total
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (event_id, self.trace_id, now, "llm", prompt_id1, 100, 0.01))
            conn.commit()
        
        comparison = compare_prompt_versions("test_prompt", self.db_path)
        
        self.assertEqual(comparison["prompt_key"], "test_prompt")
        self.assertEqual(len(comparison["versions"]), 2)
        # Version 1 should have 2 events
        version1_data = next(v for v in comparison["versions"] if v["version"] == "v1")
        self.assertEqual(version1_data["event_count"], 2)
    
    def test_get_prompt_quality_stats(self):
        """Test retrieving prompt quality statistics."""
        # Register prompt
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Test template",
            db_path=self.db_path,
        )
        
        # Create events with quality scores
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            for score in [0.8, 0.9, 0.7]:
                event_id = str(uuid4())
                now = datetime.utcnow().isoformat() + "Z"
                cursor.execute("""
                    INSERT INTO events (
                        id, trace_id, created_at, type, prompt_id, quality_score
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event_id, self.trace_id, now, "llm", prompt_id, score))
            conn.commit()
        
        stats = get_prompt_quality_stats(prompt_id=prompt_id, db_path=self.db_path)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats["event_count"], 3)
        self.assertIsNotNone(stats["avg_quality_score"])
        self.assertGreater(stats["avg_quality_score"], 0.7)
    
    def test_json_field_parsing(self):
        """Test that JSON fields are parsed correctly."""
        # Create trace with JSON metadata
        trace_id = str(uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO traces (id, created_at, metadata_json)
                VALUES (?, ?, ?)
            """, (trace_id, now, json.dumps({"key": "value"})))
            
            # Create event with JSON fields
            event_id = str(uuid4())
            cursor.execute("""
                INSERT INTO events (
                    id, trace_id, created_at, type,
                    input_json, output_json, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                trace_id,
                now,
                "llm",
                json.dumps({"input": "data"}),
                json.dumps({"output": "data"}),
                json.dumps({"meta": "data"}),
            ))
            conn.commit()
        
        # Retrieve trace
        trace = get_trace_with_events(trace_id, self.db_path)
        
        self.assertIsNotNone(trace)
        self.assertIn("metadata", trace)
        self.assertEqual(trace["metadata"]["key"], "value")
        
        # Check event JSON fields
        events = [e for e in trace["events"] if e["id"] == event_id]
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertIn("input", event)
        self.assertIn("output", event)
        self.assertEqual(event["input"]["input"], "data")


if __name__ == "__main__":
    unittest.main()
