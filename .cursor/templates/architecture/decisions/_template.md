# ADR-{NUMBER}: {TITLE}

## Status

Proposed

## Date

{YYYY-MM-DD}

## Context

{Describe the situation that requires a decision. Be specific about:

- The problem or opportunity that exists
- The forces at play (technical, business, organizational)
- The constraints that apply (time, resources, existing systems)
- Why this decision needs to be made now
- What happens if we don't decide

Provide enough context that someone unfamiliar with the project can understand the situation.}

## Decision

We will {state the decision clearly and unambiguously}.

{Expand on the decision with key details:
- What specifically will be implemented
- What boundaries or scope apply
- What is explicitly NOT part of this decision}

## Alternatives Considered

### Alternative 1: {Name}

{Brief description of this approach}

**Pros**:
- {Benefit 1}
- {Benefit 2}

**Cons**:
- {Drawback 1}
- {Drawback 2}

**Why rejected**: {Specific reason this alternative was not chosen}

### Alternative 2: {Name}

{Brief description of this approach}

**Pros**:
- {Benefit 1}
- {Benefit 2}

**Cons**:
- {Drawback 1}
- {Drawback 2}

**Why rejected**: {Specific reason this alternative was not chosen}

### Alternative 3: Do Nothing

{Description of status quo}

**Pros**:
- No implementation effort
- No risk of new bugs

**Cons**:
- {Problem remains unsolved}
- {Technical debt accumulates}

**Why rejected**: {Why the current state is unacceptable}

## Consequences

### Positive

- {Benefit that will result from this decision}
- {Another positive outcome}
- {Long-term advantage}

### Negative

- {Drawback or cost of this decision}
  - **Mitigation**: {How we will address this}
- {Another negative consequence}
  - **Mitigation**: {How we will address this}

### Neutral

- {Side effect that is neither clearly good nor bad}
- {Trade-off that shifts complexity rather than eliminating it}

## Implementation Notes

{Optional section. Include if there are important implementation details.}

### Phase 1: {Name}

- Duration: {Estimate}
- Scope: {What will be done}
- Verification: {How we know it's complete}

### Phase 2: {Name}

- Duration: {Estimate}
- Scope: {What will be done}
- Verification: {How we know it's complete}

### Migration Considerations

{If this replaces existing functionality:
- How will existing data be migrated?
- How will backward compatibility be maintained?
- What is the rollback plan?}

## References

- RFC: {Link to RFC if this ADR originated from an RFC}
- Related ADRs: {Links to related decisions}
- External Resources: {Links to documentation, articles, or research}
- Tickets: {Links to related issues or stories}

## Derived Rules

{After this ADR is accepted, list the rules that derive from it}

- `architecture.mdc`: {ARCH-XXX - brief description}
- `patterns.mdc`: {PAT-XXX - brief description}
- `constraints.mdc`: {CON-XXX - brief description}
- `conventions.mdc`: {CONV-XXX - brief description}

---

## Review History

| Date | Reviewer | Decision | Notes |
|------|----------|----------|-------|
| {YYYY-MM-DD} | {Name} | {Approved/Requested Changes} | {Brief note} |
