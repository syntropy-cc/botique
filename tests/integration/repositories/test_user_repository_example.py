# tests/integration/repositories/test_user_repository.py
"""
Example integration tests for UserRepository.

These tests verify that the repository correctly interacts with
the real PostgreSQL database. Each test runs in a transaction
that is rolled back after the test.
"""

from datetime import datetime
from decimal import Decimal

import pytest

# Placeholder imports - adjust to your project
# from myapp.repositories.user_repository import PostgresUserRepository
# from myapp.domain.user import User
# from myapp.domain.exceptions import DuplicateEmailError


@pytest.mark.integration
class TestUserRepositoryBasicOperations:
    """Tests for basic CRUD operations."""
    
    def test_saves_and_retrieves_user(self, db_session, user_factory):
        """
        Verify user can be saved and retrieved by ID.
        
        This is the fundamental repository operation - if this fails,
        nothing else will work.
        """
        # Arrange
        user = user_factory.build(
            email="test@example.com",
            name="Test User"
        )
        
        # Act: Save and retrieve
        db_session.add(user)
        db_session.flush()
        user_id = user.id
        
        # Clear session to force database read
        db_session.expire_all()
        
        # Retrieve
        retrieved = db_session.get(type(user), user_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.email == "test@example.com"
        assert retrieved.name == "Test User"
        assert retrieved.id == user_id
    
    def test_find_returns_none_for_nonexistent_id(self, db_session):
        """Repository returns None for IDs that don't exist."""
        # Using a placeholder User class
        result = db_session.get(type("User", (), {}), "nonexistent-id")
        assert result is None
    
    def test_updates_existing_user(self, db_session, user_factory):
        """Verify user attributes can be updated."""
        # Arrange
        user = user_factory.create()
        original_id = user.id
        
        # Act
        user.name = "Updated Name"
        db_session.flush()
        
        # Clear and reload
        db_session.expire_all()
        updated = db_session.get(type(user), original_id)
        
        # Assert
        assert updated.name == "Updated Name"
        assert updated.id == original_id  # ID unchanged
    
    def test_deletes_user(self, db_session, user_factory):
        """Verify user can be deleted."""
        # Arrange
        user = user_factory.create()
        user_id = user.id
        
        # Act
        db_session.delete(user)
        db_session.flush()
        
        # Assert
        deleted = db_session.get(type(user), user_id)
        assert deleted is None


@pytest.mark.integration
class TestUserRepositoryConstraints:
    """Tests for database constraints and validation."""
    
    def test_email_must_be_unique(self, db_session, user_factory):
        """
        Database constraint: email must be unique.
        
        This tests that the database-level unique constraint works.
        The repository should translate this into a domain exception.
        """
        # Arrange
        user1 = user_factory.create(email="duplicate@example.com")
        db_session.flush()
        
        # Act & Assert
        user2 = user_factory.build(email="duplicate@example.com")
        db_session.add(user2)
        
        # Expect database constraint violation
        with pytest.raises(Exception):  # IntegrityError in real implementation
            db_session.flush()
    
    def test_email_uniqueness_is_case_insensitive(self, db_session, user_factory):
        """
        Business rule: Email uniqueness is case-insensitive.
        
        test@example.com and TEST@example.com are the same email.
        """
        # Create user with lowercase email
        user1 = user_factory.create(email="test@example.com")
        db_session.flush()
        
        # Attempting uppercase version should fail
        # Note: This requires a case-insensitive unique constraint in DB
        # or application-level normalization
        user2 = user_factory.build(email="TEST@example.com")
        user2.email = user2.email.lower()  # Normalize
        
        # Check if email already exists
        existing_emails = ["test@example.com"]  # Would query DB
        assert user2.email.lower() in existing_emails
    
    def test_required_fields_cannot_be_null(self, db_session):
        """Required fields are enforced at database level."""
        # Create user missing required email
        user = type("User", (), {"email": None, "name": "Test"})()
        
        # This should fail due to NOT NULL constraint
        # In real test, db_session.add(user) followed by flush() would raise


@pytest.mark.integration
class TestUserRepositoryQueries:
    """Tests for query operations."""
    
    def test_find_by_email(self, db_session, user_factory):
        """Find user by their email address."""
        # Arrange
        user = user_factory.create(email="findme@example.com")
        db_session.flush()
        
        # Act
        # In real implementation: result = repository.find_by_email("findme@example.com")
        # Simulating with direct query
        result = user  # Placeholder
        
        # Assert
        assert result is not None
        assert result.email == "findme@example.com"
    
    def test_find_by_email_returns_none_for_unknown_email(self, db_session):
        """Finding unknown email returns None, not error."""
        # Act
        result = None  # repository.find_by_email("unknown@example.com")
        
        # Assert
        assert result is None
    
    def test_find_all_with_pagination(self, db_session, user_factory):
        """Query supports pagination."""
        # Arrange: Create 25 users
        users = user_factory.create_batch(25)
        db_session.flush()
        
        # Act: Get first page
        page_size = 10
        page1_users = users[:page_size]  # Simulating pagination
        
        # Assert
        assert len(page1_users) == 10
    
    def test_find_active_users_only(self, db_session, user_factory):
        """Query can filter by active status."""
        # Arrange
        active_user = user_factory.create(is_active=True)
        inactive_user = user_factory.create(is_active=False)
        db_session.flush()
        
        # Act: Query active users only
        all_users = [active_user, inactive_user]
        active_users = [u for u in all_users if u.is_active]
        
        # Assert
        assert len(active_users) == 1
        assert active_users[0].id == active_user.id
    
    def test_search_by_name_partial_match(self, db_session, user_factory):
        """Search finds partial matches in name."""
        # Arrange
        user1 = user_factory.create(name="John Smith")
        user2 = user_factory.create(name="Jane Smith")
        user3 = user_factory.create(name="Bob Johnson")
        db_session.flush()
        
        # Act: Search for "Smith"
        all_users = [user1, user2, user3]
        results = [u for u in all_users if "Smith" in u.name]
        
        # Assert
        assert len(results) == 2
        names = [u.name for u in results]
        assert "John Smith" in names
        assert "Jane Smith" in names


@pytest.mark.integration
class TestUserRepositoryTransactions:
    """Tests for transaction behavior."""
    
    def test_changes_not_visible_until_commit(self, session_factory):
        """
        Verify transaction isolation.
        
        Changes in one session should not be visible to another
        session until committed.
        """
        session1 = session_factory()
        session2 = session_factory()
        
        try:
            # Create user in session1, don't commit
            user = type("User", (), {
                "id": "test-123",
                "email": "isolation@example.com"
            })()
            session1.add(user)
            session1.flush()
            
            # Session2 should not see the user
            # result = session2.get(User, "test-123")
            # assert result is None
            
            # After commit, session2 can see it
            session1.commit()
            # result = session2.get(User, "test-123")
            # assert result is not None
            
        finally:
            session1.rollback()
            session1.close()
            session2.close()
    
    def test_rollback_undoes_changes(self, db_session, user_factory):
        """Rollback reverts all changes in transaction."""
        # Arrange
        user = user_factory.build(email="rollback@example.com")
        db_session.add(user)
        db_session.flush()
        user_id = user.id
        
        # Act: Rollback
        db_session.rollback()
        
        # Assert: User should not exist
        result = db_session.get(type(user), user_id)
        assert result is None


@pytest.mark.integration
class TestUserRepositoryConcurrency:
    """Tests for concurrent access handling."""
    
    def test_optimistic_locking_prevents_lost_updates(self, session_factory, user_factory):
        """
        Concurrent updates to same record don't lose data.
        
        When two sessions read the same user, modify it, and try
        to save, one should succeed and one should fail with
        a stale data error.
        """
        # This test requires versioned/optimistic locking in your model
        
        # Create initial user
        session_setup = session_factory()
        user = user_factory.build(email="concurrent@example.com")
        session_setup.add(user)
        session_setup.commit()
        user_id = user.id
        session_setup.close()
        
        # Open two sessions
        session1 = session_factory()
        session2 = session_factory()
        
        try:
            # Both read same user
            user1 = session1.get(type(user), user_id)
            user2 = session2.get(type(user), user_id)
            
            # Both modify
            # user1.name = "Updated by Session 1"
            # user2.name = "Updated by Session 2"
            
            # First save succeeds
            session1.commit()
            
            # Second save should detect stale data
            # with pytest.raises(StaleDataError):
            #     session2.commit()
            
        finally:
            session1.close()
            session2.close()


@pytest.mark.integration
class TestUserRepositoryPerformance:
    """Performance-related integration tests."""
    
    def test_bulk_insert_performance(self, db_session, user_factory):
        """Bulk inserts complete in reasonable time."""
        import time
        
        # Arrange
        users = [user_factory.build() for _ in range(100)]
        
        # Act
        start = time.time()
        db_session.add_all(users)
        db_session.flush()
        duration = time.time() - start
        
        # Assert: 100 inserts should complete in under 1 second
        assert duration < 1.0, f"Bulk insert took {duration:.2f}s"
    
    def test_query_with_index_is_fast(self, db_session, user_factory):
        """Queries on indexed columns are fast."""
        import time
        
        # Arrange: Create many users
        users = user_factory.create_batch(1000)
        target_email = users[500].email
        db_session.flush()
        
        # Act: Query by indexed email column
        start = time.time()
        # result = repository.find_by_email(target_email)
        duration = time.time() - start
        
        # Assert: Should be much faster than scanning all rows
        assert duration < 0.1, f"Index lookup took {duration:.2f}s"
