# Backlog: Apex API Platform Migration

**Last Updated:** 2026-03-11

---

## This Week

| Priority | Item | Owner | Status |
|----------|------|-------|--------|
| P0 | Auth token validation rewrite | Marcus Webb | In Progress (60%) |
| P0 | Multi-tenant schema isolation (3 edge cases) | Aisha Okafor | In Progress |
| P1 | TechFlow integration test suite completion | Lisa Park | In Progress |
| P1 | CoreBank SOC 2 evidence package | Carlos Ruiz | Blocked (legal) |
| P1 | Developer portal: auth section | Sam Chen | In Progress |
| P2 | DataBridge partner onboarding call | Lisa Park | Scheduled Thu |

## Next Week

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| P0 | Auth service: integration testing with batch 2 services | Marcus + Jun | Only if rewrite hits 90%+ |
| P0 | Begin batch 2 migration: user-service, billing-service | Jun Tanaka | Depends on auth |
| P1 | TechFlow go-live | Lisa Park | Target Mar 18 |
| P1 | Schema migration: final validation pass | Aisha Okafor | After edge cases resolved |
| P1 | Developer portal: migration guide for internal teams | Sam Chen | Unblocks self-service migration |
| P2 | Performance test plan review | Kai Nakamura | Prep for when services are ready |

## Backlog (Unprioritized)

- NexGen partner kickoff — blocked on auth, no point scheduling until auth has a firm date
- Rate limiting configuration for GraphQL gateway — Priya flagged this as important before go-live
- Deprecation notices for monolith API consumers — need comms plan, 47 internal consumers
- Monitoring dashboard for federated gateway — Kai has a draft, needs review
- Cost analysis: new platform vs monolith (infra) — Raj asked for this by end of program
- Internal developer survey: migration experience — Dana wants to run this after batch 2
- Runbook updates for on-call team — need to cover federated gateway failure modes

## Parked

Items deprioritized or waiting on dependencies:

- **gRPC support for internal services** — Originally in scope, cut in Dec sprint planning. Revisit in H2. Nobody has bandwidth and the REST-to-GraphQL path is sufficient for now.
- **Real-time subscriptions (WebSocket)** — Product wants this but it's a Phase 2 feature. Not doing it during migration.
- **Multi-region gateway deployment** — Infra team asked for this. Deferred to post-migration. One region is fine for current traffic.
- **Automated canary deployments for subgraphs** — Nice to have. Kai has a design doc but it's not blocking anything.

## Done

| Item | Completed | Notes |
|------|-----------|-------|
| Phase 1: Core GraphQL platform deployment | 2026-01-17 | Apollo Router + Federation v2, running in prod |
| Batch 1: catalog-service migration | 2026-02-03 | First service, proved the pattern |
| Batch 1: search-service migration | 2026-02-07 | Cleanest migration, good template |
| Batch 1: inventory-service migration | 2026-02-12 | Minor schema adjustments needed |
| Batch 1: pricing-service migration | 2026-02-14 | Discovered auth coupling issue during this one |
| Batch 1: notification-service migration | 2026-02-19 | Required webhook refactor |
| Batch 1: analytics-service migration | 2026-02-21 | Read-only, straightforward |
| Batch 1: content-service migration | 2026-02-26 | CMS integration needed attention |
| Batch 1: preferences-service migration | 2026-03-10 | Last of batch 1 |
| TechFlow partner SDK delivery | 2026-02-28 | Partner happy with the SDK |
| DataBridge partner SDK delivery | 2026-03-07 | Accepted, integration started |
| Decision: auth rewrite vs wrapper | 2026-02-14 | Chose rewrite after wrapper POC failed |
| Decision: defer CoreBank if needed | 2026-03-03 | Pre-approved by Raj |
| Apollo Federation v2 upgrade | 2025-12-10 | Smooth upgrade, no issues |
