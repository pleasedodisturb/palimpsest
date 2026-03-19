# Memory Bank

## What It Is

The Memory Bank is a set of markdown files that serve as persistent, shared state for AI agents working on a program. It solves the fundamental problem of AI sessions: every new chat starts with zero context.

Instead of relying on chat history (which is ephemeral) or manual briefings (which are error-prone), the Memory Bank gives agents a structured place to read context at session start and write context at session end. The files live in version control, so nothing is ever lost.

## Core Principle

**No chat forgotten. Blank slate forbidden.**

Every agent session MUST:
1. Read the Memory Bank before doing any work
2. Update the Memory Bank before ending the session
3. Commit changes so the next session (same agent or different) has full context

This is non-negotiable. An agent that skips the Memory Bank is an agent that wastes the user's time re-explaining context.

## The 7 Files

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `sessionLog.md` | Registry of all sessions — who worked, when, what happened | Every session start and end |
| `activeContext.md` | Current focus, recent events, open questions | Every session, every major checkpoint |
| `progress.md` | Milestones achieved, recent completions, next steps | When work items complete or shift |
| `decisionLog.md` | Decisions made, with context, alternatives, and rationale | When significant decisions are made |
| `systemPatterns.md` | Architecture, integration patterns, data flows | When technical patterns are established or changed |
| `productContext.md` | Project overview, goals, stakeholders, key documents | Infrequently — when project scope changes |
| `projectPreferences.md` | Communication norms, tools, workflow, formatting | Infrequently — when team preferences change |

Not every file needs updating every session. `sessionLog.md` and `activeContext.md` are always touched. The rest are updated when relevant events occur.

## Session Lifecycle

### Session Start
1. Read `sessionLog.md` — understand what happened before
2. Read `activeContext.md` — understand current focus
3. Read `progress.md` — understand where things stand
4. Register your session in `sessionLog.md` under Active Sessions

### During Session
- Update files at natural checkpoints (every 10-15 minutes of active work)
- Match events to files: decision made? Update `decisionLog.md`. Architecture changed? Update `systemPatterns.md`.

### Session End
1. Update `activeContext.md` with current state
2. Update `progress.md` if milestones moved
3. Move your session from Active to History in `sessionLog.md`
4. Commit all Memory Bank changes
5. Push to remote

## Cross-Agent Awareness

The Memory Bank is agent-agnostic. Claude Code, Cursor, and Cline all read and write the same files. This means:

- A Cursor session can pick up where Claude Code left off
- A Cline architect session can hand off to a Cline code session seamlessly
- Session history shows which agent did what, enabling accountability

Each agent's configuration template includes the Memory Bank protocol adapted to that agent's format. The protocol is the same; only the config syntax differs.

## File Location

Place Memory Bank files wherever your agent expects them. Common locations:

- `.cursor/memory/` — Cursor projects
- `.pac/memory/` — PAC convention
- `docs/memory/` — Documentation-heavy projects

The path is configurable via placeholders in each agent template. Pick one location and use it consistently.

## Getting Started

Copy the files from `example/` into your project's memory directory. They contain the correct headings and placeholder text. Start your first session by filling in `productContext.md` and `projectPreferences.md` — these rarely change and give every future session the baseline context it needs.
