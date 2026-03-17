# Before & After

What program management actually looks like — with and without Palimpsest.

---

## The Meeting

A single cross-team sync meeting. Not a big deal, right? Just a meeting. Here's what it actually takes.

### Before: The 47-Step Meeting Dance

You need to run a cross-team sync about the migration status. Here's what happens:

**Prep (3-4 hours across 2 days):**

1. Open Confluence. Find the last meeting notes. Read them. Remember what was decided.
2. Open Jira. Filter by your project. Sort by status. Cross-reference with what Confluence says.
3. Open Slack. Search for #project-channel. Scroll through 3 days of messages to find what happened since the last meeting.
4. Check Google Drive for any docs people shared that didn't make it to Confluence.
5. Draft an agenda in Google Docs.
6. Share the agenda doc with all attendees.
7. Block prep time on everyone's calendar so they actually read it.
8. Add a Google Task to each attendee's calendar: "Review agenda before sync."
9. Add a reminder to your own task list to ping people who haven't read it.
10. Two hours before the meeting, check who opened the doc. Ping the rest on Slack.
11. Review your own agenda one more time. Add anything that came up since you wrote it.

**The Meeting (1 hour):**

12. Start the meeting. Wait 4 minutes for stragglers.
13. Enable transcription. Get consent from attendees.
14. Warn anyone who joined late that it's being recorded.
15. Walk through the agenda.
16. Take notes in a separate doc while also facilitating. Somehow.
17. Capture action items as they come up. Miss at least one.
18. Agree on next steps. Realize you forgot to discuss one agenda item.

**Post-Meeting (2-3 hours across 2 days):**

19. Download the transcript.
20. Read through the transcript. Extract what actually matters.
21. Parse out action items, decisions, dates, and owners.
22. Write condensed meeting notes in Confluence.
23. Update the Confluence project page with decisions from the meeting.
24. Create Jira tickets for new action items. Link them to the right epic.
25. Assign Jira tickets. Set due dates.
26. Post meeting notes link in the Slack channel.
27. Tag people with action items in Slack so they see them.
28. Draft an email update for stakeholders who weren't in the meeting.
29. Add a calendar reminder to send the email update tomorrow morning (don't send at 7pm).
30. Add a Google Task to follow up on the Jira tickets in 3 days.
31. Update your own backlog with anything new.
32. Realize you forgot an action item from the transcript. Go back to step 24.

**Total time: 6-8 hours across 3 days. For one meeting.**

And this is the *optimistic* version. This assumes you don't get interrupted, don't lose track of a thread, and don't discover that someone else already made a decision in a DM you weren't cc'd on.

---

### After: With Palimpsest

**Prep (15 minutes):**

```
Review the program state and draft an agenda for tomorrow's cross-team sync.
Focus on: open blockers, decisions needed, anything that changed since last week.
Include talking points and suggested time allocation.
```

AI reads your program state, drafts an agenda grounded in actual status. You review, tweak, share. Done.

**The Meeting (1 hour):**

Same meeting. You still have to show up. Sorry — AI can't sit in meetings for you yet. (See [Future Vision](../docs/07-future-vision.md).)

But you paste the transcript after.

**Post-Meeting (20 minutes):**

```
Here's the transcript from today's cross-team sync.
Extract: decisions made, action items with owners and dates,
open questions, and anything that contradicts our current program state.
Update the relevant documents.
```

```
Draft a Slack summary for #project-channel. Keep it under 10 bullet points.
Also draft an email update for Raj — focus on the auth timeline discussion.
```

```
What Jira tickets should we create from this meeting?
Draft them with descriptions, acceptance criteria, and suggested assignees.
```

Three prompts. The AI reads the transcript, compares it against your program state, finds the deltas, drafts everything. You review, approve, ship.

**Total time: 45 minutes. Same day. Nothing falls through the cracks.**

---

## The Stakeholder Update

### Before (45-60 minutes)

1. Open Jira. Export the sprint report. Squint at the burndown chart.
2. Open Confluence. Read your own project page. Remember what you wrote last week.
3. Open Slack. Search for blockers mentioned this week.
4. Open your calendar. Check what meetings happened. Try to remember decisions.
5. Open Google Docs. Start drafting. Stare at the blinking cursor.
6. Write the update. Realize you forgot to check something. Go back to Jira.
7. Finish the draft. Proofread. Adjust tone (too pessimistic? too optimistic?).
8. Send. Hope you didn't miss anything.

### After (5 minutes)

```
Draft this week's stakeholder update for the VP of Engineering.
Pull from the dashboard and this week's daily digests.
Flag anything where status changed from last week.
Tone: direct, specific, no sugar-coating.
```

Review the draft. Make one edit. Send.

---

## The Context Gathering

Someone asks: "What did we decide about the auth approach and why?"

### Before (20-30 minutes)

1. Search Confluence for "auth." Get 47 results.
2. Open the 5 most likely pages. Cmd+F "auth" on each.
3. Find a mention but not the decision. Check the page history.
4. Search Slack for "auth decision." Get DMs, channel messages, thread replies.
5. Find a thread from 6 weeks ago. It has the context but no clear conclusion.
6. Ask Marcus on Slack: "Hey, did we officially decide on the rewrite?" Wait for response.
7. Marcus replies 3 hours later: "Yeah, we talked about it in the Feb 14 standup."
8. Try to find the Feb 14 standup notes. They don't exist.
9. Piece together the decision from fragments. Summarize it from memory.
10. Hope you got it right.

### After (15 seconds)

```
What did we decide about the auth approach? When was the decision made and what was the rationale?
```

> The team decided to rewrite the auth service instead of wrapping it on February 14, 2026.
> The rationale was that token validation logic was too deeply coupled to the REST routing layer —
> a wrapper would have created maintenance burden and security gaps. The trade-off was +3 weeks
> to the auth timeline, but the architecture is cleaner. This decision was made after a wrapper
> POC failed during the pricing-service migration.
>
> Source: PROGRAM_OVERVIEW.md, Key Decisions table; BACKLOG.md, Done section.

The AI doesn't guess. It cites your documents. Because you wrote it down and committed it.

---

## The Onboarding

A new engineer joins the team mid-program.

### Before (1-2 days of your time)

1. Schedule a 1:1. Walk them through the program for 90 minutes.
2. Share 15 links to various Confluence pages, Jira boards, Slack channels.
3. Answer the same 20 questions you've answered for every new joiner.
4. Three days later, answer them again because they couldn't find the Confluence page.
5. A week later, realize they're working from outdated context because they found an old version of a doc.

### After (5 minutes of your time)

```
A new engineer is joining the migration team next week.
Create an onboarding brief: what the program is, current state,
who does what, key decisions they need to know about,
and where to find things. Write it like you're explaining to a smart person
who has zero context.
```

Send them the brief and the repo link. They read it, ask smart questions on day one instead of basic ones on day five.

---

## The Pattern

Every example above has the same structure:

| | Before | After |
|---|---|---|
| **Time** | Hours spread across days | Minutes, same session |
| **Context source** | 5+ tools, manual search | One repo, AI synthesis |
| **Error rate** | High (forgotten items, stale context) | Low (grounded in committed state) |
| **Knowledge loss** | Gradual (context in heads, not docs) | None (everything committed) |
| **Scalability** | Worse with program complexity | Constant regardless of size |

The AI isn't magic. It's just reading what you wrote down. The magic is that you actually wrote it down, in one place, in a format that's searchable, versionable, and diffable.

That's the whole trick. Write it down. Commit it. Let the AI do the boring synthesis. Spend your time on the hard parts — the conversations, the decisions, the judgment calls that no AI can make for you.

---

*All examples use the [Apex API Platform Migration](../example/) scenario. Try the prompts yourself.*
