# Agent Configuration

## Multi-Agent Orchestration for Technical Program Management

Modern TPM work spans dozens of tools, documents, and communication channels. No single AI agent covers everything well. Multi-agent orchestration solves this by assigning specialized agents to specialized tasks — and connecting them through shared state.

This directory contains production-ready configuration templates for every major AI coding agent. Each template follows the **Palimpsest** methodology: treat program management artifacts as version-controlled, automatable, agent-readable code.

## Why Different Tools Need Different Configs

Each agent has its own configuration format, capability model, and session lifecycle:

| Agent | Config Format | Strengths | Best For |
|-------|--------------|-----------|----------|
| **Claude Code** | `CLAUDE.md` + `AGENTS.md` | Deep reasoning, long context, tool use | Architecture decisions, complex analysis, automation scripts |
| **Cursor** | `.cursorrules` | IDE-integrated, fast iteration | Code editing, document drafting, quick fixes |
| **Cline** | `.clinerules` (per-mode) | Modal architecture, strict boundaries | Structured workflows with review gates |

Different tools, same protocol. The configs differ in syntax but share one non-negotiable: **Memory Bank as shared state**.

## Memory Bank as Shared State

Every agent reads and writes the same Memory Bank files. This means:

- Agent A's session context is available to Agent B
- No work is ever lost between sessions or tools
- Cross-agent handoffs happen through files, not chat history

The Memory Bank is the single source of truth for program state. See `memory-bank/README.md` for the full specification.

## Directory Structure

```
agents/
├── README.md                          # This file
├── formatting-standards.md            # Markdown and writing standards
├── memory-bank/
│   ├── README.md                      # Memory Bank specification
│   ├── memory-bank.mdc               # Cursor rule file (auto-applied)
│   └── example/                       # Starter templates for Memory Bank files
│       ├── sessionLog.md
│       ├── activeContext.md
│       ├── progress.md
│       ├── decisionLog.md
│       ├── systemPatterns.md
│       ├── productContext.md
│       └── projectPreferences.md
├── claude-code/
│   ├── CLAUDE.md.template             # Entrypoint for Claude Code
│   └── AGENTS.md.template             # Full agent instructions
├── cursor/
│   ├── cursorrules.template           # Cursor rules with full protocol
│   └── skills/
│       └── auto-commit.md             # Git checkpoint skill
└── cline/
    ├── clinerules-architect.template  # Architect mode
    ├── clinerules-code.template       # Code mode
    ├── clinerules-debug.template      # Debug mode
    ├── clinerules-test.template       # Test mode
    └── clinerules-ask.template        # Ask mode
```

## Quick Start

1. Copy the Memory Bank example files into your project's `.cursor/memory/` (or equivalent)
2. Choose your agent and copy the relevant template into your project root
3. Replace `[YOUR-PROJECT]` and `$PROJECT_ROOT` placeholders with real values
4. Start a session — the agent will pick up the protocol automatically

## Principles

- **No blank slate sessions.** Every chat starts by reading prior context.
- **Commit early, commit often.** Git is the persistence layer.
- **Files over chat.** Program state lives in markdown, not in conversation history.
- **Standard markdown only.** No unicode bullets, no emoji headers, no fancy formatting.

See `formatting-standards.md` for the full writing and formatting specification.
