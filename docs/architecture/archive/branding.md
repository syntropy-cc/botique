# Architecture: Branding System

> **Version**: 1.1  
> **Date**: 2026-01-20  
> **Status**: Architecture Documentation  
> **Author**: Documentation System

---

## Overview

The branding system is the **strategic foundation** of the social media post generation pipeline. It ensures all generated content aligns with brand identity, target audiences, and brand values. Branding serves as a **guiding framework** that informs creative decisions throughout all pipeline phases, from ideation to finalization.

### Core Principle

**Branding as Guide, Not Override**: The branding system provides strategic guidance and defaults, but **never overrides explicit user definitions**. For example, if a user specifies `platform: "linkedin"`, the post will be generated for LinkedIn regardless of audience preferences (e.g., a developer profile that typically prefers Instagram). User-defined parameters take precedence over brand defaults.

### Objective

Produce content that is **highly aligned** with the defined audience while respecting user specifications, utilizing detailed audience profiles, color palettes, typography, and communication guidelines that reflect brand strategy.

---

## Branding Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    BRANDING SYSTEM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Brand Models    │  │  Audience DB     │                │
│  │  (models.py)     │  │  (SQLite)        │                │
│  │                  │  │                    │                │
│  │ • Enums          │  │ • Audience Profiles│                │
│  │ • Data Classes   │  │ • CRUD Operations │                │
│  │ • Configs        │  │ • Versioning      │                │
│  └──────────────────┘  └──────────────────┘                │
│           │                      │                             │
│           └──────────┬───────────┘                             │
│                      │                                         │
│           ┌──────────▼───────────┐                             │
│           │  Brand Library       │                             │
│           │  (library.py)        │                             │
│           │                      │                             │
│           │ • Color Palettes     │                             │
│           │ • Typography Configs │                             │
│           │ • Canvas Dimensions  │                             │
│           │ • Selection Logic    │                             │
│           └─────────────────────┘                             │
│                      │                                         │
│           ┌──────────▼───────────┐                            │
│           │  Audience Repository │                            │
│           │  (audience_repo.py)  │                            │
│           │                       │                            │
│           │ • get_profile()       │                            │
│           │ • create_profile()    │                            │
│           │ • update_profile()    │                            │
│           │ • delete_profile()   │                            │
│           │ • list_profiles()    │                            │
│           └──────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                      │
                      │ Integration Points
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Phase 1     │ │  Phase 2     │ │  Phase 3     │
│  Ideation    │ │  Config      │ │  Narrative   │
│              │ │              │ │  Architect    │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Database Architecture

The audience profiles are stored in a **Document Store model** using SQLite with full JSON storage. This design optimizes for the primary access pattern: query a specific profile by `persona_type` and use the complete profile data in prompt generation.

```
┌─────────────────────────────────────────────────────────────┐
│              audience_profiles (Main Table)                  │
├─────────────────────────────────────────────────────────────┤
│  id TEXT PRIMARY KEY                                        │
│  persona_type TEXT NOT NULL UNIQUE                          │
│  name TEXT NOT NULL                                         │
│  description TEXT                                           │
│  profile_data TEXT NOT NULL (JSON)                          │
│  created_at TEXT NOT NULL                                   │
│  updated_at TEXT NOT NULL                                   │
│  version INTEGER DEFAULT 1                                  │
│  is_active INTEGER DEFAULT 1                               │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions** (per [ADR-001](decisions/ADR-001-simplify-audience-profile-storage.md)):
- **Document Store**: Complete profile stored as JSON document in `profile_data` column
- **Single Source of Truth**: All profile attributes (personality_traits, pain_points, desires, communication_style, platforms, formats, content_preferences, emotional_triggers, brand_values, customer_journey, professional_background, market_context, success_metrics, language_examples) stored in JSON
- **Indexed Lookups**: Indexes on `persona_type` and `is_active` for fast primary access pattern
- **`persona_type` (UNIQUE)**: Ensures one active profile per persona type
- **`version`**: Supports profile versioning for tracking changes
- **`is_active`**: Soft delete capability, allows deactivating profiles without deletion

**Benefits**:
- ✅ Simplified architecture: Single source of truth eliminates data consistency risks
- ✅ Matches access pattern: Optimized for "get complete profile by persona_type"
- ✅ Flexible schema: JSON allows evolution without migrations
- ✅ Preserves all attributes: All essential prompt attributes maintained
- ✅ Easier maintenance: Simple read/write JSON operations

**Essential Attributes Preserved**:
All attributes required by prompt agents are maintained in the JSON structure:
- `persona_type`, `name`, `description`
- `personality_traits`, `pain_points`, `desires`
- `communication_style` (tone, formality, vocabulary, language_preferences, communication_channels)
- `platforms`, `formats`
- `content_preferences` (content_focus, formats, content_structure_preferences, engagement_triggers)
- `emotional_triggers` (primary, emotional_journey, positive, negative_to_avoid)
- `brand_values`, `customer_journey`
- `professional_background`, `market_context`, `success_metrics`, `language_examples`

See **[Branding Database Design](branding_database_design.md)** for complete schema details and **[ADR-001](decisions/ADR-001-simplify-audience-profile-storage.md)** for design rationale.

### Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                   │
│  (platform, persona, tone, format, etc.)                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Priority: User Input > Brand Defaults
                        │
        ┌───────────────▼───────────────┐
        │  Branding System              │
        │  (Provides Guidance)           │
        │                                │
        │  1. Query Audience Profile     │
        │     from Database              │
        │  2. Select Visual Assets       │
        │  3. Provide Communication     │
        │     Guidelines                 │
        │  4. Suggest Content Structure │
        └───────────────┬───────────────┘
                        │
                        │ Enriches but doesn't override
                        │
        ┌───────────────▼───────────────┐
        │  Pipeline Phases              │
        │                                │
        │  Phase 1: Uses audience        │
        │           profile for ideation │
        │                                │
        │  Phase 2: Selects palette/     │
        │           typography based on  │
        │           user platform/persona    │
        │                                │
        │  Phase 3: Uses audience        │
        │           preferences for      │
        │           narrative structure │
        │                                │
        │  Phase 4: Applies visual        │
        │           branding            │
        │                                │
        │  Phase 5: Uses platform       │
        │           preferences         │
        └───────────────────────────────┘
```

---

## Component Architecture

### 1. Brand Models (`src/brand/models.py`)

Defines fundamental data structures for visual and strategic identity:

#### Core Enums

- **`Platform`**: Supported social media platforms aligned with brand strategy
- **`Audience`**: Target audience types (C-Level, Founder, Developer)
- **`BrandValue`**: Core brand values (go_deep_or_go_home, open_source, community_collaboration, pioneer_new_world)

#### Data Classes

- **`ColorPalette`**: Color palette definitions with theme and best-for metadata
- **`TypographyConfig`**: Typography configurations (Poppins Bold + Inter Regular)
- **`CanvasConfig`**: Canvas dimensions for platform/format combinations
- **`VisualStyle`**: Visual style definitions with characteristics and mood keywords
- **`AudienceProfile`**: Model class for audience profiles (database-backed)

### 2. Audience Profile Storage (`src/brand/audience_repo.py`)

Database-backed repository for audience profiles:

#### Database Schema

```sql
CREATE TABLE IF NOT EXISTS audience_profiles (
    id TEXT PRIMARY KEY,
    persona_type TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    profile_data TEXT NOT NULL,  -- JSON string
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_audience_profiles_persona_type 
    ON audience_profiles(persona_type);
CREATE INDEX IF NOT EXISTS idx_audience_profiles_active 
    ON audience_profiles(is_active);
```

#### Repository Interface

```python
class AudienceRepository:
    """Repository for audience profile CRUD operations"""
    
    def get_profile(self, persona_type: str) -> Optional[Dict[str, Any]]
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]
    def create_profile(self, persona_type: str, name: str, 
                      description: str, profile_data: Dict) -> str
    def update_profile(self, persona_type: str, profile_data: Dict) -> bool
    def delete_profile(self, persona_type: str) -> bool
    def deactivate_profile(self, persona_type: str) -> bool
    def list_profiles(self, active_only: bool = True) -> List[Dict[str, Any]]
    def search_profiles(self, query: str) -> List[Dict[str, Any]]
```

#### Benefits of Database Storage

1. **Easy Management**: Add, update, or delete profiles via SQL or repository methods
2. **Versioning**: Track profile changes over time
3. **Flexibility**: JSON storage allows schema evolution without migrations
4. **Performance**: Indexed queries for fast lookups
5. **Soft Deletes**: Deactivate profiles without losing data
6. **Extensibility**: Easy to add new profile types without code changes

### 3. Brand Library (`src/brand/library.py`)

Centralized repository of brand assets with intelligent selection logic:

#### Color Palettes (6 palettes)

- **Brand Light/Dark - Professional**: For C-Level audiences
- **Brand Light/Dark - Founder**: For Founder audiences
- **Brand Dark - Developer**: For Developer audiences
- **Brand Light - Community**: Default/community content

#### Typography Configurations (3 configs)

- **Brand Primary**: Poppins + Inter (default, all audiences)
- **Brand Professional**: Inter only (C-Level, LinkedIn)
- **Brand Bold**: Poppins Heavy (Founders, high-impact)

#### Canvas Configurations

Optimized dimensions per platform/format combination (LinkedIn, Instagram, Twitter, YouTube, GitHub).

#### Selection Logic

Intelligent selection based on:
- **Platform**: Maps to default audience type
- **Tone**: Influences theme selection (light/dark)
- **Persona**: Selects specific palette and typography
- **Theme Preference**: Allows manual override (light/dark/auto)

**Important**: Selection logic **respects user input**. If user specifies platform="linkedin", the system uses LinkedIn-appropriate branding even if the detected audience type would typically prefer another platform.

---

## Integration with Pipeline Architecture

### User Input Priority

```
Priority Hierarchy:
1. Explicit User Input (highest priority)
   - platform, persona, tone, format, etc.
   
2. Brand Guidance (applied when user input is missing)
   - Audience profile from database
   - Platform-to-audience mapping
   - Visual asset selection
   
3. System Defaults (fallback)
   - Generic configurations
```

### Example: Platform Selection

**Scenario**: User specifies `platform: "linkedin"` but audience is detected as "developer" (which typically prefers GitHub/Instagram).

**Behavior**:
- ✅ Post is generated for **LinkedIn** (user input respected)
- ✅ Branding uses LinkedIn-appropriate visual assets (palette, typography, canvas)
- ✅ Audience profile (developer) is loaded from **database** and used for **content guidance** (pain points, desires, communication style)
- ✅ Content is adapted to LinkedIn format while maintaining developer-focused messaging

### Integration Points by Phase

#### Phase 1: Ideation

**Current State**: ❌ Branding not used

**Ideal State**: ✅ Branding provides guidance

**Integration**:
- Query audience profile from database based on user-specified platform or persona
- Use profile's pain points, desires, and content preferences to guide idea generation
- Consider brand values in ideation
- **Respect user-defined platform/tone/persona** - branding enriches, doesn't override

**Example**:
```python
# User input
platform = "linkedin"  # User explicitly wants LinkedIn
persona = "developer"  # User wants developer-focused content

# Branding provides guidance (from database)
repo = AudienceRepository()
audience_profile = repo.get_profile(persona)  # Loaded from database
# But respects platform choice
canvas = BrandLibrary.get_canvas_config(platform, format)  # LinkedIn dimensions
palette = BrandLibrary.select_palette(platform, tone, persona)  # LinkedIn-appropriate palette
```

#### Phase 2: Configuration

**Current State**: ✅ Partially implemented

**Integration**:
- Selects palette based on **user-specified** platform + tone + persona
- Selects typography based on **user-specified** platform + persona
- Loads audience profile from **database** and enriches idea (merges, doesn't override)
- Detects brand values from content
- Builds coherence brief with brand-aligned visual assets

**Key Point**: Visual asset selection respects user platform choice, while audience profile from database enriches content guidance.

#### Phase 3: Narrative Architect

**Current State**: ❌ Limited branding usage

**Ideal State**: ✅ Full branding integration

**Integration**:
- Receives audience profile (from database) in coherence brief context
- Uses content preferences to structure narrative (hook type, value delivery, proof elements, CTA style)
- Considers customer journey for pacing and transitions
- Uses emotional triggers to assign emotions per slide
- Aligns structure with preferred formats (when user hasn't specified)

**Key Point**: Narrative structure follows audience preferences from database, but respects user-defined format and structure requirements.

#### Phase 4: Copywriting & Visual

**Current State**: ✅ Visual branding applied

**Integration**:
- Uses selected palette and typography (from Phase 2, based on user platform)
- Applies visual branding consistently
- Can use language examples from audience profile (from database) for copywriting guidance

#### Phase 5: Caption

**Current State**: ⚠️ Can be improved

**Integration**:
- Uses platform preferences from audience profile (from database, when user hasn't specified)
- Aligns tone with communication style from profile

---

## Database Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SQLite Database                            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              audience_profiles                              │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │  id              TEXT PRIMARY KEY                           │  │
│  │  persona_type    TEXT NOT NULL UNIQUE                      │  │
│  │  name            TEXT NOT NULL                              │  │
│  │  description     TEXT                                       │  │
│  │  profile_data    TEXT NOT NULL (JSON)                      │  │
│  │  created_at      TEXT NOT NULL                              │  │
│  │  updated_at      TEXT NOT NULL                              │  │
│  │  version         INTEGER DEFAULT 1                          │  │
│  │  is_active       INTEGER DEFAULT 1                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           │                                        │
│  ┌────────────────────────▼────────────────────────┐              │
│  │         AudienceRepository                     │              │
│  │  (CRUD operations, caching, validation)        │              │
│  └────────────────────────┬────────────────────────┘              │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phase 1     │    │  Phase 2     │    │  Phase 3     │
│  Ideation    │    │  Config      │    │  Narrative   │
│              │    │              │    │  Architect    │
│  Queries     │    │  Queries     │    │  Queries      │
│  profiles    │    │  profiles    │    │  profiles     │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Helper Functions

### Audience Profile Functions

**`get_audience_profile(persona: str) -> Dict`**
- Queries database via `AudienceRepository`
- Returns complete audience profile based on persona string (partial match supported)
- Returns `None` if no match found
- **Note**: This function now queries the database instead of hardcoded dictionaries

**`enrich_idea_with_audience(idea: Dict, profile: Dict) -> Dict`**
- Enriches idea with audience profile data from database
- **Merges** attributes (doesn't override existing user-defined values)
- Only fills in missing values with profile defaults

**`get_audience_from_platform(platform: str) -> str`**
- Infers primary audience type from platform
- **Used for guidance only** - doesn't override user persona specification

**`get_content_focus_keywords(audience_type: str) -> List[str]`
- Queries database for audience profile
- Returns content focus keywords for audience type

**`get_recommended_platforms(audience_type: str) -> List[str]`**
- Queries database for audience profile
- Returns recommended platforms for audience type
- **Suggestion only** - doesn't override user platform choice

### Visual Asset Functions

**`BrandLibrary.select_palette(platform, tone, persona, theme_preference) -> ColorPalette`**
- Selects brand-aligned color palette
- **Respects user-specified platform** for selection

**`BrandLibrary.select_typography(platform, audience) -> TypographyConfig`**
- Selects brand-aligned typography
- **Respects user-specified platform** for selection

**`BrandLibrary.get_canvas_config(platform, format) -> CanvasConfig`**
- Returns canvas dimensions for platform/format
- **Uses user-specified platform** (required parameter)

### Repository Functions

**`AudienceRepository.get_profile(persona_type: str) -> Optional[Dict]`**
- Queries database for audience profile by persona type
- Returns full profile data (parsed from JSON)
- Returns `None` if not found or inactive

**`AudienceRepository.create_profile(...) -> str`**
- Creates new audience profile in database
- Validates JSON structure
- Returns profile ID

**`AudienceRepository.update_profile(persona_type: str, profile_data: Dict) -> bool`**
- Updates existing profile in database
- Increments version number
- Updates `updated_at` timestamp

**`AudienceRepository.delete_profile(persona_type: str) -> bool`**
- Soft deletes profile (sets `is_active = 0`)
- Returns `True` if successful

**`AudienceRepository.list_profiles(active_only: bool = True) -> List[Dict]`**
- Lists all profiles (optionally only active ones)
- Returns list of profile metadata

---

## Data Flow

### Branding Context Flow

```
User Input
    │
    ├─→ Platform: "linkedin" (explicit)
    ├─→ Persona: "developer" (explicit)
    └─→ Tone: "professional" (explicit)
         │
         │
    ┌────▼────┐
    │ Database│
    │ Query   │
    └────┬────┘
         │
         ├─→ Load Developer Profile from DB
         ├─→ Select LinkedIn Palette (respects platform)
         ├─→ Select LinkedIn Typography (respects platform)
         └─→ Get LinkedIn Canvas (respects platform)
              │
              │
    ┌─────────▼─────────┐
    │  Coherence Brief   │
    │                    │
    │  • Platform: linkedin (user)
    │  • Persona: developer (user)
    │  • Palette: LinkedIn-appropriate (brand)
    │  • Typography: LinkedIn-appropriate (brand)
    │  • Pain Points: Developer profile (from DB)
    │  • Desires: Developer profile (from DB)
    └────────────────────┘
```

### Database Query Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Application Code                                           │
│                                                             │
│  get_audience_profile("developer")                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  AudienceRepository                                         │
│                                                             │
│  get_profile(persona_type="developer")                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SQLite Database                                            │
│                                                             │
│  SELECT profile_data                                        │
│  FROM audience_profiles                                     │
│  WHERE persona_type = 'developer'                           │
│    AND is_active = 1                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  JSON Parsing                                               │
│                                                             │
│  Parse profile_data JSON → Dict                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Return Profile Dict                                        │
│                                                             │
│  {                                                          │
│    "name": "DEV Forjador",                                 │
│    "pain_points": [...],                                    │
│    "desires": [...],                                        │
│    ...                                                      │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Guidelines

### Principle: User Input Priority

**Always**:
- ✅ Respect explicit user definitions (platform, persona, tone, format)
- ✅ Query database for audience profiles when user input is missing
- ✅ Merge branding data with user data (don't override)
- ✅ Apply visual branding based on user-specified platform

**Never**:
- ❌ Override user-specified platform with brand recommendations
- ❌ Override user-specified persona with platform-based inference
- ❌ Ignore user-defined tone, format, or other parameters

### Integration Pattern

```python
# Pattern for integrating branding in pipeline phases

def process_with_branding(user_input, branding_system):
    # 1. Extract user-defined parameters (highest priority)
    platform = user_input.get("platform")  # Required, user-defined
    persona = user_input.get("persona")    # Optional, user-defined
    
    # 2. Get branding guidance from database (applied when user input missing)
    repo = AudienceRepository()
    if not persona:
        # Infer from platform (guidance only)
        inferred_persona = get_audience_from_platform(platform)
        persona = inferred_persona  # Use as guidance
    
    # 3. Load audience profile from database (for guidance)
    audience_profile = repo.get_profile(persona)  # Database query
    
    # 4. Select visual assets (respects user platform)
    palette = BrandLibrary.select_palette(
        platform,  # User-defined, always respected
        user_input.get("tone", "professional"),
        persona
    )
    
    # 5. Enrich with branding (merges, doesn't override)
    enriched = enrich_idea_with_audience(user_input, audience_profile)
    
    return enriched
```

### Database Initialization

```python
# Initialize database schema
from src.brand.audience_repo import init_audience_database

# Initialize database (creates tables if not exist)
init_audience_database()

# Or with custom database path
init_audience_database(db_path=Path("/custom/path/branding.db"))
```

### Migration from Hardcoded Profiles

```python
# Migration script to move hardcoded profiles to database
from src.brand.audience_repo import AudienceRepository
from src.brand.audience import AUDIENCE_PROFILES  # Old hardcoded dict

def migrate_profiles_to_database():
    """Migrate hardcoded profiles to database"""
    repo = AudienceRepository()
    
    for persona_type, profile_data in AUDIENCE_PROFILES.items():
        repo.create_profile(
            persona_type=persona_type,
            name=profile_data["name"],
            description=profile_data["description"],
            profile_data=profile_data  # Full nested structure
        )
    
    print(f"Migrated {len(AUDIENCE_PROFILES)} profiles to database")
```

---

## Benefits

### 1. Strategic Alignment

- Content aligns with brand strategy from the start
- Ideas are relevant to target audience
- Narratives follow customer journey

### 2. Consistency

- Consistent voice, tone, and vocabulary
- Language resonates with audience
- Avoids terms audience dislikes

### 3. User Control

- Users maintain full control over platform, persona, tone
- Branding provides intelligent defaults and guidance
- No unexpected overrides

### 4. Efficiency

- Less manual iteration needed
- Content closer to ideal from the start
- Intelligent defaults reduce configuration burden

### 5. Maintainability

- **Easy to add new profiles**: Just insert into database
- **Easy to update profiles**: Update JSON without code changes
- **Easy to delete profiles**: Soft delete maintains history
- **Versioning**: Track changes over time
- **No code deployment needed**: Profile changes don't require code updates

---

## References

### Related Documentation

- **[Pipeline Architecture](pipeline_architecture.md)** - Overall architecture overview
- **[Agents](agents.md)** - AI agents documentation
- **[Tools](tools.md)** - Tools documentation
- **[Memory Management](memory_management.md)** - Coherence Brief
- **[Data Structures](data_structures.md)** - Data structure schemas

### Code Locations

- `src/brand/models.py` - Brand data models
- `src/brand/audience_repo.py` - Audience profile repository (database-backed)
- `src/brand/library.py` - Brand library and selection logic
- `src/coherence/builder.py` - Brief builder (uses branding)

### Related Design Documents

- **[Branding Database Design](branding_database_design.md)** - Detailed database schema and implementation guide

---

## Conclusion

The branding system serves as a **strategic guidance framework** that enriches content generation throughout the pipeline while **respecting user-defined parameters**. It provides intelligent defaults, audience insights, and visual consistency without overriding explicit user choices.

The architecture supports:
- ✅ Strategic alignment with brand identity
- ✅ Audience-focused content guidance (from database)
- ✅ User control and flexibility
- ✅ Intelligent defaults and suggestions
- ✅ Consistent visual and communication branding
- ✅ **Easy profile management** (add/update/delete via database)
- ✅ **Versioning and history tracking**
- ✅ **No code changes needed for profile updates**

---

> **Note**: This documentation focuses on the **architecture** of the branding system and its integration with the overall pipeline. The database-backed audience profile storage makes the system more maintainable and flexible, allowing profile management without code deployments.
