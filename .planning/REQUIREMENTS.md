# Requirements: Palimpsest

**Defined:** 2026-03-19
**Core Value:** One command gives you a working AI-powered project management companion — versioned, updatable, with methodology and tooling that just works.

## v1.0 Requirements

Requirements for initial release. Each maps to roadmap phases.

### CLI Foundation

- [ ] **CLI-01**: User can install palimpsest with a single command (`pip install` / `pipx install` / `uv tool install`)
- [ ] **CLI-02**: Every command and subcommand responds to `--help` with usage info
- [ ] **CLI-03**: User can check installed version with `palimpsest --version`
- [ ] **CLI-04**: CLI displays colored terminal output with rich formatting
- [ ] **CLI-05**: CLI shows meaningful error messages (no raw tracebacks for user errors)
- [ ] **CLI-06**: Write operations support `--dry-run` to preview changes

### Project Scaffolding

- [ ] **INIT-01**: User can run `palimpsest init` to scaffold a project (replaces setup.sh)
- [ ] **INIT-02**: Init auto-detects which AI editors are present in the project/system
- [ ] **INIT-03**: Init installs correct agent config format for each detected editor (Cursor, Claude Code, Cline)
- [ ] **INIT-04**: Init is idempotent — running twice does not corrupt the project
- [ ] **INIT-05**: User can override detection with `--editors cursor,claude-code` flag
- [ ] **INIT-06**: Init initializes Memory Bank protocol files for detected editors
- [ ] **INIT-07**: Init creates file manifest (`.palimpsest/manifest.json`) tracking installed files + checksums

### Content Access

- [ ] **CONT-01**: User can browse/open methodology guides with `palimpsest docs`
- [ ] **CONT-02**: User can list and copy document templates with `palimpsest template <name>`
- [ ] **CONT-03**: User can access playbooks with `palimpsest playbook <name>`
- [ ] **CONT-04**: Anechoic async methodology ships as bundled content under its own brand
- [ ] **CONT-05**: User can access anechoic content via `palimpsest anechoic` command
- [ ] **CONT-06**: Anechoic version is pinned and tracked — updates flow with palimpsest releases

### Update & Maintenance

- [ ] **UPD-01**: User can run `palimpsest update` to pull new content
- [ ] **UPD-02**: Update detects user-modified files via manifest checksums and preserves them
- [ ] **UPD-03**: Update shows changelog of what changed between versions

### Setup Experience

- [ ] **SETUP-01**: After init, interactive wizard guides user through project setup (name, stakeholders, timeline)
- [ ] **SETUP-02**: Wizard answers pre-fill templates with real data instead of placeholders
- [ ] **SETUP-03**: Wizard surfaces anechoic async methodology as an option to explore

### Distribution

- [ ] **DIST-01**: Palimpsest is available via Homebrew (`brew install palimpsest` via custom tap)
- [ ] **DIST-02**: All methodology docs, templates, configs, playbooks, and anechoic content ship as package data

### Health & Diagnostics

- [ ] **DIAG-01**: User can run `palimpsest doctor` to validate installation health
- [ ] **DIAG-02**: Doctor checks agent configs, memory bank, env vars, and manifest integrity

## v1.1 Requirements

Deferred to next milestone. Tracked but not in current roadmap.

### Team Sync

- **SYNC-01**: User can export palimpsest setup as shareable snapshot (minus private folder)
- **SYNC-02**: User can import another user's exported snapshot to bootstrap their setup
- **SYNC-03**: Export includes manifest of private folder structure (categories, templates — not content)
- **SYNC-04**: Committed repo artifact enables team members to get up to speed instantly
- **SYNC-05**: Init wizard offers solo mode vs team sync mode

### Extended Editor Support

- **EDIT-01**: Init supports Codex editor detection and config
- **EDIT-02**: Init supports Goose editor detection and config
- **EDIT-03**: Init supports Kilo editor detection and config

## Out of Scope

| Feature | Reason |
|---------|--------|
| MCP server for live LLM integration | Interesting but separate project, not v1 |
| SaaS/hosted version | Local-first, open-source tool |
| Custom AI model training | Uses existing AI editors as-is |
| Plugin/extension system | Premature — editor config formats still evolving |
| Auto-updating (background) | Hostile UX for a tool that modifies project files |
| Windows support | macOS/Linux first; add based on demand |
| Real-time editor sync | File-system consistency is sufficient |
| GUI installer | Audience can run pip/pipx/brew |
| Node.js/npx distribution | Core is Python; adding Node doubles packaging work |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLI-01 | — | Pending |
| CLI-02 | — | Pending |
| CLI-03 | — | Pending |
| CLI-04 | — | Pending |
| CLI-05 | — | Pending |
| CLI-06 | — | Pending |
| INIT-01 | — | Pending |
| INIT-02 | — | Pending |
| INIT-03 | — | Pending |
| INIT-04 | — | Pending |
| INIT-05 | — | Pending |
| INIT-06 | — | Pending |
| INIT-07 | — | Pending |
| CONT-01 | — | Pending |
| CONT-02 | — | Pending |
| CONT-03 | — | Pending |
| CONT-04 | — | Pending |
| CONT-05 | — | Pending |
| CONT-06 | — | Pending |
| UPD-01 | — | Pending |
| UPD-02 | — | Pending |
| UPD-03 | — | Pending |
| SETUP-01 | — | Pending |
| SETUP-02 | — | Pending |
| SETUP-03 | — | Pending |
| DIST-01 | — | Pending |
| DIST-02 | — | Pending |
| DIAG-01 | — | Pending |
| DIAG-02 | — | Pending |

**Coverage:**
- v1.0 requirements: 29 total
- Mapped to phases: 0
- Unmapped: 29 ⚠️

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-19 after initial definition*
