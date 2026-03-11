# Case Study: The CRM Migration

## The Setup

A Red US company acquired a Cyan European company. As tends to happen with acquisitions, systems needed to merge. The Cyan company had been running its merchant CRM on Pipedrive — functional, beloved by sales teams, deeply integrated into daily workflows. The Red company ran everything through Salesforce.

Guess which system won.

The Cyan company — which I can tell you was Wolt, because saying "Cyan European food delivery company" every time would get old fast — needed to migrate its entire merchant relationship management infrastructure from Pipedrive to Salesforce. Hundreds of merchant accounts. Custom workflows. Years of relationship history. A sales team that had strong opinions about their tools.

I joined as the TPM three weeks before the original go-live date.

## Day One

Here's what I walked into:

- **40+ documents** scattered across Google Drive, Confluence, Slack threads, and people's heads
- **5 Slack channels** with overlapping but not identical membership
- **200+ Jira tickets** across multiple boards, some with clear ownership, many without
- **3 engineering teams** across 2 time zones working on different integration streams
- **1 sales operations team** that needed to keep selling while their tools changed underneath them

There was no single source of truth for program status. Decisions lived in Slack threads that had already scrolled past the free tier's history limit. Meeting notes existed in various Google Docs that may or may not have been shared with the right people.

The feeling on Day One was drowning. Not the dramatic kind — the quiet kind where you're smiling in meetings while mentally cataloging all the things you haven't had time to read yet.

## What I Actually Did

### Week 1: Survival Mode

I created a git repository. Put everything in markdown. Not because I had a grand methodology in mind — because I needed to stop losing things.

```
mx-crm-program/
├── docs/
│   ├── PROGRAM_OVERVIEW.md     # Everything I know, updated daily
│   ├── DASHBOARD.md            # Status at a glance
│   └── context/
│       ├── transcripts/        # Meeting notes (private)
│       └── daily-digests/      # What happened today
```

Then I pointed Cursor at it and said: "Help me understand this program."

The AI read my docs, asked clarifying questions, and within 20 minutes I had a better mental model of the program than I'd built in three days of meetings.

### Week 2-4: Building the System

The repo grew organically:

- **Morning routine**: "What happened yesterday across all channels?" — AI synthesized from daily digests and transcripts
- **Meeting prep**: "What do I need to know for the CRM Council meeting?" — AI pulled from program overview, recent decisions, open blockers
- **Stakeholder updates**: "Draft this week's update for leadership" — AI generated from git diffs and progress notes
- **Decision tracking**: Every decision got logged with context, alternatives, and rationale

I wrote Python scripts to automate the repetitive parts:
- Syncing documents from Google Drive
- Pushing updates to Confluence (where stakeholders expected to find them)
- Building a document registry across all sources
- Extracting and categorizing links from across the program's documents

### Month 2-3: The System Working

By this point, Program-as-Code was producing measurable results:

- **Morning context time**: from 90 minutes to under 10
- **Stakeholder updates**: from 2 hours of writing to 15 minutes of review
- **Decision recall**: from "I think we discussed this..." to exact quotes with dates
- **Onboarding new team members**: from a week of 1:1s to "read these 5 docs and ask the AI"

The Memory Bank protocol — where every AI session reads prior session logs before starting — meant I never had a "blank slate" conversation. The AI knew what we'd discussed yesterday, what decisions we'd made, what was still open.

## What Went Wrong

I'd be lying if I said everything worked perfectly. Here's the honest version:

**Memory Bank enthusiasm cycles.** I set up the protocol with religious devotion, maintained it for a week, then forgot to update it for three days, then felt guilty and over-updated, then forgot again. The protocol works, but it requires discipline that ebbs and flows.

**Token overflow.** As the repo grew past 50+ documents, the AI couldn't hold everything in context at once. I had to get strategic about which files to load for which conversations. This is a real limitation.

**Google OAuth pain.** Managing multiple OAuth tokens for different Google API scopes was genuinely painful. Token refresh flows broke at inconvenient moments. I ended up with a `preflight_check.py` script that runs at session start just to verify everything is still authenticated.

**The AI confidence problem.** The AI sounds equally confident when it's right and when it's wrong. When it's synthesizing from documents I wrote, accuracy is high. When it's filling gaps with general knowledge, it can be dangerously plausible. I learned to always ask for citations.

**Confluence storage format.** If you've never worked with Confluence's storage format, count yourself lucky. It's XML embedded in HTML, tables are painful to generate, and the API has opinions about whitespace that I still don't fully understand.

## What I'd Do Differently

**Start with the scripts earlier.** I built automation as needs arose, which meant a lot of manual work in the first weeks. If I'd had the sync and publishing scripts from Day One, the ROI would have been even faster.

**Enforce the Memory Bank from Day One.** The protocol is only valuable if it's consistent. I'd set up git hooks or automated reminders rather than relying on willpower.

**Be more aggressive about gitignoring.** I accidentally committed some sensitive context early on that I had to scrub from git history. The rule should be: gitignore first, decide to share later.

## The Numbers

After three months:

| Metric | Before Palimpsest | After Palimpsest |
|--------|------------|------------|
| Morning context gathering | ~90 min | ~10 min |
| Weekly stakeholder update | ~2 hours | ~15 min review |
| "Where was that decision?" | 10-30 min search | Instant |
| Onboarding a new team member | ~1 week | ~1 day |
| Documents I could find | ~60% | ~95% |
| Decisions with recorded rationale | ~20% | ~90% |

These aren't scientific measurements. They're honest estimates from someone who lived both sides.

## The Principle

The real insight isn't technical. It's this: **your program's knowledge should outlive any single conversation, any single tool, any single person.**

Markdown in git is the most portable, version-controlled, AI-friendly format we have. It doesn't depend on any vendor. It doesn't have a monthly fee. It doesn't get acquired and shut down.

The AI is a force multiplier, but the repo is the asset. If every AI tool disappeared tomorrow, you'd still have a well-organized, version-controlled, searchable knowledge base.

That's the thing I actually believe: the future of program management is code, not more SaaS tools.

---

*This case study describes professional TPM work. All code and methodology in this repository were developed independently. Internal data (employee names, system URLs, page IDs, credentials) has been removed or replaced with placeholders.*
