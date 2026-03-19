# What You Can Do With It

This isn't a theoretical framework. Here are concrete things you can do, organized by how much time they take. Every prompt listed here is one I've actually used.

## Quick Wins (5 Minutes)

These are the ones that sell people on the approach. Low effort, immediate payoff. Start here.

### Find What's Blocking

**Prompt**: "What are the current blockers across all workstreams? Who owns each one?"

**What happens**: The AI reads your DASHBOARD.md, recent meeting notes, and risk register. It compiles a list of blockers with owners and how long each has been open.

**Time comparison**: Manually? Open Jira, filter by blocked status, cross-reference with Confluence, check Slack for context. 25 minutes. With Palimpsest? One prompt, one answer, 30 seconds.

### Draft Your Standup Update

**Prompt**: "Draft my standup update for today. What did I work on yesterday, what's planned today, any blockers?"

**What happens**: The AI reads your session logs, yesterday's daily digest, and today's calendar context. It drafts a standup update in your team's format.

**Time comparison**: Manually writing a standup from memory: 10 minutes, and you'll forget something. With Palimpsest: 30 seconds, and it won't forget anything that's in the repo.

### Summarize a Meeting

**Prompt**: "Here are my raw notes from the architecture review. Structure them into: decisions made, action items with owners, open questions, and parking lot items."

**What happens**: You paste or drop raw notes. The AI structures them using your template, assigns action items based on your CONTEXT_INDEX.md (it knows who owns what), and flags anything that contradicts existing decisions.

**Time comparison**: Manually structuring meeting notes: 15-20 minutes. With Palimpsest: paste and prompt, 2 minutes.

### Check If Something Was Discussed

**Prompt**: "Has anyone mentioned data migration rollback procedures in any meeting note or decision log?"

**What happens**: The AI searches across all your files — every meeting note, every decision, every digest. It either finds the reference (with the file path and context) or tells you it hasn't been discussed, which is itself valuable information.

**Time comparison**: Manually searching Confluence: 10 minutes of keyword searching and page scanning. Manually searching Slack: another 10 minutes. Checking Google Docs: another 5. With Palimpsest: one prompt, definitive answer, 15 seconds.

### Generate a Quick Status Email

**Prompt**: "Draft a 3-sentence status email for [stakeholder name] about [workstream]. Keep it high-level, flag only what they need to know."

**What happens**: The AI reads the current dashboard status, knows who the stakeholder is from CONTEXT_INDEX.md, and drafts an appropriately scoped email. It knows a VP needs different detail than an engineering lead.

**Time comparison**: Writing a status email: 10-15 minutes of context gathering plus drafting. With Palimpsest: review a draft in 2 minutes.

## Power Features (15 Minutes)

These require the AI to synthesize across multiple files. They're where the "repo as context" approach really shines.

### Draft a Stakeholder Update

**Prompt**: "Draft the weekly stakeholder update for the steering committee. Focus on migration progress, timeline risks, and decisions needed."

**What happens**: The AI reads your DASHBOARD.md, this week's meeting notes, the risk register, and the timeline. It generates a structured update in your established format, with the right level of detail for a steering committee (high-level, decision-oriented, no implementation details).

**Time comparison**: Manually writing a stakeholder update: 45-60 minutes of gathering context across tools, then 30 minutes of writing. With Palimpsest: review and edit a draft in 15 minutes.

### Find Historical Decisions

**Prompt**: "When did we decide to use a phased rollout instead of big-bang migration? What was the reasoning? Who was in the room?"

**What happens**: The AI searches your decision log, meeting notes, and daily digests. It finds the specific meeting where the decision was made, the arguments for and against, and who participated.

**Time comparison**: Manually searching Confluence page history and Slack threads: 30+ minutes, if you even find it. With Palimpsest: one prompt, immediate answer — assuming you've been capturing decisions.

### Generate a Weekly Diff

**Prompt**: "What changed in the program this week? Compare this Friday's state to last Friday's."

**What happens**: The AI uses git history to identify every file that changed, reads the diffs, and summarizes the meaningful changes. New risks added. Blockers resolved. Timeline shifts. Decisions made.

**Time comparison**: There is no manual equivalent of this. Nobody manually tracks week-over-week program state changes. With Palimpsest, it's a built-in capability of using git.

### Audit Your Action Items

**Prompt**: "Find all action items assigned to me across all meeting notes from the past two weeks. Which ones have been completed? Which are still open? Which have I probably forgotten about?"

**What happens**: The AI cross-references action items from meeting notes against your progress logs and daily digests. It identifies items that were assigned but never appeared in any follow-up, which usually means they fell through the cracks.

**Time comparison**: Manually auditing action items: you don't. Nobody does. That's why things fall through the cracks. With Palimpsest: 5 minutes to review the list.

## Advanced (30+ Minutes)

These are the big swings. They produce artifacts that would take hours to build manually. The AI gives you a strong first draft that you refine.

### Build a Risk Register From Scratch

**Prompt**: "Analyze all meeting notes, decision logs, and status updates from the past month. Identify risks that have been mentioned but not formally tracked. Classify by likelihood and impact. Suggest mitigations."

**What happens**: The AI performs a deep read across your entire context. It identifies risks mentioned in passing during meetings, concerns raised in daily digests, and patterns in blockers that suggest systemic issues. It produces a structured risk register.

**Time comparison**: Manually building a risk register for a new program: 2-3 hours of reading and interviewing. With Palimpsest: 30 minutes of review and refinement of the AI-generated draft.

### Map Dependencies

**Prompt**: "Map the dependencies between all workstreams. For each dependency, identify: what depends on what, who owns each side, current status, and what happens if it slips."

**What happens**: The AI reads your program overview, workstream definitions, and timeline. It builds a dependency map and identifies critical path items. It flags dependencies where both sides haven't been explicitly acknowledged.

**Time comparison**: Dependency mapping is one of those things TPMs know they should do but rarely have time for. It takes a full day manually. With Palimpsest: you get a solid first draft in 30 minutes that you refine over the next hour.

### Prepare a Go/No-Go Assessment

**Prompt**: "We have a go/no-go decision for Phase 2 launch next Thursday. Build the assessment. For each criterion, pull the current state from our docs and flag anything that's not green."

**What happens**: The AI reads your launch criteria (from your program docs), cross-references with current status, test results, stakeholder sign-offs, and open blockers. It produces a go/no-go matrix with evidence for each row.

**Time comparison**: Manually preparing a go/no-go: a full day of chasing people and compiling evidence. With Palimpsest: 30 minutes to generate the draft, then you spend your time on the hard part — the conversations with stakeholders about the amber and red items.

## The Pattern

Notice what's happening across all of these: the AI isn't making things up. It's reading YOUR documents, structured the way YOU set them up, and synthesizing across them faster than you can.

The quality of the output is directly proportional to the quality of your input. Garbage repo, garbage answers. Well-maintained repo, surprisingly good answers.

That's the deal. You invest in keeping the repo current, and the AI pays you back tenfold on every query.

---

Previous: [Setup Guide](03-setup-guide.md) | Next: [Why AI Despite Hallucinations](05-why-ai-despite-hallucinations.md)
