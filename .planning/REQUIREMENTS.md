# Requirements: Palimpsest v1.0

**Defined:** 2026-03-17
**Core Value:** One command gives you a working AI-TPM in any project — versioned, updatable, with methodology and tooling that just works.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Packaging

- [ ] **PKG-01**: Project restructured from `scripts/` to `palimpsest/` with `src/` layout as a proper Python package
- [ ] **PKG-02**: All non-Python content (docs, templates, agents, playbooks, case study, showcase) ships as package_data inside the wheel
- [ ] **PKG-03**: CI step validates wheel contents — all expected files present after `pip install`
- [ ] **PKG-04**: Core CLI has zero heavy dependencies — Google/Atlassian/Slack libraries gated behind `[automation]` optional extra
- [ ] **PKG-05**: `pac --version` displays current semantic version derived from git tags

### CLI Init

- [ ] **INIT-01**: `pac init` scaffolds a complete program directory in the current folder (replacing setup.sh)
- [ ] **INIT-02**: `pac init` auto-detects installed AI editors and installs correct config format for each
- [ ] **INIT-03**: Editor detection supports Claude Code, Cursor, and Cline as day-one targets
- [ ] **INIT-04**: `pac init` creates a `.palimpsest/manifest.json` tracking all installed files with SHA-256 checksums
- [ ] **INIT-05**: `pac init` is idempotent — running twice does not corrupt or duplicate files
- [ ] **INIT-06**: `pac init --editors cursor,claude-code` allows selective editor targeting, overriding auto-detection
- [ ] **INIT-07**: `pac init --dry-run` shows what would be created without writing any files
- [ ] **INIT-08**: Memory Bank protocol initialized for all detected editors

### CLI Update

- [ ] **UPD-01**: `pac update` pulls new version of templates/docs/configs into an existing project
- [ ] **UPD-02**: Update detects user-modified files via manifest checksums and preserves user changes
- [ ] **UPD-03**: Update shows a diff/summary of what changed upstream before applying
- [ ] **UPD-04**: `pac update --dry-run` previews changes without modifying files
- [ ] **UPD-05**: Changelog displayed after update showing what changed between versions

### CLI Content Access

- [ ] **ACC-01**: `pac docs` lists and displays methodology guides from the installed package
- [ ] **ACC-02**: `pac template <name>` outputs a TPM template (to stdout or file)
- [ ] **ACC-03**: `pac playbook <name>` outputs a situational playbook
- [ ] **ACC-04**: `pac doctor` validates installation health — agent configs in place, memory bank initialized, env vars for automation

### Guided Setup

- [ ] **WIZ-01**: After scaffolding, interactive wizard walks user through program name, stakeholders, timeline
- [ ] **WIZ-02**: Wizard answers pre-fill template placeholders in generated files (no more `[PLACEHOLDER]`)
- [ ] **WIZ-03**: Wizard is skippable with `pac init --no-wizard` for automation/CI use

### Distribution

- [ ] **DIST-01**: Published to PyPI — installable via `pip install palimpsest` / `pipx install palimpsest`
- [ ] **DIST-02**: Homebrew tap with formula for `brew install palimpsest`
- [ ] **DIST-03**: GitHub Actions pipeline for automated PyPI publishing on tagged releases
- [ ] **DIST-04**: CHANGELOG.md maintained in keep-a-changelog format

### Multi-Editor Support (Extended)

- [ ] **EDIT-01**: Editor adapter pattern — each editor is a self-contained module, new editors are single-file additions
- [ ] **EDIT-02**: Codex editor adapter added
- [ ] **EDIT-03**: Goose editor adapter added
- [ ] **EDIT-04**: Kilo editor adapter added

### UX

- [ ] **UX-01**: All commands have `--help` with clear descriptions
- [ ] **UX-02**: Colored terminal output (consistent style across all commands)
- [ ] **UX-03**: Meaningful error messages for common failures (wrong Python version, permission errors, missing directory)
- [ ] **UX-04**: Non-zero exit codes on failure for CI/scripting use

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### MCP Server

- **MCP-01**: Palimpsest as MCP server exposing tools (update_dashboard, get_blockers, etc.)
- **MCP-02**: Any MCP-compatible client can connect and interact with program state

### Advanced Features

- **ADV-01**: Plugin/extension system for custom editor adapters
- **ADV-02**: Windows native support (beyond "doesn't crash")
- **ADV-03**: Real-time memory bank sync between editors
- **ADV-04**: Auto-update background check with opt-in notifications

## Out of Scope

| Feature | Reason |
|---------|--------|
| SaaS/web dashboard | Local-first, open-source tool — no hosting or auth |
| Custom AI model/LLM integration | Palimpsest configures existing editors, not provides AI |
| Node.js/npx distribution | Codebase is Python; adding Node doubles packaging work |
| GUI installer | CLI audience can run pip/pipx/brew |
| Automatic OAuth/API key setup | Security liability; varies per org; doctor checks config |
| Background auto-updates | Hostile UX for a tool that modifies project files |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PKG-01 | Phase 1 | Pending |
| PKG-02 | Phase 1 | Pending |
| PKG-03 | Phase 1 | Pending |
| PKG-04 | Phase 1 | Pending |
| PKG-05 | Phase 1 | Pending |
| INIT-01 | Phase 2 | Pending |
| INIT-02 | Phase 2 | Pending |
| INIT-03 | Phase 2 | Pending |
| INIT-04 | Phase 2 | Pending |
| INIT-05 | Phase 2 | Pending |
| INIT-06 | Phase 2 | Pending |
| INIT-07 | Phase 2 | Pending |
| INIT-08 | Phase 2 | Pending |
| UPD-01 | Phase 3 | Pending |
| UPD-02 | Phase 3 | Pending |
| UPD-03 | Phase 3 | Pending |
| UPD-04 | Phase 3 | Pending |
| UPD-05 | Phase 3 | Pending |
| ACC-01 | Phase 3 | Pending |
| ACC-02 | Phase 3 | Pending |
| ACC-03 | Phase 3 | Pending |
| ACC-04 | Phase 3 | Pending |
| WIZ-01 | Phase 4 | Pending |
| WIZ-02 | Phase 4 | Pending |
| WIZ-03 | Phase 4 | Pending |
| UX-01 | Phase 1 | Pending |
| UX-02 | Phase 1 | Pending |
| UX-03 | Phase 1 | Pending |
| UX-04 | Phase 1 | Pending |
| DIST-01 | Phase 5 | Pending |
| DIST-02 | Phase 5 | Pending |
| DIST-03 | Phase 5 | Pending |
| DIST-04 | Phase 5 | Pending |
| EDIT-01 | Phase 2 | Pending |
| EDIT-02 | Phase 5 | Pending |
| EDIT-03 | Phase 5 | Pending |
| EDIT-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 36 total
- Mapped to phases: 36
- Unmapped: 0

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-17 after initial definition*
