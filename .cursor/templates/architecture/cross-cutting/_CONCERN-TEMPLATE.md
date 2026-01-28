# {Concern Name} Architecture

> **Document Type**: Cross-Cutting Concern (Level 2)
> **Parent**: [System Architecture](../../ARCHITECTURE.md)
> **Last Updated**: {YYYY-MM-DD}
> **Owner**: {Team Name}

## Purpose

This document defines the **{Concern Name}** patterns, policies, and implementations that apply across all domains. Individual domains must comply with these standards and may extend them with domain-specific requirements.

## Scope

### What This Document Covers

- {Concern}-related principles and policies
- Standard patterns and implementations
- Compliance requirements
- Integration guidelines for domains

### What This Document Does NOT Cover

- Domain-specific business logic
- Implementation details within domains
- Infrastructure configuration (see [Infrastructure](../platform/infrastructure/ARCHITECTURE.md))

## Principles

### Principle 1: {Name}

{Description of the principle and why it matters}

**Application**: {How this principle is applied in practice}

### Principle 2: {Name}

{Description}

## Standards

### Standard {CC}-001: {Name}

**Requirement**: {Clear statement of what must be done}

**Rationale**: {Why this standard exists}

**Implementation**:
```
{Code or configuration example}
```

**Verification**: {How compliance is verified}

### Standard {CC}-002: {Name}

{Repeat structure}

## Patterns

### Pattern: {Pattern Name}

**Context**: {When to use this pattern}

**Problem**: {What problem it solves}

**Solution**: {How it solves the problem}

**Implementation**:
```
{Code example}
```

**Consequences**:
- Positive: {Benefits}
- Negative: {Trade-offs}

## Domain Integration

### Required Integration Points

Every domain MUST implement:

1. {Integration requirement 1}
2. {Integration requirement 2}
3. {Integration requirement 3}

### Integration Checklist

For each domain, verify:

- [ ] {Checklist item 1}
- [ ] {Checklist item 2}
- [ ] {Checklist item 3}

## Compliance

### Regulatory Requirements

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| {Regulation} | {What it requires} | {How we comply} |

### Audit Trail

| Event | What's Logged | Retention |
|-------|---------------|-----------|
| {Event type} | {Fields logged} | {Period} |

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| {Metric} | {What it measures} | {When to alert} |

### Dashboards

- [{Concern} Overview Dashboard]({link})
- [{Concern} Details Dashboard]({link})

## Incident Response

### {Concern}-Related Incidents

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 15 minutes | {Who} |
| High | 1 hour | {Who} |
| Medium | 4 hours | {Who} |

### Runbooks

| Scenario | Runbook |
|----------|---------|
| {Scenario 1} | [→ Runbook](./runbooks/{scenario}.md) |

## Related Decisions

| ADR | Date | Summary |
|-----|------|---------|
| [ADR-XXX](../../decisions/ADR-XXX.md) | {Date} | {Title} |

## References

- [System Architecture](../../ARCHITECTURE.md)
- {External standards or documentation}
