# Project Research Summary

**Project:** Palimpsest CLI Packaging
**Domain:** Python CLI tool for distributing AI editor configurations + TPM methodology
**Researched:** 2026-03-17
**Confidence:** MEDIUM

## Executive Summary

Palimpsest is a content-distribution CLI masquerading as a developer tool. The core challenge is not building a complex application -- it is reliably shipping non-Python content (markdown docs, agent configs, templates, playbooks) inside a Python package and keeping user installations updatable without destroying customizations. Experts building comparable tools (cookiecutter, copier, GSD) solve this by treating the CLI as a thin orchestration layer over a manifest-tracked file installation system. The recommended approach follows the same pattern: restructure the codebase into a proper `palimpsest/` Python package with content as package data, use Click for a 4-command CLI (`init`, `update`, `status`, `doctor`), and distribute via PyPI with `pipx install` as the primary UX.

The single highest-risk technical decision is the package restructure. The existing `scripts/` namespace is unpublishable, and all content directories (docs, templates, agents, playbooks) sit outside any Python package, meaning they will silently disappear from installed wheels. This must be solved first and validated with a wheel-build-and-verify CI step before any feature work begins. The second major risk is the update command: without a manifest-based checksum system designed from day one, the update flow will either destroy user work or be so conservative it never updates anything.

The recommended build backend is hatchling (not setuptools), which handles non-Python content inclusion more predictably. Core CLI dependencies are minimal: Click plus standard library. The heavy Google/Atlassian/Slack automation dependencies move behind an `[automation]` optional extra. Editor detection uses a registry-based adapter pattern that can evolve independently as AI editors change their config formats.

## Key Findings

### Recommended Stack

The stack is deliberately minimal for the core CLI, with heavy dependencies gated behind optional extras. See `.planning/research/STACK.md` for full rationale and alternatives considered.

**Core technologies:**
- **hatchling** (build backend): Predictable non-Python content inclusion via `[tool.hatch.build]`, replacing setuptools' error-prone `package_data` + `MANIFEST.in` dance
- **Click** (CLI framework): Explicit decorator-based subcommands, zero dependencies, full control over prompts and context passing -- better fit than Typer for complex subcommand logic
- **rich** (terminal output): Formatted tables for `pac status`, progress bars for `pac update`, colored output throughout
- **questionary** (interactive prompts): Multi-step guided setup wizard for `pac init`, built on prompt_toolkit
- **importlib.resources** (stdlib): Correct API for accessing bundled content at runtime -- never `__file__` paths
- **hatch-vcs + python-semantic-release** (versioning): Git-tag-derived versions with automated changelog generation

**Critical version requirement:** Python 3.10+ (for stable `importlib.resources.files()` API).

### Expected Features

See `.planning/research/FEATURES.md` for full feature landscape with complexity ratings and dependency chains.

**Must have (table stakes):**
- Single-command install via PyPI (`pipx install palimpsest`)
- `pac init` replacing setup.sh, with editor auto-detection
- `--help` and `--version` on all commands
- File manifest tracking (`.palimpsest/manifest.json`) for installed content
- Idempotent operations (safe to re-run)
- Meaningful error messages and `--dry-run` on destructive operations
- Cross-platform support (macOS + Linux; Windows deferred)

**Should have (differentiators):**
- Multi-editor agent config installation (Cursor, Claude Code, Cline as day-one targets)
- Memory Bank initialization across editors (editor-neutral path: `.palimpsest/memory/`)
- `pac update` with user-patch preservation via manifest checksums
- Interactive guided setup wizard (program name, stakeholders, timeline)
- Content access commands: `pac docs`, `pac template`, `pac playbook`
- `pac doctor` health check
- Selective editor targeting (`--editors` flag)

**Defer (v2+):**
- MCP server (explicitly out of scope per PROJECT.md)
- Plugin/extension system (premature abstraction)
- Windows support (based on demand)
- Real-time sync between editors
- Auto-updating (background updates)

### Architecture Approach

The architecture wraps the existing four-layer codebase (Content, Agent, Automation, Scaffolding) in a CLI shell. The CLI does not restructure existing code -- it ships it as a content payload. The key structural decisions are: (1) rename `scripts/` to `palimpsest/` for a proper package namespace, (2) use an adapter pattern for editor support so each editor is independently testable and new editors are single-file additions, (3) track all installed files in a project-local manifest that drives update behavior, and (4) classify content by type (skeleton, template, methodology, agent-config, memory-bank) to determine per-file update strategy. See `.planning/research/ARCHITECTURE.md` for component diagrams and data flows.

**Major components:**
1. **CLI Entry Point** (`pac`) -- Click-based command group dispatching to subcommand handlers
2. **Editor Detector + Adapters** -- Registry of editor definitions with multi-signal detection (config dirs, binaries, running processes) and per-editor config generation
3. **Content Copier** -- Reads content bundles from package data via `importlib.resources`, writes to target project, records in manifest
4. **Manifest Store** -- JSON-based tracking of installed files with SHA-256 checksums, version, and content type classification
5. **Update Engine** -- Three-way comparison (old-installed vs new-available vs user-current) with type-aware merge strategy
6. **Guided Setup Wizard** -- questionary-based interactive prompts feeding template variable substitution

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for the full inventory of 14 pitfalls with prevention strategies.

1. **Non-Python files silently missing from wheels** -- Content dirs outside a Python package disappear from installed wheels. Prevention: restructure content under `palimpsest/data/` with proper `package_data` config, validate with wheel-build CI step.
2. **Update command destroys user customizations** -- Naive file copy overwrites hours of user work. Prevention: manifest-based checksums with three-way classification (pristine/modified/new), `--dry-run` as default behavior.
3. **Editor detection based on stale heuristics** -- AI editors change config locations between versions. Prevention: multi-signal detection, manual override flag, editor registry maintained separately from core code.
4. **Heavy dependencies for a content-distribution tool** -- Google API libraries required for `pac init` is hostile UX. Prevention: core depends only on Click, automation behind `[automation]` optional extra.
5. **Homebrew formula fights Python packaging** -- Homebrew Python upgrades break formulas. Prevention: ship `pipx` as primary install method, Homebrew as secondary with vendored venv.

## Implications for Roadmap

Based on the dependency chains across all four research files, the project naturally divides into 5 phases.

### Phase 1: Package Foundation
**Rationale:** Everything depends on the package restructure. Cannot build any CLI feature until content ships correctly in a wheel. This is the critical path.
**Delivers:** Proper `palimpsest/` Python package with `src/` layout, content bundled as package data, basic `pac --version` CLI skeleton, CI step validating wheel contents.
**Addresses:** Single-command install (table stakes), `--version` (table stakes)
**Avoids:** Pitfall 1 (missing content in wheels), Pitfall 2 (importlib.resources misuse), Pitfall 7 (entry point mismatch after rename), Pitfall 9 (heavy dependencies)

### Phase 2: Init Command + Editor Support
**Rationale:** The `init` command is the first user-facing feature and the one that delivers the core value proposition ("one command, full AI-TPM"). Editor detection and adapter pattern must be built here because init depends on them. Manifest tracking starts here too.
**Delivers:** `pac init` with editor auto-detection, multi-editor config installation (Cursor + Claude Code + Cline), project scaffolding, manifest creation, `--dry-run` support.
**Uses:** Click (CLI), importlib.resources (content access), Editor Adapter pattern (architecture)
**Implements:** Editor Detector, Editor Adapters, Content Copier, Manifest Store
**Avoids:** Pitfall 5 (stale detection heuristics), Pitfall 8 (template variable injection), Pitfall 10 (config format drift), Pitfall 13 (git race conditions)

### Phase 3: Update System + Content Access
**Rationale:** The update command depends on the manifest format established in Phase 2. Content access commands (docs, template, playbook) are independent and low-complexity, making them good companions to the harder update work.
**Delivers:** `pac update` with user-patch preservation, `pac status` health check, `pac docs` / `pac template` / `pac playbook` content access, `pac doctor` diagnostics.
**Uses:** Manifest Store (reads), Content Copier (writes), rich (formatted output)
**Implements:** Update Engine, content type classification, three-way merge strategy
**Avoids:** Pitfall 3 (user data loss), Pitfall 6 (self-update chicken-and-egg)

### Phase 4: Guided Setup + Polish
**Rationale:** The interactive wizard enhances init but is not required for it. This phase adds the "delightful" layer on top of working core commands. Includes the self-update notice system.
**Delivers:** Interactive guided setup wizard (program name, stakeholders, timeline), template variable substitution with user input, version-check notices, changelog display on update.
**Uses:** questionary (prompts), rich (output formatting)
**Implements:** Guided Setup component

### Phase 5: Distribution + Automation Migration
**Rationale:** Homebrew requires a stable PyPI release. Automation script migration is independent of all other phases and can be done last. This phase is about reach, not features.
**Delivers:** PyPI publishing pipeline (GitHub Actions), Homebrew tap with formula, automation scripts reorganized under `palimpsest.automation` namespace behind `[automation]` extra, additional editor support (Codex, Goose, Kilo).
**Avoids:** Pitfall 4 (Homebrew + Python conflicts)

### Phase Ordering Rationale

- **Dependency-driven:** Package restructure (Phase 1) must precede all feature work. Init (Phase 2) must precede update (Phase 3) because update depends on the manifest format. Distribution (Phase 5) must follow a stable PyPI-publishable package.
- **Value-driven:** Init delivers the core promise fastest. Update makes the tool sticky. Content access commands are cheap wins that round out the UX.
- **Risk-driven:** The two highest-risk items (content packaging and update-without-data-loss) are tackled in Phases 1-3 when there are fewer users to break. Distribution polish comes after the core is solid.
- **Architecture-driven:** The adapter pattern and manifest schema are load-bearing design decisions. Getting them right in Phases 1-2 prevents expensive rework later.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Editor Support):** AI editor config formats may have changed since May 2025 training cutoff. Verify `.cursorrules` deprecation status, Claude Code `AGENTS.md` conventions, Cline current format. Check each editor's documentation before implementing adapters.
- **Phase 5 (Homebrew):** Homebrew Python formula patterns may have evolved. Verify `virtualenv_install_with_resources` helper still exists and check current best practices for Python CLI distribution via Homebrew.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Package Foundation):** Python packaging with hatchling is well-documented. `src/` layout, `importlib.resources`, and CI wheel validation are established patterns.
- **Phase 3 (Update System):** Manifest-based update with checksum comparison is a solved pattern (GSD, yeoman, Homebrew all do this).
- **Phase 4 (Guided Setup):** questionary + Click integration is straightforward.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Versions based on May 2025 training data. Core choices (Click, hatchling, rich) are stable and unlikely to be wrong. Validate specific version numbers before implementation. |
| Features | MEDIUM | Feature landscape derived from comparable tools and PROJECT.md requirements. Editor-specific features need validation against current editor versions. |
| Architecture | MEDIUM | Patterns are well-established (adapter, manifest-tracking, content-type classification). Package layout needs validation with actual wheel builds. |
| Pitfalls | HIGH | Python packaging pitfalls are thoroughly documented and stable knowledge. Editor-specific pitfalls (detection, config drift) are MEDIUM. |

**Overall confidence:** MEDIUM -- the core approach is sound and well-precedented, but specific technology versions and editor config formats need validation before implementation begins.

### Gaps to Address

- **Editor config format currency:** All editor config path/format knowledge is from May 2025. Cursor, Claude Code, and Cline may have changed conventions. Validate during Phase 2 planning.
- **hatchling version compatibility:** Verify hatch-vcs works with the chosen hatchling version. Run `pip index versions hatchling` before starting Phase 1.
- **Homebrew formula best practices:** Check current Homebrew docs for Python CLI formula patterns before Phase 5. The `virtualenv_install_with_resources` approach may have changed.
- **PyPI name availability:** Verify `palimpsest` is available on PyPI. If taken, need an alternative (`palimpsest-tpm`, `pac-tpm`, etc.).
- **Memory Bank path convention:** Current hardcoding to `.cursor/memory/` needs resolution. Research recommends `.palimpsest/memory/` as editor-neutral default, but this changes the existing user workflow. Decide during Phase 2 planning.

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis: `pyproject.toml`, `setup.sh`, `agents/` directory, `scripts/` layout
- `.planning/PROJECT.md` project requirements and GSD prior art
- `.planning/codebase/CONCERNS.md` existing tech debt inventory
- Python packaging standards: PEP 621, PEP 660, importlib.resources stdlib docs

### Secondary (MEDIUM confidence)
- Training data knowledge (May 2025 cutoff): Click, hatchling, rich, questionary APIs and best practices
- Comparable tool patterns: cookiecutter, copier, GSD, django-admin, cargo init, gh CLI
- Homebrew Python formula patterns from existing formulas (poetry, httpie, aws-cli)
- AI editor config conventions: Claude Code `CLAUDE.md`, Cursor `.cursorrules`/`.cursor/rules/`, Cline `.clinerules`

### Tertiary (LOW confidence)
- Specific version numbers for all recommended packages -- validate with `pip index versions` before implementation
- Codex, Goose, and Kilo config conventions -- these editors are pre-1.0 or newly released, documentation sparse

---
*Research completed: 2026-03-17*
*Ready for roadmap: yes*
