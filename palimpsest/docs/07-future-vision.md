# Where This Could Go

## The Current State

Right now, Palimpsest is a human-driven system with AI assistance. You maintain the repo. You ask the AI questions. You review the output. The AI is a tool, not an agent.

This is the right starting point. You have to understand the manual process before you can automate it well. Every time I've tried to skip ahead to automation without deeply understanding the workflow, I've automated the wrong thing.

But the manual phase isn't the end state.

## The Personal AI Assistant Vision

The end state is a personal AI assistant that knows your program as well as you do — maybe better, because it doesn't forget things — and proactively manages the information layer so you can focus on the human layer.

Not a chatbot. Not a dashboard. An assistant that works alongside you throughout the day, handling the context management so you can handle the relationships, decisions, and strategy.

## Multi-Agent Rhythm

The future architecture is a set of specialized agents, each triggered at natural program management moments:

### Pre-Day Agent

- **Trigger**: 30 minutes before your first meeting
- **Sources**: Overnight Slack activity, Jira ticket changes, email digests, calendar for today
- **Output**: Morning briefing — what changed, what's on your plate, what needs attention
- **Key behavior**: Surfaces only what matters. Filters noise aggressively.

### Pre-Meeting Agent

- **Trigger**: 5 minutes before each calendar event
- **Sources**: Meeting agenda, attendee list cross-referenced with CONTEXT_INDEX.md, relevant program docs, previous meeting notes with same group
- **Output**: Meeting prep card — context you need, open items from last time, suggested talking points
- **Key behavior**: Knows who's in the meeting and what they care about.

### Post-Meeting Agent

- **Trigger**: Meeting ends (or you paste raw notes)
- **Sources**: Your raw notes, previous action items, decision log
- **Output**: Structured meeting notes, updated action items, new decisions logged, follow-up tasks created
- **Key behavior**: Compares new decisions against existing decisions and flags contradictions.

### End-of-Day Agent

- **Trigger**: End of your working day
- **Sources**: Everything that happened today — meetings, commits, Slack, Jira updates
- **Output**: Daily digest committed to repo, updated DASHBOARD.md, tomorrow's priority suggestions
- **Key behavior**: Commits the day's state to git. Tomorrow's Pre-Day Agent picks up where this one left off.

## Bidirectional Sync

Currently, most integrations are one-directional: pull data INTO the repo. The future is bidirectional:

- Meeting note generates action items. Action items automatically become Jira tickets.
- Risk register update triggers a Slack notification to the relevant owner.
- Dashboard status change triggers a Confluence page update.
- Stakeholder update draft goes directly to Google Docs for collaborative editing.

The repo becomes the orchestration layer. Changes flow out to the tools people already use, so nobody has to change their workflow to benefit from yours.

## Agent Orchestration via Memory Bank

The Memory Bank (sessionLog.md, activeContext.md, progress.md) currently exists for human-AI session continuity. In the future, it becomes the coordination layer between agents.

Pre-Meeting Agent writes context. Post-Meeting Agent reads it and builds on it. End-of-Day Agent synthesizes across all of them. Pre-Day Agent reads yesterday's End-of-Day output.

No agent starts from scratch. Every agent picks up where the last one left off. The Memory Bank is the handoff protocol.

This is where the "as Code" part of Program-as-Code becomes most powerful. Because the state is in files and the handoff protocol is in files, the coordination between agents is just file I/O. No complex message passing systems. No pub/sub infrastructure. One agent writes a file. The next agent reads it. Git tracks everything.

## The Invisible TPM

Here's the philosophical endpoint: the best TPM work is invisible. Nobody notices when information flows smoothly, when risks are flagged early, when stakeholders get the right update at the right time. They only notice when those things don't happen.

AI-augmented program management pushes more of the visible busywork (status updates, meeting notes, context gathering) into the background, freeing the TPM to do the invisible work (relationship building, risk intuition, strategic alignment) that actually determines whether programs succeed or fail.

The tools should disappear. The program should just... work.

We're not there yet. But every piece of this vision is technically feasible with current technology. It's an engineering and integration problem, not a research problem.

## What Needs to Happen

Concretely, three things need to mature:

1. **Reliable scheduling**: AI agents need to run on cron-like triggers without babysitting. Today's tools (Claude Code with task scheduling, GitHub Actions, etc.) are close but not quite seamless.
2. **Approval workflows**: A lightweight way for the AI to propose an action and wait for human approval. Not a full ticketing system — something closer to a mobile notification with approve/reject buttons.
3. **Cross-tool authentication**: The OAuth/API token management across Google, Atlassian, Slack, and GitHub needs to be more robust. See [Known Issues](08-known-issues.md) for why this is still painful.

None of these are unsolvable. They're just not solved yet in a way that a non-engineer TPM can set up in an afternoon.

---

Previous: [FAQ](06-faq.md) | Next: [Known Issues](08-known-issues.md)
