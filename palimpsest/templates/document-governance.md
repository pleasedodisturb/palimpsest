# Document Governance: [YOUR-PROJECT]

**Owner:** [OWNER]
**Established:** [DATE]
**Last Reviewed:** [DATE]

---

## Why This Matters

Documentation rots faster than code. Without explicit ownership and review cadence, documents become misleading artifacts — worse than no documentation at all, because people trust them.

## Document Status Definitions

| Status | Meaning | Action Required |
|--------|---------|----------------|
| **Active** | Current, accurate, maintained | Review on cadence |
| **Needs Update** | Known gaps or outdated sections | Owner updates within 2 weeks |
| **Obsolete** | Superseded by newer document | Mark clearly, link to replacement |
| **Abandoned** | No owner, no maintenance | Archive or assign new owner |

Every document header should include: Owner, Status, Last Updated, Next Review.

## Ownership Model

### Roles

- **Creator:** Writes the initial version. Becomes the default maintainer unless reassigned.
- **Maintainer:** Keeps the document accurate. Responsible for review cadence. Can delegate but not abdicate.
- **Reviewer:** Provides periodic feedback on accuracy and relevance. Domain expert, not necessarily the writer.

### Rules

- Every document has exactly one maintainer (not a team — a person)
- When a maintainer leaves the project, ownership transfers explicitly in writing
- Orphaned documents get flagged in monthly review and either adopted or archived

## Review Cadence

### Monthly Light Review

- **What:** Skim for obvious inaccuracies, broken links, outdated references
- **Who:** Maintainer
- **Time:** 10-15 minutes per document
- **Output:** Status updated, minor fixes applied

### Quarterly Deep Review

- **What:** Full accuracy check, structural assessment, relevance evaluation
- **Who:** Maintainer + Reviewer
- **Time:** 30-60 minutes per document
- **Output:** Updated content, status confirmed, next quarter's review scheduled

## Document Lifecycle

```
BRD (Business Requirements)
  |
  v
PRD (Product Requirements)
  |
  v
Technical Design / Architecture
  |
  v
Tickets / User Stories
  |
  v
Runbooks / Operational Docs
```

Each level should trace back to the one above it. If a PRD can't point to a BRD, either the BRD is missing or the PRD is solving a problem nobody agreed on.

## Document Registry

Maintain a central index of all program documents:

| Document | Owner | Status | Last Updated | Next Review | Location |
|----------|-------|--------|-------------|-------------|----------|
| [Document 1] | [OWNER] | Active | [DATE] | [DATE] | [link] |
| [Document 2] | [OWNER] | Active | [DATE] | [DATE] | [link] |
| [Document 3] | [OWNER] | Needs Update | [DATE] | [DATE] | [link] |

## Maintenance Guidelines

- **Update immediately** when a decision changes the content
- **Don't create new docs** when updating existing ones would suffice
- **Archive, don't delete** — someone might need the historical context
- **Link, don't duplicate** — one source of truth per topic
- **Date everything** — "recently" and "soon" become meaningless within weeks
