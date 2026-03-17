# Palimpsest v1.0 — Packaged AI-TPM Blueprint

## What This Is

An open-source blueprint that lets anyone summon a full AI-powered Technical Program Manager into any project with a single command. Today palimpsest is a loose collection of methodology docs, agent configs, Python scripts, templates, and playbooks scattered across a git repo. The goal is to package all of this into a versioned, installable artifact — one command drops the full AI-TPM capability into a project, then an interactive guided setup helps configure the program context.

The target audience is both TPMs who use AI editors and developers building TPM tooling. It should work across Claude Code, Cursor, Cline, Codex, Goose, and Kilo.

## Core Value

One command gives you a working AI-TPM in any project — versioned, updatable, with methodology and tooling that just works.

## Requirements

### Validated

- ✓ Methodology documentation (10 guides covering full TPM lifecycle) — existing
- ✓ Agent configurations for Cursor, Claude Code, Cline — existing
- ✓ Memory Bank protocol (7-file shared state across agents) — existing
- ✓ Python automation scripts (sync, content, publishing, automation) — existing
- ✓ Project scaffolding via setup.sh — existing
- ✓ Markdown templates for program docs — existing
- ✓ Playbooks for common TPM situations — existing
- ✓ Case study (Wolt CRM migration narrative) — existing
- ✓ CI pipeline (GitHub Actions, Python 3.10-3.12) — existing
- ✓ Privacy model (.gitignore-enforced public/private boundary) — existing

### Active

- [ ] Single-command install that drops full AI-TPM into any project
- [ ] Runtime detection — identify which AI editor(s) are present and install correct config format
- [ ] Multi-editor support — Claude Code, Cursor, Cline, Codex, Goose, Kilo
- [ ] Interactive guided setup after install (program name, stakeholders, timeline)
- [ ] Versioned releases with semantic versioning
- [ ] Update command that pulls new templates/docs while preserving user changes
- [ ] Standalone binary distribution (Python required at runtime, but packaged cleanly)
- [ ] Changelog generation so users see what changed between versions
- [ ] Ship all content as package data (templates, agent configs, docs, playbooks, methodology)
- [ ] Python automation scripts remain functional and installable as optional extras

### Out of Scope

- MCP server for live LLM integration — interesting but separate project, not v1
- SaaS/hosted version — this is a local-first, open-source blueprint
- Custom AI model training — uses existing AI editors as-is
- Replacing GSD or other dev workflow tools — complementary, not competitive
- Supporting non-AI editors — the value prop requires an AI-capable editor

## Context

### What exists today

Palimpsest is a brownfield project with substantial content but primitive packaging. The `pyproject.toml` declares a Python package but only ships the `scripts/` directory. The methodology (10 docs), templates, agent configs, playbooks, showcase, and case study are all outside the package boundary. `setup.sh` is a Bash script that copies files from `project-template/` — it works but isn't versioned, updatable, or discoverable.

### Prior art: GSD (Get Shit Done)

GSD solves a similar distribution problem for AI development workflows. Key patterns to learn from:
- **npx-based installer** (`bin/install.js`) that detects the runtime and installs to the right config directory
- **Slash commands** installed as markdown files the AI editor natively reads
- **Agent definitions** installed globally or per-project
- **File manifest** for tracking what was installed (enables clean updates/uninstalls)
- **Version tracking** with update checks via hooks
- **User patch preservation** during updates

### Technical landscape

The codebase has 30+ environment variables, 8 JSON config files, and 13 test files. The Python scripts have known tech debt (duplicated auth code, broad exception handling, deprecated datetime usage) documented in `.planning/codebase/CONCERNS.md`. Packaging should not attempt to fix all tech debt — it should wrap what exists cleanly.

## Constraints

- **Python required**: The automation scripts are Python; users need Python 3.10+ at runtime
- **No hardcoded values**: All credentials, domains, IDs from environment variables (existing convention)
- **Cross-platform agent configs**: Each AI editor has different config formats — must translate correctly
- **Preserve existing structure**: The methodology docs, case study, and playbooks should ship as-is, not be restructured for packaging
- **Backward compatible**: Existing users who cloned the repo should have a migration path

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python CLI + binary over npx | Core scripts are Python; adding Node.js as dependency increases friction | — Pending |
| brew install as target UX | Widest reach for CLI tools, familiar to both devs and technical TPMs | — Pending |
| Runtime detection at install time | Different editors need different config formats; GSD proves this pattern works | — Pending |
| Update command with user-patch preservation | Templates will be customized; updates must not destroy user work | — Pending |
| Ship methodology as package data, not separate docs site | "One command, full TPM" means everything in one artifact | — Pending |

---
*Last updated: 2026-03-17 after initialization*
