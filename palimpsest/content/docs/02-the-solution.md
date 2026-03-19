# The Solution: Program-as-Code

## The Name

A palimpsest is a manuscript where earlier writing has been scraped away and written over — but traces of the old text still show through. That's exactly what a program repo is: layers of decisions, each one visible through git history, nothing truly lost.

The approach itself is simple: Program-as-Code. If you're explaining it to someone, that's all you need.

## The Core Idea

Take everything you know about Infrastructure-as-Code and apply it to program management.

Infrastructure-as-Code says: don't configure servers by clicking through UIs. Write the desired state in files. Version them in git. Let automation handle the rest.

Program-as-Code says: don't manage program state by clicking through Confluence, Jira, Slack, and Google Drive. Write the canonical state in markdown files. Version them in git. Let AI handle the synthesis, querying, and output generation.

That's it. That's the whole idea.

```
Your program state = markdown files in a git repo
Your program tools = AI editors that read those files
Your program outputs = generated from that single source of truth
```

## Why This Works

### Versioned State

Every change to your program state is a git commit. You can see exactly what changed, when, and (if you write decent commit messages) why. Try doing that with a Confluence page that 6 people edit.

`git log --oneline docs/status/` tells you more about your program's evolution than any changelog anyone has ever manually maintained.

### AI as Amplifier

Here's the key insight that makes everything click: AI editors (Cursor, VS Code with Copilot, Claude Code, Windsurf, Kiro, Aider) can read your entire repo. Every file. Every folder. The full context.

When you ask "what are the top risks right now?" — the AI isn't guessing. It's reading your actual risk register, cross-referencing with your meeting notes, checking your timeline, and synthesizing an answer grounded in YOUR data.

This is fundamentally different from asking ChatGPT the same question. ChatGPT knows nothing about your program. Your AI editor knows everything about it.

### Structure Creates Calm

When everything has a place and everything is in its place, the anxiety loop breaks. You stop worrying about what you might have missed because the repo IS the complete picture. If it's not in the repo, it hasn't been captured yet — and that's a clear, actionable problem instead of a vague feeling of dread.

## Comparisons

### vs ChatGPT / Claude Projects

| Aspect | ChatGPT / Claude | Palimpsest |
|--------|-----------------|------|
| Context | Upload files manually, limited context window | AI reads entire repo automatically |
| Memory | Session-based, forgets between chats | Git history is permanent memory |
| Collaboration | Single user | Full git collaboration, branching, PRs |
| Versioning | None | Every change tracked |
| Offline access | No | Yes, it's local files |
| Customization | System prompts | Full repo structure + agent instructions |

### vs Glean / Enterprise Search

| Aspect | Glean | Palimpsest |
|--------|-------|------|
| Approach | Search across existing tools | Single source of truth |
| Context quality | Indexes everything, including noise | Curated, structured context |
| Writability | Read-only search | Read-write, generates outputs |
| AI grounding | Searches company-wide | Scoped to your program |
| Setup cost | Enterprise deployment | One git repo |

### vs Notion / Confluence

| Aspect | Notion / Confluence | Palimpsest |
|--------|-------------------|------|
| Format | Proprietary, locked in | Plain markdown, portable |
| Version control | Page history (limited) | Full git history |
| AI integration | Built-in AI (limited context) | Any AI editor, full repo context |
| Offline | Limited | Full offline access |
| Automation | API + plugins | Scripts, CI/CD, anything |
| Collaboration | Real-time editing | Git workflows (PRs, branches) |
| Export | Painful | It's already files |

## Technology Stack

The beauty of Palimpsest is that the stack is almost embarrassingly simple:

- **Storage**: Markdown files in folders
- **Version control**: Git (GitHub, GitLab, whatever)
- **AI interface**: Any AI-capable editor
- **Automation**: Shell scripts, Python, whatever you know
- **Publishing**: Push to Confluence, Google Docs, Slack via scripts

No databases. No custom platforms. No SaaS subscriptions (beyond what you already have). No vendor lock-in.

## IDE Agnostic

This is important: Palimpsest does not care which editor you use. The methodology works with:

- **Cursor** — what I use most, great AI integration
- **VS Code + GitHub Copilot** — solid, widely available
- **Claude Code** — CLI-based, powerful for automation
- **Windsurf** — another strong AI editor option
- **Kiro** — Amazon's spec-driven AI editor
- **Aider** — open source, terminal-based
- **Any future AI editor** — because the data is just files

The repo is the product, not the tool. If a better editor appears tomorrow, you switch editors and keep everything else. Try doing that with Notion.

## Model Flexibility

Same principle applies to AI models. Your Palimpsest repo works with:

- Claude (Anthropic)
- GPT-4 / GPT-4o (OpenAI)
- Gemini (Google)
- Local models via Ollama
- Whatever ships next quarter

The AI reads markdown files. Any AI can read markdown files. You're never locked into a model provider.

## The Daily Experience, Transformed

### Before Palimpsest

| Time | Activity |
|------|----------|
| 8:00 | Open Slack, scroll through channels |
| 8:20 | Open Jira, check board |
| 8:35 | Open Confluence, find status page |
| 8:50 | Open Google Drive, find meeting notes |
| 9:05 | Open calendar, prep for first meeting |
| 9:15 | Still not confident about program state |
| 9:30 | First meeting. Wing it. |

### After Palimpsest

| Time | Activity |
|------|----------|
| 8:00 | Open editor. Ask: "What changed since yesterday?" |
| 8:02 | Read the AI-generated summary. Full picture in 2 minutes. |
| 8:05 | Ask: "What should I focus on today?" |
| 8:07 | Prioritized list based on actual program state. |
| 8:10 | Ask: "Draft my standup update." |
| 8:11 | Done. Copy-paste. |
| 8:15 | Actually think about strategy. |
| 9:30 | First meeting. Prepared. |

The difference isn't marginal. It's a category change in how you spend your morning.

---

Previous: [The Problem](01-problem-statement.md) | Next: [Setup Guide](03-setup-guide.md)
