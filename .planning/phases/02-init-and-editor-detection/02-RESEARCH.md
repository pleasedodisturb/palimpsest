# Phase 2: Init & Editor Detection - Research

**Researched:** 2026-03-20
**Domain:** CLI scaffolding (interactive prompts, file generation), editor config detection, file manifests with checksums
**Confidence:** HIGH

## Summary

Phase 2 transforms `pal` from a CLI skeleton into a functional scaffolding tool. The core work is: (1) implement `pal init` as an interactive guided setup command using Typer prompts + Rich panels, (2) auto-detect which AI editors (Cursor, Claude Code, Cline) are present by scanning for their dotfiles/directories, (3) generate editor-specific config files from a canonical `agent.md`, (4) copy all bundled content into the user's project with correct directory structure, (5) track everything in a `.palimpsest/manifest.json` with SHA-256 checksums for idempotent re-runs, and (6) implement a privacy model where users choose gitignore profiles.

The existing Phase 1 codebase provides a solid foundation: Typer app with global flags, Rich console singleton, `PalError` error handling, and `importlib.resources`-based content access. Phase 2 adds the first write-heavy command. The `setup.sh` script serves as a prototype with proven scaffolding logic that must be replicated and extended in Python.

**Primary recommendation:** Use Typer's built-in `typer.prompt()`, `typer.confirm()`, and Rich's `Prompt.ask(choices=[...])` for the interactive flow. Use `shutil.copytree` with custom `copy_function` for content deployment. Use `hashlib.sha256` with chunked reads (not `file_digest()` which is 3.11+) for manifest checksums. Detect editors by checking for specific dotfiles/directories -- no process scanning needed.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Guided interactive setup (like `npm init` interactive mode)
- Ask program name, key stakeholders, timeline, integrations during setup
- Works in BOTH new directories and existing repos
- With name arg or in empty dir: creates new project directory; in existing repo: adds palimpsest files alongside existing content
- Git init: only if not already in a git repo
- Conflict handling in existing repos: prompt per conflict (skip, overwrite, or backup)
- ALL content gets copied into the user's project (not kept in package)
- Content locations: `docs/` for program docs, `docs/palimpsest/` for methodology, `docs/palimpsest/playbooks/`, `docs/palimpsest/templates/`, `docs/palimpsest/showcase/`, `docs/palimpsest/case-study/` (ANONYMIZED)
- Memory Bank (7 files) in `.palimpsest/memory-bank/` (editor-neutral location)
- `agent.md` in project root is the CANONICAL source of truth for all editor configs
- Always created during init -- single source
- Editor-specific files (CLAUDE.md, .cursorrules, .clinerules-*) are auto-generated FROM agent.md
- Detection flow: scan for dotfiles/configs, show detected, confirm, offer undetected as optional, generate for selected
- Config sync: manual `pal sync-config` command, `pal check` warns if stale
- `--editors cursor,claude-code` flag overrides auto-detection
- `.palimpsest/manifest.json` tracks all installed files with checksums
- Idempotent operations (running init twice is safe)
- Privacy model: inline explanation during init, two types (private/public), presets (Solo/Team/Open), customizable per content type
- VCS handling: user chooses during init (team vs personal)
- `--dry-run` on init and all write operations

### Claude's Discretion
- Temp file handling during scaffold
- agent.md template structure and sections
- How to detect editor presence (which dotfiles/processes to check)
- Exact manifest.json schema

### Deferred Ideas (OUT OF SCOPE)
- `pal update` command with user-patch preservation -- Phase 4
- `pal sync` command for external service sync -- future
- Homebrew formula -- Phase 5
- Runtime detection of which AI editor is actively running -- nice to have, not this phase
- Guided setup wizard (program name, stakeholders, timeline) -- Phase 4 (SETUP-01..03)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INIT-01 | User can run `palimpsest init` to scaffold a project (replaces setup.sh) | Typer subcommand with interactive prompts; content copying via `importlib.resources` + `shutil`; setup.sh logic as reference implementation |
| INIT-02 | Init auto-detects which AI editors are present in the project/system | Filesystem scanning for `.cursor/`, `CLAUDE.md`, `.claude/`, `.clinerules*` dotfiles; no process detection needed |
| INIT-03 | Init installs correct agent config format for each detected editor | Template rendering from `agent.md` canonical source; Cursor: `.cursor/rules/*.mdc`, Claude Code: `CLAUDE.md`, Cline: `.clinerules-*.md` |
| INIT-04 | Init is idempotent -- running twice does not corrupt the project | Manifest-based file tracking with SHA-256 checksums; skip unchanged files, prompt for modified files |
| INIT-05 | User can override detection with `--editors cursor,claude-code` flag | Typer Option with comma-separated string parsing |
| INIT-06 | Init initializes Memory Bank protocol files for detected editors | Copy 7 starter files from bundled content to `.palimpsest/memory-bank/`; editor configs reference this shared location |
| INIT-07 | Init creates file manifest (`.palimpsest/manifest.json`) tracking installed files + checksums | JSON manifest with file paths, SHA-256 hashes, install timestamp, version |
| CLI-06 | Write operations support `--dry-run` to preview changes | Global or per-command `--dry-run` flag; Rich table showing planned operations without executing |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| typer | >=0.24.0 | CLI framework, prompts, subcommands | Already in use from Phase 1; `typer.prompt()`, `typer.confirm()` for interactive flow |
| rich | >=14.0.0 | Terminal formatting, panels, tables, prompts | Already in use; `Prompt.ask(choices=[...])` for selection, `Panel` for privacy explanation, `Table` for dry-run preview |
| hashlib | stdlib | SHA-256 file checksums | Standard library, no external dependency. Use chunked reads for 3.10 compat |
| shutil | stdlib | Directory/file copying | `shutil.copy2` preserves metadata; `shutil.copytree` for recursive copy |
| pathlib | stdlib | Path manipulation | Already used in Phase 1 content module |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json | stdlib | Manifest serialization | Writing/reading `.palimpsest/manifest.json` |
| importlib.resources | stdlib (3.10+) | Access bundled content | Reading template files and content from installed package |
| subprocess | stdlib | Git operations | `git init`, `git rev-parse --git-dir` for repo detection |
| string.Template / str.format | stdlib | Template rendering | Replacing `$PROJECT_ROOT`, `$PROGRAM_NAME` placeholders in agent configs |
| datetime | stdlib | Timestamps | Manifest creation timestamps |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Rich Prompt.ask for choices | questionary / InquirerPy | Adds dependency; Rich is already present and sufficient for single-select + confirm |
| hashlib manual chunking | `hashlib.file_digest()` | `file_digest()` is 3.11+ only; project targets 3.10+ |
| string.Template for configs | Jinja2 | Adds dependency for simple placeholder replacement; Jinja2 warranted only if conditional logic needed in templates |
| shutil.copytree | manual walk + copy | shutil handles edge cases (permissions, symlinks, existing dirs) |

**No new dependencies required.** Phase 2 uses only the existing Typer + Rich stack plus stdlib modules.

## Architecture Patterns

### Recommended Project Structure (additions to Phase 1)
```
palimpsest/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Existing -- add init subcommand registration
│   └── init_cmd.py           # NEW: `pal init` command implementation
├── init/                      # NEW: Init business logic (separated from CLI layer)
│   ├── __init__.py
│   ├── scaffold.py           # File copying, directory creation
│   ├── editors.py            # Editor detection and config generation
│   ├── manifest.py           # Manifest read/write/verify
│   ├── privacy.py            # Privacy profile and .gitignore generation
│   └── agent_md.py           # agent.md template + editor config rendering
├── console.py                # Existing
├── errors.py                 # Existing
└── content/                  # Existing bundled content
```

### Pattern 1: Typer Subcommand with Interactive Flow
**What:** Register `init` as a Typer command with optional arguments that fall back to interactive prompts when not provided.
**When to use:** The main init command entry point.
**Example:**
```python
# palimpsest/cli/init_cmd.py
import typer
from rich.prompt import Prompt, Confirm
from palimpsest.console import console

def init_command(
    name: str = typer.Argument(None, help="Project name (prompted if omitted)"),
    editors: str = typer.Option(None, "--editors", help="Comma-separated editors: cursor,claude-code,cline"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing files"),
) -> None:
    """Initialize a new palimpsest project."""
    # If no name provided, detect context or prompt
    if name is None:
        name = Prompt.ask("[bold]Program name[/bold]", default=Path.cwd().name)

    # Editor detection (unless overridden)
    if editors is None:
        detected = detect_editors(Path.cwd())
        # Show detected, confirm, offer others
    else:
        selected = editors.split(",")

    # Privacy profile selection
    profile = Prompt.ask(
        "Privacy profile",
        choices=["solo", "team", "open"],
        default="team",
    )

    if dry_run:
        show_dry_run_preview(plan)
        return

    execute_scaffold(plan)
```

### Pattern 2: Editor Detection via Filesystem Scanning
**What:** Check for known dotfiles/directories that indicate editor presence.
**When to use:** During init to auto-select which editor configs to generate.
**Example:**
```python
# palimpsest/init/editors.py
from dataclasses import dataclass
from pathlib import Path

EDITOR_SIGNALS = {
    "cursor": {
        "name": "Cursor",
        "signals": [".cursor/", ".cursorrules", ".cursor/rules/"],
        "generates": [".cursor/rules/palimpsest.mdc"],
    },
    "claude-code": {
        "name": "Claude Code",
        "signals": ["CLAUDE.md", ".claude/"],
        "generates": ["CLAUDE.md"],
    },
    "cline": {
        "name": "Cline",
        "signals": [".clinerules", ".clinerules-architect", ".roo/"],
        "generates": [
            ".clinerules-architect",
            ".clinerules-code",
            ".clinerules-debug",
            ".clinerules-test",
            ".clinerules-ask",
        ],
    },
}

def detect_editors(project_dir: Path) -> dict[str, bool]:
    """Detect which AI editors are present by checking for their dotfiles."""
    results = {}
    for editor_id, info in EDITOR_SIGNALS.items():
        found = any(
            (project_dir / signal).exists()
            for signal in info["signals"]
        )
        results[editor_id] = found
    return results
```

### Pattern 3: Manifest-Based Idempotent Operations
**What:** Track every installed file with its SHA-256 hash. On re-run, compare hashes to detect user modifications.
**When to use:** Every file write during scaffold.
**Example:**
```python
# palimpsest/init/manifest.py
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

MANIFEST_PATH = ".palimpsest/manifest.json"

def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 hex digest. Compatible with Python 3.10+."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def create_manifest(files: dict[str, str], version: str) -> dict:
    """Create manifest structure.

    Args:
        files: mapping of relative_path -> sha256_hex
        version: palimpsest version string
    """
    return {
        "version": version,
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "files": {
            path: {
                "checksum": checksum,
                "installed_version": version,
            }
            for path, checksum in files.items()
        },
    }

def check_file_status(manifest: dict, file_path: str, project_dir: Path) -> str:
    """Check status of a file against manifest.

    Returns: 'new', 'unchanged', 'modified', 'missing'
    """
    full_path = project_dir / file_path
    if file_path not in manifest.get("files", {}):
        return "new"
    if not full_path.exists():
        return "missing"
    current = compute_checksum(full_path)
    if current == manifest["files"][file_path]["checksum"]:
        return "unchanged"
    return "modified"
```

### Pattern 4: Dry-Run Preview with Rich Table
**What:** Show a table of planned operations without executing them.
**When to use:** When `--dry-run` is passed.
**Example:**
```python
from rich.table import Table
from palimpsest.console import console

def show_dry_run_preview(plan: list[dict]) -> None:
    """Display what would be created/modified without doing it."""
    table = Table(title="Dry Run Preview", show_lines=True)
    table.add_column("Action", style="bold")
    table.add_column("Path")
    table.add_column("Status")

    for item in plan:
        action_style = {
            "create": "green",
            "overwrite": "yellow",
            "skip": "dim",
        }.get(item["action"], "white")
        table.add_row(
            f"[{action_style}]{item['action']}[/]",
            item["path"],
            item.get("reason", ""),
        )

    console.print(table)
    console.print(f"\n[info]Total: {len(plan)} files would be affected[/info]")
```

### Pattern 5: Conflict Resolution for Existing Repos
**What:** When a file already exists and differs from what we'd install, prompt the user.
**When to use:** During init in an existing repo.
**Example:**
```python
from rich.prompt import Prompt

def resolve_conflict(file_path: str, action: str = "overwrite") -> str:
    """Prompt user for conflict resolution.

    Returns: 'skip', 'overwrite', or 'backup'
    """
    return Prompt.ask(
        f"[warning]File exists:[/warning] {file_path}",
        choices=["skip", "overwrite", "backup"],
        default="skip",
    )
```

### Anti-Patterns to Avoid
- **Coupling CLI prompts with business logic:** The `init_cmd.py` should orchestrate prompts, but `scaffold.py` should accept a configuration dict and know nothing about user interaction. This enables testing and `--dry-run`.
- **Writing files without manifest tracking:** Every file written during init MUST be recorded in the manifest. A missed file means idempotent re-runs can't detect it.
- **Hardcoding editor detection paths:** Use the `EDITOR_SIGNALS` dict pattern so new editors can be added in one place.
- **Using `.cursorrules` for Cursor:** The `.cursorrules` format is deprecated. Use `.cursor/rules/*.mdc` format instead (see Editor Config Formats section below).
- **Detecting editors by process scanning:** Unreliable, platform-dependent, requires elevated permissions on some systems. Dotfile scanning is sufficient and deterministic.

## Editor Config Formats (Current State)

### Cursor (2025-2026)
- **OLD (deprecated):** `.cursorrules` file in project root
- **NEW (current):** `.cursor/rules/*.mdc` files with frontmatter metadata
- `.mdc` files support: `description` (when to apply), `globs` (file patterns), `alwaysApply` (boolean)
- **Recommendation:** Generate `.cursor/rules/palimpsest.mdc` with `alwaysApply: true`
- **Confidence:** HIGH -- verified via official Cursor docs and web search

### Claude Code
- `CLAUDE.md` in project root -- the primary config file
- `.claude/` directory for extended settings
- `AGENTS.md` for multi-agent setups (referenced from CLAUDE.md)
- **Recommendation:** Generate `CLAUDE.md` incorporating agent.md content with Memory Bank protocol
- **Confidence:** HIGH -- verified via official blog and documentation

### Cline
- `.clinerules` in project root (single file) or `.clinerules-{mode}` for modal configs
- Modal configs: architect, code, debug, test, ask
- `.roo/` directory also recognized (Roo is a Cline variant)
- **Recommendation:** Generate `.clinerules-{mode}` files for each modal config
- **Confidence:** HIGH -- verified via GitHub repo and extension docs

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interactive CLI prompts | Custom input() loops | `typer.prompt()`, `Rich.Prompt.ask()`, `typer.confirm()` | Validation, styling, default values handled automatically |
| File copying with metadata | Manual open/read/write | `shutil.copy2` / `shutil.copytree` | Handles permissions, timestamps, encoding, cross-platform |
| Git repo detection | Parse `.git/config` | `subprocess.run(["git", "rev-parse", "--git-dir"])` | Handles worktrees, bare repos, nested repos correctly |
| Checksum computation | Manual bytes manipulation | `hashlib.sha256` with chunked reads | Battle-tested, handles large files, streaming |
| Directory tree display | Custom recursive print | `rich.tree.Tree` | Beautiful output, handles unicode, depth control |
| Template placeholder replacement | Regex substitution | `string.Template.safe_substitute()` | Handles missing keys gracefully, standard pattern |
| Gitignore generation | Hardcoded strings | Template with conditional sections | Maintainable, testable, matches privacy profile choice |

**Key insight:** This phase has many moving parts (interactive prompts, file operations, editor detection, manifest tracking, privacy profiles) but each individual piece is simple. The complexity is in orchestration, not in any single component. Keep the pieces small and testable.

## Common Pitfalls

### Pitfall 1: Template Placeholders Left Unresolved
**What goes wrong:** Generated config files contain `$PROJECT_ROOT` or `[YOUR-PROJECT]` literals instead of actual values.
**Why it happens:** Template rendering step skipped or not all placeholders mapped. The existing templates use `$PROJECT_ROOT` (shell-style) which conflicts with Python's `string.Template` `$` syntax.
**How to avoid:** (a) Audit all `.template` files for placeholder patterns. (b) Use `string.Template.safe_substitute()` which leaves unmatched placeholders intact rather than raising. (c) Add a verification step that scans generated files for remaining `$` or `[YOUR-` patterns.
**Warning signs:** Generated CLAUDE.md contains literal `$PROJECT_ROOT` text.

### Pitfall 2: Encoding Issues in Content Copying
**What goes wrong:** Markdown files with unicode characters (em-dashes, smart quotes, non-ASCII names) get garbled during copy.
**Why it happens:** Opening files in text mode with wrong encoding, or using `shutil.copy2` (which copies bytes, so this is actually safe).
**How to avoid:** Use `shutil.copy2` for file copying (binary-safe). Only open files in text mode when rendering templates, and always specify `encoding="utf-8"`.
**Warning signs:** Case study or methodology docs have garbled characters after init.

### Pitfall 3: Manifest Not Updated on Partial Failure
**What goes wrong:** Init crashes halfway through. Some files are written but manifest doesn't reflect them. Re-running init overwrites user's changes to those files.
**Why it happens:** Manifest written only at the end, not incrementally.
**How to avoid:** Write manifest after each file operation, not at the end. Or: build the complete plan first, execute all writes, then write manifest atomically. The second approach is simpler -- if init crashes, the user re-runs it and the conflict resolution handles duplicates.
**Warning signs:** Running init twice after a crash produces unexpected overwrites.

### Pitfall 4: Existing CLAUDE.md Overwritten Without Warning
**What goes wrong:** User already has a CLAUDE.md for their project. Init overwrites it with the palimpsest template.
**Why it happens:** Init doesn't check for existing files before writing.
**How to avoid:** The conflict resolution pattern (skip/overwrite/backup) MUST apply to all generated files, especially editor configs. For CLAUDE.md specifically, consider appending palimpsest content rather than replacing.
**Warning signs:** User's custom CLAUDE.md disappears after running `pal init`.

### Pitfall 5: Memory Bank Path Inconsistency
**What goes wrong:** Memory Bank files are in `.palimpsest/memory-bank/` but agent config templates reference `.cursor/memory/`.
**Why it happens:** The existing templates use `.cursor/memory/` (Cursor-specific path). The CONTEXT.md decision moves Memory Bank to `.palimpsest/memory-bank/` (editor-neutral).
**How to avoid:** Update ALL template references to use `.palimpsest/memory-bank/` as the canonical path. The agent.md template must use this path, and all generated editor configs must reference it.
**Warning signs:** Agent configs tell the AI to look in `.cursor/memory/` but files are in `.palimpsest/memory-bank/`.

### Pitfall 6: Privacy Profiles Not Actually Enforced
**What goes wrong:** User selects "solo" privacy but `.gitignore` doesn't cover all private paths.
**Why it happens:** Privacy profile generates `.gitignore` entries but doesn't verify coverage.
**How to avoid:** Each privacy profile must have a complete, tested `.gitignore` template. Test that the generated `.gitignore` actually excludes the right paths. Include a `pal check` verification (future) that validates the privacy boundary.
**Warning signs:** Private files accidentally committed to git.

### Pitfall 7: Case Study Not Anonymized
**What goes wrong:** The case study mentions "Wolt" or real employee names.
**Why it happens:** Content is copied directly from `case-study/wolt-crm-migration.md` without transformation.
**How to avoid:** Either (a) pre-anonymize the case study in the bundled content (at build time, before Phase 2), or (b) apply anonymization transforms during init. Option (a) is better -- the shipped package should never contain non-anonymized content.
**Warning signs:** grep for "Wolt" in installed case study returns matches.

## Code Examples

### Complete Init Command Registration
```python
# palimpsest/cli/main.py -- additions
from palimpsest.cli.init_cmd import init_command

# In the app setup:
app.command(name="init")(init_command)
```

### SHA-256 Checksum (Python 3.10 Compatible)
```python
# palimpsest/init/manifest.py
import hashlib
from pathlib import Path

def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file. Python 3.10+ compatible."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()
```

### Manifest JSON Schema
```json
{
  "palimpsest_version": "0.1.0",
  "created_at": "2026-03-20T10:00:00+00:00",
  "updated_at": "2026-03-20T10:00:00+00:00",
  "privacy_profile": "team",
  "editors": ["cursor", "claude-code"],
  "files": {
    "docs/PROGRAM_OVERVIEW.md": {
      "checksum": "sha256:a1b2c3...",
      "category": "program-docs",
      "installed_version": "0.1.0"
    },
    "docs/palimpsest/01-problem-statement.md": {
      "checksum": "sha256:d4e5f6...",
      "category": "methodology",
      "installed_version": "0.1.0"
    },
    ".palimpsest/memory-bank/sessionLog.md": {
      "checksum": "sha256:g7h8i9...",
      "category": "memory-bank",
      "installed_version": "0.1.0"
    },
    "CLAUDE.md": {
      "checksum": "sha256:j0k1l2...",
      "category": "editor-config",
      "installed_version": "0.1.0",
      "editor": "claude-code"
    }
  }
}
```

### Privacy Profile Gitignore Templates
```python
# palimpsest/init/privacy.py
PRIVACY_PROFILES = {
    "solo": {
        "description": "Everything private -- maximally safe for personal use",
        "gitignore_extra": [
            # Gitignore everything in .palimpsest
            ".palimpsest/",
            "docs/context/",
        ],
    },
    "team": {
        "description": "Structured public/private split -- recommended for team projects",
        "gitignore_extra": [
            # Private context
            "docs/context/transcripts/",
            "docs/context/private-notes/",
            "docs/context/slack-digests/",
            # Memory bank stays committed for team continuity
        ],
    },
    "open": {
        "description": "Most things public -- for open programs with minimal private data",
        "gitignore_extra": [
            "docs/context/private-notes/",
        ],
    },
}
```

### Content Deployment from Package
```python
# palimpsest/init/scaffold.py
from importlib.resources import files
from pathlib import Path
import shutil

CONTENT_MAP = {
    # source (in package) -> destination (in user project)
    "docs": "docs/palimpsest",
    "templates": "docs/palimpsest/templates",
    "playbooks": "docs/palimpsest/playbooks",
    "showcase": "docs/palimpsest/showcase",
    "case-study": "docs/palimpsest/case-study",
}

def deploy_content(project_dir: Path, category: str, dest_subdir: str) -> list[tuple[str, str]]:
    """Copy bundled content to project directory.

    Returns list of (relative_path, checksum) tuples.
    """
    source = files("palimpsest.content").joinpath(category)
    dest = project_dir / dest_subdir
    dest.mkdir(parents=True, exist_ok=True)

    installed = []
    for item in source.iterdir():
        if item.name.startswith("__"):  # skip __init__.py, __pycache__
            continue
        if item.is_file():
            dest_file = dest / item.name
            shutil.copy2(str(item), str(dest_file))
            rel_path = str(dest_file.relative_to(project_dir))
            checksum = compute_checksum(dest_file)
            installed.append((rel_path, checksum))

    return installed
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.cursorrules` (single file) | `.cursor/rules/*.mdc` (directory of rules) | Late 2024 / early 2025 | Generate `.mdc` format, not `.cursorrules` |
| `.clinerules` (single file) | `.clinerules-{mode}` (modal configs) | Mid 2024 | Generate per-mode config files |
| `hashlib.file_digest()` | Still new (3.11+) | Python 3.11 | Use manual chunked reads for 3.10 compat |
| `setup.sh` bash scaffolding | Python CLI scaffolding | This phase | Full replacement of `setup.sh` |
| Memory Bank in `.cursor/memory/` | Memory Bank in `.palimpsest/memory-bank/` | This phase (decision) | Editor-neutral location |

**Deprecated/outdated:**
- `.cursorrules` single file: Cursor has moved to `.cursor/rules/*.mdc`. Still works for backward compatibility but will be removed.
- Memory Bank in `.cursor/memory/`: Editor-specific. Moving to `.palimpsest/memory-bank/` per CONTEXT.md decision.

## Open Questions

1. **agent.md template structure**
   - What we know: It's the canonical source for all editor configs. Editor-specific files are generated from it.
   - What's unclear: Exact section structure, what content goes in it vs in editor-specific configs. The existing templates have editor-specific structure that may not map cleanly to a single canonical format.
   - Recommendation: Design agent.md as a superset -- include all sections from all editor templates. Each editor's generator extracts the sections relevant to that editor and formats them in the editor's expected syntax.

2. **Case study anonymization timing**
   - What we know: Must be anonymized before shipping. No "Wolt", no real names, no internal URLs.
   - What's unclear: Should this happen at build time (pre-package) or at init time (during copy)?
   - Recommendation: Pre-anonymize in the bundled content. The package should never contain non-anonymized content. This is a pre-Phase 2 task or early Phase 2 task.

3. **Guided setup scope in Phase 2**
   - What we know: CONTEXT.md says "ask program name, key stakeholders, timeline, integrations during setup" but DEFERRED says "Guided setup wizard -- Phase 4 (SETUP-01..03)".
   - What's unclear: How much interactivity belongs in Phase 2 vs Phase 4.
   - Recommendation: Phase 2 asks for program name (needed for directory creation and template rendering) and privacy profile. Detailed setup (stakeholders, timeline, integrations) is Phase 4's SETUP-01..03.

4. **CLAUDE.md collision with existing projects**
   - What we know: Claude Code uses `CLAUDE.md` as its config file. A user's project may already have one.
   - What's unclear: Should palimpsest append to existing CLAUDE.md, create a separate file, or replace it?
   - Recommendation: If `CLAUDE.md` exists, show its first few lines and offer options: append palimpsest section, replace, or skip. The appended section should be clearly demarcated with comments.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=7.4.0 (already configured from Phase 1) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ scripts/tests/ -v --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INIT-01 | `pal init` creates project scaffold with correct directory structure | integration | `python -m pytest tests/test_init.py::test_scaffold_creates_structure -x` | No -- Wave 0 |
| INIT-01 | Init works in empty directory (new project) | integration | `python -m pytest tests/test_init.py::test_init_new_directory -x` | No -- Wave 0 |
| INIT-01 | Init works in existing repo (adds files alongside) | integration | `python -m pytest tests/test_init.py::test_init_existing_repo -x` | No -- Wave 0 |
| INIT-02 | Editor detection finds Cursor by .cursor/ directory | unit | `python -m pytest tests/test_editors.py::test_detect_cursor -x` | No -- Wave 0 |
| INIT-02 | Editor detection finds Claude Code by CLAUDE.md | unit | `python -m pytest tests/test_editors.py::test_detect_claude_code -x` | No -- Wave 0 |
| INIT-02 | Editor detection finds Cline by .clinerules | unit | `python -m pytest tests/test_editors.py::test_detect_cline -x` | No -- Wave 0 |
| INIT-03 | Cursor config generated as .cursor/rules/palimpsest.mdc | unit | `python -m pytest tests/test_editors.py::test_generate_cursor_config -x` | No -- Wave 0 |
| INIT-03 | Claude Code config generated as CLAUDE.md | unit | `python -m pytest tests/test_editors.py::test_generate_claude_config -x` | No -- Wave 0 |
| INIT-03 | Cline configs generated as .clinerules-{mode} files | unit | `python -m pytest tests/test_editors.py::test_generate_cline_configs -x` | No -- Wave 0 |
| INIT-04 | Running init twice does not duplicate files | integration | `python -m pytest tests/test_init.py::test_idempotent_reinit -x` | No -- Wave 0 |
| INIT-04 | Re-init detects user-modified files and prompts | integration | `python -m pytest tests/test_init.py::test_reinit_conflict_detection -x` | No -- Wave 0 |
| INIT-05 | `--editors cursor,claude-code` overrides detection | unit | `python -m pytest tests/test_init.py::test_editors_override_flag -x` | No -- Wave 0 |
| INIT-06 | Memory Bank 7 files created in .palimpsest/memory-bank/ | integration | `python -m pytest tests/test_init.py::test_memory_bank_created -x` | No -- Wave 0 |
| INIT-07 | Manifest created with correct checksums | unit | `python -m pytest tests/test_manifest.py::test_manifest_creation -x` | No -- Wave 0 |
| INIT-07 | Manifest checksums match actual file content | unit | `python -m pytest tests/test_manifest.py::test_checksum_verification -x` | No -- Wave 0 |
| CLI-06 | `--dry-run` shows preview without writing files | integration | `python -m pytest tests/test_init.py::test_dry_run_no_writes -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ scripts/tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_init.py` -- Init command integration tests (uses tmp_path fixtures for isolated filesystem)
- [ ] `tests/test_editors.py` -- Editor detection and config generation unit tests
- [ ] `tests/test_manifest.py` -- Manifest creation, reading, checksum verification
- [ ] `tests/test_privacy.py` -- Privacy profile selection, .gitignore generation
- [ ] Update `tests/conftest.py` -- Add fixtures for temporary project directories, mock editor dotfiles

**Testing strategy notes:**
- Integration tests for init use `tmp_path` pytest fixture to create isolated project directories
- Editor detection tests create fake dotfiles in tmp_path to simulate different editor environments
- Use `typer.testing.CliRunner` for CLI-level tests (already established in Phase 1)
- `--dry-run` tests verify no files are written by checking `tmp_path` is empty after invocation

## Sources

### Primary (HIGH confidence)
- Phase 1 implementation: `palimpsest/cli/main.py`, `palimpsest/console.py`, `palimpsest/errors.py`, `palimpsest/content/__init__.py` -- direct code review
- Existing `setup.sh` -- reference implementation for scaffolding logic
- Existing agent templates in `agents/` -- template content and placeholder patterns
- Python stdlib docs (hashlib, shutil, pathlib) -- standard library APIs
- Typer docs (https://typer.tiangolo.com/tutorial/prompt/) -- prompting patterns
- Rich docs (https://rich.readthedocs.io/en/latest/prompt.html) -- Prompt.ask, Confirm, choices

### Secondary (MEDIUM confidence)
- Cursor rules format: verified `.mdc` format via official docs redirect + web search (`.cursorrules` deprecated)
- Cline `.clinerules` format: verified via GitHub repo and VS Code extension docs
- Claude Code `CLAUDE.md` and `.claude/` structure: verified via official blog (https://claude.com/blog/using-claude-md-files)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, all stdlib + existing Typer/Rich
- Architecture: HIGH -- patterns are straightforward file operations + CLI prompts
- Editor detection: HIGH -- dotfile patterns verified against current editor documentation
- Pitfalls: HIGH -- based on direct analysis of existing templates and CONTEXT.md decisions
- Manifest schema: MEDIUM -- schema is at Claude's discretion, recommended pattern is sound but untested

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (stable domain, 30 days; editor config formats may evolve faster)
