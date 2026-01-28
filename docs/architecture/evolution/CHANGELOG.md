# Architecture Changelog

All notable architectural changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
adapted for architectural decisions.

## Types of Changes

- **Added**: New components, services, patterns, or capabilities
- **Changed**: Modifications to existing architecture, refactoring
- **Deprecated**: Features or patterns marked for future removal
- **Removed**: Components or patterns removed from the system
- **Security**: Changes addressing security concerns
- **Performance**: Architectural changes for performance improvement

---

## [Unreleased]

### Added

- Hierarchical architecture documentation structure following template standards
- Root ARCHITECTURE.md with complete system overview and document map
- Domain architecture documents:
  - Branding domain architecture
  - Pipeline domain architecture
  - Agents domain architecture
  - Tools domain architecture
  - Memory domain architecture (key architectural component)
- Cross-cutting concern documents:
  - Data Models architecture

### Changed

- Reorganized flat architecture documentation into hierarchical structure
- Translated all Portuguese content to English
- Memory management reclassified from cross-cutting concern to core domain (key architectural component)
- System description updated to reflect full autonomous marketing agency scope

---

## [1.0.0] - 2026-01-27

### Added

- **[ADR-001](../decisions/ADR-001-simplify-audience-profile-storage.md)**: Simplify audience profile storage to document store model
  - Impact: Branding domain database design
  - Migration: Simplified from hybrid normalized/JSON/many-to-many to pure document store

### Changed

- Architecture documentation reorganized into hierarchical structure
  - Previous: Flat structure with mixed Portuguese/English content
  - Current: Hierarchical structure with domain-specific and cross-cutting documents, all in English
  - Rationale: Better organization, easier navigation, consistent structure following templates

---
