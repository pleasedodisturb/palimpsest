---
phase: 01-package-foundation
plan: 01
subsystem: infra
tags: [setuptools, package-data, importlib-resources, pyproject-toml]

# Dependency graph
requires: []
provides:
  - "palimpsest/ package directory with all content as package data"
  - "importlib.resources helpers (get_package_files, read_template, read_doc)"
  - "Zero-dep base install with [scripts] extras for heavy deps"
  - "pac entry point at palimpsest.scripts.core.preflight_check:main"
affects: [02-cli-core, 03-editor-detection, 04-wizard-setup, 05-polish]

# Tech tracking
tech-stack:
  added: [importlib.resources, setuptools-package-data]
  patterns: [content-as-package-data, extras-based-dependency-splitting]

key-files:
  created:
    - palimpsest/__init__.py
    - palimpsest/data/__init__.py
    - palimpsest/scripts/tests/test_package_data.py
  modified:
    - pyproject.toml
    - .github/workflows/test.yml

key-decisions:
  - "Zero base dependencies -- content-only install has no deps, heavy Google API deps in [scripts] extras"
  - "All content dirs become Python packages via __init__.py for setuptools discovery"
  - "Package data accessed via importlib.resources.files() -- stdlib, no external deps needed"

patterns-established:
  - "Content-as-package-data: all .md, .template, .mdc, .json, .gitignore files included via setuptools globs"
  - "Extras splitting: base (content), [scripts] (Google API), [pdf] (PyPDF2), [dev] (pytest), [all] (scripts+pdf)"
  - "Package data helpers: palimpsest.data module with get_package_files(), read_template(), read_doc()"

requirements-completed: [PKG-01, PKG-02]

# Metrics
duration: 4min
completed: 2026-03-18
---

# Phase 1 Plan 1: Package Restructure Summary

**Repo restructured into palimpsest/ package with 8 content dirs as package data, zero-dep base install, and importlib.resources helpers**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-17T23:52:59Z
- **Completed:** 2026-03-17T23:57:00Z
- **Tasks:** 3
- **Files modified:** 136

## Accomplishments
- Moved all 9 directories (docs, templates, agents, playbooks, case-study, showcase, project-template, example, scripts) into palimpsest/ with git mv preserving blame history
- Updated pyproject.toml: palimpsest* package discovery, package-data globs, zero base deps, [scripts] extras, correct pac entry point
- Created 15 integration tests validating all content directories accessible via importlib.resources
- All 184 tests pass (169 existing + 15 new) with zero modifications to existing test logic

## Task Commits

Each task was committed atomically:

1. **Task 1: Create package directory structure and move all content** - `83eeb1d` (feat)
2. **Task 2: Update pyproject.toml and CI config for new structure** - `ba00f7d` (chore)
3. **Task 3: Create package data integration tests and verify all existing tests pass** - `0519805` (test)

## Files Created/Modified
- `palimpsest/__init__.py` - Package root with __version__
- `palimpsest/data/__init__.py` - importlib.resources helpers (get_package_files, read_template, read_doc)
- `palimpsest/scripts/tests/test_package_data.py` - 15 integration tests for PKG-01
- `pyproject.toml` - Package discovery, package-data, zero deps, extras, entry point, test paths
- `.github/workflows/test.yml` - Updated install and test commands for new paths
- 22 `__init__.py` files across all content subdirectories

## Decisions Made
- Zero base dependencies: content-only install needs nothing, Google API deps moved to [scripts] extras
- All content subdirectories get __init__.py for setuptools package discovery
- Package data accessed via importlib.resources.files() (stdlib, no external deps)
- Recreated .venv (old one pointed to different project)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Recreated broken .venv**
- **Found during:** Task 3 (test execution)
- **Issue:** Existing .venv had broken interpreter pointing to /Users/pleasedodisturb/Projects/carcadence/
- **Fix:** Removed and recreated .venv with python3 -m venv .venv
- **Files modified:** .venv/ (gitignored, not committed)
- **Verification:** pip install and pytest both work correctly
- **Committed in:** N/A (gitignored)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to run tests. No scope creep.

## Issues Encountered
None beyond the venv fix documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Package structure complete, ready for CLI development (Phase 2)
- All content accessible as package data via importlib.resources
- Entry point resolves correctly for pac CLI
- Test suite fully green

---
*Phase: 01-package-foundation*
*Completed: 2026-03-18*
