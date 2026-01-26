"""
Unit tests for prompt registry.

Tests prompt versioning, registration, and retrieval.

Location: tests/tools/core/test_prompt_registry.py
"""

import hashlib
import tempfile
import unittest
from pathlib import Path

from src.core.prompt_registry import (
    _compute_template_hash,
    register_prompt,
    find_existing_prompt,
    get_prompt,
    get_latest_prompt,
    list_prompt_versions,
    get_prompt_by_key_and_version,
)
from src.core.llm_log_db import init_database, db_connection


class TestComputeTemplateHash(unittest.TestCase):
    """Test cases for template hash computation."""
    
    def test_compute_template_hash(self):
        """Test hash computation produces consistent results."""
        template = "Test prompt template"
        
        hash1 = _compute_template_hash(template)
        hash2 = _compute_template_hash(template)
        
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA256 produces 64 char hex string
    
    def test_compute_template_hash_different_inputs(self):
        """Test that different templates produce different hashes."""
        template1 = "First template"
        template2 = "Second template"
        
        hash1 = _compute_template_hash(template1)
        hash2 = _compute_template_hash(template2)
        
        self.assertNotEqual(hash1, hash2)


class TestPromptRegistry(unittest.TestCase):
    """Test cases for prompt registry functions."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        init_database(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db_path.exists():
            self.db_path.unlink()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_prompt_first_version(self):
        """Test first prompt registration creates v1."""
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Test template",
            description="Test description",
            db_path=self.db_path,
        )
        
        self.assertIsNotNone(prompt_id)
        self.assertEqual(version, "v1")
        
        # Verify in database
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row["prompt_key"], "test_prompt")
            self.assertEqual(row["version"], "v1")
            self.assertEqual(row["template"], "Test template")
    
    def test_register_prompt_new_version(self):
        """Test registering different template creates new version."""
        # Register first version
        prompt_id1, version1 = register_prompt(
            prompt_key="test_prompt",
            template="First template",
            db_path=self.db_path,
        )
        
        # Register second version with different template
        prompt_id2, version2 = register_prompt(
            prompt_key="test_prompt",
            template="Second template",
            db_path=self.db_path,
        )
        
        self.assertNotEqual(prompt_id1, prompt_id2)
        self.assertEqual(version1, "v1")
        self.assertEqual(version2, "v2")
    
    def test_register_prompt_duplicate_prevention(self):
        """Test that registering same template returns existing prompt."""
        # Register first time
        prompt_id1, version1 = register_prompt(
            prompt_key="test_prompt",
            template="Same template",
            db_path=self.db_path,
        )
        
        # Register same template again
        prompt_id2, version2 = register_prompt(
            prompt_key="test_prompt",
            template="Same template",
            db_path=self.db_path,
        )
        
        # Should return same prompt_id and version
        self.assertEqual(prompt_id1, prompt_id2)
        self.assertEqual(version1, version2)
        
        # Verify only one row in database
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM prompts WHERE prompt_key = ?", ("test_prompt",))
            count = cursor.fetchone()[0]
            
            self.assertEqual(count, 1)
    
    def test_register_prompt_normalization(self):
        """Test that trailing whitespace is normalized."""
        # Register with trailing whitespace
        prompt_id1, version1 = register_prompt(
            prompt_key="test_prompt",
            template="Template with spaces   \n\n",
            db_path=self.db_path,
        )
        
        # Register same template without trailing whitespace
        prompt_id2, version2 = register_prompt(
            prompt_key="test_prompt",
            template="Template with spaces",
            db_path=self.db_path,
        )
        
        # Should match (normalized)
        self.assertEqual(prompt_id1, prompt_id2)
    
    def test_register_prompt_metadata(self):
        """Test that metadata is stored correctly."""
        metadata = {"author": "test", "experiment": "exp1"}
        
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Test template",
            metadata=metadata,
            db_path=self.db_path,
        )
        
        # Retrieve and verify
        prompt = get_prompt(prompt_id, self.db_path)
        
        self.assertIsNotNone(prompt)
        self.assertIn("metadata", prompt)
        self.assertEqual(prompt["metadata"]["author"], "test")
        self.assertEqual(prompt["metadata"]["experiment"], "exp1")
    
    def test_find_existing_prompt(self):
        """Test finding existing prompt by template."""
        # Register prompt
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Find me template",
            db_path=self.db_path,
        )
        
        # Find it
        result = find_existing_prompt(
            prompt_key="test_prompt",
            template="Find me template",
            db_path=self.db_path,
        )
        
        self.assertIsNotNone(result)
        found_id, found_version = result
        self.assertEqual(found_id, prompt_id)
        self.assertEqual(found_version, version)
    
    def test_find_existing_prompt_not_found(self):
        """Test finding non-existent prompt returns None."""
        result = find_existing_prompt(
            prompt_key="nonexistent",
            template="Not found",
            db_path=self.db_path,
        )
        
        self.assertIsNone(result)
    
    def test_find_existing_prompt_hash_collision(self):
        """Test that hash collisions are handled correctly."""
        # Register a prompt
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Original template",
            db_path=self.db_path,
        )
        
        # Try to find with different template (should not find)
        result = find_existing_prompt(
            prompt_key="test_prompt",
            template="Different template",
            db_path=self.db_path,
        )
        
        self.assertIsNone(result)
    
    def test_get_prompt_by_id(self):
        """Test retrieving prompt by ID."""
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Retrieve me",
            description="Test description",
            db_path=self.db_path,
        )
        
        prompt = get_prompt(prompt_id, self.db_path)
        
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["id"], prompt_id)
        self.assertEqual(prompt["prompt_key"], "test_prompt")
        self.assertEqual(prompt["version"], version)
        self.assertEqual(prompt["template"], "Retrieve me")
        self.assertEqual(prompt["description"], "Test description")
    
    def test_get_prompt_by_id_not_found(self):
        """Test retrieving non-existent prompt returns None."""
        prompt = get_prompt("nonexistent_id", self.db_path)
        
        self.assertIsNone(prompt)
    
    def test_get_latest_prompt(self):
        """Test retrieving latest version of prompt."""
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
        
        prompt_id3, version3 = register_prompt(
            prompt_key="test_prompt",
            template="Version 3",
            db_path=self.db_path,
        )
        
        latest = get_latest_prompt("test_prompt", self.db_path)
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest["id"], prompt_id3)
        self.assertEqual(latest["version"], "v3")
        self.assertEqual(latest["template"], "Version 3")
    
    def test_get_latest_prompt_not_found(self):
        """Test retrieving latest of non-existent prompt returns None."""
        latest = get_latest_prompt("nonexistent", self.db_path)
        
        self.assertIsNone(latest)
    
    def test_list_prompt_versions(self):
        """Test listing all versions of a prompt."""
        # Register multiple versions
        register_prompt(
            prompt_key="test_prompt",
            template="Version 1",
            db_path=self.db_path,
        )
        
        register_prompt(
            prompt_key="test_prompt",
            template="Version 2",
            db_path=self.db_path,
        )
        
        versions = list_prompt_versions("test_prompt", self.db_path)
        
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]["version"], "v1")
        self.assertEqual(versions[1]["version"], "v2")
        
        # Should be sorted by created_at
        self.assertLess(versions[0]["created_at"], versions[1]["created_at"])
    
    def test_list_prompt_versions_empty(self):
        """Test listing versions of non-existent prompt returns empty list."""
        versions = list_prompt_versions("nonexistent", self.db_path)
        
        self.assertEqual(len(versions), 0)
    
    def test_get_prompt_by_key_and_version(self):
        """Test retrieving specific version by key and version."""
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Specific version",
            db_path=self.db_path,
        )
        
        prompt = get_prompt_by_key_and_version("test_prompt", "v1", self.db_path)
        
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["id"], prompt_id)
        self.assertEqual(prompt["version"], "v1")
    
    def test_get_prompt_by_key_and_version_not_found(self):
        """Test retrieving non-existent version returns None."""
        prompt = get_prompt_by_key_and_version("nonexistent", "v1", self.db_path)
        
        self.assertIsNone(prompt)
    
    def test_prompt_metadata_storage(self):
        """Test that metadata JSON is stored and retrieved correctly."""
        metadata = {
            "author": "test_author",
            "git_commit": "abc123",
            "experiment": "test_experiment",
        }
        
        prompt_id, version = register_prompt(
            prompt_key="test_prompt",
            template="Test template",
            metadata=metadata,
            db_path=self.db_path,
        )
        
        prompt = get_prompt(prompt_id, self.db_path)
        
        self.assertIsNotNone(prompt)
        self.assertIn("metadata", prompt)
        self.assertEqual(prompt["metadata"]["author"], "test_author")
        self.assertEqual(prompt["metadata"]["git_commit"], "abc123")


if __name__ == "__main__":
    unittest.main()
