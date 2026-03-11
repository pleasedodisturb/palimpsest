# Program Overview: Apex API Platform Migration

**Program Lead:** Sam Chen (TPM)
**Start Date:** 2025-11-04
**Target Completion:** 2026-05-02
**Status:** At Risk

---

## Summary

Apex Corp is migrating its core API platform from a monolithic REST architecture (internally called "The Monolith" or just "mono") to a federated GraphQL platform built on Apollo Federation. The migration affects 23 internal services, 4 external partner integrations, and approximately 340 API endpoints.

The business driver is straightforward: the monolith can't scale to support the product roadmap. Mobile and web teams are spending 40% of their sprint capacity on API workarounds. Partner integrations take 3-4 months to build because every new integration touches the same codebase. The GraphQL platform should reduce integration time to 2-3 weeks and unblock the mobile team's Q3 roadmap.

## Current Status

We're at the end of Month 4 of a 6-month program. Phase 1 (Core Platform) shipped on time. Phase 2 (Service Migration) is in progress but behind schedule — 8 of 14 services migrated, with the remaining 6 blocked on the auth service rewrite.

The auth blocker is the biggest risk. The original plan assumed we could wrap the existing auth service with a GraphQL layer, but the token validation logic is too deeply coupled to the REST routing. We're now doing a partial rewrite, which added 3 weeks to the auth timeline. This cascades to everything downstream.

Data migration complexity was underestimated. The schema translation layer for the legacy PostgreSQL schemas is hitting edge cases we didn't anticipate — particularly around multi-tenant data isolation. The data team is handling it, but it's consuming capacity that was allocated for performance testing.

The good news: partner integrations for TechFlow and DataBridge are ahead of schedule. Both partners have been responsive and their engineering teams are competent. This buys us some slack on the overall timeline.

## Key Metrics

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Services migrated | 8/14 | 14/14 by Apr 11 | Slowing |
| API endpoints ported | 187/340 | 340/340 by Apr 25 | On track |
| Partner integrations live | 1/4 | 4/4 by May 02 | Ahead |
| P95 latency (GraphQL) | 142ms | <200ms | Stable |
| Error rate (new platform) | 0.3% | <0.5% | Improving |
| Test coverage (migrated) | 78% | >80% | Improving |

## Component Status

| Component | Owner | Status | Notes |
|-----------|-------|--------|-------|
| Core GraphQL Platform | Priya Sharma | On Track | Shipped Phase 1, stable in prod |
| Auth Service Migration | Marcus Webb | At Risk | Partial rewrite in progress, +3 weeks |
| Service Migration (batch 1) | Jun Tanaka | Complete | 8/8 services live |
| Service Migration (batch 2) | Jun Tanaka | Blocked | Waiting on auth service |
| Data Migration Layer | Aisha Okafor | At Risk | Schema edge cases consuming extra capacity |
| Partner Integration: TechFlow | Lisa Park | On Track | API testing phase, ahead of schedule |
| Partner Integration: DataBridge | Lisa Park | On Track | Contract signed, SDK delivered |
| Partner Integration: NexGen | Lisa Park | Not Started | Depends on auth completion |
| Partner Integration: CoreBank | Carlos Ruiz | At Risk | Security review pending, complex requirements |
| Performance & Load Testing | DevOps (Kai) | Not Started | Blocked on sufficient services being migrated |
| Documentation & Developer Portal | Sam Chen | In Progress | 60% complete, updating as services migrate |

## Active Blockers

| Blocker | Impact | Owner | Resolution ETA |
|---------|--------|-------|---------------|
| Auth service rewrite | Blocks batch 2 migration (6 services) and NexGen integration | Marcus Webb | Mar 28 |
| CoreBank security review | Blocks CoreBank integration — they require SOC 2 Type II evidence for the new platform | Carlos Ruiz + Legal | Apr 04 |
| Schema migration edge cases | Consuming data team capacity, delays performance testing start | Aisha Okafor | Mar 21 |

## Key Decisions

| Decision | Date | Rationale | Impact |
|----------|------|-----------|--------|
| Rewrite auth service instead of wrapping | 2026-02-14 | Token validation too coupled to REST routing; wrapper would create maintenance burden and security gaps | +3 weeks to auth timeline, but cleaner architecture |
| Defer CoreBank integration to Phase 3 if security review extends past Apr 04 | 2026-03-03 | CoreBank is the most complex partner with strictest requirements; delaying doesn't affect other partners | Reduces timeline risk if security review takes longer |
| Use Apollo Federation v2 over v1 | 2025-12-10 | Better entity resolution, @override directive, cleaner subgraph composition | Minor migration effort for existing subgraphs, but future-proofs the architecture |
| Keep monolith running in parallel until Jun 30 | 2026-01-20 | Risk mitigation — if migration has issues, we can route traffic back | Additional infra cost (~$12k/month) but dramatically reduces blast radius |
| Batch service migration into two groups | 2025-12-18 | Reduce risk by migrating independent services first, dependent services after auth | Batch 1 completed without issues, validated approach |

## Timeline

| Milestone | Target Date | Status | Notes |
|-----------|------------|--------|-------|
| Phase 1: Core Platform | 2026-01-17 | Complete | Shipped on schedule |
| Batch 1 Services (8) | 2026-02-28 | Complete | All 8 live, no incidents |
| Auth Service Migration | 2026-03-28 | At Risk | Was Mar 07, pushed due to rewrite |
| Batch 2 Services (6) | 2026-04-11 | At Risk | Blocked on auth |
| Partner Integrations (4) | 2026-05-02 | Mixed | TechFlow/DataBridge ahead; NexGen/CoreBank at risk |
| Performance Validation | 2026-04-18 | Not Started | Need 80%+ services migrated first |
| Monolith Decommission | 2026-06-30 | Not Started | Extended parallel run for safety |

## Team

| Role | Person | Responsibility |
|------|--------|---------------|
| TPM | Sam Chen | Overall delivery, stakeholder comms, risk management |
| Engineering Lead | Priya Sharma | Architecture, core platform, technical decisions |
| Auth Lead | Marcus Webb | Auth service rewrite, token migration |
| Migration Lead | Jun Tanaka | Service-by-service migration execution |
| Data Lead | Aisha Okafor | Schema migration, data integrity |
| Partner Lead | Lisa Park | TechFlow, DataBridge, NexGen integrations |
| Partner Lead (Financial) | Carlos Ruiz | CoreBank integration, compliance |
| DevOps | Kai Nakamura | Infrastructure, CI/CD, performance testing |
| PM | Dana Reeves | Product requirements, prioritization |
| VP Engineering (Sponsor) | Raj Patel | Executive sponsor, budget authority |

## Links

- **Jira Board:** APEX-MIGRATION
- **Slack Channel:** #apex-platform-migration
- **Architecture Docs:** Confluence > Engineering > Apex Platform
- **Runbooks:** Confluence > Engineering > Apex Runbooks
- **Incident Channel:** #apex-incidents (for migration-related issues)
