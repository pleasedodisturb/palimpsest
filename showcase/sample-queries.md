# Sample Queries

Deeper examples of how to interact with your program context through an AI agent. Organized by what you're trying to accomplish.

---

## Status Queries

### Current Program Health

```
What's the overall status of the program right now?
Summarize blockers, at-risk items, and anything that needs my attention today.
```

**Expected behavior:** Agent reads the dashboard and backlog, synthesizes status across workstreams, and highlights items that need action.

**Tip:** Ask follow-up questions to drill into specific areas — "Tell me more about the API integration blocker."

### Stakeholder-Ready Summary

```
I have a meeting with [stakeholder role] in 30 minutes.
Give me a 2-minute verbal summary of program status, tailored to what they care about.
```

**Expected behavior:** Agent adjusts the summary based on the audience — technical details for engineering leaders, business outcomes for executives, timeline and dependencies for project managers.

### Historical Context

```
What decisions have we made about [topic] and what was the rationale?
```

**Expected behavior:** Agent searches the decision log and related documents, returns a chronological summary of decisions with their rationale.

## Drafting Queries

### Weekly Update

```
Draft this week's stakeholder update. Pull data from the dashboard and backlog.
Flag anything where the status changed from last week.
```

**Tip:** Review the draft for accuracy before sending — the agent synthesizes, but you own the message.

### BRD from Scratch

```
I need a BRD for [initiative]. Here's the context: [paste context].
Draft the document using our template, and flag sections where you need more information.
```

**Expected behavior:** Agent creates a structured BRD with placeholders clearly marked for sections that need human input.

### Communication Draft

```
Draft a message to [audience] about [topic].
Tone: [direct/diplomatic/urgent]. Keep it under [N] sentences.
```

**Tip:** Specify the tone explicitly. "Tell the team we're cutting Feature X" produces very different drafts depending on whether you say "direct" vs "diplomatic."

## Analysis Queries

### Risk Identification

```
Review the current program state. What risks am I not tracking?
Look at dependencies, timeline pressure, and resource constraints.
```

**Expected behavior:** Agent examines the backlog, timeline, and dependencies to surface risks that aren't explicitly captured in the risk register.

### Dependency Mapping

```
Map all cross-team dependencies for [workstream].
For each, note: who owns it, what's the status, what happens if it's late.
```

**Expected behavior:** Agent traces dependencies from backlog items and documents, producing a structured dependency map.

### Trend Analysis

```
Compare the last 4 weekly updates. What trends do you see?
Are blockers getting resolved or accumulating? Is velocity stable?
```

**Expected behavior:** Agent reads historical updates and identifies patterns — improving areas, persistent blockers, velocity changes.

## Research Queries

### Context Gathering

```
I need to understand [topic] for an upcoming decision.
Search our documentation and summarize what we know, what we've tried, and what gaps exist.
```

**Expected behavior:** Agent searches across program documents, synthesizes findings, and identifies information gaps.

### Competitive/Prior Art

```
Have we dealt with a similar problem before?
Search for any past decisions, discussions, or documents about [topic].
```

**Tip:** This is especially powerful when program history spans months — the agent can surface context you've forgotten.

### Onboarding Context

```
A new person is joining [workstream]. Build a context package:
what they need to know, key documents to read, people to meet, current state of the workstream.
```

**Expected behavior:** Agent compiles a tailored onboarding brief pulling from program docs, team structure, and current backlog.

---

## Tips for Better Queries

1. **Be specific about format** — "as a table," "as bullet points," "as a Slack message"
2. **Specify the audience** — the same information is presented differently for different people
3. **Include constraints** — "keep it under 200 words," "focus on the last 2 weeks"
4. **Ask for gaps** — "what information are you missing to give a better answer?"
5. **Iterate** — the first response is a draft; refine with follow-up questions
