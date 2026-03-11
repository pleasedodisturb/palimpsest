# Dashboard: Apex API Platform Migration

**Last Updated:** 2026-03-11
**Overall Status:** At Risk

---

## At a Glance

| Metric | Value | Trend |
|--------|-------|-------|
| Overall progress | 54% | Slowing |
| Active blockers | 3 | Up (was 1 last week) |
| Items completed this week | 2 | Down (was 5) |
| Days to next milestone | 17 (Auth: Mar 28) | -- |
| Services in production | 8/14 | Flat |

## Health by Workstream

| Workstream | Status | One-liner |
|------------|--------|-----------|
| Core Platform | On Track | Stable, no incidents in 6 weeks |
| Auth Migration | At Risk | Rewrite at 60%, hitting token edge cases |
| Service Migration | Blocked | Batch 2 waiting on auth, team helping with data layer |
| Data Migration | At Risk | 3 schema edge cases remaining, ETA Mar 21 |
| Partner: TechFlow | On Track | API testing, launch next week |
| Partner: DataBridge | On Track | SDK delivered, integration in progress |
| Partner: NexGen | Blocked | Can't start without new auth |
| Partner: CoreBank | At Risk | Security review in legal limbo |
| Performance Testing | Not Started | Need 80%+ services first |

## Blockers

| Blocker | Severity | Owner | Age (days) | Action Needed |
|---------|----------|-------|-----------|---------------|
| Auth service rewrite behind | High | Marcus Webb | 25 | Daily standups, pair programming with Priya on token edge cases |
| CoreBank SOC 2 evidence request | Medium | Carlos Ruiz | 8 | Legal reviewing what we can share; meeting Thursday |
| Schema migration edge cases | Medium | Aisha Okafor | 12 | 3 remaining cases, Jun's team helping |

## This Week

### Completed

- DataBridge SDK delivered and accepted by partner team
- Migrated notification preferences endpoint (was the last easy one)

### In Progress

| Item | Owner | ETA | Status |
|------|-------|-----|--------|
| Auth token validation rewrite | Marcus Webb | Mar 28 | At Risk — 60% done |
| Multi-tenant schema isolation fix | Aisha Okafor | Mar 21 | In Progress — 3 cases left |
| TechFlow integration testing | Lisa Park | Mar 18 | On Track |
| Developer portal documentation | Sam Chen | Mar 25 | On Track — 60% complete |
| CoreBank security review prep | Carlos Ruiz | Mar 14 | Waiting on legal |

### Blocked

| Item | Blocked By | Impact |
|------|-----------|--------|
| Batch 2 service migration (6 services) | Auth service rewrite | Delays overall completion by 3+ weeks |
| NexGen partner integration | Auth service rewrite | Can't onboard partner without new auth flow |
| Performance/load testing | Need 80%+ services on new platform | Can't validate platform at scale |

## Key Dates

| Date | Event | Status |
|------|-------|--------|
| Mar 18 | TechFlow integration go-live | On Track |
| Mar 21 | Schema edge cases resolved (target) | At Risk |
| Mar 28 | Auth service rewrite complete (target) | At Risk |
| Apr 04 | CoreBank security review deadline | At Risk |
| Apr 11 | All services migrated (target) | At Risk |
| Apr 18 | Performance validation complete | Depends on above |
| May 02 | Program completion (original target) | At Risk |

## Decisions Needed This Week

1. **CoreBank fallback plan:** If security review isn't resolved by Apr 04, do we defer to Phase 3 (already pre-approved) or push the whole program timeline? Need Raj's input.
2. **Auth scope reduction:** Marcus is asking whether we can ship auth with a subset of token types and handle legacy tokens via the monolith proxy. Reduces scope but adds operational complexity.

## Quick Links

- [Program Overview](PROGRAM_OVERVIEW.md)
- [Backlog](BACKLOG.md)
- [Stakeholder Update Template](templates/STAKEHOLDER_UPDATE.md)
