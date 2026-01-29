# tests/conftest.py
"""
Root conftest.py providing shared fixtures for all test levels.

This file is automatically loaded by pytest and makes fixtures available
to all tests in the project. Organize fixtures by scope and purpose.

Usage:
    Fixtures defined here are automatically available to all tests.
    Import factories and helpers as needed in test files.
"""

import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Generator, Any
from unittest.mock import Mock, AsyncMock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Adjust imports based on your project structure
# from myapp.database import Base
# from myapp.models import User, Order
# from myapp.services import UserService, OrderService


# =============================================================================
# CONFIGURATION
# =============================================================================

# Test database URL - use environment variable or default to test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db"
)

TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")


# =============================================================================
# SESSION-SCOPED FIXTURES (Run once per test session)
# =============================================================================

@pytest.fixture(scope="session")
def database_engine():
    """
    Create database engine once per test session.
    
    Creates all tables at start, drops them at end.
    Use for integration tests that need real database.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True  # Verify connections before use
    )
    
    # Create all tables
    # Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup: Drop all tables
    # Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(database_engine):
    """Session factory for creating database sessions."""
    return sessionmaker(bind=database_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def redis_client():
    """
    Redis client for the test session.
    
    Use for integration tests that need real Redis.
    """
    import redis
    
    client = redis.Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    
    # Verify connection
    client.ping()
    
    yield client
    
    # Cleanup
    client.flushdb()  # Clear test database
    client.close()


# =============================================================================
# FUNCTION-SCOPED DATABASE FIXTURES (Fresh for each test)
# =============================================================================

@pytest.fixture
def db_session(session_factory) -> Generator[Session, None, None]:
    """
    Database session with automatic rollback after each test.
    
    This provides test isolation - changes made during a test are
    rolled back, leaving the database clean for the next test.
    
    Usage:
        def test_something(db_session):
            user = User(email="test@example.com")
            db_session.add(user)
            db_session.flush()  # Get ID without committing
            
            # Test logic here
            
            # Changes are automatically rolled back after test
    """
    connection = session_factory.kw["bind"].connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    # Begin a nested transaction (savepoint)
    nested = connection.begin_nested()
    
    # Handle rollbacks within the test
    @pytest.fixture(autouse=True)
    def handle_savepoint():
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_session_committed(session_factory) -> Generator[Session, None, None]:
    """
    Database session that commits changes.
    
    Use when you need to test transaction boundaries or
    when the code under test manages its own transactions.
    
    WARNING: Changes persist until explicitly cleaned up.
    """
    session = session_factory()
    
    yield session
    
    # Rollback any uncommitted changes
    session.rollback()
    session.close()


# =============================================================================
# FACTORY FIXTURES
# =============================================================================

@pytest.fixture
def user_factory(db_session):
    """
    Factory for creating User test objects.
    
    Usage:
        def test_something(user_factory):
            # Create with defaults
            user = user_factory.create()
            
            # Create with overrides
            admin = user_factory.create(role="admin")
            
            # Create without persisting (for unit tests)
            user = user_factory.build()
    """
    class UserFactory:
        @staticmethod
        def build(**overrides):
            """Create User instance without persisting."""
            defaults = {
                "id": str(uuid.uuid4()),
                "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
                "name": "Test User",
                "is_active": True,
                "created_at": datetime.utcnow(),
            }
            defaults.update(overrides)
            # return User(**defaults)
            return type("User", (), defaults)()  # Placeholder
        
        @staticmethod
        def create(**overrides):
            """Create and persist User instance."""
            user = UserFactory.build(**overrides)
            db_session.add(user)
            db_session.flush()
            return user
        
        @staticmethod
        def create_batch(count: int, **overrides):
            """Create multiple users."""
            return [UserFactory.create(**overrides) for _ in range(count)]
        
        # Trait methods for common variations
        @staticmethod
        def admin(**overrides):
            """Create admin user."""
            return UserFactory.create(role="admin", **overrides)
        
        @staticmethod
        def inactive(**overrides):
            """Create inactive user."""
            return UserFactory.create(is_active=False, **overrides)
        
        @staticmethod
        def premium(**overrides):
            """Create premium subscriber."""
            return UserFactory.create(
                subscription_tier="premium",
                subscription_expires=datetime.utcnow() + timedelta(days=365),
                **overrides
            )
    
    return UserFactory


@pytest.fixture
def order_factory(db_session, user_factory):
    """
    Factory for creating Order test objects.
    
    Automatically creates associated user if not provided.
    """
    class OrderFactory:
        @staticmethod
        def build(**overrides):
            """Create Order instance without persisting."""
            defaults = {
                "id": str(uuid.uuid4()),
                "status": "pending",
                "total": Decimal("99.99"),
                "created_at": datetime.utcnow(),
            }
            defaults.update(overrides)
            return type("Order", (), defaults)()  # Placeholder
        
        @staticmethod
        def create(**overrides):
            """Create and persist Order instance."""
            # Create customer if not provided
            if "customer" not in overrides and "customer_id" not in overrides:
                customer = user_factory.create()
                overrides["customer_id"] = customer.id
            
            order = OrderFactory.build(**overrides)
            db_session.add(order)
            db_session.flush()
            return order
        
        @staticmethod
        def with_items(item_count: int = 3, **overrides):
            """Create order with line items."""
            order = OrderFactory.create(**overrides)
            # Add items...
            return order
    
    return OrderFactory


@pytest.fixture
def product_factory(db_session):
    """Factory for creating Product test objects."""
    class ProductFactory:
        _counter = 0
        
        @classmethod
        def build(cls, **overrides):
            cls._counter += 1
            defaults = {
                "id": f"prod-{cls._counter:04d}",
                "name": f"Test Product {cls._counter}",
                "price": Decimal("29.99"),
                "stock": 100,
                "is_active": True,
            }
            defaults.update(overrides)
            return type("Product", (), defaults)()
        
        @classmethod
        def create(cls, **overrides):
            product = cls.build(**overrides)
            db_session.add(product)
            db_session.flush()
            return product
        
        @classmethod
        def out_of_stock(cls, **overrides):
            return cls.create(stock=0, **overrides)
    
    return ProductFactory


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_email_service():
    """
    Mock email service for testing email-related functionality.
    
    Usage:
        def test_sends_welcome_email(mock_email_service):
            service.register_user("test@example.com")
            
            mock_email_service.send.assert_called_once()
    """
    mock = Mock()
    mock.send.return_value = {"message_id": "test-123", "status": "sent"}
    mock.send_bulk.return_value = [{"message_id": f"test-{i}"} for i in range(10)]
    return mock


@pytest.fixture
def mock_payment_gateway():
    """
    Mock payment gateway for testing payment flows.
    
    Provides methods to simulate success, failure, and errors.
    """
    class MockPaymentGateway:
        def __init__(self):
            self.charges = []
            self._should_fail = False
            self._should_timeout = False
            self._decline_reason = None
        
        def charge(self, amount, customer_id, **kwargs):
            if self._should_timeout:
                raise TimeoutError("Connection timed out")
            
            if self._should_fail:
                return {
                    "success": False,
                    "error": self._decline_reason or "Card declined"
                }
            
            charge_id = f"ch_{uuid.uuid4().hex[:16]}"
            self.charges.append({
                "id": charge_id,
                "amount": amount,
                "customer_id": customer_id,
                **kwargs
            })
            return {"success": True, "charge_id": charge_id}
        
        def refund(self, charge_id, amount=None):
            return {"success": True, "refund_id": f"re_{uuid.uuid4().hex[:16]}"}
        
        # Test helpers
        def simulate_failure(self, reason="Card declined"):
            self._should_fail = True
            self._decline_reason = reason
        
        def simulate_timeout(self):
            self._should_timeout = True
        
        def reset(self):
            self._should_fail = False
            self._should_timeout = False
            self._decline_reason = None
            self.charges.clear()
    
    return MockPaymentGateway()


@pytest.fixture
def mock_event_bus():
    """
    Mock event bus for testing event publishing.
    
    Records published events for verification.
    """
    class MockEventBus:
        def __init__(self):
            self.published_events = []
        
        def publish(self, event):
            self.published_events.append(event)
        
        async def publish_async(self, event):
            self.published_events.append(event)
        
        def get_events_of_type(self, event_type):
            return [e for e in self.published_events if type(e).__name__ == event_type]
        
        def clear(self):
            self.published_events.clear()
    
    return MockEventBus()


@pytest.fixture
def mock_repository():
    """Generic mock repository for unit tests."""
    mock = Mock()
    mock.find_by_id.return_value = None
    mock.find_all.return_value = []
    mock.save.return_value = None
    mock.delete.return_value = None
    return mock


# =============================================================================
# HTTP CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def api_client(app):
    """
    Test client for API testing.
    
    Requires 'app' fixture to be defined (e.g., FastAPI, Flask app).
    """
    from fastapi.testclient import TestClient
    # from flask.testing import FlaskClient
    
    return TestClient(app)


@pytest.fixture
def authenticated_client(api_client, user_factory):
    """
    API client with authenticated user.
    
    Creates a test user and adds authentication headers.
    """
    user = user_factory.create()
    
    # Generate token (adjust based on your auth implementation)
    # token = create_access_token(user)
    token = "test-token-placeholder"
    
    api_client.headers["Authorization"] = f"Bearer {token}"
    api_client.user = user
    
    return api_client


# =============================================================================
# TIME FIXTURES
# =============================================================================

@pytest.fixture
def freeze_time():
    """
    Context manager for freezing time in tests.
    
    Usage:
        def test_expiry(freeze_time):
            with freeze_time("2024-01-15"):
                subscription = create_subscription()
            
            with freeze_time("2024-02-15"):
                assert subscription.is_expired()
    """
    from freezegun import freeze_time as ft
    return ft


@pytest.fixture
def fixed_now():
    """
    Fixed datetime for deterministic tests.
    
    Usage:
        def test_created_at(fixed_now, monkeypatch):
            monkeypatch.setattr("myapp.utils.datetime", Mock(utcnow=lambda: fixed_now))
            user = create_user()
            assert user.created_at == fixed_now
    """
    return datetime(2024, 1, 15, 10, 30, 0)


# =============================================================================
# FILE SYSTEM FIXTURES
# =============================================================================

@pytest.fixture
def temp_directory(tmp_path):
    """
    Temporary directory for file-related tests.
    
    Automatically cleaned up after test.
    """
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def sample_csv_file(temp_directory):
    """Sample CSV file for testing file processing."""
    csv_path = temp_directory / "sample.csv"
    csv_path.write_text("name,value,date\nitem1,100,2024-01-15\nitem2,200,2024-01-16\n")
    return csv_path


@pytest.fixture
def sample_json_file(temp_directory):
    """Sample JSON file for testing."""
    import json
    
    json_path = temp_directory / "sample.json"
    data = {"users": [{"id": 1, "name": "Test"}], "count": 1}
    json_path.write_text(json.dumps(data, indent=2))
    return json_path


# =============================================================================
# ASYNC FIXTURES
# =============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def async_mock():
    """Factory for creating async mocks."""
    def _create_async_mock(**kwargs):
        return AsyncMock(**kwargs)
    return _create_async_mock


# =============================================================================
# CLEANUP AND HELPERS
# =============================================================================

@pytest.fixture(autouse=True)
def reset_sequence_generators():
    """Reset any sequence generators between tests."""
    yield
    # Reset counters if you have any global sequence generators
    # SequenceGenerator.reset()


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear any caches between tests."""
    yield
    # Clear LRU caches, module-level caches, etc.
    # some_cached_function.cache_clear()


# =============================================================================
# MARKERS AND CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (use real dependencies)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full system)")
    config.addinivalue_line("markers", "slow: Slow tests (excluded from quick runs)")
    config.addinivalue_line("markers", "external: Tests requiring external services")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection based on markers and options.
    
    Skip slow/external tests unless explicitly requested.
    """
    if config.getoption("--run-slow", default=False):
        return
    
    skip_slow = pytest.mark.skip(reason="Slow test - use --run-slow to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--run-external",
        action="store_true",
        default=False,
        help="Run tests requiring external services"
    )
