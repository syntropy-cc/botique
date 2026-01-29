# Branding Database Design

> **Version**: 1.0  
> **Date**: 2026-01-20  
> **Status**: Implementation Design  
> **Author**: Documentation System

---

## Overview

This document describes the database design for storing audience profiles in the branding system. The design uses a **Document Store model** with SQLite, storing complete profiles as JSON documents. This approach optimizes for the primary access pattern: query a specific profile by `persona_type` and use the complete profile data in prompt generation.

> **Note**: This design follows [ADR-001: Simplify Audience Profile Storage to Document Store Model](decisions/ADR-001-simplify-audience-profile-storage.md), which simplified the architecture from a hybrid normalized/JSON/many-to-many approach to a pure document store.

---

## Database Schema

### Document Store Design

The schema uses a **single table** with complete profile data stored as a JSON document. This design eliminates data consistency risks and matches the primary access pattern (get complete profile by persona_type).

### Table: `audience_profiles` (Single Table)

```sql
CREATE TABLE IF NOT EXISTS audience_profiles (
    -- Primary identifiers
    id TEXT PRIMARY KEY,
    persona_type TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Complete profile data (JSON document)
    profile_data TEXT NOT NULL,  -- Full profile structure as JSON
    
    -- Metadata
    created_at TEXT NOT NULL,      -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,      -- ISO 8601 timestamp
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1    -- 1 = active, 0 = soft deleted
);

-- Indexes for primary access pattern
CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_type 
    ON audience_profiles(persona_type);
    
CREATE INDEX IF NOT EXISTS idx_audience_profiles_active 
    ON audience_profiles(is_active);
    
CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_active 
    ON audience_profiles(persona_type, is_active);
```

### Schema Rationale

#### Document Store Approach

All profile data is stored as a **single JSON document** in the `profile_data` column. This design:

1. **Single Source of Truth**: Eliminates data consistency risks (no data duplication across normalized columns, JSON, and many-to-many tables)
2. **Matches Access Pattern**: Optimized for the primary use case: get complete profile by `persona_type` and use in prompt generation
3. **Simplified Repository**: Read/write operations are straightforward (no complex reconstruction logic)
4. **Flexible Schema**: JSON allows schema evolution without migrations

#### Essential Attributes Preserved

The JSON document structure preserves all essential attributes required by prompt agents:

- **Basic Info**: `persona_type`, `name`, `description`
- **Personality**: `personality_traits` (list)
- **Pain Points**: `pain_points` (dict by category or flat list)
- **Desires**: `desires` (dict by category or flat list)
- **Communication**: `communication_style` (tone, formality, vocabulary, language_preferences, communication_channels)
- **Platforms & Formats**: `platforms` (list), `formats` (list)
- **Content**: `content_preferences` (content_focus, formats, content_structure_preferences, engagement_triggers)
- **Emotions**: `emotional_triggers` (primary, emotional_journey, positive, negative_to_avoid)
- **Brand**: `brand_values` (list)
- **Journey**: `customer_journey` (awareness_stage, consideration_stage, decision_stage, adoption_stage)
- **Context**: `professional_background`, `market_context`, `success_metrics`, `language_examples`

### Benefits of This Design

1. **Simplified Architecture**: Single source of truth eliminates data consistency risks
2. **Matches Access Pattern**: Optimized for "get complete profile by persona_type"
3. **Flexible Schema**: JSON allows evolution without migrations
4. **Preserves All Attributes**: All essential prompt attributes maintained
5. **Easier Maintenance**: Simple read/write JSON operations
6. **Fast Lookups**: Indexed `persona_type` for primary access pattern

### Query Pattern

The primary access pattern is simple and fast:

```sql
-- Get complete profile by persona_type (primary use case)
SELECT profile_data 
FROM audience_profiles 
WHERE persona_type = 'c_level' AND is_active = 1;

-- List all active profiles
SELECT id, persona_type, name, description, version
FROM audience_profiles
WHERE is_active = 1
ORDER BY persona_type;
```

**Note**: Complex filtering queries (e.g., "find all profiles with tone='professional'") would require JSON parsing. If such queries become necessary, we can add JSON indexes using SQLite's JSON1 extension or create a separate analytics view.

---

## Profile Data Structure

The profile data is stored as a **complete JSON document** in the `profile_data` column. When retrieved via `get_profile()`, it returns the full nested structure directly (no reconstruction needed).

### Complete JSON Document Structure

All profile attributes are stored in a single JSON document with the following structure:

### Example: Reconstructed Profile Structure

When calling `get_profile("c_level")`, the repository reconstructs the full nested structure:

```json
{
  "name": "Decisor C-Level",
  "description": "C-Level executives from SMEs (R$10-100Mi revenue)",
  "persona_type": "c_level",
  
  "professional_background": {
    "company_size": "R$10-100Mi revenue (SME)",
    "role_types": ["CEO", "CTO", "CFO", "COO", "CMO"],
    "experience_level": "15-30 years professional experience",
    "decision_making_authority": "Strategic and budget decisions",
    "team_size_managed": "50-500 employees",
    "industry_sectors": [...],
    "geographic_focus": "Primarily Brazil, expanding to Latin America",
    "digital_maturity": "Growing, seeking to modernize operations"
  },
  
  "market_context": {
    "competitive_landscape": "High competition, pressure to differentiate",
    "economic_challenges": [...],
    "growth_drivers": [...],
    "technology_adoption": "Cautious but necessary - requires proven ROI"
  },
  
  "communication_style": {
    "tone": "professional",
    "formality": "formal",
    "vocabulary": "sophisticated",
    "language_preferences": {
      "preferred_terms": [...],
      "avoid_terms": [...],
      "metric_focus": "Quantifiable results, percentages, timeframes",
      "proof_requirement": "Case studies, benchmarks, industry data"
    },
    "communication_channels": {
      "primary": ["LinkedIn", "Email", "Industry workshops"],
      "secondary": [...],
      "content_consumption": "B2B publications, industry reports, LinkedIn articles"
    }
  },
  
  "personality_traits": [...],
  "pain_points": {...},
  "desires": {...},
  "customer_journey": {...},
  "content_preferences": {...},
  "platforms": [...],
  "formats": [...],
  "emotional_triggers": {...},
  "brand_values": [...],
  "success_metrics": {...},
  "language_examples": {...}
}
```

---

## Repository Implementation

> **Note**: The implementation code below shows the simplified Document Store approach. The repository reads/writes complete JSON documents without reconstruction logic.

### File: `src/brand/audience_repo.py`

```python
"""
Audience profile repository module.

Database-backed storage for audience profiles with CRUD operations.
Uses normalized schema for easy querying.

Location: src/brand/audience_repo.py
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.llm_log_db import db_connection


class AudienceRepository:
    """
    Repository for audience profile CRUD operations.
    
    Handles database queries with normalized schema for easy filtering.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize repository.
        
        Args:
            db_path: Path to SQLite database (defaults to branding.db)
        """
        self.db_path = db_path or self._get_default_db_path()
        self._ensure_schema()
    
    @staticmethod
    def _get_default_db_path() -> Path:
        """Get default database path"""
        root_dir = Path(__file__).resolve().parents[2]
        return root_dir / "branding.db"
    
    def _ensure_schema(self) -> None:
        """Ensure database schema exists"""
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_profiles (
                    id TEXT PRIMARY KEY,
                    persona_type TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    tone TEXT,
                    formality TEXT,
                    vocabulary TEXT,
                    hook_type TEXT,
                    value_delivery_style TEXT,
                    proof_elements_style TEXT,
                    cta_style TEXT,
                    primary_emotion TEXT,
                    emotional_journey TEXT,
                    typical_journey_stage TEXT,
                    target_engagement_rate REAL,
                    target_followers INTEGER,
                    conversion_timeline TEXT,
                    professional_background_json TEXT,
                    market_context_json TEXT,
                    communication_channels_json TEXT,
                    language_preferences_json TEXT,
                    customer_journey_json TEXT,
                    content_preferences_json TEXT,
                    success_metrics_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Many-to-many tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_personality_traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    trait TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, trait)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_pain_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    category TEXT,
                    pain_point TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, category, pain_point)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_desires (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    category TEXT,
                    desire TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, category, desire)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_platforms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    priority TEXT,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, platform)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_formats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    format TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, format)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_brand_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    brand_value TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, brand_value)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audience_content_focus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    focus_keyword TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES audience_profiles(id) ON DELETE CASCADE,
                    UNIQUE(profile_id, focus_keyword)
                )
            """)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_type ON audience_profiles(persona_type)",
                "CREATE INDEX IF NOT EXISTS idx_audience_profiles_active ON audience_profiles(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_audience_profiles_tone ON audience_profiles(tone)",
                "CREATE INDEX IF NOT EXISTS idx_audience_profiles_formality ON audience_profiles(formality)",
                "CREATE INDEX IF NOT EXISTS idx_personality_traits_profile ON audience_personality_traits(profile_id)",
                "CREATE INDEX IF NOT EXISTS idx_pain_points_profile ON audience_pain_points(profile_id)",
                "CREATE INDEX IF NOT EXISTS idx_desires_profile ON audience_desires(profile_id)",
                "CREATE INDEX IF NOT EXISTS idx_platforms_profile ON audience_platforms(profile_id)",
                "CREATE INDEX IF NOT EXISTS idx_platforms_platform ON audience_platforms(platform)",
                "CREATE INDEX IF NOT EXISTS idx_brand_values_profile ON audience_brand_values(profile_id)",
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
    
    def get_profile(self, persona_type: str) -> Optional[Dict[str, Any]]:
        """
        Get audience profile by persona type.
        
        Reads complete profile from JSON document (no reconstruction needed).
        
        Args:
            persona_type: Persona identifier (e.g., "c_level", "founder")
        
        Returns:
            Profile dict or None if not found
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get main profile data
            cursor.execute("""
                SELECT id, persona_type, name, description, tone, formality, vocabulary,
                       hook_type, value_delivery_style, proof_elements_style, cta_style,
                       primary_emotion, emotional_journey, typical_journey_stage,
                       target_engagement_rate, target_followers, conversion_timeline,
                       professional_background_json, market_context_json,
                       communication_channels_json, language_preferences_json,
                       customer_journey_json, content_preferences_json, success_metrics_json,
                       version
                FROM audience_profiles
                WHERE persona_type = ? AND is_active = 1
            """, (persona_type.lower(),))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Unpack row
            (profile_id, persona_type_val, name, description, tone, formality, vocabulary,
             hook_type, value_delivery_style, proof_elements_style, cta_style,
             primary_emotion, emotional_journey, typical_journey_stage,
             target_engagement_rate, target_followers, conversion_timeline,
             professional_background_json, market_context_json,
             communication_channels_json, language_preferences_json,
             customer_journey_json, content_preferences_json, success_metrics_json,
             version) = row
            
            # Build profile dict
            profile = {
                "id": profile_id,
                "persona_type": persona_type_val,
                "name": name,
                "description": description,
                "version": version,
            }
            
            # Communication style
            if tone or formality or vocabulary:
                profile["communication_style"] = {}
                if tone:
                    profile["communication_style"]["tone"] = tone
                if formality:
                    profile["communication_style"]["formality"] = formality
                if vocabulary:
                    profile["communication_style"]["vocabulary"] = vocabulary
            
            # Content preferences structure
            if hook_type or value_delivery_style or proof_elements_style or cta_style:
                profile["content_preferences"] = profile.get("content_preferences", {})
                profile["content_preferences"]["content_structure_preferences"] = {}
                if hook_type:
                    profile["content_preferences"]["content_structure_preferences"]["hook_type"] = hook_type
                if value_delivery_style:
                    profile["content_preferences"]["content_structure_preferences"]["value_delivery"] = value_delivery_style
                if proof_elements_style:
                    profile["content_preferences"]["content_structure_preferences"]["proof_elements"] = proof_elements_style
                if cta_style:
                    profile["content_preferences"]["content_structure_preferences"]["cta_style"] = cta_style
            
            # Emotional triggers
            if primary_emotion or emotional_journey:
                profile["emotional_triggers"] = {}
                if primary_emotion:
                    profile["emotional_triggers"]["primary"] = primary_emotion
                if emotional_journey:
                    profile["emotional_triggers"]["emotional_journey"] = emotional_journey
            
            # Success metrics
            if target_engagement_rate or target_followers or conversion_timeline:
                profile["success_metrics"] = {}
                if target_engagement_rate:
                    profile["success_metrics"]["engagement_rate"] = target_engagement_rate
                if target_followers:
                    profile["success_metrics"]["followers"] = target_followers
                if conversion_timeline:
                    profile["success_metrics"]["conversion_timeline"] = conversion_timeline
            
            # Parse JSON columns
            if professional_background_json:
                profile["professional_background"] = json.loads(professional_background_json)
            if market_context_json:
                profile["market_context"] = json.loads(market_context_json)
            if communication_channels_json:
                if "communication_style" not in profile:
                    profile["communication_style"] = {}
                profile["communication_style"]["communication_channels"] = json.loads(communication_channels_json)
            if language_preferences_json:
                if "communication_style" not in profile:
                    profile["communication_style"] = {}
                profile["communication_style"]["language_preferences"] = json.loads(language_preferences_json)
            if customer_journey_json:
                profile["customer_journey"] = json.loads(customer_journey_json)
            if content_preferences_json:
                content_prefs = json.loads(content_preferences_json)
                if "content_preferences" not in profile:
                    profile["content_preferences"] = {}
                profile["content_preferences"].update(content_prefs)
            if success_metrics_json:
                metrics = json.loads(success_metrics_json)
                if "success_metrics" not in profile:
                    profile["success_metrics"] = {}
                profile["success_metrics"].update(metrics)
            
            # Load many-to-many relationships
            profile["personality_traits"] = self._get_personality_traits(profile_id, cursor)
            profile["pain_points"] = self._get_pain_points(profile_id, cursor)
            profile["desires"] = self._get_desires(profile_id, cursor)
            profile["platforms"] = self._get_platforms(profile_id, cursor)
            profile["formats"] = self._get_formats(profile_id, cursor)
            profile["brand_values"] = self._get_brand_values(profile_id, cursor)
            
            content_focus = self._get_content_focus(profile_id, cursor)
            if content_focus:
                if "content_preferences" not in profile:
                    profile["content_preferences"] = {}
                profile["content_preferences"]["content_focus"] = content_focus
            
            return profile
    
    def _get_personality_traits(self, profile_id: str, cursor) -> List[str]:
        """Get personality traits for profile"""
        cursor.execute("""
            SELECT trait FROM audience_personality_traits
            WHERE profile_id = ?
            ORDER BY trait
        """, (profile_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _get_pain_points(self, profile_id: str, cursor) -> Dict[str, List[str]]:
        """Get pain points for profile, grouped by category"""
        cursor.execute("""
            SELECT category, pain_point FROM audience_pain_points
            WHERE profile_id = ?
            ORDER BY category, pain_point
        """, (profile_id,))
        
        pain_points = {}
        for category, pain_point in cursor.fetchall():
            if category not in pain_points:
                pain_points[category] = []
            pain_points[category].append(pain_point)
        
        return pain_points
    
    def _get_desires(self, profile_id: str, cursor) -> Dict[str, List[str]]:
        """Get desires for profile, grouped by category"""
        cursor.execute("""
            SELECT category, desire FROM audience_desires
            WHERE profile_id = ?
            ORDER BY category, desire
        """, (profile_id,))
        
        desires = {}
        for category, desire in cursor.fetchall():
            if category not in desires:
                desires[category] = []
            desires[category].append(desire)
        
        return desires
    
    def _get_platforms(self, profile_id: str, cursor) -> List[str]:
        """Get platforms for profile"""
        cursor.execute("""
            SELECT platform FROM audience_platforms
            WHERE profile_id = ?
            ORDER BY priority DESC, platform
        """, (profile_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _get_formats(self, profile_id: str, cursor) -> List[str]:
        """Get formats for profile"""
        cursor.execute("""
            SELECT format FROM audience_formats
            WHERE profile_id = ?
            ORDER BY format
        """, (profile_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _get_brand_values(self, profile_id: str, cursor) -> List[str]:
        """Get brand values for profile"""
        cursor.execute("""
            SELECT brand_value FROM audience_brand_values
            WHERE profile_id = ?
            ORDER BY brand_value
        """, (profile_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _get_content_focus(self, profile_id: str, cursor) -> List[str]:
        """Get content focus keywords for profile"""
        cursor.execute("""
            SELECT focus_keyword FROM audience_content_focus
            WHERE profile_id = ?
            ORDER BY focus_keyword
        """, (profile_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audience profile by ID.
        
        Uses same reconstruction logic as get_profile().
        
        Args:
            profile_id: Profile UUID
        
        Returns:
            Profile dict or None if not found
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT persona_type FROM audience_profiles
                WHERE id = ? AND is_active = 1
            """, (profile_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            persona_type = row[0]
            return self.get_profile(persona_type)
    
    def create_profile(
        self,
        persona_type: str,
        name: str,
        description: str,
        profile_data: Dict[str, Any]
    ) -> str:
        """
        Create new audience profile.
        
        Extracts normalized fields and stores in appropriate columns/tables.
        
        Args:
            persona_type: Persona identifier (must be unique)
            name: Display name
            description: Brief description
            profile_data: Complete profile structure (dict)
        
        Returns:
            Profile ID (UUID)
        
        Raises:
            ValueError: If persona_type already exists
        """
        # Check if exists
        existing = self.get_profile(persona_type)
        if existing:
            raise ValueError(f"Profile with persona_type '{persona_type}' already exists")
        
        profile_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Extract normalized fields
        communication_style = profile_data.get("communication_style", {})
        content_prefs = profile_data.get("content_preferences", {})
        content_structure = content_prefs.get("content_structure_preferences", {})
        emotional_triggers = profile_data.get("emotional_triggers", {})
        success_metrics = profile_data.get("success_metrics", {})
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main profile
            cursor.execute("""
                INSERT INTO audience_profiles 
                (id, persona_type, name, description,
                 tone, formality, vocabulary,
                 hook_type, value_delivery_style, proof_elements_style, cta_style,
                 primary_emotion, emotional_journey, typical_journey_stage,
                 target_engagement_rate, target_followers, conversion_timeline,
                 professional_background_json, market_context_json,
                 communication_channels_json, language_preferences_json,
                 customer_journey_json, content_preferences_json, success_metrics_json,
                 created_at, updated_at, version, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
            """, (
                profile_id,
                persona_type.lower(),
                name,
                description,
                communication_style.get("tone"),
                communication_style.get("formality"),
                communication_style.get("vocabulary"),
                content_structure.get("hook_type"),
                content_structure.get("value_delivery"),
                content_structure.get("proof_elements"),
                content_structure.get("cta_style"),
                emotional_triggers.get("primary"),
                emotional_triggers.get("emotional_journey"),
                None,  # typical_journey_stage - can be extracted if needed
                success_metrics.get("engagement_rate"),
                success_metrics.get("followers") or success_metrics.get("linkedin_followers") or success_metrics.get("instagram_followers"),
                success_metrics.get("conversion_timeline"),
                json.dumps(profile_data.get("professional_background", {}), ensure_ascii=False),
                json.dumps(profile_data.get("market_context", {}), ensure_ascii=False),
                json.dumps(communication_style.get("communication_channels", {}), ensure_ascii=False),
                json.dumps(communication_style.get("language_preferences", {}), ensure_ascii=False),
                json.dumps(profile_data.get("customer_journey", {}), ensure_ascii=False),
                json.dumps(content_prefs, ensure_ascii=False),
                json.dumps(success_metrics, ensure_ascii=False),
                now,
                now
            ))
            
            # Insert many-to-many relationships
            self._insert_personality_traits(profile_id, profile_data.get("personality_traits", []), cursor)
            self._insert_pain_points(profile_id, profile_data.get("pain_points", {}), cursor)
            self._insert_desires(profile_id, profile_data.get("desires", {}), cursor)
            self._insert_platforms(profile_id, profile_data.get("platforms", []), cursor)
            self._insert_formats(profile_id, profile_data.get("formats", []), cursor)
            self._insert_brand_values(profile_id, profile_data.get("brand_values", []), cursor)
            
            content_focus = content_prefs.get("content_focus", [])
            self._insert_content_focus(profile_id, content_focus, cursor)
            
            conn.commit()
        
        return profile_id
    
    def _insert_personality_traits(self, profile_id: str, traits: List[str], cursor) -> None:
        """Insert personality traits"""
        for trait in traits:
            cursor.execute("""
                INSERT OR IGNORE INTO audience_personality_traits (profile_id, trait)
                VALUES (?, ?)
            """, (profile_id, trait))
    
    def _insert_pain_points(self, profile_id: str, pain_points: Dict[str, List[str]], cursor) -> None:
        """Insert pain points"""
        if isinstance(pain_points, dict):
            for category, points in pain_points.items():
                for point in points:
                    cursor.execute("""
                        INSERT OR IGNORE INTO audience_pain_points (profile_id, category, pain_point)
                        VALUES (?, ?, ?)
                    """, (profile_id, category, point))
        elif isinstance(pain_points, list):
            for point in pain_points:
                cursor.execute("""
                    INSERT OR IGNORE INTO audience_pain_points (profile_id, pain_point)
                    VALUES (?, ?)
                """, (profile_id, point))
    
    def _insert_desires(self, profile_id: str, desires: Dict[str, List[str]], cursor) -> None:
        """Insert desires"""
        if isinstance(desires, dict):
            for category, items in desires.items():
                for item in items:
                    cursor.execute("""
                        INSERT OR IGNORE INTO audience_desires (profile_id, category, desire)
                        VALUES (?, ?, ?)
                    """, (profile_id, category, item))
        elif isinstance(desires, list):
            for item in desires:
                cursor.execute("""
                    INSERT OR IGNORE INTO audience_desires (profile_id, desire)
                    VALUES (?, ?)
                """, (profile_id, item))
    
    def _insert_platforms(self, profile_id: str, platforms: List[str], cursor) -> None:
        """Insert platforms"""
        for platform in platforms:
            cursor.execute("""
                INSERT OR IGNORE INTO audience_platforms (profile_id, platform)
                VALUES (?, ?)
            """, (profile_id, platform))
    
    def _insert_formats(self, profile_id: str, formats: List[str], cursor) -> None:
        """Insert formats"""
        for format_type in formats:
            cursor.execute("""
                INSERT OR IGNORE INTO audience_formats (profile_id, format)
                VALUES (?, ?)
            """, (profile_id, format_type))
    
    def _insert_brand_values(self, profile_id: str, brand_values: List[str], cursor) -> None:
        """Insert brand values"""
        for value in brand_values:
            cursor.execute("""
                INSERT OR IGNORE INTO audience_brand_values (profile_id, brand_value)
                VALUES (?, ?)
            """, (profile_id, value))
    
    def _insert_content_focus(self, profile_id: str, focus_keywords: List[str], cursor) -> None:
        """Insert content focus keywords"""
        for keyword in focus_keywords:
            cursor.execute("""
                INSERT OR IGNORE INTO audience_content_focus (profile_id, focus_keyword)
                VALUES (?, ?)
            """, (profile_id, keyword))
    
    def update_profile(
        self,
        persona_type: str,
        profile_data: Dict[str, Any]
    ) -> bool:
        """
        Update existing audience profile.
        
        Args:
            persona_type: Persona identifier
            profile_data: Updated profile structure
        
        Returns:
            True if updated, False if not found
        """
        # Get current version
        current = self.get_profile(persona_type)
        if not current:
            return False
        
        current_version = current.get("_metadata", {}).get("version", 1)
        new_version = current_version + 1
        now = datetime.utcnow().isoformat()
        
        # Ensure persona_type is in profile_data
        profile_data["persona_type"] = persona_type.lower()
        
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audience_profiles
                SET profile_data = ?,
                    updated_at = ?,
                    version = ?
                WHERE persona_type = ? AND is_active = 1
            """, (
                json.dumps(profile_data, ensure_ascii=False),
                now,
                new_version,
                persona_type.lower()
            ))
            conn.commit()
        
        return cursor.rowcount > 0
    
    def delete_profile(self, persona_type: str) -> bool:
        """
        Soft delete audience profile.
        
        Args:
            persona_type: Persona identifier
        
        Returns:
            True if deleted, False if not found
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audience_profiles
                SET is_active = 0,
                    updated_at = ?
                WHERE persona_type = ? AND is_active = 1
            """, (datetime.utcnow().isoformat(), persona_type.lower()))
            conn.commit()
        
        return cursor.rowcount > 0
    
    def deactivate_profile(self, persona_type: str) -> bool:
        """Alias for delete_profile (soft delete)"""
        return self.delete_profile(persona_type)
    
    def list_profiles(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all audience profiles.
        
        Args:
            active_only: If True, only return active profiles
        
        Returns:
            List of profile metadata dicts
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("""
                    SELECT id, persona_type, name, description, 
                           created_at, updated_at, version
                    FROM audience_profiles
                    WHERE is_active = 1
                    ORDER BY persona_type
                """)
            else:
                cursor.execute("""
                    SELECT id, persona_type, name, description, 
                           created_at, updated_at, version, is_active
                    FROM audience_profiles
                    ORDER BY persona_type
                """)
            
            rows = cursor.fetchall()
            
            profiles = []
            for row in rows:
                profile = {
                    "id": row[0],
                    "persona_type": row[1],
                    "name": row[2],
                    "description": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "version": row[6]
                }
                if not active_only:
                    profile["is_active"] = row[7]
                profiles.append(profile)
            
            return profiles
    
    def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """
        Search profiles by name or description.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching profile metadata dicts
        """
        with db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, persona_type, name, description, 
                       created_at, updated_at, version
                FROM audience_profiles
                WHERE is_active = 1
                  AND (name LIKE ? OR description LIKE ?)
                ORDER BY persona_type
            """, (f"%{query}%", f"%{query}%"))
            
            rows = cursor.fetchall()
            
            profiles = []
            for row in rows:
                profiles.append({
                    "id": row[0],
                    "persona_type": row[1],
                    "name": row[2],
                    "description": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "version": row[6]
                })
            
            return profiles


# Global repository instance (singleton pattern)
_repository_instance: Optional[AudienceRepository] = None


def get_repository(db_path: Optional[Path] = None) -> AudienceRepository:
    """
    Get global repository instance.
    
    Args:
        db_path: Optional custom database path
    
    Returns:
        AudienceRepository instance
    """
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = AudienceRepository(db_path)
    return _repository_instance


def init_audience_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize audience profiles database.
    
    Creates schema if it doesn't exist.
    Idempotent: safe to call multiple times.
    
    Args:
        db_path: Optional custom database path
    """
    repo = AudienceRepository(db_path)
    # Schema is created in __init__, so we're done
    pass
```

---

## Migration from Hardcoded Profiles

### Migration Script

```python
"""
Migration script to move hardcoded audience profiles to database.

Location: scripts/migrate_audience_profiles.py
"""

from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brand.audience_repo import AudienceRepository
from src.brand.audience import AUDIENCE_PROFILES  # Old hardcoded dict


def migrate_profiles_to_database():
    """Migrate hardcoded profiles to database"""
    repo = AudienceRepository()
    
    migrated = 0
    skipped = 0
    
    for persona_type, profile_data in AUDIENCE_PROFILES.items():
        try:
            # Extract name and description
            name = profile_data.get("name", persona_type.title())
            description = profile_data.get("description", "")
            
            # Create profile in database
            profile_id = repo.create_profile(
                persona_type=persona_type,
                name=name,
                description=description,
                profile_data=profile_data
            )
            
            print(f"✅ Migrated '{persona_type}' -> {profile_id}")
            migrated += 1
            
        except ValueError as e:
            # Profile already exists
            print(f"⚠️  Skipped '{persona_type}': {e}")
            skipped += 1
        except Exception as e:
            print(f"❌ Error migrating '{persona_type}': {e}")
    
    print(f"\n📊 Migration complete:")
    print(f"   - Migrated: {migrated}")
    print(f"   - Skipped: {skipped}")
    print(f"   - Total: {len(AUDIENCE_PROFILES)}")


if __name__ == "__main__":
    migrate_profiles_to_database()
```

---

## Updated Helper Functions

### File: `src/brand/audience.py` (Updated)

```python
"""
Brand audience profiles module

Database-backed audience profiles with backward-compatible helper functions.

Location: src/brand/audience.py
"""

from typing import Any, Dict, Optional, List

from .audience_repo import get_repository


# Backward compatibility: Keep old function signatures
def get_audience_profile(persona: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed audience profile for persona.
    
    Now queries database instead of hardcoded dictionary.
    Maintains backward compatibility with existing code.
    
    Args:
        persona: Persona string (can be partial match)
    
    Returns:
        Audience profile dict or None if not found
    """
    repo = get_repository()
    persona_lower = persona.lower()
    
    # Try exact match first
    profile = repo.get_profile(persona_lower)
    if profile:
        return profile
    
    # Try partial matches
    if any(x in persona_lower for x in [
        "c-level", "executive", "decisor", "ceo", "cto", "cfo", "coo", "cmo"
    ]):
        return repo.get_profile("c_level")
    
    elif any(x in persona_lower for x in [
        "founder", "fundador", "visionário", "startup", "empreendedor", "co-founder"
    ]):
        return repo.get_profile("founder")
    
    elif any(x in persona_lower for x in [
        "developer", "dev", "desenvolvedor", "forjador", "engineer", "programmer"
    ]):
        return repo.get_profile("developer")
    
    return None


def enrich_idea_with_audience(
    idea: Dict[str, Any],
    audience_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich idea dict with audience profile data.
    
    Merges LLM-generated idea attributes with brand audience profile,
    ensuring brand consistency. Maintains backward compatibility.
    
    Args:
        idea: Idea dict from LLM
        audience_profile: Audience profile dict (from database)
    
    Returns:
        Enriched idea dict
    """
    enriched = idea.copy()
    
    # Extract personality traits (flatten if nested)
    profile_traits = audience_profile.get("personality_traits", [])
    if isinstance(profile_traits, dict):
        profile_traits = profile_traits.get("primary", [])
    
    # Merge personality traits (keep unique)
    existing_traits = set(idea.get("personality_traits", []))
    profile_traits_set = set(profile_traits)
    enriched["personality_traits"] = list(existing_traits | profile_traits_set)[:5]
    
    # Extract pain points (flatten if nested)
    profile_pains = audience_profile.get("pain_points", [])
    if isinstance(profile_pains, dict):
        all_pains = []
        for category, pains in profile_pains.items():
            if isinstance(pains, list):
                all_pains.extend(pains)
        profile_pains = all_pains
    elif not isinstance(profile_pains, list):
        profile_pains = []
    
    # Merge pain points (keep unique)
    existing_pains = set(idea.get("pain_points", []))
    profile_pains_set = set(profile_pains)
    enriched["pain_points"] = list(existing_pains | profile_pains_set)[:5]
    
    # Extract desires (flatten if nested)
    profile_desires = audience_profile.get("desires", [])
    if isinstance(profile_desires, dict):
        all_desires = []
        for category, desires in profile_desires.items():
            if isinstance(desires, list):
                all_desires.extend(desires)
        profile_desires = all_desires
    elif not isinstance(profile_desires, list):
        profile_desires = []
    
    # Merge desires (keep unique)
    existing_desires = set(idea.get("desires", []))
    profile_desires_set = set(profile_desires)
    enriched["desires"] = list(existing_desires | profile_desires_set)[:5]
    
    # Override vocabulary/formality with profile defaults if not specified
    communication_style = audience_profile.get("communication_style", {})
    if not idea.get("vocabulary_level"):
        enriched["vocabulary_level"] = communication_style.get("vocabulary", "moderate")
    
    if not idea.get("formality"):
        enriched["formality"] = communication_style.get("formality", "neutral")
    
    # Add brand values
    enriched["brand_values"] = audience_profile.get("brand_values", [])
    
    # Add full profile context for agents (preserve for detailed context)
    enriched["audience_profile_full"] = audience_profile
    
    return enriched


def get_audience_from_platform(platform: str) -> str:
    """
    Infer primary audience type from platform.
    
    Based on brand strategy platform mapping.
    
    Args:
        platform: Social media platform
    
    Returns:
        Audience type string ("c_level", "founder", or "developer")
    """
    platform_lower = platform.lower()
    
    platform_mapping = {
        "linkedin": "c_level",        # Authority & B2B Leads
        "instagram": "founder",        # Community & Awareness
        "twitter": "founder",          # Viral Reach
        "github": "developer",         # OSS Credibility
        "discord": "developer",        # Deep Interaction
        "youtube": "founder",          # Deep Education (mixed, default to founder)
    }
    
    return platform_mapping.get(platform_lower, "founder")


def get_content_focus_keywords(audience_type: str) -> List[str]:
    """
    Get content focus keywords for audience type.
    
    Queries database for audience profile.
    
    Args:
        audience_type: "c_level", "founder", or "developer"
    
    Returns:
        List of content focus keywords
    """
    repo = get_repository()
    profile = repo.get_profile(audience_type)
    if not profile:
        return []
    
    content_prefs = profile.get("content_preferences", {})
    return content_prefs.get("content_focus", [])


def get_recommended_platforms(audience_type: str) -> List[str]:
    """
    Get recommended platforms for audience type.
    
    Queries database for audience profile.
    
    Args:
        audience_type: "c_level", "founder", or "developer"
    
    Returns:
        List of platform names
    """
    repo = get_repository()
    profile = repo.get_profile(audience_type)
    if not profile:
        return ["linkedin", "instagram"]
    
    return profile.get("platforms", [])
```

---

## Query Examples

### Useful Queries

```sql
-- Find all professional, formal profiles
SELECT persona_type, name, description
FROM audience_profiles 
WHERE tone = 'professional' AND formality = 'formal' AND is_active = 1;

-- Find profiles that use LinkedIn
SELECT ap.persona_type, ap.name, pl.platform, pl.priority
FROM audience_profiles ap
JOIN audience_platforms pl ON ap.id = pl.profile_id
WHERE pl.platform = 'linkedin' AND ap.is_active = 1;

-- Find profiles with specific pain point
SELECT ap.persona_type, ap.name, pp.category, pp.pain_point
FROM audience_profiles ap
JOIN audience_pain_points pp ON ap.id = pp.profile_id
WHERE pp.pain_point = 'compressed_margins' AND ap.is_active = 1;

-- Find profiles by brand value
SELECT ap.persona_type, ap.name, bv.brand_value
FROM audience_profiles ap
JOIN audience_brand_values bv ON ap.id = bv.profile_id
WHERE bv.brand_value = 'go_deep_or_go_home' AND ap.is_active = 1;

-- Find profiles with high engagement rate target
SELECT persona_type, name, target_engagement_rate
FROM audience_profiles
WHERE target_engagement_rate > 0.04 AND is_active = 1
ORDER BY target_engagement_rate DESC;

-- Find profiles by content focus keyword
SELECT ap.persona_type, ap.name, cf.focus_keyword
FROM audience_profiles ap
JOIN audience_content_focus cf ON ap.id = cf.profile_id
WHERE cf.focus_keyword = 'roi_rapido' AND ap.is_active = 1;

-- Get all personality traits for a profile
SELECT trait
FROM audience_personality_traits
WHERE profile_id = (SELECT id FROM audience_profiles WHERE persona_type = 'c_level')
ORDER BY trait;

-- Count profiles by tone
SELECT tone, COUNT(*) as count
FROM audience_profiles
WHERE is_active = 1
GROUP BY tone
ORDER BY count DESC;
```

---

## Usage Examples

### Creating a New Profile

```python
from src.brand.audience_repo import AudienceRepository

repo = AudienceRepository()

new_profile = {
    "name": "Marketing Manager",
    "description": "Mid-level marketing managers in B2B companies",
    "persona_type": "marketing_manager",
    "professional_background": {
        "company_size": "50-500 employees",
        "role_types": ["Marketing Manager", "CMO", "Marketing Director"],
        ...
    },
    "communication_style": {
        "tone": "professional",
        "formality": "moderate",
        ...
    },
    ...
}

profile_id = repo.create_profile(
    persona_type="marketing_manager",
    name="Marketing Manager",
    description="Mid-level marketing managers in B2B companies",
    profile_data=new_profile
)
```

### Updating a Profile

```python
repo = AudienceRepository()

# Get current profile
profile = repo.get_profile("developer")

# Modify it
profile["communication_style"]["tone"] = "technical_casual"

# Update in database
repo.update_profile("developer", profile)
```

### Querying Profiles

```python
repo = AudienceRepository()

# Get specific profile
profile = repo.get_profile("founder")

# List all profiles
all_profiles = repo.list_profiles(active_only=True)

# Search profiles
results = repo.search_profiles("C-Level")
```

---

## Benefits Summary

1. **Easy Management**: Add/update/delete profiles via SQL or Python API
2. **No Code Changes**: Profile updates don't require code deployment
3. **Versioning**: Track changes over time
4. **Soft Deletes**: Deactivate profiles without losing data
5. **Flexibility**: JSON storage allows schema evolution
6. **Performance**: Indexed queries for fast lookups
7. **Backward Compatible**: Existing code continues to work

---

## Design Summary

This design follows a **Document Store model** (per [ADR-001](decisions/ADR-001-simplify-audience-profile-storage.md)) that:

- **Stores complete profiles as JSON documents** in a single `profile_data` column
- **Eliminates data consistency risks** by having a single source of truth
- **Matches the primary access pattern**: get complete profile by `persona_type` for prompt generation
- **Preserves all essential attributes** required by prompt agents (persona, pain_points, desires, personality_traits, communication_style, platforms, formats, content_preferences, emotional_triggers, brand_values, customer_journey, professional_background, market_context, success_metrics, language_examples)
- **Simplifies repository logic**: straightforward read/write JSON operations

## Next Steps

1. Implement simplified `AudienceRepository` class (Document Store approach)
2. Create migration script to move hardcoded profiles to database
3. Update `get_audience_profile()` to use database
4. Run migration to populate database
5. Test with existing pipeline phases (ensure all prompt attributes are accessible)
6. Remove hardcoded `AUDIENCE_PROFILES` dict (optional, for cleanup)
