[![Tests](https://github.com/pleasedodisturb/palimpsest/actions/workflows/test.yml/badge.svg)](https://github.com/pleasedodisturb/palimpsest/actions/workflows/test.yml)

# Palimpsest

> *pa·limp·sest* · /ˈpalɪm(p)sɛst/ · noun
>
> A manuscript or piece of writing material on which the original writing has been effaced to make room for later writing, but of which traces remain.
>
> From Greek *palimpsēstos* — "scraped again."

**Your program's second brain.**

Yes, the name is absurd. Try saying it three times fast. Try putting it in a slide deck. Try explaining it to your VP. We know. But you're managing complex technical programs for a living — your life is already weird. Embrace it.

---

Every program is a palimpsest. Decisions written over decisions. Requirements rewritten mid-flight. Architecture docs that say one thing while the code says another. Slack threads where the real agreement happened, buried under everything that came after.

The traces are all there — if you know where to look.

This project takes that idea literally. You put your program's entire state — status, decisions, risks, stakeholder context, the stuff that actually matters — into a git repository. Markdown files. Every layer committed, every revision visible, nothing truly lost.

Then you point an AI at it.

---

You know that feeling. Monday morning. 47 unread Slack messages, a Confluence page someone updated Friday at 6pm, a Jira board that doesn't match what was agreed in yesterday's standup, and a Google Doc with comments from three people who each think they're describing the same decision differently.

You spend 90 minutes just figuring out *where things are*. Before you've done a single useful thing.

Palimpsest fixes this. The AI doesn't hallucinate your program state. It *reads* it. Every decision has a commit. Every change has a diff. Every question gets an answer that cites your actual documents, not a vague summary from a model that's guessing.

## The Problem (in case you haven't lived it)

A typical TPM on a complex program deals with:

- **5+ tools** that don't talk to each other (Slack, Confluence, Jira, Drive, Calendar)
- **40+ documents** scattered across all of them
- **Decisions buried in Slack threads** that nobody can find two weeks later
- **Status meetings** that exist only because nobody trusts the written artifacts
- **Context that lives in people's heads** and walks out the door when they go on vacation

The industry's answer is "better tooling." Another dashboard. Another integration. Another notification.

Palimpsest's answer is simpler: **write it down, commit it, let AI help you navigate it.**

## Quick Start

```bash
# Clone the repo
git clone https://github.com/pleasedodisturb/palimpsest.git
cd palimpsest

# Create a new project
./setup.sh my-program --with-github

# Open in your AI editor
cd my-program
cursor .

# Ask your first question
"What's the structure of this project?"
```

Or install the Python toolkit:

```bash
pip install -e .
pac --service all  # Check service connectivity
```

Five minutes. That's it. You now have a structured program repo with AI memory, document templates, and optional integrations with Google Drive, Confluence, Jira, and Slack.

## What's Inside

```
palimpsest/
├── docs/                    # The methodology (10 guides, start here)
├── example/                 # A fully populated fictional program (see it in action)
├── case-study/              # How this was battle-tested at Wolt
├── templates/               # TPM document templates (BRD, PRD, etc.)
├── agents/                  # AI agent configs (Cursor, Claude Code, Cline)
│   └── memory-bank/         # Persistent AI memory protocol
├── scripts/                 # Python automation toolkit
│   ├── core/                # Auth, service clients, markers
│   ├── sync/                # Google Drive, Calendar, scheduled sync
│   ├── content/             # Upload to Docs/Confluence, link extraction
│   ├── automation/          # Auto-commit, clipboard, daily runner
│   └── publishing/          # Confluence news/weekly, Jira drafts
├── playbooks/               # TPM playbooks (async collaboration, etc.)
├── showcase/                # Demo prompts and quick wins
├── project-template/        # What setup.sh generates
├── setup.sh                 # Project bootstrapper
└── pyproject.toml           # Python package config
```

## See It In Action

The [`example/`](example/) directory contains a fully populated fictional program — **Apex Corp's API Platform Migration**. It's a 6-month migration that's 4 months in, currently at risk because the auth team is behind and a partner's security review is stuck in legal limbo.

It has real-looking status docs, a populated backlog, daily digests with honest observations about team dynamics, and a stakeholder update that was drafted from program state. Open it in your AI editor and ask questions — that's the fastest way to understand what Palimpsest actually feels like.

Want the visceral version? Read the [**Before & After**](showcase/before-after.md) — a side-by-side comparison of what running a meeting, writing a stakeholder update, gathering context, and onboarding someone looks like with and without Palimpsest. The meeting example alone covers the 32-step dance of prep, transcription, parsing, Jira tickets, Confluence updates, email drafts, and follow-up reminders that most TPMs do on autopilot and nobody ever writes down. Spoiler: it collapses from 6-8 hours across 3 days to 45 minutes same-day.

## The Methodology

Ten documents. Read them in order or jump to what you need.

| # | Guide | The gist |
|---|-------|----------|
| 01 | [Problem Statement](docs/01-problem-statement.md) | Why TPMs are drowning in context and tools aren't helping |
| 02 | [The Solution](docs/02-the-solution.md) | Markdown + Git + AI. Why it works. How it works. |
| 03 | [Setup Guide](docs/03-setup-guide.md) | Get running in 10 minutes, no excuses |
| 04 | [Use Cases](docs/04-use-cases.md) | 15 things you can actually do with this, today |
| 05 | [Why AI Despite Hallucinations](docs/05-why-ai-despite-hallucinations.md) | Addressing the skeptics (and they're right to be skeptical) |
| 06 | [FAQ](docs/06-faq.md) | The questions everyone asks |
| 07 | [Future Vision](docs/07-future-vision.md) | Where this could go if we're not careful |
| 08 | [Known Issues](docs/08-known-issues.md) | What doesn't work. Honest list. |
| 09 | [Personal AI Assistant](docs/09-personal-ai-assistant.md) | The endgame: an AI that knows your program as well as you do |
| 10 | [Privacy Model](docs/10-privacy-model.md) | What's public, what's private, and why it matters |

## The Toolkit

The `scripts/` directory is where methodology meets automation. Pure Python, config-driven, no hardcoded values.

**Sync** — Pull documents from Google Drive, fetch calendar events, run scheduled pipelines. Your repo stays current without manual copy-pasting.

**Content** — Upload markdown to Google Docs or Confluence, build document registries, extract and categorize links across your entire program. Markdown is the source of truth; everything else is a render target.

**Automation** — Auto-commit changes on a schedule, watch your clipboard for meeting transcripts, run daily update pipelines. The boring stuff that you forget to do at 5pm on Friday.

**Publishing** — Push daily news updates to Confluence, generate weekly summaries, create team member sheets, draft Jira tickets from your backlog. Your stakeholders get updates without you writing the same thing in three places.

```bash
pac --service all                                    # What's connected?
python scripts/sync/gdrive_sync.py --list            # What's in Drive?
python scripts/content/upload_to_confluence.py SPACE doc.md "Title"  # Ship it
```

Everything talks to external services through environment variables. Zero secrets in code. Zero hardcoded IDs. Swap the config, point it at your stack.

## AI Agent Configs

Pre-built configurations for the editors people actually use:

| Tool | Config | What it does |
|------|--------|-------------|
| **Cursor** | `agents/cursor/` | Rules file + skills for structured program management |
| **Claude Code** | `agents/claude-code/` | CLAUDE.md + AGENTS.md templates with full context |
| **Cline** | `agents/cline/` | Five mode-specific rulesets (architect/code/debug/test/ask) |

All three share the **Memory Bank** protocol — persistent AI memory that survives across sessions. Your AI reads prior session logs, active context, and progress before doing anything. No more blank-slate conversations where you explain the same thing for the tenth time.

The editor is swappable. The repo structure and memory protocol are the constants.

## Origin Story

The first version of this was built on the fly at Wolt, during a CRM migration program I was running as a TPM. Joined mid-flight — 40+ documents scattered across 5 tools, decisions buried in Slack threads, no single source of truth. The methodology started as survival: dump everything into markdown, commit it, let AI help me make sense of it.

It worked. Whether Wolt is still kicking it with this approach or it joined the graveyard of good ideas that don't get adopted before they get obsolete — I honestly don't know. But the patterns were real, and they deserved a proper implementation. Not something hacked together under deadline pressure, but built from the ground up with the right structure, tests, and documentation.

So that's what Palimpsest is. Same battle-tested methodology, rebuilt properly. The name fits — a palimpsest is a manuscript where earlier writing has been scraped away and written over, but traces of the old text still show through. That's exactly what a git-based program repo is: layers of decisions, each one visible through the history, nothing truly lost.

All code and documentation written independently. The methodology is professional knowledge. The implementation is new. See the [case study](case-study/wolt-crm-migration.md) for the full story.

## Who Is This For

- **TPMs** running complex, multi-stakeholder programs who are tired of being human routers
- **Program Managers** who spend more time finding information than thinking about it
- **Engineering Managers** coordinating across teams and timezones
- **Anyone** who has ever opened their laptop on Monday and thought "where the hell did we leave off?"

> **Hot take:** You don't have to be a TPM. You don't even need to know what a TPM is, or who the TPM is on your project. You're probably doing their job anyway — because the actual TPM is too busy to care, sawing away at the tree with the handle of the axe, the blade having been lost sometime around 2014 while debating the Agile Manifesto and whether Scrum is the way to fix the project, the organization, and democracy at large.
>
> If you're the person who ends up knowing where everything is because nobody else bothered to write it down — this is for you.

## Works With Everything

| Tool | Notes |
|------|-------|
| **Cursor** | Best experience — native MCP support, inline AI |
| **VS Code** | With Copilot, Continue, or Cline extensions |
| **Claude Code** | CLI-only, no IDE needed, full power |
| **Windsurf** | Codeium's agentic IDE |
| **Kiro** | AWS's spec-driven IDE |
| **Aider** | CLI pair programming |

If it can read markdown and talk to an LLM, it works with Palimpsest.

---

## License

MIT. Use it, adapt it, make it your own. If it helps you run a better program, that's the whole point.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Especially welcome: your own use cases, fixes, clarifications, and hard questions via issues. The best methodology improvements come from people actually using this under pressure.

---

*Built by a TPM who got tired of drowning. Tested under fire. Named after a manuscript that never forgets.*
