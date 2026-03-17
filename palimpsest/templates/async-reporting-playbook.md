# Async-First Reporting Playbook

**Program:** [YOUR-PROJECT]
**Owner:** [OWNER]
**Established:** [DATE]

---

## Core Principles

### 1. Broadcast, Don't Request

Information should flow outward automatically. If someone has to ask "what's the status?" — the reporting system has failed. Push updates on a cadence. Make them findable. Never make people chase you.

### 2. Decisions at Execution Level

The people closest to the work make the decisions. Escalate only when you need authority you don't have, resources you can't access, or cross-team alignment you can't drive yourself. Everything else — just decide, document, and move on.

### 3. Signal Over Noise

Every update should answer: what changed, what's blocked, what needs a decision. If nothing changed, say so in one line. Don't pad updates to look busy. Brevity earns trust.

## Communication Channels

| Channel | Purpose | Cadence | Audience |
|---------|---------|---------|----------|
| [status-channel] | Automated status broadcasts | Daily/Weekly | Full team + stakeholders |
| [team-channel] | Working discussions, quick decisions | Continuous | Core team |
| [escalation-channel] | Blockers needing leadership input | As needed | Leadership + TPM |
| [document-repo] | Persistent documentation | Updated as needed | Everyone |

## Weekly Cadence

| Day | Activity | Owner | Output |
|-----|----------|-------|--------|
| Monday | Review priorities, update backlog | [OWNER] | Updated backlog |
| Tuesday | Check metrics, identify blockers | [OWNER] | Blocker list |
| Wednesday | Mid-week pulse (optional) | [OWNER] | Quick status post |
| Thursday | Prep stakeholder update | [OWNER] | Draft update |
| Friday | Publish weekly update, update dashboard | [OWNER] | Stakeholder update + dashboard |

## Update Format

Use this structure for all async updates:

```
Status: On Track | At Risk | Blocked

What happened:
- [completed items]

What's next:
- [upcoming items]

Blocked:
- [blocker] — need [specific action] from [person]

Decision needed:
- [decision] — options: [A] vs [B], recommend [X]
```

## Automation Opportunities

| Task | Manual Effort | Automation Approach |
|------|--------------|-------------------|
| Status compilation | 30-60 min/week | Pull from project tracker, auto-format |
| Metrics collection | 15-30 min/week | API queries, dashboard refresh |
| Stakeholder update | 45-60 min/week | Template + auto-populated data |
| Meeting notes distribution | 10-15 min/meeting | Auto-summary and broadcast |

## Escalation Ladder

### Level 0 — Self-Serve

- Information is in the dashboard or status channel
- No action needed from anyone else
- "Check the dashboard" is a valid answer

### Level 1 — Async Escalation

- Post in the escalation channel with context, impact, and ask
- Tag the specific person who can help
- Set a response deadline (usually 24h)
- If no response by deadline, escalate to Level 2

### Level 2 — Synchronous Escalation

- Schedule a focused call (15 min max)
- Pre-share context document before the call
- Come with a recommendation, not just a problem
- Document the outcome immediately after

## Anti-Patterns to Avoid

- **Status meetings as the only information channel** — if the meeting is cancelled, information shouldn't stop flowing
- **Updates that only go up** — the team needs visibility too
- **"Let's discuss live" for everything** — most things can be resolved async with good context
- **Weekly updates that require reading 10 documents** — summarize, link, let people drill down

## Measuring Success

You know async reporting is working when:

- Leadership stops asking "what's the status?"
- Team members can find answers without asking someone
- Meetings are for decisions, not information transfer
- New team members can get context without a 1-hour onboarding call
