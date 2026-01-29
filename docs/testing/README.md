# Testing Framework for AI-Assisted Development

This framework provides a comprehensive, structured approach to testing when working with AI coding assistants like Cursor. It ensures consistency, quality, and maintainability across all test types through explicit rules, templates, and best practices.

## Philosophy

The core principle behind this framework is that tests are not an afterthought but a fundamental deliverable. Well-written tests serve as executable specifications, living documentation, and safety nets against regression. When working with AI assistants, explicit testing rules prevent the common pitfall of generating superficial tests that provide false confidence.

## Quick Start

Copy the `.cursor/rules/` directory to your project and place the documentation templates in your `docs/testing/` directory. Customize the test strategy document for your specific project needs.

```
your-project/
├── .cursor/
│   └── rules/
│       ├── testing-strategy.mdc       # Core testing principles
│       ├── unit-testing.mdc           # Unit test specifics
│       ├── integration-testing.mdc    # Integration test patterns
│       ├── e2e-contract-testing.mdc   # E2E and contract tests
│       ├── test-data-fixtures.mdc     # Data management
│       └── mocking-test-doubles.mdc   # Mocking guidelines
│
├── docs/
│   └── testing/
│       └── TEST-STRATEGY.md           # Your test strategy
│
└── tests/
    ├── unit/
    ├── integration/
    ├── e2e/
    ├── contracts/
    ├── factories/
    ├── fixtures/
    └── conftest.py
```

## Framework Components

### Rule Files

The framework consists of six rule files, each addressing a specific aspect of testing.

**testing-strategy.mdc** (Priority 1) establishes the foundational principles that govern all testing. It defines the test pyramid distribution, coverage requirements, test structure patterns like Arrange-Act-Assert, and quality standards. Every other rule file builds upon these principles.

**unit-testing.mdc** (Priority 2) focuses specifically on unit tests. It defines what constitutes a unit, establishes boundaries for isolation, and provides patterns for testing different types of code including domain entities, value objects, services, and pure functions. It includes comprehensive guidance on boundary testing and state machine testing.

**integration-testing.mdc** (Priority 2) addresses tests that verify interactions with real dependencies. It covers database testing with transaction management, message queue testing, HTTP API testing, and strategies for testing external services. The emphasis is on testing the integration itself rather than duplicating business logic tests.

**e2e-contract-testing.mdc** (Priority 2) covers end-to-end tests and contract tests. E2E tests verify critical user journeys through the entire system. Contract tests verify that services communicate correctly according to agreed specifications. Both are expensive to maintain, so the rules emphasize strategic usage.

**test-data-fixtures.mdc** (Priority 3) provides comprehensive guidance on managing test data. It covers the factory pattern for object creation, pytest fixture organization, builder patterns for complex objects, and the Object Mother pattern for common scenarios. Proper test data management is essential for maintainable tests.

**mocking-test-doubles.mdc** (Priority 3) establishes when and how to use test doubles. It distinguishes between dummies, stubs, spies, mocks, and fakes, providing guidance on selecting the appropriate type. The emphasis is on mocking at system boundaries rather than internal collaborators.

### Test Strategy Document

The TEST-STRATEGY-TEMPLATE.md provides a comprehensive template for documenting your project's testing approach. It covers objectives, test pyramid distribution, coverage requirements, environment strategy, CI/CD integration, specialized testing (performance, security, accessibility), and metrics.

## Key Concepts

### Test Pyramid

The framework advocates for a pyramid distribution of tests with more tests at lower levels and fewer at higher levels. Unit tests should constitute roughly 60% of your test count, being fast and focused. Component tests add another 20%, testing modules in isolation. Integration tests comprise 15%, verifying real dependencies work correctly. E2E tests round out the remaining 5%, covering only critical user journeys.

This distribution exists because lower-level tests are faster to write, faster to execute, and easier to maintain. When a unit test fails, you know exactly what broke. When an E2E test fails, you might spend significant time debugging to find the actual issue.

### Test Independence

Every test must be completely independent. Tests should not rely on execution order, shared mutable state, or side effects from other tests. Each test sets up its own preconditions and cleans up after itself. This enables parallel execution and prevents mysterious failures when tests run in different orders.

### Mock at Boundaries

One of the most important principles is to mock only at system boundaries, not internal collaborators. When you mock internal classes, your tests become tightly coupled to implementation details. Refactoring breaks tests even when behavior is preserved. Instead, mock at the edges: databases (through repository interfaces), external APIs, file systems, and system clocks.

### Test Data Management

The factory pattern centralizes object creation with sensible defaults that can be overridden. Rather than constructing test objects manually with many parameters, factories provide clean, intention-revealing creation methods. Combined with fixtures that manage lifecycle and cleanup, this approach makes tests more maintainable and resistant to schema changes.

## Usage Guidelines

### For Unit Tests

Focus on testing behavior, not implementation. Each test should verify one logical concept. Use descriptive names that document what the test verifies. Mock only external dependencies, never domain objects or internal services. Aim for millisecond execution times.

### For Integration Tests

Integration tests verify that components work correctly with real dependencies. Use transaction rollback to isolate tests. Focus on testing the integration point itself (connection handling, serialization, error handling) rather than duplicating business logic tests. Accept that these tests will be slower than unit tests.

### For E2E Tests

Reserve E2E tests for critical user journeys that generate revenue or are essential for core functionality. Use the Page Object pattern to isolate selectors from test logic. Create test data through APIs rather than the UI when possible. Accept some flakiness and build in appropriate retries and waits.

### For Test Data

Use factories for creating test objects with sensible defaults. Make test data minimal (only relevant fields), explicit (clearly test data), and meaningful (values relate to what's being tested). Use builders for complex objects with many optional configurations.

### For Mocking

Choose the right type of test double for your needs. Use dummies for unused parameters, stubs for predetermined return values, spies for call verification, mocks for interaction verification, and fakes for realistic behavior. Always use spec= to ensure mocks match interfaces.

## Integration with Architecture Framework

This testing framework complements the architecture framework. The testing rules reference architectural concepts like layers, boundaries, and domain objects. Test organization often mirrors source organization, which follows architectural boundaries.

When the architecture framework requires an ADR for significant changes, consider including test strategy implications. When new domains or services are created, create corresponding test structure and factories.

## Customization

The framework is designed to be customized for your specific needs. The placeholders in templates (marked with {PLACEHOLDER}) should be replaced with your project-specific values. Coverage thresholds can be adjusted based on your risk tolerance and codebase characteristics. Test pyramid distribution can shift based on your architecture (microservices might have more integration tests).

## Best Practices Summary

Write tests that verify behavior, not implementation. Each test should be independent and deterministic. Use factories and builders for test data management. Mock at system boundaries, not internal collaborators. Maintain the test pyramid distribution. Treat test code with the same quality standards as production code.

## Related Resources

This framework incorporates principles from established testing methodologies including Test-Driven Development (TDD), Behavior-Driven Development (BDD), the Testing Pyramid concept by Martin Fowler, Consumer-Driven Contract Testing, and the xUnit Test Patterns book by Gerard Meszaros.
