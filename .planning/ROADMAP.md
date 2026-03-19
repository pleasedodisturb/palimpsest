# Roadmap: Palimpsest v1.0

## Overview

Palimpsest v1.0 transforms a loose collection of TPM methodology, agent configs, templates, and scripts into a single-command installable toolkit. The roadmap progresses from packaging foundation (making content ship inside a wheel) through the core init command with editor detection, content access commands, update/setup experience, and finally distribution via Homebrew. Each phase delivers a complete, verifiable capability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Package Foundation** - Restructure into installable Python package with CLI skeleton and all content bundled
- [ ] **Phase 2: Init & Editor Detection** - `pac init` with editor auto-detection, config installation, manifest tracking
- [ ] **Phase 3: Content Access & Diagnostics** - Browse docs/templates/playbooks/anechoic content + `pac doctor` health check
- [ ] **Phase 4: Update System & Guided Setup** - `pac update` with user-patch preservation + interactive setup wizard
- [ ] **Phase 5: Distribution** - Homebrew tap and PyPI publishing pipeline

## Phase Details

### Phase 1: Package Foundation
**Goal**: Users can install palimpsest from PyPI and get a working CLI with version info and help text, with all methodology content bundled inside the package
**Depends on**: Nothing (first phase)
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, DIST-02
**Success Criteria** (what must be TRUE):
  1. User can run `pipx install palimpsest` (or pip/uv equivalent) and get a working `pac` command
  2. Running `pac --version` prints the installed version number
  3. Running `pac --help` and `pac <subcommand> --help` display usage info for all registered commands
  4. CLI output uses colored, rich-formatted text (not raw print statements)
  5. User errors produce meaningful messages, not Python tracebacks
**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md — Package restructure, content bundling, pyproject.toml entry points
- [ ] 01-02-PLAN.md — Typer CLI with Rich output, error handling, and test suite

### Phase 2: Init & Editor Detection
**Goal**: Users can run `pac init` in any project to get full AI-TPM scaffolding with correct editor configs for their detected environment
**Depends on**: Phase 1
**Requirements**: INIT-01, INIT-02, INIT-03, INIT-04, INIT-05, INIT-06, INIT-07, CLI-06
**Success Criteria** (what must be TRUE):
  1. User runs `pac init` in a project directory and gets methodology docs, templates, playbooks, and agent configs installed
  2. Init auto-detects which AI editors (Cursor, Claude Code, Cline) are present and installs the correct config format for each
  3. Running `pac init` a second time does not duplicate or corrupt previously installed files
  4. User can override editor detection with `--editors cursor,claude-code` flag
  5. A manifest file (`.palimpsest/manifest.json`) exists after init, tracking all installed files with checksums
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: Content Access & Diagnostics
**Goal**: Users can browse and access all bundled content (docs, templates, playbooks, anechoic methodology) through CLI commands, and validate their installation health
**Depends on**: Phase 2
**Requirements**: CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, CONT-06, DIAG-01, DIAG-02
**Success Criteria** (what must be TRUE):
  1. User can run `pac docs` to browse and open methodology guides
  2. User can run `pac template <name>` to list and copy document templates into their project
  3. User can run `pac playbook <name>` to access TPM playbooks
  4. User can run `pac anechoic` to access bundled anechoic async methodology content
  5. User can run `pac doctor` and see a health report covering agent configs, memory bank, env vars, and manifest integrity
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: Update System & Guided Setup
**Goal**: Users can update their installation without losing customizations, and new users get an interactive wizard that pre-fills templates with real project data
**Depends on**: Phase 2
**Requirements**: UPD-01, UPD-02, UPD-03, SETUP-01, SETUP-02, SETUP-03
**Success Criteria** (what must be TRUE):
  1. User can run `pac update` and receive new/changed content from a newer palimpsest version
  2. Files the user has manually edited are preserved during update (detected via manifest checksums)
  3. Update shows a changelog summarizing what changed between the old and new version
  4. After `pac init`, an interactive wizard guides the user through project setup (program name, stakeholders, timeline) and pre-fills templates with their answers
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: Distribution
**Goal**: Users can install palimpsest via Homebrew with a single `brew install` command
**Depends on**: Phase 4
**Requirements**: DIST-01
**Success Criteria** (what must be TRUE):
  1. User can run `brew install palimpsest` (via custom tap) and get a working `pac` command
  2. Homebrew-installed version behaves identically to pip-installed version
**Plans**: TBD

Plans:
- [ ] 05-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Package Foundation | 0/2 | Planning complete | - |
| 2. Init & Editor Detection | 0/? | Not started | - |
| 3. Content Access & Diagnostics | 0/? | Not started | - |
| 4. Update System & Guided Setup | 0/? | Not started | - |
| 5. Distribution | 0/? | Not started | - |
