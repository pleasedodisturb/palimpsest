# The Problem: Drowning in Context

## The Scenario

You join a complex program as a TPM. Day one, someone hands you access to 40+ documents spread across 5 different tools. Confluence spaces with nested pages three levels deep. Google Drive folders shared by people who left the company. Jira boards with 200+ tickets and custom workflows nobody documented. Slack channels where critical decisions were made six months ago and buried under memes.

Welcome to your new job. Good luck.

## It's Not Just You

Before we go further: this isn't a "bad at your job" problem. I've talked to TPMs at Google, Meta, Stripe, and a dozen startups. The ones who are honest all describe some version of the same thing. The tools are different (Asana instead of Jira, Linear instead of Confluence, whatever) but the shape of the problem is identical.

Too many sources. Too much context. Too little time to synthesize it. And a calendar full of meetings where you're expected to have the complete picture.

The industry's answer has been "better tools" — and every new tool makes it slightly worse because now there's one more source of truth that isn't actually the source of truth.

## The Morning Routine Nobody Talks About

Here's what my first two weeks looked like every morning:

1. Open Slack. Scroll through 4 channels. Find 3 things that need attention.
2. Open Jira. Check the board. Cross-reference with what I just read in Slack.
3. Open Confluence. Find the status page. It was last updated 11 days ago.
4. Open Google Drive. Find the meeting notes from yesterday's sync. They're in someone else's folder.
5. Open my calendar. Realize I have 6 meetings today and I still don't know the current state of the program.

Time spent: 90 minutes. Every single morning.

And I still wasn't confident I had the full picture.

## The Symptoms

### Context Switching Tax

Every tool switch costs you mental energy. Not just the click — the mental model swap. Confluence thinks in pages and trees. Jira thinks in tickets and sprints. Slack thinks in conversations and threads. Your brain has to translate between all of them, constantly.

Research says context switching costs 15-25 minutes of recovery time. A TPM switches context 20+ times before lunch.

### The Update Treadmill

You spend your morning gathering context. Then you spend your afternoon reformatting that context into updates for different audiences. Weekly status email. Confluence page update. Jira ticket comments. Slack summary. Dashboard refresh.

You're not managing the program. You're managing the information about the program. There's a difference, and it's killing your effectiveness.

### The Anxiety Loop

Here's the feeling: you're in a meeting, someone asks "what's the status of X?" and you're 80% sure you know, but there's a 20% chance something changed in a Slack thread you didn't read, or a Jira ticket someone updated without telling you, or a Google Doc someone edited last night.

That 20% uncertainty compounds. Across 15 workstreams, you're constantly operating with partial information and hoping nobody notices.

### Knowledge Silos

The real killer. Critical context lives in people's heads. When they're on vacation, in a different timezone, or — worse — leave the company, that context evaporates.

I've watched entire programs lose months of institutional knowledge because one senior engineer left and nobody had documented the architectural decisions that shaped the whole migration approach.

### The Invisible Overhead

There's a category of work that doesn't show up on any project plan: the overhead of keeping yourself informed. It's not a task in Jira. It's not a meeting on the calendar. It's the 10 minutes between meetings spent re-reading Slack threads to make sure you didn't miss anything. It's the Sunday evening scan of your inbox because something might have changed on Friday afternoon.

This overhead is invisible to everyone except the person doing it. Your manager doesn't see it. Your stakeholders don't see it. It doesn't appear in any utilization report. But it's eating 30-40% of your productive capacity.

### The Compounding Effect

Each of these symptoms feeds the others. Context switching means you miss updates. Missing updates means you're less confident. Less confidence means you over-prepare. Over-preparing means more context switching. It's a flywheel, and it spins faster as the program grows.

By the time you're managing a program with 15+ workstreams, 30+ stakeholders, and 6+ months of history, the overhead has consumed your ability to do the actual job: making decisions, managing risks, and keeping people aligned.

## The Real Cost

This isn't about efficiency for efficiency's sake. Here's what drowning in context actually costs:

- **Missed risks**: You can't flag what you can't see. When context is scattered, risks hide in the gaps between tools.
- **Slow decisions**: Every decision requires a context-gathering phase. "Let me check on that and get back to you" becomes your catchphrase.
- **Reactive management**: You're always responding to what just happened instead of anticipating what's coming. The program runs you, not the other way around.
- **Burnout**: The cognitive load of maintaining a mental model across 5 tools, 40 documents, and 15 stakeholders is unsustainable. TPMs burn out not because the work is hard, but because the information management is exhausting.

## What We Actually Need

The problem isn't that the tools are bad. Confluence is fine. Jira is fine. Slack is fine. They're all fine individually.

The problem is that no single tool holds the complete picture, and no human can reliably synthesize across all of them every day without losing something.

What we need is:

- **One place** where all program context lives — or at least points to where things live
- **Versioned state** so we can see what changed, when, and why
- **Machine-readable structure** so we can automate the boring parts
- **Human-readable output** so stakeholders still get what they need
- **AI amplification** so the 90-minute morning routine becomes 5 minutes

Not a new tool. Not another dashboard. A different approach to how program state is stored, maintained, and queried.

That's what Program-as-Code is.

---

Next: [The Solution: Program-as-Code](02-the-solution.md)
