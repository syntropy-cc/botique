"""
Test Artifact Storage.

Manages storage and retrieval of test artifacts (JSON files, images, outputs).
"""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.core.llm_log_db import db_connection, get_db_path


def get_test_results_dir() -> Path:
    """
    Get base directory for test results.
    
    Returns:
        Path to test results directory
    """
    root_dir = Path(__file__).resolve().parents[4]
    return root_dir / "tests" / "pipeline" / "test_results"


class TestArtifactStorage:
    """
    Manages storage and retrieval of test artifacts.
    
    Stores artifacts in organized directory structure and maintains
    metadata in database for efficient retrieval.
    """
    
    def __init__(
        self,
        test_run_id: str,
        base_dir: Optional[Path] = None,
        db_path: Optional[Path] = None,
    ):
        """
        Initialize artifact storage.
        
        Args:
            test_run_id: Unique test run identifier
            base_dir: Base directory for test results (uses default if None)
            db_path: Path to database (uses default if None)
        """
        self.test_run_id = test_run_id
        self.base_dir = base_dir or get_test_results_dir()
        self.db_path = db_path or get_db_path()
        
        # Create directory structure
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.run_dir = self.base_dir / "runs" / today / f"test_run_{test_run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create phase directories
        for phase in ["phase1", "phase2", "phase3", "phase4", "phase5"]:
            (self.run_dir / phase).mkdir(exist_ok=True)
        
        # Create slides directory for phase4
        (self.run_dir / "phase4" / "slides").mkdir(parents=True, exist_ok=True)
    
    def save_artifact(
        self,
        phase: str,
        artifact_name: str,
        data: Union[Dict[str, Any], list, str, bytes],
        artifact_type: Optional[str] = None,
    ) -> Path:
        """
        Save artifact to storage.
        
        Args:
            phase: Phase name (phase1, phase2, etc.)
            artifact_name: Name of artifact file (e.g., "ideas.json")
            data: Artifact data (dict/list for JSON, str for text, bytes for binary)
            artifact_type: Type of artifact (json, image, text) - auto-detected if None
            
        Returns:
            Path to saved artifact
        """
        phase_dir = self.run_dir / phase
        artifact_path = phase_dir / artifact_name
        
        # Determine artifact type
        if artifact_type is None:
            if artifact_name.endswith((".json", ".jsonl")):
                artifact_type = "json"
            elif artifact_name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                artifact_type = "image"
            else:
                artifact_type = "text"
        
        # Save artifact based on type
        if artifact_type == "json":
            if isinstance(data, (dict, list)):
                artifact_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                artifact_path.write_text(str(data), encoding="utf-8")
        elif artifact_type == "image":
            if isinstance(data, bytes):
                artifact_path.write_bytes(data)
            else:
                raise ValueError(f"Cannot save image artifact: data must be bytes, got {type(data)}")
        else:  # text
            if isinstance(data, str):
                artifact_path.write_text(data, encoding="utf-8")
            else:
                artifact_path.write_text(str(data), encoding="utf-8")
        
        # Store metadata in database
        artifact_id = str(uuid.uuid4())
        metadata = {
            "artifact_name": artifact_name,
            "artifact_type": artifact_type,
            "saved_at": datetime.utcnow().isoformat() + "Z",
        }
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO test_artifacts
                (artifact_id, test_run_id, phase_name, artifact_type, artifact_path, artifact_metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                artifact_id,
                self.test_run_id,
                phase,
                artifact_type,
                str(artifact_path.relative_to(self.base_dir)),
                json.dumps(metadata),
            ))
            conn.commit()
        
        return artifact_path
    
    def load_artifact(
        self,
        phase: str,
        artifact_name: str,
    ) -> Union[Dict[str, Any], list, str, bytes, None]:
        """
        Load artifact from storage.
        
        Args:
            phase: Phase name
            artifact_name: Name of artifact file
            
        Returns:
            Artifact data (dict/list for JSON, str for text, bytes for binary)
            or None if not found
        """
        artifact_path = self.run_dir / phase / artifact_name
        
        if not artifact_path.exists():
            return None
        
        # Determine type from extension
        if artifact_name.endswith((".json", ".jsonl")):
            content = artifact_path.read_text(encoding="utf-8")
            return json.loads(content)
        elif artifact_name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            return artifact_path.read_bytes()
        else:
            return artifact_path.read_text(encoding="utf-8")
    
    def has_artifact(self, phase: str, artifact_name: str) -> bool:
        """
        Check if artifact exists.
        
        Args:
            phase: Phase name
            artifact_name: Name of artifact file
            
        Returns:
            True if artifact exists, False otherwise
        """
        artifact_path = self.run_dir / phase / artifact_name
        return artifact_path.exists()
    
    def list_artifacts(self, phase: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all artifacts for this test run.
        
        Args:
            phase: Optional phase name to filter by
            
        Returns:
            List of artifact metadata dictionaries
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            if phase:
                cursor.execute("""
                    SELECT artifact_id, phase_name, artifact_type, artifact_path, artifact_metadata_json
                    FROM test_artifacts
                    WHERE test_run_id = ? AND phase_name = ?
                    ORDER BY created_at
                """, (self.test_run_id, phase))
            else:
                cursor.execute("""
                    SELECT artifact_id, phase_name, artifact_type, artifact_path, artifact_metadata_json
                    FROM test_artifacts
                    WHERE test_run_id = ?
                    ORDER BY phase_name, created_at
                """, (self.test_run_id,))
            
            artifacts = []
            for row in cursor.fetchall():
                artifact = {
                    "artifact_id": row["artifact_id"],
                    "phase_name": row["phase_name"],
                    "artifact_type": row["artifact_type"],
                    "artifact_path": row["artifact_path"],
                    "metadata": json.loads(row["artifact_metadata_json"]) if row["artifact_metadata_json"] else {},
                }
                artifacts.append(artifact)
            
            return artifacts
    
    def get_artifact_path(self, phase: str, artifact_name: str) -> Optional[Path]:
        """
        Get full path to artifact.
        
        Args:
            phase: Phase name
            artifact_name: Name of artifact file
            
        Returns:
            Full path to artifact or None if not found
        """
        artifact_path = self.run_dir / phase / artifact_name
        if artifact_path.exists():
            return artifact_path
        return None
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Save test run metadata.
        
        Args:
            metadata: Metadata dictionary
        """
        metadata_path = self.run_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
