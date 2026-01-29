"""
Unit tests for LLM logger.

Tests LLM logging functionality, trace creation, event logging, and context management.

Location: tests/tools/core/test_llm_logger.py
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.llm_logger import LLMLogger


class TestLLMLoggerInitialization(unittest.TestCase):
    """Test cases for LLMLogger initialization."""
    
    def test_logger_initialization(self):
        """Test basic logger initialization."""
        logger = LLMLogger()
        
        self.assertTrue(logger.enabled)
        self.assertTrue(logger.use_sql)
        self.assertIsNotNone(logger.session_id)
        self.assertIsInstance(logger.calls, list)
        self.assertEqual(len(logger.calls), 0)
    
    def test_logger_initialization_with_custom_db(self):
        """Test logger initialization with custom database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "custom.db"
            
            logger = LLMLogger(db_path=db_path)
            
            self.assertEqual(logger.db_path, db_path)
            self.assertTrue(db_path.exists())  # Database should be initialized
    
    def test_logger_initialization_disabled(self):
        """Test logger initialization with logging disabled."""
        logger = LLMLogger(enabled=False)
        
        self.assertFalse(logger.enabled)
    
    def test_logger_initialization_no_sql(self):
        """Test logger initialization without SQL backend."""
        logger = LLMLogger(use_sql=False)
        
        self.assertFalse(logger.use_sql)


class TestLLMLoggerContext(unittest.TestCase):
    """Test cases for context management."""
    
    def setUp(self):
        """Set up logger for testing."""
        self.logger = LLMLogger(use_sql=False)
    
    def test_set_context(self):
        """Test setting context."""
        self.logger.set_context(
            article_slug="test-article",
            post_id="post_001",
            slide_number=1,
        )
        
        self.assertEqual(self.logger.current_article_slug, "test-article")
        self.assertEqual(self.logger.current_post_id, "post_001")
        self.assertEqual(self.logger.current_slide_number, 1)
    
    def test_set_context_partial(self):
        """Test setting partial context."""
        self.logger.set_context(article_slug="test-article")
        
        self.assertEqual(self.logger.current_article_slug, "test-article")
        self.assertIsNone(self.logger.current_post_id)
        self.assertIsNone(self.logger.current_slide_number)
    
    def test_set_context_updates(self):
        """Test that context can be updated."""
        self.logger.set_context(post_id="post_001")
        self.logger.set_context(post_id="post_002")
        
        self.assertEqual(self.logger.current_post_id, "post_002")


class TestLLMLoggerTrace(unittest.TestCase):
    """Test cases for trace creation."""
    
    def setUp(self):
        """Set up logger with temporary database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.logger = LLMLogger(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up."""
        if self.db_path.exists():
            self.db_path.unlink()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_trace(self):
        """Test trace creation."""
        trace_id = self.logger.create_trace(
            name="test_trace",
            user_id="user_123",
            tenant_id="tenant_456",
            tags="test,debug",
            metadata={"key": "value"},
        )
        
        self.assertIsNotNone(trace_id)
        self.assertEqual(self.logger.current_trace_id, trace_id)
        
        # Verify in database
        from src.core.llm_log_queries import get_trace_with_events
        trace = get_trace_with_events(trace_id, self.db_path)
        
        self.assertIsNotNone(trace)
        self.assertEqual(trace["name"], "test_trace")
        self.assertEqual(trace["user_id"], "user_123")
        self.assertEqual(trace["tenant_id"], "tenant_456")
        self.assertIn("metadata", trace)
        self.assertEqual(trace["metadata"]["key"], "value")
    
    def test_create_trace_minimal(self):
        """Test trace creation with minimal parameters."""
        trace_id = self.logger.create_trace(name="minimal_trace")
        
        self.assertIsNotNone(trace_id)
        self.assertEqual(self.logger.current_trace_id, trace_id)


class TestLLMLoggerEvents(unittest.TestCase):
    """Test cases for event logging."""
    
    def setUp(self):
        """Set up logger with temporary database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.logger = LLMLogger(db_path=self.db_path)
        self.trace_id = self.logger.create_trace(name="test_trace")
    
    def tearDown(self):
        """Clean up."""
        if self.db_path.exists():
            self.db_path.unlink()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_llm_event(self):
        """Test logging LLM event."""
        event_id = self.logger.log_llm_event(
            trace_id=self.trace_id,
            name="test.llm_call",
            model="deepseek-chat",
            input_text="Test prompt",
            input_obj={"prompt": "Test prompt"},
            output_text="Test response",
            output_obj={"content": "Test response"},
            duration_ms=1000.5,
            tokens_input=100,
            tokens_output=50,
            tokens_total=150,
        )
        
        self.assertIsNotNone(event_id)
        
        # Verify in database
        from src.core.llm_log_queries import get_events_by_trace
        events = get_events_by_trace(self.trace_id, self.db_path)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["name"], "test.llm_call")
        self.assertEqual(event["model"], "deepseek-chat")
        self.assertEqual(event["input_text"], "Test prompt")
    
    def test_log_step_event(self):
        """Test logging step event."""
        event_id = self.logger.log_step_event(
            trace_id=self.trace_id,
            name="test.step",
            input_text="Input",
            output_text="Output",
            duration_ms=500.0,
            type="step",
            status="success",
        )
        
        self.assertIsNotNone(event_id)
        
        # Verify in database
        from src.core.llm_log_queries import get_events_by_trace
        events = get_events_by_trace(self.trace_id, self.db_path)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["type"], "step")
        self.assertEqual(event["name"], "test.step")
    
    def test_log_call(self):
        """Test logging call using log_call method."""
        self.logger.log_call(
            prompt="Test prompt",
            response="Test response",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.7,
            duration_ms=1000.0,
            tokens_input=100,
            tokens_output=50,
            tokens_total=150,
        )
        
        # Verify in-memory log
        self.assertEqual(len(self.logger.calls), 1)
        call = self.logger.calls[0]
        self.assertEqual(call["model"], "deepseek-chat")
        self.assertEqual(call["input"]["prompt"], "Test prompt")
        self.assertEqual(call["output"]["content"], "Test response")
    
    def test_log_call_with_error(self):
        """Test logging call with error."""
        self.logger.log_call(
            prompt="Test prompt",
            response=None,
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.7,
            duration_ms=1000.0,
            status="error",
            error="Connection timeout",
        )
        
        call = self.logger.calls[0]
        self.assertEqual(call["status"], "error")
        self.assertEqual(call["error"], "Connection timeout")
    
    def test_context_inheritance(self):
        """Test that context is inherited in events."""
        self.logger.set_context(
            article_slug="test-article",
            post_id="post_001",
            slide_number=1,
        )
        
        self.logger.log_call(
            prompt="Test",
            response="Response",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.7,
            duration_ms=1000.0,
        )
        
        call = self.logger.calls[0]
        self.assertEqual(call["context"]["article_slug"], "test-article")
        self.assertEqual(call["context"]["post_id"], "post_001")
        self.assertEqual(call["context"]["slide_number"], 1)
    
    def test_parent_child_relationships(self):
        """Test event hierarchy with parent-child relationships."""
        # Log parent event
        parent_id = self.logger.log_llm_event(
            trace_id=self.trace_id,
            name="parent.event",
            model="deepseek-chat",
            input_text="Parent input",
            input_obj={},
            output_text="Parent output",
            output_obj={},
            duration_ms=1000.0,
        )
        
        # Log child event
        child_id = self.logger.log_llm_event(
            trace_id=self.trace_id,
            name="child.event",
            model="deepseek-chat",
            input_text="Child input",
            input_obj={},
            output_text="Child output",
            output_obj={},
            duration_ms=500.0,
            parent_id=parent_id,
        )
        
        # Verify relationship
        from src.core.llm_log_queries import get_event_tree
        tree = get_event_tree(parent_id, self.db_path)
        
        self.assertIsNotNone(tree)
        self.assertEqual(len(tree["children"]), 1)
        self.assertEqual(tree["children"][0]["id"], child_id)


class TestLLMLoggerCostCalculation(unittest.TestCase):
    """Test cases for cost calculation."""
    
    def setUp(self):
        """Set up logger."""
        self.logger = LLMLogger(use_sql=False)
    
    def test_cost_calculation(self):
        """Test cost calculation logic."""
        cost = self.logger._calculate_cost(
            model="deepseek-chat",
            tokens_input=1000,
            tokens_output=500,
        )
        
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)
    
    def test_cost_calculation_none_tokens(self):
        """Test cost calculation with None tokens."""
        cost = self.logger._calculate_cost(
            model="deepseek-chat",
            tokens_input=None,
            tokens_output=None,
        )
        
        self.assertIsNone(cost)
    
    def test_cost_calculation_unknown_model(self):
        """Test cost calculation with unknown model."""
        cost = self.logger._calculate_cost(
            model="unknown-model",
            tokens_input=1000,
            tokens_output=500,
        )
        
        self.assertIsNone(cost)


class TestLLMLoggerPhaseDetection(unittest.TestCase):
    """Test cases for phase and function detection."""
    
    def setUp(self):
        """Set up logger."""
        self.logger = LLMLogger(use_sql=False)
    
    def test_detect_phase_and_function(self):
        """Test phase and function detection from stack trace."""
        # This test is difficult to mock properly due to stack trace inspection
        # Instead, we'll test that the method returns valid values
        phase, function = self.logger._detect_phase_and_function()
        
        # Should return valid strings (may be "unknown" if called from test context)
        self.assertIsInstance(phase, str)
        self.assertIsInstance(function, str)
        self.assertIsNotNone(phase)
        self.assertIsNotNone(function)


class TestLLMLoggerDisabled(unittest.TestCase):
    """Test cases for disabled logger."""
    
    def setUp(self):
        """Set up disabled logger."""
        self.logger = LLMLogger(enabled=False)
    
    def test_log_call_disabled(self):
        """Test that log_call does nothing when disabled."""
        initial_calls = len(self.logger.calls)
        
        self.logger.log_call(
            prompt="Test",
            response="Response",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.7,
            duration_ms=1000.0,
        )
        
        self.assertEqual(len(self.logger.calls), initial_calls)
    
    def test_create_trace_disabled(self):
        """Test that create_trace returns session_id when disabled."""
        trace_id = self.logger.create_trace(name="test")
        
        self.assertEqual(trace_id, self.logger.session_id)


class TestLLMLoggerSession(unittest.TestCase):
    """Test cases for session management."""
    
    def setUp(self):
        """Set up logger."""
        self.logger = LLMLogger(use_sql=False)
    
    def test_get_session_id(self):
        """Test getting session ID."""
        session_id = self.logger.get_session_id()
        
        self.assertIsNotNone(session_id)
        self.assertEqual(session_id, self.logger.session_id)
    
    def test_reset_session(self):
        """Test resetting session."""
        original_session_id = self.logger.session_id
        self.logger.log_call(
            prompt="Test",
            response="Response",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            max_tokens=100,
            temperature=0.7,
            duration_ms=1000.0,
        )
        
        self.logger.reset_session()
        
        self.assertNotEqual(self.logger.session_id, original_session_id)
        self.assertEqual(len(self.logger.calls), 0)
        self.assertIsNone(self.logger.current_trace_id)


if __name__ == "__main__":
    unittest.main()
