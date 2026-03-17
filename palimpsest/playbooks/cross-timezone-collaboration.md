# Cross-Timezone Collaboration

How to run a program across time zones without defaulting to "let's find a time that works for everyone" (it never does).

---

## The Problem

Distributed teams default to synchronous habits designed for co-located work. The result: meetings at painful hours, decisions that wait for overlap windows, and half the team always feeling out of the loop.

## Async-First Philosophy

The default communication mode is async. Synchronous time is expensive — it requires coordination, interrupts flow, and excludes someone if you have more than two time zones.

**Sync is for:**
- Decisions that need real-time debate
- Relationship building
- Complex problem-solving where back-and-forth would take days async

**Everything else is async.**

## Overlap Windows

### Map Your Overlaps

For each time zone pair, identify the overlap window. Then protect it.

| Zone Pair | Overlap Window | Use For |
|-----------|---------------|---------|
| [Zone A] + [Zone B] | [time range] | [primary use] |
| [Zone B] + [Zone C] | [time range] | [primary use] |
| [Zone A] + [Zone C] | [time range] | [primary use] |

### Rotation Strategy

If overlap is thin (under 2 hours), rotate meeting times so the same people aren't always inconvenienced. Track whose turn it is.

- Week 1: Meeting at time favorable to Zone A
- Week 2: Meeting at time favorable to Zone B
- Week 3: Meeting at time favorable to Zone C
- Repeat

## Async Handoff Format

When you finish your work day and hand off to the next time zone, post a structured update:

```
Handoff — [Date]

Done today:
- [what you completed]

In progress:
- [what's mid-flight, where you left off]

Needs input:
- [specific question for specific person]

Blocked on:
- [what you can't proceed without]

Context:
- [anything the next person needs to know]
```

Post this in the team channel, not a DM. Everyone benefits from visibility.

## Meeting Guidelines

### Before Scheduling a Meeting

Ask:
1. Can this be resolved in a document or thread? If yes, do that.
2. Does this need real-time discussion? If no, do it async.
3. Who actually needs to be there? Invite only them.

### When You Must Meet

- **Max 30 minutes** — if it needs longer, break it into parts
- **Pre-read required** — share context 24h before, expect people to read it
- **Record everything** — someone will miss it, make that painless
- **Decisions in writing** — post the outcome in the channel within 1 hour
- **Notes are non-negotiable** — no notes means the meeting didn't happen

### Standing Meetings

Keep the minimum viable set:

| Meeting | Cadence | Duration | Purpose |
|---------|---------|----------|---------|
| Team sync | Weekly | 25 min | Blockers, decisions, alignment |
| Stakeholder update | Bi-weekly | 25 min | Progress, risks, asks |
| 1:1s | Weekly | 25 min | Individual support, feedback |

Everything else should justify its existence quarterly.

## Tools and Practices

### Documentation as the Source of Truth

- Decisions live in the decision log, not in Slack threads
- Status lives in the dashboard, not in someone's head
- Context lives in shared docs, not in meeting recordings

### Async Decision-Making

1. Post the decision with context, options, and your recommendation
2. Set a deadline for input (usually 24-48h)
3. If no objections by deadline, the recommendation stands
4. Document the outcome

### Time Zone Etiquette

- Don't expect immediate responses outside someone's working hours
- Use scheduled sends for non-urgent messages
- Mark messages as urgent only when they genuinely are
- Respect "do not disturb" hours — your urgency is not their emergency

## Common Pitfalls

- **"Quick sync" culture** — quick syncs multiply and eat all overlap time
- **Decisions only in meetings** — excludes async contributors
- **Recording-dependent** — if people have to watch a 45-min recording to stay informed, the meeting format is wrong
- **Hero hours** — one person consistently taking the bad time slot erodes trust and burns people out
