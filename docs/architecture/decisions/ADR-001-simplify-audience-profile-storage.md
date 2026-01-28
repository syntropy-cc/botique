# ADR-001: Simplify Audience Profile Storage to Document Store Model

## Status

Accepted

## Date

2026-01-27

## Context

The branding system stores audience profiles to guide content generation throughout the pipeline. The current design proposes a hybrid database schema that stores data in three places:

1. **Normalized columns** for "frequently queried" fields (tone, formality, vocabulary, etc.)
2. **JSON columns** for complex nested structures (professional_background, market_context, etc.)
3. **Many-to-many tables** for arrays/lists (personality_traits, pain_points, platforms, etc.)

This hybrid approach creates several architectural problems:

- **Data Consistency Risk**: The same logical data exists in multiple places (e.g., `tone` in normalized column and `communication_style.tone` in JSON), requiring complex reconstruction logic and risking synchronization errors
- **Query Pattern Mismatch**: The normalized columns optimize for queries like `WHERE tone = 'professional'`, but the actual primary access pattern is: get profile by `persona_type` → load entire profile → use in-memory structure
- **Over-Normalization**: Many-to-many tables are used for simple arrays that are never queried individually (personality_traits, platforms, formats), adding JOIN complexity without benefit
- **Complex Repository Logic**: The repository must reconstruct nested structures from normalized columns + JSON + many-to-many tables, making it error-prone and hard to maintain
- **Update Complexity**: Updates must maintain consistency across three storage locations, increasing risk of data inconsistency

The primary use case is: **query a specific profile by persona_type and use the complete profile data in prompt generation for LLM agents**. All essential attributes (persona, pain_points, desires, personality_traits, communication_style, platforms, formats, content_focus, emotional_triggers, brand_values, customer_journey, language_preferences, professional_background, market_context) must be preserved and accessible.

## Decision

We will simplify the audience profile storage to a **Document Store model** using SQLite with full JSON storage.

Specifically:

1. **Store complete profile as JSON**: All profile data will be stored in a single `profile_data` JSON column, maintaining the complete nested structure
2. **Index only essential fields**: Create indexes on `persona_type` and `is_active` for the primary access pattern (lookup by persona_type)
3. **Remove hybrid complexity**: Eliminate normalized columns and many-to-many tables, storing everything in the JSON document
4. **Preserve all attributes**: Ensure all essential attributes used by prompt agents are maintained in the JSON structure:
   - `persona_type`, `name`, `description`
   - `personality_traits` (list)
   - `pain_points` (dict by category or flat list)
   - `desires` (dict by category or flat list)
   - `communication_style` (tone, formality, vocabulary, language_preferences, communication_channels)
   - `platforms` (list)
   - `formats` (list)
   - `content_preferences` (content_focus, formats, content_structure_preferences, engagement_triggers)
   - `emotional_triggers` (primary, emotional_journey, positive, negative_to_avoid)
   - `brand_values` (list)
   - `customer_journey` (awareness_stage, consideration_stage, decision_stage, adoption_stage)
   - `professional_background` (complete nested structure)
   - `market_context` (complete nested structure)
   - `success_metrics` (complete nested structure)
   - `language_examples` (phrases_that_resonate, writing_style_notes)

5. **Simplify repository**: The repository will read/write complete JSON documents without reconstruction logic

**Boundaries**:
- This decision applies only to audience profile storage
- Visual asset selection (palettes, typography, canvas) remains in `BrandLibrary` (unchanged)
- The repository interface remains backward-compatible (same method signatures)

## Alternatives Considered

### Alternative 1: Fully Normalized Schema

Store all data in normalized tables with proper foreign keys and relationships.

**Pros**:
- Optimal for complex queries and analytics
- Strong data integrity through foreign keys
- Better for reporting and filtering

**Cons**:
- Much more complex schema (20+ tables)
- Complex JOINs for simple profile retrieval
- Difficult to evolve schema
- Overkill for current access pattern (single profile lookup)

**Why rejected**: The primary access pattern is "get complete profile by persona_type", not complex filtering. The added complexity doesn't justify the benefits for this use case.

### Alternative 2: Hybrid Model (Current Design)

Keep the hybrid approach with normalized columns + JSON + many-to-many tables.

**Pros**:
- Supports both full profile retrieval and filtered queries
- Indexed columns for fast filtering

**Cons**:
- Data consistency risk (same data in multiple places)
- Complex reconstruction logic
- Update operations must maintain consistency across 3 storage locations
- Over-normalization for simple arrays
- Query pattern mismatch (optimized for queries we don't use)

**Why rejected**: The complexity and consistency risks outweigh the benefits. The normalized columns optimize for queries that aren't the primary access pattern.

### Alternative 3: Do Nothing

Keep hardcoded profiles in Python dictionaries.

**Pros**:
- No implementation effort
- No database complexity
- Simple and fast

**Cons**:
- No versioning or change tracking
- Requires code deployment for profile updates
- No soft delete capability
- Hard to manage multiple profiles
- No queryability

**Why rejected**: The system needs database-backed storage for profile management, versioning, and future extensibility.

## Consequences

### Positive

- **Simplified Architecture**: Single source of truth (JSON document), eliminating data consistency risks
- **Easier Maintenance**: Repository logic is straightforward (read/write JSON), no complex reconstruction
- **Flexible Schema**: JSON allows schema evolution without migrations
- **Matches Access Pattern**: Optimized for the primary use case (get complete profile by persona_type)
- **Preserves All Attributes**: All essential prompt attributes are maintained in the JSON structure
- **Faster Development**: Simpler implementation reduces development time and bugs
- **Better Testability**: Easier to test with simple JSON documents

### Negative

- **Limited Query Flexibility**: Cannot efficiently query by individual attributes (e.g., "find all profiles with tone='professional'") without JSON parsing
  - **Mitigation**: If such queries become necessary, we can add JSON indexes (SQLite supports JSON1 extension) or create a separate analytics view
- **No Built-in Referential Integrity**: JSON doesn't enforce relationships
  - **Mitigation**: Application-level validation ensures data integrity
- **Slightly Larger Storage**: JSON may use more space than normalized tables
  - **Mitigation**: Profile data is small (< 50KB per profile), storage impact is negligible

### Neutral

- **Query Performance**: Single-table lookup is fast for primary access pattern; complex queries would require JSON parsing (acceptable trade-off)
- **Schema Evolution**: JSON allows flexible evolution, but requires careful versioning strategy

## Implementation Notes

### Phase 1: Schema Simplification

- Duration: 1-2 days
- Scope: 
  - Create simplified schema with single `profile_data` JSON column
  - Remove normalized columns and many-to-many tables
  - Create indexes on `persona_type` and `is_active`
- Verification: Schema creates successfully, indexes are present

### Phase 2: Repository Refactoring

- Duration: 2-3 days
- Scope:
  - Simplify `get_profile()` to read JSON directly (no reconstruction)
  - Simplify `create_profile()` to write complete JSON
  - Simplify `update_profile()` to update JSON document
  - Remove many-to-many insertion methods
- Verification: All CRUD operations work correctly, tests pass

### Phase 3: Migration

- Duration: 1 day
- Scope:
  - Migrate existing hardcoded profiles to database
  - Validate all essential attributes are preserved
  - Test with existing pipeline phases
- Verification: All prompt agents receive complete profile data with all attributes

### Migration Considerations

- **Backward Compatibility**: Repository interface remains the same (same method signatures), so existing code continues to work
- **Data Migration**: Existing hardcoded profiles will be migrated to JSON format in database
- **Rollback Plan**: If issues arise, can revert to hardcoded profiles temporarily while fixing database issues

## References

- Related Documentation: [Branding Domain Architecture](../domains/branding/ARCHITECTURE.md)
- Code Locations: `src/brand/audience_repo.py`, `src/brand/audience.py`
- Prompt Usage: `src/narrative/architect.py`, `src/copywriting/writer.py`, `src/coherence/builder.py`

## Derived Rules

- `architecture.mdc`: ARCH-XXX - Audience profiles stored as JSON documents in SQLite
- `patterns.mdc`: PAT-XXX - Repository pattern for audience profile data access
- `constraints.mdc`: CON-XXX - Profile data must preserve all essential prompt attributes

---

## Review History

| Date | Reviewer | Decision | Notes |
|------|----------|----------|-------|
| 2026-01-20 | Architecture Review | Accepted | Document Store model aligns with primary access pattern |
