# The Ultimate Vision: Personal AI Assistant

## What This Actually Means

Not Siri. Not Alexa. Not a chatbot that answers questions about your calendar.

A persistent, context-aware agent that understands your program at a deep level, operates continuously throughout your day, and handles the information management layer of program management so you can focus on the human layer.

Think of it as a junior TPM who never sleeps, never forgets, reads every document, and has no ego about being corrected.

## Full Configuration Vision

The assistant would be configured through a single file in your repo, something like:

```yaml
assistant:
  name: "tpm-buddy"
  program: "CRM Migration"
  owner: "vitalik"

  data_sources:
    - type: repo
      path: "."
      priority: 1
    - type: google_calendar
      calendars: ["primary", "team-shared"]
      priority: 2
    - type: slack
      channels: ["#your-team", "#your-engineering", "#your-stakeholders"]
      priority: 3
    - type: jira
      project: "YOUR-PROJECT-KEY"
      priority: 4
    - type: confluence
      space: "MCRM"
      priority: 5

  output_targets:
    - type: repo_commit
      auto: true
    - type: confluence
      requires_approval: true
    - type: slack
      requires_approval: true
    - type: jira
      requires_approval: true
```

The config defines what the assistant can read (everything) and what it can write (selectively, with approval gates).

## Agent Phases

### Morning Briefing

| Aspect | Detail |
|--------|--------|
| Trigger | 30 min before first calendar event |
| Sources | Overnight Slack, Jira changes, email digests, calendar |
| Output | Briefing committed to `docs/context/daily-digests/YYYY-MM-DD.md` |
| Approval | None needed — it's writing to your private repo |

The briefing answers: What changed while I was offline? What's on my calendar today? What needs my attention before each meeting?

### Pre-Meeting Prep

| Aspect | Detail |
|--------|--------|
| Trigger | 5 min before each calendar event |
| Sources | Meeting invite, attendee CONTEXT_INDEX entries, previous notes with same group, open action items |
| Output | Meeting prep card pushed to your editor or notification |
| Approval | None needed — it's for your eyes only |

The prep card answers: What's the context for this meeting? What did we discuss last time? What's still open? What should I bring up?

### Post-Meeting Processing

| Aspect | Detail |
|--------|--------|
| Trigger | You paste raw notes or a transcript lands in the repo |
| Sources | Raw notes, transcript, previous meeting context, decision log |
| Output | Structured notes, updated action items, decision log entries |
| Approval | Required before any external publish (Confluence, Jira ticket creation) |

This is where the assistant earns its keep. Turning raw meeting chaos into structured, actionable artifacts in minutes instead of the 20 minutes it takes manually.

### End-of-Day Wrap

| Aspect | Detail |
|--------|--------|
| Trigger | End of working hours (configurable) |
| Sources | All of today's activity — meetings, commits, Slack, Jira |
| Output | Daily digest, updated DASHBOARD.md, suggested tomorrow priorities |
| Approval | None for repo commits. Required for any external notifications. |

The wrap answers: What happened today? What's the program state now? What should tomorrow-me focus on?

## Todo Integration

Action items are the lifeblood of program management. The assistant would:

1. Extract action items from meeting notes automatically
2. Track them in a structured file (`docs/action-items.md`)
3. Match them against Jira tickets (create new ones with approval)
4. Flag overdue items in the morning briefing
5. Include status in stakeholder updates

No more action items living in meeting notes that nobody re-reads.

## Calendar Awareness

The assistant understands your calendar as a source of program rhythm:

- Recurring meetings mapped to workstreams
- Prep triggered by calendar events, not manual prompts
- Time blocks protected for focus work
- Meeting frequency used as a signal (too many syncs on one workstream = it's probably in trouble)

## The Control Principle: AI Proposes, Human Disposes

This is the non-negotiable design principle: **the assistant proposes, you decide**.

- It drafts the stakeholder update. You edit and send.
- It suggests creating a Jira ticket. You approve or dismiss.
- It flags a risk. You decide whether to escalate.
- It recommends canceling a meeting. You make the call.

The assistant never acts externally without explicit approval. Internal repo operations (commits, file updates) can be automated. Anything that touches another human (Slack message, Confluence publish, Jira ticket) requires your sign-off.

This isn't just a safety measure. It's philosophically important. The TPM's value is judgment, relationships, and accountability. Those can't be delegated to AI. Everything else can.

## Current State vs. Aspiration

Let's be honest about the gap:

| Capability | Current State | Aspiration |
|-----------|---------------|------------|
| Morning briefing | Manual prompt in editor | Automatic, pre-generated |
| Meeting prep | Manual prompt, hit-or-miss | Calendar-triggered, consistent |
| Meeting notes | Paste + prompt | Auto-capture from transcript |
| Action item tracking | In meeting notes, manually | Extracted, tracked, synced |
| Stakeholder updates | AI-drafted, manually triggered | Auto-drafted on schedule |
| Risk detection | Manual, prompt-based | Continuous, pattern-based |
| Cross-tool sync | Script-based, manual trigger | Event-driven, real-time |

Every item in the "Current State" column works today. It's just manual. The aspiration column is automation of triggers and workflows.

The building blocks exist. The integration work is what's left. It's plumbing, not research.

---

Previous: [Known Issues](08-known-issues.md) | Next: [Privacy Model](10-privacy-model.md)
