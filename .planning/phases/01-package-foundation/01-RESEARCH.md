# Phase 1: Package Foundation - Research

**Researched:** 2026-03-18
**Domain:** Python packaging (setuptools, package_data, importlib.resources)
**Confidence:** HIGH

## Summary

The palimpsest repo currently ships only `scripts*` as a Python package. All content (docs, templates, agents, playbooks, case-study, showcase, project-template) lives at the repo root and is not included in any pip install. The restructure requires moving content into a proper `palimpsest/` Python package directory so setuptools can include it as package_data, then making scripts an optional extras group with the heavy Google/API dependencies.

The tests use a `load_module` fixture that loads scripts by file path (`importlib.util.spec_from_file_location`), NOT by Python import path. This is excellent news -- it means the test suite is resilient to package restructuring. The `SCRIPTS_DIR` in conftest.py resolves via `Path(__file__).resolve().parent.parent`, so tests will continue to work as long as the relative directory structure within the scripts subtree is preserved.

**Primary recommendation:** Use flat layout with a `palimpsest/` package directory at the repo root. Move all content directories inside it. Move scripts into `palimpsest/scripts/`. Use `[tool.setuptools.package-data]` to include `*.md`, `*.template`, `*.mdc`, `*.json` files. Split dependencies so base install has zero heavy deps, scripts extras pulls in google-api-python-client etc.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PKG-01 | Ship all content as package data (templates, agent configs, docs, playbooks, methodology) | Use `[tool.setuptools.package-data]` with glob patterns for md/template/mdc/json files inside `palimpsest/` package. Access via `importlib.resources.files()` |
| PKG-02 | Python automation scripts remain functional and installable as optional extras | Move scripts into `palimpsest/scripts/`, create `[scripts]` optional dep group with heavy deps, base install has no heavy deps |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| setuptools | >=68.0 | Build system | Already in use, mature, well-documented package_data support |
| wheel | latest | Build format | Already in use |
| importlib.resources | stdlib (3.9+) | Runtime access to package data | Modern stdlib, no extra deps, works with zip imports |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | >=7.4.0 | Testing | Already in dev extras, no changes needed |
| pytest-cov | >=4.0.0 | Coverage | Already in dev extras |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| setuptools | hatchling/flit | Would require rewriting build config; setuptools already works and supports package_data natively |
| flat layout | src layout | src layout prevents accidental local imports but adds complexity; flat layout is simpler for this migration and already matches the repo structure |
| package_data | data_files | data_files installs to unpredictable platform-specific locations; package_data keeps files inside the package -- the only correct choice |

## Architecture Patterns

### Recommended Project Structure
```
palimpsest/                    # NEW: Python package directory
    __init__.py                # Package init, exposes __version__
    data/                      # NEW: wrapper for content access
        __init__.py            # Helper functions using importlib.resources
    docs/                      # MOVED from repo root
        *.md
    templates/                 # MOVED from repo root
        *.md
    agents/                    # MOVED from repo root
        claude-code/
        cursor/
        cline/
        memory-bank/
        *.md
    playbooks/                 # MOVED from repo root
        *.md
    case-study/                # MOVED from repo root
        *.md
    showcase/                  # MOVED from repo root
        *.md
    project-template/          # MOVED from repo root
        .cursor/
        docs/
        *.md
    example/                   # MOVED from repo root
        ...
    scripts/                   # MOVED from repo root scripts/
        __init__.py            # Already exists
        core/
        sync/
        content/
        automation/
        publishing/
        tests/                 # Tests stay with scripts
            conftest.py
            test_*.py
pyproject.toml                 # Updated config
README.md                      # Stays at repo root
CLAUDE.md                      # Stays at repo root
CONTRIBUTING.md                # Stays at repo root
LICENSE                        # Stays at repo root
setup.sh                       # Stays at repo root (legacy)
```

### Pattern 1: Package Data via pyproject.toml
**What:** Declare non-Python files as package_data so they are included in the wheel/sdist
**When to use:** Always -- this is the mechanism that makes content installable
**Example:**
```toml
# Source: https://setuptools.pypa.io/en/latest/userguide/datafiles.html
[tool.setuptools.packages.find]
include = ["palimpsest*"]

[tool.setuptools.package-data]
"palimpsest" = [
    "**/*.md",
    "**/*.template",
    "**/*.mdc",
    "**/*.json",
    "**/*.gitignore",
]
```

### Pattern 2: Runtime Data Access via importlib.resources
**What:** Access package data files at runtime using the modern stdlib API
**When to use:** When any code needs to read bundled content files
**Example:**
```python
# Source: https://docs.python.org/3/library/importlib.resources.html
from importlib.resources import files

def get_template(name: str) -> str:
    """Read a template file from package data."""
    return files("palimpsest").joinpath("templates", name).read_text()

def get_data_path(subpath: str):
    """Get a Traversable path to any package data file."""
    return files("palimpsest").joinpath(subpath)
```

### Pattern 3: Optional Extras for Heavy Dependencies
**What:** Base install has zero or minimal deps; heavy deps are in extras groups
**When to use:** When most users want the content, not the scripts
**Example:**
```toml
[project]
dependencies = []  # Base install: content only, no deps

[project.optional-dependencies]
scripts = [
    "google-api-python-client>=2.100.0",
    "google-auth-httplib2>=0.1.1",
    "google-auth-oauthlib>=1.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
]
pdf = ["PyPDF2>=3.0.0"]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
]
all = ["palimpsest[scripts,pdf]"]
```

### Pattern 4: Entry Point Gated on Extras
**What:** CLI entry point exists but gracefully fails if deps not installed
**When to use:** For the `pac` CLI command
**Example:**
```toml
[project.scripts]
pac = "palimpsest.scripts.core.preflight_check:main"
```

### Anti-Patterns to Avoid
- **Using `__file__` for data access:** Breaks with zip imports and PEP 302 hooks. Use `importlib.resources.files()` instead.
- **Using `pkg_resources`:** Deprecated, slow startup, replaced by `importlib.resources`.
- **Using `data_files`:** Installs to unpredictable system locations. Files become unretrievable at runtime.
- **Putting content directories at repo root and relying on MANIFEST.in:** Content must be inside the Python package directory for `package_data` to work.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finding package data at runtime | Custom path resolution with `__file__` | `importlib.resources.files()` | Works with zip imports, eggs, and all packaging formats |
| Including non-Python files in wheel | MANIFEST.in hacks, custom build steps | `[tool.setuptools.package-data]` glob patterns | Native setuptools support, declarative, well-tested |
| Splitting optional dependencies | Runtime import checks with try/except at module level | `[project.optional-dependencies]` extras | Standard pip mechanism, declared in metadata |

## Common Pitfalls

### Pitfall 1: Content directories without __init__.py
**What goes wrong:** Setuptools does not recognize a directory as a package if it lacks `__init__.py`. The `package-data` globs only apply to discovered packages.
**Why it happens:** Content directories (docs/, templates/, agents/) are not Python packages and have no `__init__.py`.
**How to avoid:** Add an empty `__init__.py` to every content subdirectory inside `palimpsest/`. This makes them Python packages that setuptools discovers, and then `package-data` globs match their files. Alternatively, use `[tool.setuptools.package-data] "palimpsest" = ["**/*.md", ...]` with the top-level package glob -- but subdirectories still need `__init__.py` to be found as sub-packages.
**Warning signs:** `pip install .` succeeds but `importlib.resources.files("palimpsest").joinpath("templates/prd.md")` raises FileNotFoundError.

### Pitfall 2: Forgetting nested subdirectories need __init__.py too
**What goes wrong:** `agents/claude-code/`, `agents/cursor/`, `agents/memory-bank/example/`, `project-template/docs/` etc. are nested directories. Each level needs `__init__.py` or the files inside won't be included.
**Why it happens:** `package-data` only covers files in discovered packages. Each directory in the path must be a package.
**How to avoid:** Recursively add `__init__.py` to ALL directories that contain content files. A simple script: `find palimpsest -type d -exec touch {}/__init__.py \;`
**Warning signs:** Top-level templates work but nested agent configs are missing after install.

### Pitfall 3: Forgetting to include non-standard file extensions
**What goes wrong:** Files with extensions like `.template`, `.mdc`, `.gitignore` are silently excluded from the wheel.
**Why it happens:** Only explicitly listed glob patterns in `package-data` are included.
**How to avoid:** Audit all file extensions in content directories and add them to `package-data` globs. Current extensions: `.md`, `.template`, `.mdc`, `.json`, `.gitignore`.
**Warning signs:** Install works but specific config files are missing.

### Pitfall 4: Test conftest.py SCRIPTS_DIR resolution breaks
**What goes wrong:** `SCRIPTS_DIR = Path(__file__).resolve().parent.parent` currently resolves to `scripts/`. After move to `palimpsest/scripts/`, this still resolves to `palimpsest/scripts/` which is correct -- the relative structure is preserved.
**Why it happens:** This is actually safe because `parent.parent` goes from `tests/` up to `scripts/`, and `load_module` uses relative paths like `"core/agent_marker.py"`.
**How to avoid:** No action needed. The `load_module` fixture is path-based and self-contained.
**Warning signs:** None expected, but run tests immediately after restructure to confirm.

### Pitfall 5: pyproject.toml testpaths and pythonpath must update
**What goes wrong:** Current `testpaths = ["scripts/tests"]` and `pythonpath = ["scripts"]` will break.
**Why it happens:** The directories moved from `scripts/` to `palimpsest/scripts/`.
**How to avoid:** Update to `testpaths = ["palimpsest/scripts/tests"]` and `pythonpath = ["palimpsest/scripts"]`.
**Warning signs:** `pytest` finds no tests or imports fail.

### Pitfall 6: The `pac` entry point import path changes
**What goes wrong:** `pac = "scripts.core.preflight_check:main"` breaks because the module path changed.
**Why it happens:** Package is now `palimpsest.scripts.core.preflight_check`.
**How to avoid:** Update the entry point path in pyproject.toml.
**Warning signs:** `pac` command crashes with ImportError after install.

## Code Examples

### pyproject.toml -- Complete Updated Configuration
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "palimpsest"
version = "0.1.0"
description = "AI-augmented Technical Program Management toolkit"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Vitalik Pavlenko"}
]
keywords = ["tpm", "program-management", "ai", "automation", "markdown"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business",
]

# Base install: content only, no heavy deps
dependencies = []

[project.optional-dependencies]
scripts = [
    "google-api-python-client>=2.100.0",
    "google-auth-httplib2>=0.1.1",
    "google-auth-oauthlib>=1.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
]
pdf = ["PyPDF2>=3.0.0"]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
]
all = ["palimpsest[scripts,pdf]"]

[project.scripts]
pac = "palimpsest.scripts.core.preflight_check:main"

[project.urls]
Homepage = "https://github.com/pleasedodisturb/palimpsest"
Documentation = "https://github.com/pleasedodisturb/palimpsest/tree/main/docs"
Repository = "https://github.com/pleasedodisturb/palimpsest"
Issues = "https://github.com/pleasedodisturb/palimpsest/issues"

[tool.setuptools.packages.find]
include = ["palimpsest*"]

[tool.setuptools.package-data]
"palimpsest" = [
    "**/*.md",
    "**/*.template",
    "**/*.mdc",
    "**/*.json",
    "**/*.gitignore",
]

[tool.pytest.ini_options]
testpaths = ["palimpsest/scripts/tests"]
pythonpath = ["palimpsest/scripts"]
```

### palimpsest/__init__.py
```python
"""Palimpsest - AI-augmented Technical Program Management toolkit."""

__version__ = "0.1.0"
```

### palimpsest/data/__init__.py -- Data Access Helper
```python
"""Helpers for accessing palimpsest package data."""

from importlib.resources import files


def get_package_files():
    """Return a Traversable pointing to the palimpsest package root."""
    return files("palimpsest")


def read_template(name: str) -> str:
    """Read a template file by name."""
    return get_package_files().joinpath("templates", name).read_text()


def read_doc(name: str) -> str:
    """Read a methodology doc by name."""
    return get_package_files().joinpath("docs", name).read_text()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pkg_resources` for data access | `importlib.resources.files()` | Python 3.9 (2020), stable since 3.11 | No extra deps, faster startup |
| `setup.py` with `package_data={}` | `pyproject.toml` with `[tool.setuptools.package-data]` | setuptools 61+ (2022) | Fully declarative, no code needed |
| `data_files` for non-package data | `package_data` (data INSIDE package) | Long-standing recommendation | Reliable runtime access |
| MANIFEST.in for sdist inclusion | `include-package-data = true` (default) + VCS plugin | setuptools 43+ | Automatic if files are tracked by git |

**Deprecated/outdated:**
- `pkg_resources`: Slow, deprecated in favor of `importlib.resources` and `importlib.metadata`
- `setup.py` for declarative config: Replaced by `pyproject.toml`
- `data_files`: "There is no supported facility to reliably retrieve" files installed this way (PyPA docs)

## Open Questions

1. **Should `example/` directory be included as package data?**
   - What we know: It contains 2 files (example usage). It is useful for documentation.
   - What's unclear: Whether users need it at runtime or just in the repo.
   - Recommendation: Include it -- small overhead, useful for reference. Can always exclude later.

2. **Should `project-template/` include dotfiles like `.gitignore` and `.cursor/mcp.json`?**
   - What we know: These are critical for the Phase 2 `palimpsest init` command to work correctly.
   - What's unclear: Dotfiles can be tricky with glob patterns and VCS.
   - Recommendation: Explicitly include them via glob patterns `**/*.gitignore` and `**/*.json`. Verify after build.

3. **Should the `scripts/examples/` directory (currently empty) be preserved?**
   - What we know: It exists but is empty.
   - Recommendation: Preserve it for future use but no action needed now.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=7.4.0 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest palimpsest/scripts/tests/ -x --tb=short` |
| Full suite command | `python -m pytest palimpsest/scripts/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PKG-01 | Content files accessible via importlib.resources after install | integration | `python -m pytest palimpsest/scripts/tests/test_package_data.py -x` | No -- Wave 0 |
| PKG-01 | All expected content directories present in installed package | smoke | `python -c "from importlib.resources import files; assert files('palimpsest').joinpath('templates').is_dir()"` | No -- Wave 0 |
| PKG-02 | All 169 existing script tests pass after restructure | unit | `python -m pytest palimpsest/scripts/tests/ -x --tb=short` | Yes (existing 14 test files) |
| PKG-02 | Scripts importable via palimpsest.scripts.* path | smoke | `python -c "from palimpsest.scripts.core import preflight_check"` | No -- Wave 0 |
| PKG-02 | pac CLI entry point works after install | smoke | `pac --help` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest palimpsest/scripts/tests/ -x --tb=short`
- **Per wave merge:** `python -m pytest palimpsest/scripts/tests/ -v`
- **Phase gate:** Full suite green + smoke tests for package data access

### Wave 0 Gaps
- [ ] `palimpsest/scripts/tests/test_package_data.py` -- covers PKG-01 (verify content files are accessible via importlib.resources)
- [ ] Smoke test script for PKG-02 (verify pac entry point and import paths)
- [ ] No framework install needed -- pytest already in dev extras

## Sources

### Primary (HIGH confidence)
- [Setuptools Data Files Support](https://setuptools.pypa.io/en/latest/userguide/datafiles.html) - package_data vs data_files guidance, pyproject.toml config
- [Setuptools pyproject.toml Configuration](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html) - packages.find, package-data, optional-dependencies
- [Python importlib.resources docs](https://docs.python.org/3/library/importlib.resources.html) - files() API, Traversable interface

### Secondary (MEDIUM confidence)
- [Python Packaging User Guide - Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - general packaging guidance

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - setuptools package_data is well-documented, verified against official docs
- Architecture: HIGH - flat layout with package_data is the standard setuptools pattern for this use case
- Pitfalls: HIGH - verified against real project structure; test fixture analysis confirms tests are path-based and resilient
- Import migration: HIGH - straightforward rename from `scripts.*` to `palimpsest.scripts.*`

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable domain, setuptools rarely breaks backward compat)
