# Known Issues (Hall of Shame)

Intellectual honesty requires admitting what doesn't work well. Here's everything that has bitten me, roughly in order of how much time I've wasted on each.

## Memory Bank Enthusiasm Cycles

**The problem**: Every new AI session starts by reading the Memory Bank and getting very excited about updating it. The AI writes detailed session logs, verbose progress updates, and elaborate active context summaries. This is great for the first week.

By week three, the Memory Bank files are 500+ lines each. The AI spends a meaningful chunk of its context window just reading its own previous session notes. The session logs become a novel nobody reads.

**What I've tried**: Aggressive pruning. Moving old sessions to "History" sections. Summarization. All of these work temporarily until the enthusiasm cycle restarts.

**Current mitigation**: Hard line limits in agent instructions. Archive aggressively. Accept that some Memory Bank rot is inevitable and do a full cleanup every few weeks.

**Honest assessment**: This is a fundamental tension in the design. The Memory Bank needs to be comprehensive enough to restore context but concise enough to not waste tokens. I haven't found the equilibrium point yet. Maybe it doesn't exist.

## Context Fragmentation

**The problem**: Despite the "single source of truth" aspiration, context inevitably fragments. Someone shares something in Slack that doesn't make it into the repo. A decision happens in a hallway conversation. A Google Doc gets updated but the sync script hasn't run.

**The honest truth**: Palimpsest reduces fragmentation dramatically compared to the baseline. It does not eliminate it. If you expect perfection, you'll be disappointed. The repo is the best single source, not the complete source.

**Current mitigation**: Daily sync routines. Discipline about capturing hallway decisions. Accepting that "90% of context in one place" is a massive improvement over "20% of context in five places."

## Token Limits

**The problem**: Large programs generate a lot of markdown. At some point, your repo exceeds what the AI can process in a single context window. You ask a question about a file the AI hasn't read, and it either admits it doesn't know or (worse) makes something up.

**What happens in practice**: For a program with 6+ months of daily digests, meeting notes, and decision logs, you can easily hit 200+ files and hundreds of thousands of tokens. No current model processes all of that simultaneously.

**Current mitigation**: Repo structure matters. Keep the most important files (DASHBOARD.md, PROGRAM_OVERVIEW.md, recent digests) at the top of the tree. Archive old content. Use specific file references in prompts: "read docs/meeting-notes/2026-03-05.md" instead of "read all meeting notes."

## The AI Confidence Problem

**The problem**: AI models don't say "I don't know" enough. You ask about a workstream and the AI gives you a confident, detailed answer that is subtly wrong because it's synthesizing from outdated meeting notes and missing the Slack conversation that changed everything.

**When this hurts**: Status updates going to leadership. You trust the draft, skim it, and send it. Then someone corrects you in the steering committee meeting. Fun.

**Current mitigation**: Always verify AI-generated status against your most recent source. Build a habit of asking "when was this information last updated?" Not a technology fix — a behavior fix.

## Google OAuth Pain

**The problem**: Google's OAuth flow for desktop applications is genuinely hostile to developer experience. Tokens expire. Refresh tokens sometimes stop working. The consent screen needs to be re-approved periodically. If you're using a Google Workspace account, your admin might need to approve the app.

**How much time I've wasted on this**: Too much. Multiple hours across multiple weeks. The actual sync scripts work great once auth is working. Getting auth working is the problem.

**Current mitigation**: `preflight_check.py` catches expired tokens before scripts fail silently. But the underlying OAuth experience is what it is. Google doesn't seem interested in making it better.

## Confluence API Quirks

**The problem**: Confluence's API has opinions about HTML formatting that don't always align with what you'd expect from a markdown conversion. Tables render weirdly. Nested lists sometimes flatten. Code blocks lose syntax highlighting.

**Specific annoyances**:
- The storage format (XHTML) doesn't map cleanly from markdown
- Updating a page sometimes resets the "last edited by" to your API user, confusing people who watch page changes
- Rate limits are generous but not documented consistently

**Current mitigation**: A custom markdown-to-Confluence converter that handles the common edge cases. It works for 90% of content. The other 10% needs manual cleanup in the Confluence editor, which defeats the purpose.

## Git Conflicts in Memory Files

**The problem**: If you use multiple editors or multiple machines, the Memory Bank files (sessionLog.md, activeContext.md) are high-conflict. Every session writes to them. Merge conflicts are frequent and annoying.

**Why this is extra painful**: Merge conflicts in the files that tell the AI what's going on are exactly the files you don't want corrupted.

**Current mitigation**: Only work from one machine at a time. If you must use multiple, do a pull before starting and a push-then-pull when switching. Not elegant. Works.

## The "Works on My Machine" Problem

**The meta-issue**: I built this system for my specific workflow, my specific program, my specific tool stack. When other people try to adopt it, they hit friction I never encountered because my assumptions are baked into the setup.

This documentation is part of the fix. But I know there are assumptions I haven't surfaced yet because I don't know they're assumptions.

If you hit something weird, that's expected. File an issue. I'll add it to this page.

## Script Maintenance Debt

**The problem**: I wrote 22+ automation scripts over several months. Each one solved a specific problem at a specific time. Some of them have hardcoded assumptions that made sense in January and don't make sense now. Some have dependencies that drift. Some duplicate logic from other scripts.

**The honest truth**: It's technical debt. In a codebase of one developer (me) who is also a TPM and not primarily a software engineer, code quality takes a back seat to "does it work right now." This is fine until it isn't, and the "isn't" usually arrives at the worst possible time.

**Current mitigation**: `preflight_check.py` catches the most common failures. The test suite covers critical paths. Everything else is "fix it when it breaks."

## The Naming Problem

**The problem**: This project went through several name changes before landing on Palimpsest. If you find references to older names in corners we missed, that's why.

**Current mitigation**: This documentation. One name, one project. Palimpsest.

---

Previous: [Future Vision](07-future-vision.md) | Next: [Personal AI Assistant](09-personal-ai-assistant.md)
