# Phase 1: Package Foundation - Research

**Researched:** 2026-03-19
**Domain:** Python packaging (setuptools), CLI framework (Typer + Rich), package data bundling
**Confidence:** HIGH

## Summary

Phase 1 transforms palimpsest from a loose collection of scripts into an installable Python package with a polished CLI skeleton. The core work is: (1) restructure into a proper `src/palimpsest/` package layout, (2) build a Typer-based CLI with Rich output, (3) bundle all methodology content as package data, and (4) register `pal`, `palimpsest`, and `pac` as entry points.

The technology choices (Typer 0.24.x, Rich 14.x, setuptools with pyproject.toml) are well-established, current, and well-documented. The main complexity is the package restructuring -- moving from the current `scripts*` layout to a proper `palimpsest/` package that includes both code and content data. The existing `scripts/` code is NOT being rewritten in this phase; it should be wrapped or left accessible, not broken.

**CRITICAL BLOCKER:** The `palimpsest` name is already taken on PyPI (v0.0.2 by Robert Trigg, last updated Oct 2023, appears abandoned with no description). This must be resolved before Phase 5 (PyPI publishing). Options: (a) contact the owner to request transfer, (b) use `palimpsest-tpm` or similar on PyPI, (c) file a PEP 541 name reclaim request. For Phase 1 (local development), this does not block work -- the package name in pyproject.toml can stay `palimpsest` for now.

**Primary recommendation:** Use Typer 0.24+ with Rich 14+ for the CLI. Structure as a `palimpsest/cli/` subpackage with one file per command group. Bundle content via `[tool.setuptools.package-data]` and access at runtime with `importlib.resources`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Primary command: `pal` (short, memorable)
- Also register `palimpsest` and keep `pac` as aliases in pyproject.toml
- CLI framework: Typer (modern, type-hint based on Click)
- Terminal UX: Rich library for beautiful prompts, panels, progress bars, styled output
- Expand `[tool.setuptools.packages.find]` to include CLI module
- Add `package-data` for all content (templates, docs, agents, playbooks, methodology, anechoic)
- All methodology docs, templates, configs, playbooks ship inside the wheel
- Anechoic async methodology bundled as content under its own brand (version-pinned from ~/Projects/anechoic)
- Global CLI flags: `--verbose` / `-v` and `--quiet` / `-q`
- Error handling: Rich panels with fix suggestions (Rust compiler error style)
- Verbose mode shows full traceback and context
- User errors produce meaningful messages, not Python tracebacks

### Claude's Discretion
- Exact Rich theme/color palette
- Exact Typer command group organization
- How to structure the CLI module (single file vs package)
- How to vendor/bundle anechoic content during build

### Deferred Ideas (OUT OF SCOPE)
- `init`, `check`, `docs` commands -- Phase 2 and 3
- Editor detection and config installation -- Phase 2
- `pal update` with user-patch preservation -- Phase 4
- Homebrew formula -- Phase 5
- `--dry-run` flag -- Phase 2 (when write operations exist)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CLI-01 | User can install palimpsest with a single command (`pip install` / `pipx install` / `uv tool install`) | Package restructuring with pyproject.toml entry points; setuptools package-data for content bundling |
| CLI-02 | Every command and subcommand responds to `--help` with usage info | Typer generates help automatically from function signatures and docstrings |
| CLI-03 | User can check installed version with `palimpsest --version` | `importlib.metadata.version()` + Typer callback pattern |
| CLI-04 | CLI displays colored terminal output with rich formatting | Rich library integration; Typer uses Rich by default for error display |
| CLI-05 | CLI shows meaningful error messages (no raw tracebacks for user errors) | Custom exception handler wrapping Typer's `pretty_exceptions_enable`; Rich panels for structured error display |
| DIST-02 | All methodology docs, templates, configs, playbooks, and anechoic content ship as package data | `[tool.setuptools.package-data]` with glob patterns; `importlib.resources` for runtime access |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| typer | >=0.24.0 | CLI framework | Type-hint based, built on Click, auto-generates help, native Rich integration. Current: 0.24.1 |
| rich | >=14.0.0 | Terminal formatting | Panels, tables, styled text, progress bars, tracebacks. Current: 14.3.3. Typer depends on it already |
| setuptools | >=68.0 | Build backend | Already in use; supports package-data, entry points via pyproject.toml |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| importlib.metadata | stdlib (3.10+) | Version resolution | Reading package version at runtime for `--version` |
| importlib.resources | stdlib (3.10+) | Package data access | Reading bundled content files (docs, templates, etc.) at runtime |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typer | Click | Typer IS Click underneath; Typer adds type hints and less boilerplate |
| Typer | argparse | stdlib but vastly more boilerplate, no Rich integration, no auto-help |
| Rich | Colorama | Colorama is colors only; Rich provides panels, tables, markdown rendering |

**Installation (add to pyproject.toml dependencies):**
```toml
dependencies = [
    "typer>=0.24.0",
    "rich>=14.0.0",
    # ... existing deps can be moved to optional if not needed for CLI
]
```

**Version verification (2026-03-19):**
- typer: 0.24.1 (latest on PyPI)
- rich: 14.3.3 (latest on PyPI)

## Architecture Patterns

### Recommended Project Structure
```
palimpsest/                      # Root package
├── __init__.py                  # Package version, metadata
├── cli/                         # CLI subpackage
│   ├── __init__.py              # Typer app creation, global flags
│   ├── main.py                  # Entry point function, app callback
│   └── version.py               # --version callback
├── errors.py                    # Custom exception classes + Rich error panels
├── console.py                   # Rich Console singleton, theme, output helpers
└── content/                     # Bundled content as package data
    ├── __init__.py              # Content access helpers (importlib.resources)
    ├── docs/                    # Methodology guides (copied from repo root docs/)
    ├── templates/               # TPM templates (copied from repo root templates/)
    ├── agents/                  # Agent configs (copied from repo root agents/)
    ├── playbooks/               # Playbooks (copied from repo root playbooks/)
    ├── showcase/                # Demo content (copied from repo root showcase/)
    ├── case-study/              # Case study (copied from repo root case-study/)
    └── anechoic/                # Anechoic methodology (vendored from external)
```

### Pattern 1: Typer App with Callback for Global Flags
**What:** Use `@app.callback()` to define `--verbose`, `--quiet`, and `--version` as global flags processed before any subcommand.
**When to use:** Always -- this is the entry point for all CLI invocations.
**Example:**
```python
# Source: https://typer.tiangolo.com/tutorial/commands/one-or-multiple/
import typer
from importlib.metadata import version as pkg_version

app = typer.Typer(
    name="pal",
    help="AI-augmented Technical Program Management toolkit.",
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,  # security: don't leak env vars
)

def version_callback(value: bool):
    if value:
        from rich import print as rprint
        rprint(f"palimpsest {pkg_version('palimpsest')}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output.",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q",
        help="Minimal output.",
    ),
):
    """AI-augmented Technical Program Management toolkit."""
    # Store flags in app context for subcommands to read
    pass
```

### Pattern 2: Rich Error Panels (Rust-style)
**What:** Catch known exceptions and display Rich panels with error + fix suggestion.
**When to use:** For all user-facing error conditions.
**Example:**
```python
# Source: Rich docs + Typer exception handling
from rich.console import Console
from rich.panel import Panel

console = Console(stderr=True)

class PalError(Exception):
    """Base error with user-facing message and fix suggestion."""
    def __init__(self, message: str, hint: str = ""):
        self.message = message
        self.hint = hint
        super().__init__(message)

def handle_error(error: PalError, verbose: bool = False):
    body = f"[bold red]Error:[/] {error.message}"
    if error.hint:
        body += f"\n\n[bold green]Hint:[/] {error.hint}"
    console.print(Panel(body, title="[red]pal[/]", border_style="red"))
    if verbose:
        console.print_exception()
    raise typer.Exit(code=1)
```

### Pattern 3: Package Data Access via importlib.resources
**What:** Access bundled content files at runtime without relying on `__file__` paths.
**When to use:** Whenever CLI needs to read bundled docs, templates, or configs.
**Example:**
```python
# Source: https://setuptools.pypa.io/en/latest/userguide/datafiles.html
from importlib.resources import files

def get_content_path(category: str, filename: str) -> str:
    """Get path to a bundled content file."""
    return str(files("palimpsest.content").joinpath(category, filename))

def list_content(category: str) -> list[str]:
    """List files in a content category."""
    resource_dir = files("palimpsest.content").joinpath(category)
    return [item.name for item in resource_dir.iterdir() if item.is_file()]
```

### Pattern 4: Entry Points for Multiple Command Names
**What:** Register `pal`, `palimpsest`, and `pac` all pointing to the same entry function.
**When to use:** pyproject.toml configuration.
**Example:**
```toml
[project.scripts]
pal = "palimpsest.cli.main:run"
palimpsest = "palimpsest.cli.main:run"
pac = "palimpsest.cli.main:run"
```

### Anti-Patterns to Avoid
- **Putting all CLI code in one file:** Typer apps should use `add_typer()` with one file per command group for maintainability. Phase 1 has few commands, but the structure should support Phase 2-3 growth.
- **Using `__file__` for content paths:** Breaks in zip imports and editable installs. Always use `importlib.resources`.
- **Catching all exceptions silently:** The existing `scripts/` code has 30+ bare `except Exception` handlers. The new CLI layer must NOT perpetuate this -- use typed exceptions.
- **Storing state in module-level globals:** Use Typer context (`ctx.obj`) to pass verbose/quiet flags between callback and commands.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | Custom argparse setup | Typer decorators | Type hints generate help, validation, completion automatically |
| Terminal colors/formatting | ANSI escape codes | Rich Console + markup | Cross-platform, handles width detection, degradation |
| Version detection | Hardcoded string | `importlib.metadata.version()` | Reads from installed package metadata; single source of truth in pyproject.toml |
| Help text generation | Manual help strings | Typer auto-generation from docstrings | Always in sync with actual parameters |
| Error formatting | Custom print formatting | Rich Panel | Consistent styling, respects terminal width, handles unicode |
| Package data access | `os.path` / `__file__` hacks | `importlib.resources` | Works with zip imports, editable installs, frozen apps |

**Key insight:** Typer + Rich together handle 90% of CLI UX concerns. The implementation effort should focus on package restructuring and content bundling, not CLI infrastructure.

## Common Pitfalls

### Pitfall 1: Package Data Not Included in Wheel
**What goes wrong:** Content files (markdown docs, templates) are present in sdist but missing from wheel.
**Why it happens:** `[tool.setuptools.package-data]` globs don't match, or content directories lack `__init__.py` files needed for setuptools to recognize them as packages.
**How to avoid:** (a) Every directory containing content MUST have an `__init__.py`. (b) Verify with `python -m build && unzip -l dist/*.whl | grep .md` that markdown files appear in the wheel. (c) Use explicit glob patterns: `"palimpsest/content/**/*.md"`.
**Warning signs:** `importlib.resources` raises `FileNotFoundError` after `pip install`.

### Pitfall 2: Egg-Info Cache Stale After Restructuring
**What goes wrong:** After renaming packages or moving files, old `*.egg-info/SOURCES.txt` caches stale file lists.
**Why it happens:** Setuptools reads `SOURCES.txt` to determine what to include. Stale entries cause missing or phantom files.
**How to avoid:** Delete `palimpsest.egg-info/` before rebuilding after any package structure change.
**Warning signs:** Files you moved still appear at old paths, or newly added files are missing.

### Pitfall 3: Breaking Existing `scripts/` Import Paths
**What goes wrong:** Existing code imports like `from scripts.core.service_clients import ...` break after restructuring.
**Why it happens:** Moving packages or changing `[tool.setuptools.packages.find]` changes what Python can import.
**How to avoid:** Phase 1 should ADD the new `palimpsest/` package structure WITHOUT removing the existing `scripts/` package from setuptools discovery. The old `pac` entry point can be redirected, but the import path `scripts.*` should remain functional. Existing tests should keep passing.
**Warning signs:** `pytest scripts/tests/` fails after restructuring.

### Pitfall 4: Typer Version Mismatch Between `is_eager` and Callbacks
**What goes wrong:** The `--version` flag doesn't work when combined with subcommands.
**Why it happens:** Without `is_eager=True`, the callback runs after argument parsing, which fails if a required subcommand is missing.
**How to avoid:** Always set `is_eager=True` on the version Option.
**Warning signs:** Running `pal --version` without a subcommand produces an error instead of printing the version.

### Pitfall 5: Content Symlinks vs Copies
**What goes wrong:** Content directories are symlinked from repo root into the package, but symlinks don't survive `pip install` or wheel building.
**Why it happens:** Wheels are zip archives; they cannot contain symlinks.
**How to avoid:** Content must be COPIED into the package directory, not symlinked. For development, use `pip install -e .` with `[tool.setuptools.package-data]` pointing to actual files. For anechoic (external), use a build-time copy script or maintain a vendored copy.
**Warning signs:** Works in editable install, breaks in regular `pip install`.

### Pitfall 6: PyPI Name Collision
**What goes wrong:** `pip install palimpsest` installs the wrong package (Robert Trigg's v0.0.2, not ours).
**Why it happens:** The name `palimpsest` is already taken on PyPI.
**How to avoid:** For Phase 1 (local development only), this is not a blocker -- `pip install -e .` and `pipx install .` work with local paths. Before Phase 5 (PyPI publishing), resolve the name: request transfer via PEP 541 (package appears abandoned since Oct 2023), or use `palimpsest-tpm`.
**Warning signs:** Users who run `pip install palimpsest` get someone else's package.

## Code Examples

### Complete Entry Point Setup
```python
# palimpsest/cli/main.py
# Source: Typer docs + importlib.metadata docs
import typer
from importlib.metadata import version as pkg_version, PackageNotFoundError

from palimpsest.console import console

app = typer.Typer(
    name="pal",
    help="AI-augmented Technical Program Management toolkit.",
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

def _version_callback(value: bool) -> None:
    if value:
        try:
            ver = pkg_version("palimpsest")
        except PackageNotFoundError:
            ver = "0.0.0-dev"
        console.print(f"palimpsest [bold]{ver}[/bold]")
        raise typer.Exit()

@app.callback()
def callback(
    version: bool = typer.Option(
        False, "--version", "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output.",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q",
        help="Minimal output.",
    ),
) -> None:
    """AI-augmented Technical Program Management toolkit."""
    pass

def run() -> None:
    """Entry point for console_scripts."""
    app()
```

### Console Singleton with Theme
```python
# palimpsest/console.py
# Source: Rich docs
from rich.console import Console
from rich.theme import Theme

PAL_THEME = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "hint": "dim green",
    "command": "bold magenta",
})

console = Console(theme=PAL_THEME)
err_console = Console(theme=PAL_THEME, stderr=True)
```

### Structured Error Display
```python
# palimpsest/errors.py
from rich.panel import Panel
from palimpsest.console import err_console

class PalError(Exception):
    """User-facing error with optional fix suggestion."""
    def __init__(self, message: str, hint: str = ""):
        self.message = message
        self.hint = hint
        super().__init__(message)

def display_error(error: PalError, verbose: bool = False) -> None:
    parts = [f"[error]{error.message}[/error]"]
    if error.hint:
        parts.append(f"\n[hint]Hint: {error.hint}[/hint]")
    err_console.print(
        Panel("\n".join(parts), title="[error]error[/error]", border_style="red")
    )
    if verbose:
        err_console.print_exception(show_locals=False)
```

### pyproject.toml Package Data Configuration
```toml
# Relevant sections for content bundling
[tool.setuptools.packages.find]
include = ["palimpsest*", "scripts*"]

[tool.setuptools.package-data]
"palimpsest.content" = [
    "**/*.md",
    "**/*.template",
    "**/*.mdc",
    "**/*.json",
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `setup.py` + `setup.cfg` | `pyproject.toml` only | PEP 621 (2021), widely adopted by 2023 | Already using pyproject.toml -- no change needed |
| `pkg_resources.resource_filename()` | `importlib.resources.files()` | Python 3.9+ (refined 3.10+) | Use `importlib.resources` -- `pkg_resources` is deprecated |
| Click for CLI | Typer (built on Click) | Typer stable since ~2022 | Typer is the modern choice; Click still works underneath |
| `__version__` in `__init__.py` | `importlib.metadata.version()` | Python 3.8+ | Single source of truth in pyproject.toml |
| Colorama for colors | Rich for full terminal UX | Rich stable since 2020, dominant by 2023 | Rich provides far more than colors |

**Deprecated/outdated:**
- `pkg_resources`: Deprecated, slow at import time. Use `importlib.metadata` and `importlib.resources`.
- `setup.py`: Not needed for pure-Python packages. `pyproject.toml` is sufficient.
- `entry_points` in `setup.cfg`: Use `[project.scripts]` in pyproject.toml instead.

## Open Questions

1. **PyPI name `palimpsest` is taken**
   - What we know: Taken by Robert Trigg, v0.0.2, last update Oct 2023, no project description, appears abandoned
   - What's unclear: Whether PEP 541 reclaim will succeed, how long it takes
   - Recommendation: Proceed with Phase 1 using `palimpsest` locally. File PEP 541 request before Phase 5. Have `palimpsest-tpm` as fallback name.

2. **Content directory structure: copy vs reference**
   - What we know: Content (docs/, templates/, agents/, etc.) currently lives at the repo root. For package distribution, it must be inside the `palimpsest/` package.
   - What's unclear: Whether to maintain two copies (repo root for GitHub browsing + palimpsest/content/ for packaging) or restructure the entire repo.
   - Recommendation: For Phase 1, copy content into `palimpsest/content/` and keep the repo root copies as the "source." Add a build/sync step or symlinks for development. The wheel only ships `palimpsest/content/`.

3. **Anechoic content vendoring**
   - What we know: Lives at `~/Projects/anechoic/`, needs to be version-pinned and bundled.
   - What's unclear: Exact copy mechanism, version pinning strategy (git tag? file?).
   - Recommendation: Create a `scripts/vendor_anechoic.py` or Makefile target that copies from `~/Projects/anechoic/` into `palimpsest/content/anechoic/` with a version marker file. Run before `python -m build`.

4. **Existing `scripts/` package: keep or migrate?**
   - What we know: All existing functionality lives under `scripts/`. The new CLI lives under `palimpsest/cli/`. Both need to coexist.
   - What's unclear: Whether existing scripts should be importable from both `scripts.*` and `palimpsest.scripts.*`.
   - Recommendation: Phase 1 keeps `scripts/` as-is. The new `palimpsest/` package is additive. Later phases can migrate scripts under `palimpsest/` if needed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=7.4.0 (already configured) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ scripts/tests/ -v --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CLI-01 | Package installs and `pal` command is available | smoke | `pip install -e . && pal --help` | No -- Wave 0 |
| CLI-02 | All commands respond to `--help` | unit | `python -m pytest tests/test_cli.py::test_help_flags -x` | No -- Wave 0 |
| CLI-03 | `pal --version` prints version | unit | `python -m pytest tests/test_cli.py::test_version -x` | No -- Wave 0 |
| CLI-04 | CLI uses Rich formatted output | unit | `python -m pytest tests/test_cli.py::test_rich_output -x` | No -- Wave 0 |
| CLI-05 | User errors show panels, not tracebacks | unit | `python -m pytest tests/test_cli.py::test_error_handling -x` | No -- Wave 0 |
| DIST-02 | Content files bundled in package | unit | `python -m pytest tests/test_content.py::test_bundled_content -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ scripts/tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/` directory at project root (new, for palimpsest package tests)
- [ ] `tests/test_cli.py` -- CLI smoke tests using `typer.testing.CliRunner`
- [ ] `tests/test_content.py` -- Content bundling validation
- [ ] `tests/test_errors.py` -- Error display formatting
- [ ] `tests/conftest.py` -- Shared fixtures for new test suite
- [ ] Update `pyproject.toml` `[tool.pytest.ini_options]` testpaths to include `tests/`

**Note:** Typer provides `typer.testing.CliRunner` (wraps Click's `CliRunner`) for testing CLI invocations without subprocess calls. This is the standard pattern:

```python
from typer.testing import CliRunner
from palimpsest.cli.main import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "palimpsest" in result.output

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
```

## Sources

### Primary (HIGH confidence)
- Typer official docs (https://typer.tiangolo.com/) -- CLI patterns, callbacks, Rich integration, exception handling
- setuptools docs (https://setuptools.pypa.io/en/latest/userguide/datafiles.html) -- package-data, importlib.resources
- PyPI registry -- verified typer 0.24.1, rich 14.3.3 current versions
- Python stdlib docs -- importlib.metadata, importlib.resources

### Secondary (MEDIUM confidence)
- PyPI `palimpsest` package page (https://pypi.org/project/palimpsest/) -- name collision confirmed, appears abandoned

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- verified current versions on PyPI, well-documented libraries
- Architecture: HIGH -- Typer patterns are well-established, setuptools package-data is standard
- Pitfalls: HIGH -- based on official docs warnings and direct codebase analysis
- Content bundling: MEDIUM -- the specific content-copy workflow for this project needs validation during implementation

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain, 30 days)
