# Decision Documentation

How to capture decisions so your future self and your team don't waste time re-litigating things that were already settled.

---

## Why Document Decisions

Context loss is the enemy of velocity. People leave. People forget. People join mid-program and ask "why did we do it this way?" If the answer lives only in someone's memory, you'll spend time re-debating instead of building.

Good decision documentation does three things:
1. **Prevents re-litigation** — the rationale is on record
2. **Enables onboarding** — newcomers understand the "why" behind the current state
3. **Supports reversals** — when conditions change, you know what assumptions to re-examine

## When to Document a Decision

Simple threshold: **if more than one person needs to know about it, write it down.**

Always document:
- Architecture or technology choices
- Scope changes (what was added or cut, and why)
- Process changes (how the team works)
- Trade-offs (what you gave up and what you gained)
- Reversals (when you changed a previous decision)

Don't document:
- Trivial choices with no lasting impact
- Personal workflow preferences
- Anything that will be obvious from the code or config

## Decision Log Structure

### Entry Format

```markdown
## DEC-[number]: [Decision Title]

**Date:** [DATE]
**Decision Maker:** [OWNER]
**Status:** Proposed | Decided | Reversed

### Context

What situation prompted this decision? What problem were we solving?

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| Option A | [pros] | [cons] |
| Option B | [pros] | [cons] |
| Option C | [pros] | [cons] |

### Decision

We chose [Option X].

### Rationale

Why this option over the others. Be specific. Include data if you have it.

### Reversibility

- **Reversible:** Yes / No / Partially
- **Cost to reverse:** Low / Medium / High
- **Conditions for reversal:** [what would need to change]

### Consequences

- [Expected positive outcome]
- [Expected trade-off or risk accepted]
- [Follow-up actions required]
```

## Decision Log as a Living Document

Keep all decisions in a single, chronological log. Don't scatter them across meeting notes, Slack threads, and emails.

| ID | Decision | Date | Status | Owner |
|----|----------|------|--------|-------|
| DEC-001 | [Title] | [DATE] | Decided | [OWNER] |
| DEC-002 | [Title] | [DATE] | Decided | [OWNER] |
| DEC-003 | [Title] | [DATE] | Reversed | [OWNER] |

## Tips

- **Write the rationale while it's fresh** — you won't remember the nuance next week
- **Include what you rejected** — the "why not" is as important as the "why"
- **Link to the discussion** — Slack thread, document, meeting notes
- **Mark reversals explicitly** — don't delete old decisions, add a reversal entry that references the original
- **Review the log quarterly** — some decisions have expiration dates; check if assumptions still hold
