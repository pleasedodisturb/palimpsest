# Roadmap

## Phases

- [x] **Phase 1: Package Foundation** - Restructure the repo so all content ships as package data and scripts remain installable (completed 2026-03-17)
- [ ] **Phase 2: CLI and Install** - Build the single-command install experience with standalone distribution
- [ ] **Phase 3: Editor Detection** - Runtime detection of AI editors and multi-editor config generation
- [ ] **Phase 4: Guided Setup** - Interactive post-install wizard that configures program context
- [ ] **Phase 5: Versioning and Updates** - Semantic versioning, update-with-patch-preservation, and changelog

## Phase Details

### Phase 1: Package Foundation
**Goal**: The palimpsest package includes all methodology, templates, agent configs, playbooks, and case study as installable package data, while keeping Python scripts functional as optional extras
**Depends on**: Nothing (first phase)
**Requirements**: PKG-01, PKG-02
**Success Criteria** (what must be TRUE):
  1. Running `pip install palimpsest` installs the full package including all methodology docs, templates, agent configs, playbooks, and case study as accessible package data
  2. A user can import and run any existing Python automation script after installing with optional extras (e.g., `pip install palimpsest[scripts]`)
  3. Existing tests pass against the restructured package layout without modification to test logic
**Plans**: 1 plan
Plans:
- [ ] 01-01-PLAN.md -- Restructure repo into palimpsest/ package with content as package data and scripts as optional extras

### Phase 2: CLI and Install
**Goal**: A user can run a single command to drop the full AI-TPM capability into any project directory
**Depends on**: Phase 1 (package must contain all content before install can deploy it)
**Requirements**: INST-01, INST-02
**Success Criteria** (what must be TRUE):
  1. Running `palimpsest init` (or equivalent) in any project directory creates the full AI-TPM file structure (program docs, templates, Memory Bank, .gitignore)
  2. The CLI is installable via `pip install palimpsest` and optionally via `brew install palimpsest` or `pipx install palimpsest` without requiring the user to clone the repo
  3. The install command works on a fresh machine with only Python 3.10+ available (no other prerequisites)
**Plans**: TBD

### Phase 3: Editor Detection
**Goal**: The install process automatically detects which AI editor(s) are present and installs the correct configuration format for each
**Depends on**: Phase 2 (install command must exist before detection can be wired into it)
**Requirements**: DETECT-01, DETECT-02
**Success Criteria** (what must be TRUE):
  1. When a user runs the install command in a project that uses Cursor, the correct `.cursorrules` and skills files are generated automatically
  2. When a user runs the install command in a project that uses Claude Code, the correct `CLAUDE.md` and `AGENTS.md` are generated automatically
  3. When a user runs the install command in a project with multiple AI editors, all detected editors get their correct config files
  4. When no supported editor is detected, the user is prompted to choose which editor config(s) to install
  5. All six target editors are supported: Claude Code, Cursor, Cline, Codex, Goose, Kilo
**Plans**: TBD

### Phase 4: Guided Setup
**Goal**: After install, an interactive wizard walks the user through configuring their program context so the AI-TPM has real project information to work with
**Depends on**: Phase 2 (install creates the scaffolding that setup populates)
**Requirements**: SETUP-01
**Success Criteria** (what must be TRUE):
  1. After running `palimpsest init`, the user is guided through entering program name, key stakeholders, timeline, and communication channels
  2. The wizard populates PROGRAM_OVERVIEW.md, DASHBOARD.md, and Memory Bank files with the user's actual program context (not just placeholders)
  3. The user can skip the wizard (non-interactive mode) and fill in details later
**Plans**: TBD

### Phase 5: Versioning and Updates
**Goal**: Users can update their palimpsest installation to get new templates and methodology without losing their customizations
**Depends on**: Phase 1 (package structure), Phase 2 (CLI exists)
**Requirements**: LIFE-01, LIFE-02, LIFE-03
**Success Criteria** (what must be TRUE):
  1. The package uses semantic versioning and users can check their installed version via `palimpsest --version`
  2. Running `palimpsest update` pulls new templates, docs, and configs while preserving files the user has modified (three-way merge or patch-based)
  3. After an update, the user can see what changed via an auto-generated changelog (either displayed in terminal or written to a file)
  4. The update command warns before overwriting any user-modified file and offers a diff preview
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Package Foundation | 1/1 | Complete   | 2026-03-17 |
| 2. CLI and Install | 0/? | Not started | - |
| 3. Editor Detection | 0/? | Not started | - |
| 4. Guided Setup | 0/? | Not started | - |
| 5. Versioning and Updates | 0/? | Not started | - |

---
*Last updated: 2026-03-18 after Phase 1 planning*
