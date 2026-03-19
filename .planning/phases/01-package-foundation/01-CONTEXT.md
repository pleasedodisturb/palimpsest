# Phase 1: Package Foundation - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning
**Source:** Split from Phase 2 (CLI and Install) context

<domain>
## Phase Boundary

Restructure palimpsest into an installable Python package with a CLI skeleton and all content bundled as package data. After this phase, a user can `pipx install palimpsest` and get a working `pal` command with `--help`, `--version`, colored output, and meaningful error messages. This phase does NOT cover: `init`, editor detection, content access commands, or update functionality — those are later phases.

</domain>

<decisions>
## Implementation Decisions

### CLI entry point and naming
- Primary command: `pal` (short, memorable)
- Also register `palimpsest` and keep `pac` as aliases in pyproject.toml
- CLI framework: Typer (modern, type-hint based on Click)
- Terminal UX: Rich library for beautiful prompts, panels, progress bars, styled output

### Package restructuring
- Expand `[tool.setuptools.packages.find]` to include CLI module
- Add `package-data` for all content (templates, docs, agents, playbooks, methodology, anechoic)
- All methodology docs, templates, configs, playbooks ship inside the wheel
- Anechoic async methodology bundled as content under its own brand (version-pinned from ~/Projects/anechoic)

### Global CLI flags
- `--verbose` / `-v` — extra detail output
- `--quiet` / `-q` — minimal output

### Error handling
- Rich panels with fix suggestions (Rust compiler error style)
- What went wrong + suggested fix in a styled panel
- Verbose mode shows full traceback and context
- User errors produce meaningful messages, not Python tracebacks

### Claude's Discretion
- Exact Rich theme/color palette
- Exact Typer command group organization
- How to structure the CLI module (single file vs package)
- How to vendor/bundle anechoic content during build

</decisions>

<specifics>
## Specific Ideas

- CLI should feel polished — think experience similar to `create-next-app` or `cargo init`
- `pal` is the muscle-memory command; `palimpsest` is for discoverability and documentation
- GSD's installer patterns are prior art worth learning from — but this is Python, not Node

</specifics>

<canonical_refs>
## Canonical References

### Project definition
- `.planning/PROJECT.md` — Core value prop, constraints, key decisions
- `.planning/REQUIREMENTS.md` — CLI-01 through CLI-05, DIST-02

### Current package structure
- `pyproject.toml` — Current package config (only ships `scripts*`, needs expansion)

### Content to bundle as package data
- `docs/` — 10 methodology guides
- `templates/` — TPM document templates
- `agents/` — Agent configurations
- `playbooks/` — TPM situation playbooks
- `showcase/` — Demo prompts and quick wins
- `case-study/wolt-crm-migration.md` — Case study (needs anonymization)
- `~/Projects/anechoic/` — Anechoic async methodology (external, version-pinned)

### Architecture context
- `.planning/codebase/ARCHITECTURE.md` — Content-as-code pattern, 4 layers, data flow
- `.planning/codebase/STRUCTURE.md` — Full directory layout, naming conventions, package structure
- `.planning/codebase/CONCERNS.md` — Known tech debt (don't fix in this phase, wrap cleanly)

</canonical_refs>

<code_context>
## Existing Code Insights

### Integration Points
- `pyproject.toml` — Must expand `[tool.setuptools.packages.find]` to include CLI module, and add `package-data` for templates/docs/agents
- `pyproject.toml` `[project.scripts]` — Add `pal` and `palimpsest` entry points alongside existing `pac`
- `pyproject.toml` `[project.dependencies]` — Add `typer`, `rich` as new dependencies

### Established Patterns
- Environment variable driven config (no hardcoded values) — CLI must follow this
- `pac` namespace for agent markers — keep this convention

</code_context>

<deferred>
## Deferred Ideas

- `init`, `check`, `docs` commands — Phase 2 and 3
- Editor detection and config installation — Phase 2
- `pal update` with user-patch preservation — Phase 4
- Homebrew formula — Phase 5
- `--dry-run` flag — Phase 2 (when write operations exist)

</deferred>

---

*Phase: 01-package-foundation*
*Context gathered: 2026-03-19 (split from 02-cli-and-install context)*
