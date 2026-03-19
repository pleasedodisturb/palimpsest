# Phase 2: Init & Editor Detection - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning
**Source:** Split from Phase 2 (CLI and Install) context

<domain>
## Phase Boundary

Users can run `pal init` in any project to get full AI-powered project management scaffolding with correct editor configs for their detected environment. This phase covers: init command, editor auto-detection, multi-editor config installation, Memory Bank initialization, file manifest, idempotent operations, `--editors` override, `--dry-run` flag, and privacy model. It does NOT cover: content browsing commands, update/versioning, or guided setup wizard (those are later phases).

</domain>

<decisions>
## Implementation Decisions

### Init command behavior
- Guided interactive setup (like `npm init` interactive mode)
- Ask program name, key stakeholders, timeline, integrations during setup
- Works in BOTH new directories and existing repos:
  - With name arg or in empty dir: creates new project directory
  - In existing repo: adds palimpsest files alongside existing content
- Git init: only if not already in a git repo. If already in repo, just add files
- Conflict handling in existing repos: prompt per conflict (skip, overwrite, or backup)

### Init output — what gets scaffolded
- ALL content gets copied into the user's project (not kept in package):
  - Program docs (PROGRAM_OVERVIEW, DASHBOARD, BACKLOG) — project root `docs/`
  - Methodology docs (10 guides) — `docs/palimpsest/`
  - Playbooks — `docs/palimpsest/playbooks/`
  - Templates — `docs/palimpsest/templates/`
  - Showcase (demo prompts, quick wins) — `docs/palimpsest/showcase/`
  - Case study — `docs/palimpsest/case-study/` (ANONYMIZED — strip Wolt name, employee names, internal URLs; use changed/fictional names throughout)
- Memory Bank (7 files) — `.palimpsest/memory-bank/` (editor-neutral location)
- Agent configs — generated from agent.md (see editor detection section)
- .gitignore — generated based on privacy profile selection
- Context directories — `docs/context/` with privacy-appropriate structure

### Editor detection and agent.md
- `agent.md` in project root is the CANONICAL source of truth for all editor configs
- Always created during init — this is the single source
- Editor-specific files (CLAUDE.md, .cursorrules, .clinerules-*) are auto-generated FROM agent.md
- Detection flow:
  1. Scan for editor dotfiles/configs (.cursor/, CLAUDE.md, .clinerules)
  2. Show what was detected, ask user to confirm which to configure
  3. For editors NOT detected, show as optional ("We didn't detect Cursor, want to install Cursor config anyway?")
  4. Generate editor-specific config files from agent.md for all selected editors
- Config sync:
  - Manual command `pal sync-config` to regenerate editor configs from agent.md
  - `pal check` warns if editor configs are stale (out of sync with agent.md)

### Selective editor targeting
- `--editors cursor,claude-code` flag overrides auto-detection
- Power users want explicit control over which editors get configured

### File manifest
- `.palimpsest/manifest.json` tracks all installed files with checksums
- Enables idempotent operations (running init twice is safe)
- Foundation for future `pal update` with user-patch preservation

### Privacy model
- Inline explanation during init (Rich panel explaining public vs private before user chooses)
- Two types of data:
  - **Private** (gitignored): 1:1 notes, sensitive context — critical for AI context but never exposed
  - **Public** (committed): Team meeting transcripts, daily digests, shared docs
- User can choose per content type whether to gitignore
- Privacy preset profiles offered during init:
  - "Solo" — everything private (maximally safe)
  - "Team project" — structured public/private split (recommended default)
  - "Open program" — most things public
- After selecting preset, user can customize individual content type visibility
- Generated .gitignore reflects all choices

### VCS handling of .palimpsest/
- User chooses during init: team project (commit all) vs personal (gitignore memory bank)
- Different .gitignore templates based on choice

### Dry-run mode
- `--dry-run` on init and all write operations — preview changes without writing
- Existing convention in the codebase, extended to CLI

### Claude's Discretion
- Temp file handling during scaffold
- agent.md template structure and sections
- How to detect editor presence (which dotfiles/processes to check)
- Exact manifest.json schema

</decisions>

<specifics>
## Specific Ideas

- The privacy explanation during init is a differentiator — most tools don't explain data sensitivity to users
- Case study MUST be anonymized before shipping: no "Wolt", no real employee names, no internal URLs. Use fictional but realistic replacements
- GSD's installer patterns (file manifest, version tracking, user patch preservation) are prior art worth learning from — but this is Python, not Node

</specifics>

<canonical_refs>
## Canonical References

### Project definition
- `.planning/PROJECT.md` — Core value prop, constraints, key decisions
- `.planning/REQUIREMENTS.md` — INIT-01 through INIT-07, CLI-06

### Existing implementation to migrate
- `setup.sh` — Current scaffolding logic (bash). This is the prototype for `pal init`
- `project-template/` — Current template directory used by setup.sh
- `scripts/core/preflight_check.py` — Current `pac` CLI entry point

### Content to ship
- `docs/` — 10 methodology guides to include in scaffold
- `templates/` — TPM document templates
- `agents/` — Agent configurations (source for agent.md template)
- `playbooks/` — TPM situation playbooks
- `showcase/` — Demo prompts and quick wins
- `case-study/wolt-crm-migration.md` — Case study (needs anonymization)
- `agents/memory-bank/` — Memory Bank protocol spec and example files

### Architecture context
- `.planning/codebase/ARCHITECTURE.md` — Content-as-code pattern, 4 layers, data flow
- `.planning/codebase/STRUCTURE.md` — Full directory layout, naming conventions, package structure

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `setup.sh` — Full scaffolding logic. The guided setup flow, directory creation, template writing, git init, and MCP config generation can all inform the Python CLI implementation
- `project-template/` — Existing template files for PROGRAM_OVERVIEW, DASHBOARD, BACKLOG, .gitignore, MCP config, context README
- `agents/memory-bank/example/` — 7 starter Memory Bank files
- `agents/formatting-standards.md` — Writing standards that should inform the agent.md template

### Established Patterns
- Environment variable driven config (no hardcoded values) — CLI must follow this
- `pac` namespace for agent markers — keep this convention
- `.gitignore` privacy boundary — well-established pattern to build on

</code_context>

<deferred>
## Deferred Ideas

- `pal update` command with user-patch preservation — Phase 4
- `pal sync` command for external service sync — future
- Homebrew formula — Phase 5
- Runtime detection of which AI editor is actively running — nice to have, not this phase
- Guided setup wizard (program name, stakeholders, timeline) — Phase 4 (SETUP-01..03)

</deferred>

---

*Phase: 02-init-and-editor-detection*
*Context gathered: 2026-03-19 (split from 02-cli-and-install context)*
