"""
Migration script for audience profiles.

Migrates hardcoded AUDIENCE_PROFILES from src/brand/audience.py to database.

Usage:
    python scripts/migrate_audience_profiles.py [--db-path PATH] [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.brand.audience import AUDIENCE_PROFILES
from src.brand.audience_repo import AudienceRepository, init_audience_database


# Essential attributes that must be preserved (per ADR-001)
ESSENTIAL_ATTRIBUTES = [
    "persona_type",
    "name",
    "description",
    "personality_traits",
    "pain_points",
    "desires",
    "communication_style",
    "platforms",
    "formats",
    "content_preferences",
    "emotional_triggers",
    "brand_values",
    "customer_journey",
    "professional_background",
    "market_context",
    "success_metrics",
    "language_examples",
]


def validate_profile(profile_data: Dict, persona_type: str) -> List[str]:
    """
    Validate profile has all essential attributes.
    
    Args:
        profile_data: Profile data dict
        persona_type: Persona type identifier
    
    Returns:
        List of missing attributes (empty if valid)
    """
    missing = []
    
    for attr in ESSENTIAL_ATTRIBUTES:
        if attr not in profile_data:
            missing.append(attr)
    
    return missing


def migrate_profiles(
    db_path: Path = None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Migrate profiles from AUDIENCE_PROFILES dict to database.
    
    Args:
        db_path: Path to database file (None for default)
        dry_run: If True, validate but don't insert
    
    Returns:
        Dict with migration statistics
    """
    stats = {
        "total": len(AUDIENCE_PROFILES),
        "migrated": 0,
        "skipped": 0,
        "errors": 0,
        "validation_errors": 0,
    }
    
    # Initialize database
    if not dry_run:
        init_audience_database(db_path)
        repo = AudienceRepository(db_path)
    else:
        repo = None
    
    print("=" * 70)
    print("MIGRATE AUDIENCE PROFILES TO DATABASE")
    print("=" * 70)
    print(f"Source: AUDIENCE_PROFILES dict ({stats['total']} profiles)")
    print(f"Database: {db_path or 'default location'}")
    print(f"Mode: {'DRY RUN' if dry_run else 'MIGRATION'}")
    print()
    
    # Validate and migrate each profile
    for persona_type, profile_data in AUDIENCE_PROFILES.items():
        print(f"Processing: {persona_type}...")
        
        # Validate structure
        missing = validate_profile(profile_data, persona_type)
        if missing:
            print(f"  ❌ Validation failed: missing attributes: {', '.join(missing)}")
            stats["validation_errors"] += 1
            stats["skipped"] += 1
            continue
        
        # Check if already exists
        if not dry_run:
            existing = repo.get_profile(persona_type)
            if existing:
                print(f"  ⚠️  Profile already exists, skipping...")
                stats["skipped"] += 1
                continue
        
        # Extract name and description
        name = profile_data.get("name", persona_type)
        description = profile_data.get("description", "")
        
        if dry_run:
            print(f"  ✓ Would migrate: {name}")
            stats["migrated"] += 1
        else:
            try:
                profile_id = repo.create_profile(
                    persona_type=persona_type,
                    name=name,
                    description=description,
                    profile_data=profile_data,
                )
                print(f"  ✓ Migrated: {name} (ID: {profile_id})")
                stats["migrated"] += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                stats["errors"] += 1
                stats["skipped"] += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Total profiles: {stats['total']}")
    print(f"Migrated: {stats['migrated']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Validation errors: {stats['validation_errors']}")
    print(f"Errors: {stats['errors']}")
    print()
    
    if dry_run:
        print("DRY RUN: No data was written to database.")
        print("Run without --dry-run to perform actual migration.")
    else:
        if stats["migrated"] > 0:
            print("✓ Migration completed successfully!")
        else:
            print("⚠️  No profiles were migrated.")
    
    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate hardcoded audience profiles to database"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Path to SQLite database file (default: uses BRANDING_DB_PATH or data/branding.db)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate profiles but don't insert into database",
    )
    
    args = parser.parse_args()
    
    try:
        stats = migrate_profiles(
            db_path=args.db_path,
            dry_run=args.dry_run,
        )
        
        # Exit with error code if validation failed
        if stats["validation_errors"] > 0 or stats["errors"] > 0:
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
