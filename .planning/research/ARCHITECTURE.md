# Architecture Patterns

**Domain:** Python CLI packaging and multi-editor AI tool distribution
**Researched:** 2026-03-17
**Overall confidence:** MEDIUM (training data only; web search unavailable for verification)

## Recommended Architecture

The packaging layer wraps the existing four-layer architecture (Content, Agent, Automation, Scaffolding) in a **CLI shell** that handles installation, editor detection, content distribution, and versioned updates. The existing codebase is treated as a **content payload** -- the packaging layer does not restructure it, it ships it.

```
+------------------------------------------------------------------+
|                        palimpsest CLI                             |
|  (pac init / pac update / pac status)                            |
+------------------------------------------------------------------+
|                                                                  |
|  +------------------+  +------------------+  +-----------------+ |
|  |  Editor Detector |  |  Content Copier  |  |  Update Engine  | |
|  |  (detect + adapt)|  |  (install files) |  |  (diff + merge) | |
|  +--------+---------+  +--------+---------+  +--------+--------+ |
|           |                      |                     |          |
|  +--------v---------+  +--------v---------+  +--------v--------+ |
|  |  Editor Adapters |  |  Content Bundles |  |  Manifest Store | |
|  |  - claude-code   |  |  - methodology   |  |  (.palimpsest/  | |
|  |  - cursor        |  |  - templates     |  |   manifest.json)| |
|  |  - cline         |  |  - playbooks     |  |                 | |
|  |  - codex         |  |  - memory-bank   |  |                 | |
|  |  - goose         |  |  - project-skel  |  |                 | |
|  |  - kilo          |  |  - case-study    |  |                 | |
|  +------------------+  +------------------+  +-----------------+ |
|                                                                  |
|  +--------------------------------------------------------------+|
|  |  Existing Automation Layer (scripts/)                        ||
|  |  Optional extra -- installed only when user opts in          ||
|  +--------------------------------------------------------------+|
+------------------------------------------------------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | Build Phase |
|-----------|---------------|-------------------|-------------|
| **CLI Entry Point** (`pac`) | Parse subcommands, dispatch to handlers | All components | Phase 1 |
| **Editor Detector** | Detect which AI editors are configured in the target project | Editor Adapters, CLI | Phase 1 |
| **Editor Adapters** (one per editor) | Transform generic agent config templates into editor-specific format | Content Copier (reads templates), Editor Detector (receives target list) | Phase 2 |
| **Content Copier** | Copy content bundles from package data into target project directory | Manifest Store (records what was placed), Content Bundles (reads source) | Phase 1 |
| **Content Bundles** | Package data containing all shipped content (methodology, templates, etc.) | Read-only, accessed by Content Copier | Phase 1 |
| **Manifest Store** | Track installed files, versions, checksums for update diffing | Content Copier (writes), Update Engine (reads) | Phase 1 |
| **Update Engine** | Compare installed manifest to new version, apply changes while preserving user edits | Manifest Store (reads old state), Content Bundles (reads new state), filesystem (reads user state) | Phase 3 |
| **Guided Setup** | Interactive prompts after init to configure program context | CLI (invoked after init), Content Copier (templates with placeholders) | Phase 2 |
| **Automation Scripts** | Existing Python automation toolkit (sync, publish, etc.) | Independent; installed as optional `[automation]` extra | Phase 4 |

## Data Flow

### Install Flow (`pac init`)

```
User runs: pac init my-program

1. CLI parses args
   |
2. Editor Detector scans target directory and environment:
   - .cursorrules / .cursor/ exists?  --> Cursor detected
   - CLAUDE.md or .claude/ exists?    --> Claude Code detected
   - .clinerules* exists?             --> Cline detected
   - .codex/ or codex config exists?  --> Codex detected
   - .goose/ exists?                  --> Goose detected
   - kilo config exists?              --> Kilo detected
   - None detected?                   --> Prompt user to select
   |
3. Content Copier writes project skeleton:
   - docs/PROGRAM_OVERVIEW.md, DASHBOARD.md, BACKLOG.md
   - docs/context/ structure with .gitignore privacy rules
   - .gitignore (merged with existing if present)
   |
4. Editor Adapters write editor-specific configs:
   - For each detected editor, transform agent template --> editor format
   - Claude Code: CLAUDE.md + AGENTS.md
   - Cursor: .cursorrules + .cursor/skills/ + .cursor/memory/
   - Cline: .clinerules-{mode} files
   - Memory Bank files (shared protocol, editor-specific paths)
   |
5. Manifest Store writes .palimpsest/manifest.json:
   {
     "version": "1.0.0",
     "installed_at": "2026-03-17T...",
     "files": {
       "docs/PROGRAM_OVERVIEW.md": {"checksum": "abc123", "type": "template"},
       "CLAUDE.md": {"checksum": "def456", "type": "agent-config", "editor": "claude-code"}
     },
     "editors": ["claude-code", "cursor"]
   }
   |
6. Guided Setup (optional, --no-interactive to skip):
   - Prompts: program name, key stakeholders, timeline
   - Fills placeholders in PROGRAM_OVERVIEW.md and DASHBOARD.md
   |
7. Git init + initial commit (optional, --no-git to skip)
```

### Update Flow (`pac update`)

```
User runs: pac update

1. CLI reads .palimpsest/manifest.json
   - No manifest? Error: "Not a palimpsest project. Run pac init."
   |
2. Update Engine compares versions:
   - Current installed version (from manifest)
   - Available version (from installed pac package)
   |
3. For each file in new version's content bundle:
   |
   a. File exists in manifest AND on disk:
      - Compute current disk checksum
      - Compare to manifest checksum (what we originally installed)
      - If checksums match: user hasn't modified --> overwrite with new version
      - If checksums differ: user has customized --> THREE options:
        i.  File is "template" type: skip, warn user (their changes preserved)
        ii. File is "methodology" type: overwrite, save user version as .user-backup
        iii. File is "agent-config" type: regenerate from template (configs are derived)
      |
   b. File exists in new version but NOT in manifest (new file):
      - Copy to target, add to manifest
      |
   c. File exists in manifest but NOT in new version (removed upstream):
      - Leave in place, mark as "orphaned" in manifest
   |
4. Update manifest with new version, new checksums
   |
5. Print summary: X files updated, Y skipped (user-modified), Z new files added
```

### Status Flow (`pac status`)

```
User runs: pac status

1. Read .palimpsest/manifest.json
2. For each tracked file:
   - Exists on disk? Checksum matches manifest?
   - Classify: "pristine" / "modified" / "deleted"
3. Check installed pac version vs PyPI/GitHub latest
4. Report: editors detected, files tracked, modifications, update available
```

## Package Structure (pyproject.toml changes)

The key architectural decision is **how content ships inside the Python package**. Use `importlib.resources` (Python 3.9+) to access package data at runtime.

### Recommended source layout

```
palimpsest/                     # NEW: proper Python package (replaces scripts/ as top-level)
  __init__.py                   # version, metadata
  cli/
    __init__.py
    main.py                     # Click app with subcommands
    init_cmd.py                 # pac init implementation
    update_cmd.py               # pac update implementation
    status_cmd.py               # pac status implementation
  detect/
    __init__.py
    detector.py                 # Editor detection logic
    adapters/
      __init__.py
      base.py                   # Abstract adapter interface
      claude_code.py
      cursor.py
      cline.py
      codex.py
      goose.py
      kilo.py
  content/
    __init__.py
    copier.py                   # File copying with placeholder substitution
    manifest.py                 # Manifest read/write/diff
    updater.py                  # Update engine (checksum comparison + merge strategy)
  setup_wizard/
    __init__.py
    prompts.py                  # Interactive guided setup
  automation/                   # Existing scripts, reorganized under palimpsest namespace
    __init__.py
    core/                       # Moved from scripts/core/
    sync/                       # Moved from scripts/sync/
    content/                    # Moved from scripts/content/ (renamed to avoid collision)
    publishing/                 # Moved from scripts/publishing/
  data/                         # Package data (non-Python content shipped in wheel)
    methodology/                # Copied from docs/
    templates/                  # Copied from templates/
    playbooks/                  # Copied from playbooks/
    agents/                     # Copied from agents/
    project-skeleton/           # Copied from project-template/
    case-study/                 # Copied from case-study/
    showcase/                   # Copied from showcase/
    memory-bank/                # Copied from agents/memory-bank/
```

### Why this layout

1. **`palimpsest/` as top-level package** instead of `scripts/`. The current `scripts` namespace is generic and will collide with other packages. Renaming to `palimpsest` gives a proper namespace. The `scripts/` directory remains in the repo for development but `pyproject.toml` maps `palimpsest` as the installed package.

2. **`data/` as package data, not a Python package**. The markdown files, templates, and agent configs ship inside the wheel via `[tool.setuptools.package-data]`. At runtime, `importlib.resources.files("palimpsest.data")` provides the path. This means `pip install palimpsest` includes everything -- no separate download step.

3. **Editor adapters as a plugin-like pattern**. Each adapter implements a common interface (`detect() -> bool`, `install(target_dir, content_dir)`, `config_paths() -> list[Path]`). Adding a new editor means adding one file. No central switch statement.

4. **Automation as optional extra**. The heavy Google/Atlassian/Slack dependencies stay behind `pip install palimpsest[automation]`. The core CLI (init/update/status) has zero external dependencies beyond Click.

## Patterns to Follow

### Pattern 1: Adapter Interface for Editor Support

**What:** Each AI editor gets an adapter class implementing a common protocol.
**When:** Any time editor-specific behavior is needed (detection, config installation, config path resolution).

```python
from abc import ABC, abstractmethod
from pathlib import Path

class EditorAdapter(ABC):
    """Base class for AI editor integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable editor name."""
        ...

    @abstractmethod
    def detect(self, project_dir: Path) -> bool:
        """Return True if this editor is configured in the project."""
        ...

    @abstractmethod
    def install(self, project_dir: Path, content_dir: Path, context: dict) -> list[Path]:
        """Install editor-specific configs. Return list of created files."""
        ...

    @abstractmethod
    def config_paths(self, project_dir: Path) -> list[Path]:
        """Return paths where this editor expects config files."""
        ...
```

**Why:** Six editors now, likely more coming. Plugin pattern avoids a growing if/elif chain and makes each editor independently testable.

### Pattern 2: Manifest-Tracked File Installation

**What:** Every file the CLI writes is recorded in `.palimpsest/manifest.json` with checksum, type, source version.
**When:** During `init` and `update`.

```python
# manifest.json schema
{
    "palimpsest_version": "1.0.0",
    "installed_at": "2026-03-17T10:30:00Z",
    "updated_at": "2026-03-17T10:30:00Z",
    "editors": ["claude-code", "cursor"],
    "files": {
        "relative/path/to/file.md": {
            "sha256": "abc123...",
            "type": "template|methodology|agent-config|skeleton",
            "source": "data/templates/prd.md",
            "installed_version": "1.0.0"
        }
    }
}
```

**Why:** Without a manifest, the update command cannot distinguish "user deleted this intentionally" from "this file was never installed." GSD proves this pattern works.

### Pattern 3: Content Type Classification

**What:** Each shipped file has a type that determines update behavior.
**When:** During `pac update`, the type drives merge strategy.

| Type | Update Behavior | Rationale |
|------|----------------|-----------|
| `skeleton` | Skip if exists (even if unmodified) | Project structure files like PROGRAM_OVERVIEW.md are always user-owned after init |
| `template` | Skip if modified, overwrite if pristine | Templates are references; user modifications are intentional |
| `methodology` | Always overwrite, backup if modified | Methodology docs are the product; users should get latest |
| `agent-config` | Regenerate from template | These are derived from templates + detected editors; always rebuild |
| `memory-bank` | Skip if exists | Memory state is always user-owned |

**Why:** A single update strategy for all file types would either destroy user work (always overwrite) or prevent users from getting improvements (never overwrite). Classification lets each type do the right thing.

### Pattern 4: Minimal Core Dependencies

**What:** The `pac` CLI (init/update/status) depends only on Click + standard library. Automation extras pull in the heavy dependencies.

```toml
[project]
dependencies = [
    "click>=8.1",
]

[project.optional-dependencies]
automation = [
    "google-api-python-client>=2.100.0",
    "google-auth-httplib2>=0.1.1",
    "google-auth-oauthlib>=1.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.4.0",
]
```

**Why:** Most users will use `pac init` and never touch the automation scripts. Requiring Google API libraries for project scaffolding is unnecessary friction. Click is 80KB and has no transitive dependencies.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Generating Files with String Concatenation

**What:** Building file content by concatenating strings or f-strings (as current `setup.sh` does with heredocs).
**Why bad:** Impossible to test, hard to maintain, escaping bugs (already noted in CONCERNS.md with the heredoc quoting issue).
**Instead:** Ship actual template files in `data/` with Jinja2-style placeholders (or simple `{variable}` substitution). The Content Copier reads templates and fills values.

### Anti-Pattern 2: Monolithic init Command

**What:** A single function that detects editors, copies files, writes configs, runs guided setup, and inits git.
**Why bad:** Untestable, hard to extend, impossible to run partial operations.
**Instead:** Each step is a separate function/class. The CLI composes them. Each is independently testable. Users can `pac init --skip-git --skip-setup` to control what runs.

### Anti-Pattern 3: Detecting Editors by Binary Presence

**What:** Checking if `cursor` or `claude` is on `$PATH` to determine which editors to configure.
**Why bad:** Users may have editors installed but not use them for this project. Multiple editors may be present. Binary names differ across platforms.
**Instead:** Detect by **project-level config files** (`.cursorrules`, `CLAUDE.md`, `.clinerules*`). If none found, prompt the user to select. Also check well-known directories (`.cursor/`, `.claude/`).

### Anti-Pattern 4: Storing Manifest Outside Project

**What:** Tracking installed state in `~/.palimpsest/` or similar global location.
**Why bad:** Breaks when projects move, doesn't survive `git clone`, not visible in `git status`.
**Instead:** `.palimpsest/manifest.json` lives in the project root. The `.palimpsest/` directory can be gitignored or committed (user's choice). Recommend committing it so collaborators get update tracking.

## Key Architecture Decisions

### Decision 1: Click over Typer for CLI

**Use Click** (not Typer). Click is mature, well-documented, has zero dependencies beyond standard library, and is the de facto standard for Python CLIs. Typer adds a runtime dependency on Click anyway plus type annotation magic that obscures the command structure. For a CLI with three subcommands, Click's explicit decorator pattern is clearer.

**Confidence:** HIGH (well-established ecosystem knowledge)

### Decision 2: importlib.resources over pkg_resources

**Use `importlib.resources`** (standard library since Python 3.9, backport available). Do not use `pkg_resources` (deprecated, slow) or `__file__`-relative paths (breaks in zip-imported packages). The `files()` API with `as_file()` context manager handles both installed wheels and editable installs.

```python
from importlib.resources import files

def get_content_path(bundle: str) -> Path:
    """Get path to a content bundle within package data."""
    return files("palimpsest.data").joinpath(bundle)
```

**Confidence:** HIGH (standard library, well-documented behavior)

### Decision 3: SHA-256 Checksums for Manifest

**Use SHA-256** for file checksums in the manifest. Fast enough for the number of files involved (dozens, not thousands), avoids the MD5 security scanner noise already flagged in CONCERNS.md, and is the standard choice.

**Confidence:** HIGH

### Decision 4: No Jinja2 for Templates

**Use `str.format_map()` or simple string replacement** for template placeholders, not Jinja2. The templates have at most 5-10 placeholders (program name, date, stakeholder names). Adding Jinja2 as a dependency for this is overkill. If templates grow complex enough to need conditionals or loops, revisit.

**Confidence:** MEDIUM (could be wrong if templates grow complex; revisit in Phase 2)

### Decision 5: Rename Package Namespace from `scripts` to `palimpsest`

**Rename the Python package from `scripts` to `palimpsest`**. The `scripts` namespace is generic, unpublishable to PyPI, and confusing (`from scripts.core import ...` reads like you are importing something generic). This is a breaking change for existing dev installs but there are no known external consumers.

Migration path: Update `pyproject.toml`, move/rename the package directory, update all internal imports, update CI, update CLAUDE.md references.

**Confidence:** HIGH (this is clearly needed for a publishable package)

## Build Order (Dependencies Between Components)

The components have clear dependency ordering that maps to implementation phases:

```
Phase 1: Foundation
  1a. Package restructure (scripts/ -> palimpsest/, pyproject.toml)
  1b. CLI skeleton with Click (pac command with empty subcommands)
  1c. Content bundling (data/ directory, package-data config)
  1d. Manifest schema + read/write

Phase 2: Core Commands
  2a. Editor Detector (needs: nothing)
  2b. Editor Adapters (needs: 2a for interface contract)
  2c. Content Copier (needs: 1c for content paths, 1d for manifest)
  2d. pac init command (needs: 2a, 2b, 2c)
  2e. Guided Setup wizard (needs: 2d to run after init)

Phase 3: Update System
  3a. Update Engine / checksum diff (needs: 1d for manifest, 1c for new content)
  3b. pac update command (needs: 3a, content type classification)
  3c. pac status command (needs: 1d for manifest reading)

Phase 4: Distribution + Automation
  4a. Automation scripts under palimpsest namespace (needs: 1a)
  4b. PyPI publishing pipeline
  4c. Homebrew formula (needs: 4b for PyPI release)
  4d. Binary distribution via pipx / shiv (needs: 4b)
```

**Critical path:** 1a -> 1b -> 1c -> 1d -> 2c -> 2d (init command working end-to-end).

**Parallelizable work:**
- 2a (Editor Detector) and 1c/1d (Content/Manifest) are independent
- 2e (Guided Setup) can be developed independently and plugged in
- 4a (Automation migration) is entirely independent of 2.x and 3.x

## Scalability Considerations

| Concern | Now (6 editors) | At 15 editors | At 50+ templates |
|---------|-----------------|---------------|------------------|
| Editor detection | Linear scan, sub-millisecond | Still fine, linear scan of 15 checks | N/A |
| Package size | ~500KB of markdown + templates | Same | ~2MB, still fine for pip |
| Update diffing | O(n) where n = installed files, ~50 files | Same | ~200 files, still sub-second |
| Template substitution | Simple string replace | Same | May need Jinja2 if templates get conditionals |

The architecture is designed for **dozens of editors and hundreds of content files**. It would need rethinking only if palimpsest became a plugin marketplace (out of scope).

## Sources

- Existing codebase analysis (`.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `CONCERNS.md`)
- `pyproject.toml` and `setup.sh` in current repo
- Python packaging standards: PEP 621 (pyproject.toml metadata), PEP 660 (editable installs), importlib.resources documentation
- Click library documentation (training data, not live-verified -- MEDIUM confidence)
- GSD patterns described in `.planning/PROJECT.md` (prior art section)
