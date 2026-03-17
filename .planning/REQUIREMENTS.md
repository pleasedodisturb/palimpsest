# Requirements

## v1 Requirements

### PKG: Package Restructure

| ID | Requirement | Priority |
|----|-------------|----------|
| PKG-01 | Ship all content as package data (templates, agent configs, docs, playbooks, methodology) | Must have |
| PKG-02 | Python automation scripts remain functional and installable as optional extras | Must have |

### INST: Install Experience

| ID | Requirement | Priority |
|----|-------------|----------|
| INST-01 | Single-command install that drops full AI-TPM into any project | Must have |
| INST-02 | Standalone binary distribution (Python required at runtime, but packaged cleanly) | Must have |

### DETECT: Editor Detection and Configuration

| ID | Requirement | Priority |
|----|-------------|----------|
| DETECT-01 | Runtime detection -- identify which AI editor(s) are present and install correct config format | Must have |
| DETECT-02 | Multi-editor support -- Claude Code, Cursor, Cline, Codex, Goose, Kilo | Must have |

### SETUP: Post-Install Setup

| ID | Requirement | Priority |
|----|-------------|----------|
| SETUP-01 | Interactive guided setup after install (program name, stakeholders, timeline) | Must have |

### LIFECYCLE: Versioning and Updates

| ID | Requirement | Priority |
|----|-------------|----------|
| LIFE-01 | Versioned releases with semantic versioning | Must have |
| LIFE-02 | Update command that pulls new templates/docs while preserving user changes | Must have |
| LIFE-03 | Changelog generation so users see what changed between versions | Must have |

## v2 / Out of Scope

- MCP server for live LLM integration
- SaaS/hosted version
- Custom AI model training
- Replacing GSD or other dev workflow tools
- Supporting non-AI editors

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PKG-01 | Phase 1 | Pending |
| PKG-02 | Phase 1 | Pending |
| INST-01 | Phase 2 | Pending |
| INST-02 | Phase 2 | Pending |
| DETECT-01 | Phase 3 | Pending |
| DETECT-02 | Phase 3 | Pending |
| SETUP-01 | Phase 4 | Pending |
| LIFE-01 | Phase 5 | Pending |
| LIFE-02 | Phase 5 | Pending |
| LIFE-03 | Phase 5 | Pending |

---
*Last updated: 2026-03-18 after roadmap creation*
