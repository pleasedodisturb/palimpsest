# Weekly Status Update — March 7, 2026

**Program:** Apex API Platform Migration
**Status:** At Risk (was: On Track)
**Sent to:** Raj Patel (VP Eng), Dana Reeves (PM), Engineering Leads

---

## Summary

Batch 1 service migration is nearly complete (7/8 done, last one shipping Monday). Partner integrations ahead of schedule — DataBridge SDK delivered today. However, the auth service rewrite is now estimated at +3 weeks over original plan, which blocks batch 2 migration and cascades to program timeline. Recommending we hold the May 2 target but flag it as at risk.

## Completed This Week

- Content-service migration shipped (7th of 8 batch 1 services)
- DataBridge partner SDK delivered and accepted
- Auth rewrite: JWT and API key validation working in new service
- Schema migration: 1 of 4 remaining edge cases resolved

## In Progress

- Auth service rewrite — 50% complete, revised ETA Mar 28
- Schema migration edge cases — 3 remaining
- TechFlow integration testing — on track for Mar 18 go-live
- Developer portal documentation — 55% complete

## Blocked

| Issue | Impact | Action Needed | Owner |
|-------|--------|---------------|-------|
| Auth service rewrite (scope increase) | Blocks 6 services + NexGen partner | No action needed — Marcus is on it, timeline adjusted | Marcus Webb |
| CoreBank security review | Blocks CoreBank integration | Their team is unresponsive; escalating through account manager | Carlos Ruiz |

## Risks

1. **Auth rewrite timeline (HIGH):** If auth slips past Mar 28, the entire program timeline shifts. Mitigation: Priya available to pair program, batch 2 team redirected to help where possible.
2. **CoreBank security review (MEDIUM):** If no response by Mar 14, recommend deferring to Phase 3. Pre-approved fallback ready.
3. **Performance testing window (LOW):** Currently squeezed. If services aren't at 80% by Apr 11, we may need to extend the parallel run period.

## Decision Needed

**CoreBank fallback trigger date.** Current proposal: if security review isn't resolved by Apr 4, defer to Phase 3. Raj — does this timing work for you, or do you want to give them more runway?

## Next Week Focus

1. Ship preferences-service (last batch 1 service)
2. Auth rewrite: OAuth refresh token path
3. CoreBank escalation through account manager
4. TechFlow integration final testing

---

*Generated from program state on 2026-03-07. Reviewed and edited by Sam Chen.*
