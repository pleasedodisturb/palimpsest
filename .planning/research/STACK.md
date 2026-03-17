# Technology Stack: Packaging and Distribution

**Project:** Palimpsest CLI packaging
**Researched:** 2026-03-17
**Scope:** What's needed to package and distribute palimpsest as an installable CLI tool
**Confidence note:** WebSearch/WebFetch unavailable during research. Versions based on training data (cutoff May 2025). Flag versions for validation before implementation.

## Recommended Stack

### Build Backend

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **hatchling** | >= 1.25.0 | Build backend replacing setuptools | Native support for `[tool.hatch.build]` include/exclude patterns, built-in version management via `hatch-vcs`, simpler package-data inclusion than setuptools. The existing setuptools config only ships `scripts/` -- switching to hatchling makes it straightforward to add `docs/`, `templates/`, `agents/`, `playbooks/` as package data without fighting `MANIFEST.in` or `package_data` globs. | MEDIUM |
| **hatch** | >= 1.12.0 | Build/env management CLI | Project management tool built on hatchling. Handles virtual environments, build, publish, and version bumping. Replaces scattered `pip install -e .` + manual version workflows. | MEDIUM |

**Why not keep setuptools?** Setuptools can do this, but including non-Python content (markdown files, agent configs, templates) as package data requires `MANIFEST.in` + `package_data` + careful `find_packages` configuration. Hatchling's `[tool.hatch.build.targets.wheel]` with explicit `include` paths is more predictable. The migration cost is low -- just change `[build-system]` and add `[tool.hatch.build]` in pyproject.toml.

**Why not flit or pdm?** Flit is too simple for this use case (no custom build hooks). PDM is heavier than needed -- palimpsest doesn't need a lockfile manager or PEP 582 support.

### CLI Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **click** | >= 8.1.0 | CLI framework with subcommands | Battle-tested, no type-annotation magic, explicit decorators. Palimpsest needs subcommands (`pac init`, `pac update`, `pac status`, `pac detect`) with options and arguments. Click's `@click.group()` + `@group.command()` pattern maps 1:1 to this. Existing argparse code can be gradually migrated. | HIGH |

**Why not typer?** Typer wraps Click and adds type-annotation-based argument parsing. It's nice for simple CLIs, but palimpsest has complex subcommand logic (runtime detection, interactive setup, update with patch preservation). Typer's magic becomes a hindrance when you need fine-grained control over prompts, context passing, and error handling. Click gives full control without an abstraction layer. The existing codebase already uses argparse (imperative style), so Click's explicit decorator style is a smaller mental model shift than Typer's implicit-from-types approach.

**Why not argparse?** Already in use, but argparse subcommands are verbose and lack built-in features Click provides: automatic help generation, option groups, context passing between commands, plugin-friendly architecture, and rich error messages. The migration is worth it for the CLI-as-product quality bar.

### Interactive Prompts

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **questionary** | >= 2.0.0 | Interactive guided setup (init wizard) | Clean API for select, text, confirm, checkbox prompts. Built on prompt_toolkit. Integrates well with Click. The `pac init` command needs a guided setup wizard (program name, stakeholders, timeline, editor detection confirmation). | MEDIUM |

**Why not InquirerPy?** InquirerPy is also good but less actively maintained. Questionary has a cleaner API and better Click integration.

**Why not click.prompt/click.confirm?** Too basic for multi-step wizards. Click's built-in prompts work for single values but not for select-from-list or checkbox patterns needed during `pac init`.

### Terminal Output

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **rich** | >= 13.0.0 | Formatted terminal output | Tables, progress bars, syntax highlighting, panels. `pac status` needs to display editor detection results, version info, and content inventory as formatted tables. `pac update` needs progress indication. Rich is the standard for Python CLI tools that care about UX. | HIGH |

### Package Data and Resource Access

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **importlib.resources** | stdlib (3.10+) | Access bundled markdown/config files at runtime | The standard library way to read files bundled inside a Python package. Palimpsest needs to read templates, agent configs, docs, and playbooks from within the installed package to copy them into user projects. `importlib.resources.files()` (available since 3.9) is the correct API. No third-party dependency needed. | HIGH |

**Why not pkg_resources?** Deprecated. Slow. Part of setuptools, not stdlib in modern Python.

**Why not __file__ path resolution?** Breaks with zip-imported packages and is fragile across installation methods. `importlib.resources` works regardless of how the package is installed.

### Version Management

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **hatch-vcs** | >= 0.4.0 | Git-tag-based versioning | Derives version from git tags automatically. No manual version string maintenance. Tag `v1.0.0` and the build picks it up. Works with hatchling as a build hook. | MEDIUM |
| **python-semantic-release** | >= 9.0.0 | Automated version bumping + changelog | Reads conventional commits, determines next version (major/minor/patch), creates git tag, generates CHANGELOG.md, optionally publishes to PyPI. Integrates with GitHub Actions. | MEDIUM |

**Why not commitizen?** Commitizen is also good but python-semantic-release has better GitHub Actions integration and is more focused on the release pipeline (vs commitizen which also enforces commit message format, which palimpsest already has conventions for).

**Why not towncrier?** Towncrier requires manually creating fragment files per change. python-semantic-release derives changelogs from commit messages, which is lower friction for a project where one maintainer does most commits.

### Distribution

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **PyPI** | -- | Primary package registry | `pip install palimpsest` is the baseline. Every other distribution method builds on this. | HIGH |
| **pipx** | >= 1.5.0 | Isolated CLI installation | `pipx install palimpsest` installs in an isolated venv with the `pac` command available globally. This is the recommended way to install Python CLI tools. Users don't pollute their system Python. | HIGH |
| **Homebrew formula** (custom tap) | -- | `brew install` distribution | A Homebrew tap (`homebrew-palimpsest`) with a formula that installs via pipx or a virtualenv under Homebrew's prefix. This is the target UX from PROJECT.md. | MEDIUM |

**Distribution strategy (ordered by priority):**

1. **PyPI first** -- publish sdist + wheel to PyPI. This is the foundation.
2. **pipx recommended** -- docs tell users `pipx install palimpsest`. Zero config needed from us.
3. **Homebrew tap** -- create `pleasedodisturb/homebrew-palimpsest` repo with a formula. Formula either uses `pip install` into a Homebrew-managed venv (like `aws-cli`, `poetry`, etc.) or uses the `resource` stanza pattern for dependencies.
4. **GitHub Releases** -- attach wheel/sdist to GitHub releases for direct download.

**Why not PyInstaller/Nuitka/shiv for binary distribution?** Palimpsest requires Python at runtime (the automation scripts import Python libraries, users may extend them). Freezing into a binary hides the Python requirement without removing it and adds cross-platform build complexity. The `pipx` + `brew` path gives the same "one command install" UX without the binary packaging overhead.

**Why not conda?** Wrong audience. TPMs and developers using AI editors are not conda users.

### Homebrew Formula Pattern

| Technology | Purpose | Why | Confidence |
|------------|---------|-----|------------|
| **Formula with virtualenv** | Homebrew-native Python app installation | Homebrew's standard pattern for Python CLI tools. The formula creates a virtualenv, installs the package + deps, and links the `pac` binary. See `poetry`, `httpie`, `aws-cli` formulas for precedent. Uses `depends_on "python@3.12"` and `include_language "python"` stanzas. | MEDIUM |

### Editor Runtime Detection

| Technology | Purpose | Why | Confidence |
|------------|---------|-----|------------|
| **shutil.which** | Detect CLI tools in PATH | stdlib. Check for `claude`, `cursor`, `cline` binaries. | HIGH |
| **pathlib + os.environ** | Detect config directories | Check for `~/.claude/`, `~/.cursor/`, `~/.cline/`, etc. Presence of config dirs indicates editor installation even if binary isn't in PATH. | HIGH |
| **subprocess.run** | Probe editor version/status | Call `claude --version`, `cursor --version` etc. to confirm working installation. | HIGH |

No third-party library needed for runtime detection. This is filesystem/PATH probing -- stdlib handles it.

### Update Mechanism with Patch Preservation

| Technology | Purpose | Why | Confidence |
|------------|---------|-----|------------|
| **difflib** (stdlib) | Three-way merge for user-modified files | When updating templates that users have customized, use three-way merge: (old-shipped, new-shipped, user-current). `difflib` provides the primitives. | MEDIUM |
| **hashlib** (stdlib) | Detect user modifications | Hash shipped files at install time, store manifest. On update, compare current hash to shipped hash -- if different, user modified the file. | HIGH |
| **JSON manifest** | Track installed files + versions | `~/.palimpsest/manifest.json` or `.palimpsest/manifest.json` in project. Records what was installed, version, file hashes. Enables clean updates and uninstalls. GSD uses this pattern successfully. | HIGH |

### Development and Quality

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **ruff** | >= 0.5.0 | Linter + formatter | Replaces flake8, isort, black in one tool. Fast. The codebase has no linter currently (noted in CONCERNS.md). | HIGH |
| **mypy** | >= 1.10.0 | Type checking | Gradual typing for the CLI layer. Not needed for existing scripts immediately, but new CLI code should be typed. | MEDIUM |
| **pytest** | >= 8.0.0 | Test runner (keep existing) | Already in use. Bump minimum to 8.x for better output and fixture improvements. | HIGH |

## Stack NOT to Use

| Technology | Why Not |
|------------|---------|
| **setuptools** (as build backend) | Hatchling handles content-as-package-data much more cleanly. Setuptools' MANIFEST.in + package_data is error-prone for shipping markdown content. |
| **Typer** | Abstraction over Click adds complexity without benefit for this CLI's needs. |
| **PyInstaller / Nuitka** | Binary freezing is wrong model. Users need Python runtime for the automation scripts. |
| **Poetry** | Good tool, wrong fit. Poetry is a dependency manager; palimpsest doesn't need lockfiles or dependency resolution beyond what pip provides. Poetry's build backend is less flexible than hatchling for custom package data. |
| **pkg_resources** | Deprecated. Use `importlib.resources`. |
| **argparse** (for new CLI) | Keep in existing scripts for backward compat, but new `pac` CLI should use Click. |
| **conda / conda-forge** | Wrong audience. Adds maintenance burden for negligible reach. |
| **towncrier** | Fragment-file workflow is too heavy for a single-maintainer project. |
| **Sphinx** | Docs are markdown-native. No need for RST-based doc generation. |

## Package Structure (Target)

```
palimpsest/
  pyproject.toml          # hatchling build backend
  src/
    palimpsest/
      __init__.py         # version via hatch-vcs
      cli/
        __init__.py
        main.py           # click group: pac
        init.py           # pac init (interactive setup)
        update.py         # pac update (version upgrade)
        status.py         # pac status (health check)
        detect.py         # pac detect (editor runtime detection)
      core/               # migrated from scripts/core/
      sync/               # migrated from scripts/sync/
      content/            # migrated from scripts/content/
      publishing/         # migrated from scripts/publishing/
      automation/         # migrated from scripts/automation/
      data/               # package data (content files)
        docs/             # methodology guides
        templates/        # TPM document templates
        agents/           # editor config templates
        playbooks/        # TPM playbooks
        project-template/ # scaffolding template
  tests/
  CHANGELOG.md
```

**Key change:** Move to `src/` layout. This is the modern Python packaging standard. It prevents accidental imports from the source tree during development (forces you to install the package).

## Installation Commands (Target UX)

```bash
# Primary: pipx (isolated install)
pipx install palimpsest

# Alternative: Homebrew
brew tap pleasedodisturb/palimpsest
brew install palimpsest

# Alternative: pip (for venv users)
pip install palimpsest

# Development
git clone https://github.com/pleasedodisturb/palimpsest
cd palimpsest
pip install -e ".[dev]"
```

## Dependencies (New, for CLI packaging)

```toml
[project]
dependencies = [
    # Existing (keep)
    "google-api-python-client>=2.100.0",
    "google-auth-httplib2>=0.1.1",
    "google-auth-oauthlib>=1.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    # New (for CLI)
    "click>=8.1.0",
    "rich>=13.0.0",
    "questionary>=2.0.0",
]

[project.optional-dependencies]
pdf = ["PyPDF2>=3.0.0"]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
]

[project.scripts]
pac = "palimpsest.cli.main:cli"
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| Build backend | hatchling | setuptools | Setuptools makes shipping non-Python content files harder than it needs to be |
| Build backend | hatchling | poetry-core | Poetry's build system is less flexible for custom package data inclusion |
| CLI framework | click | typer | Typer's type-annotation magic adds abstraction without benefit for complex subcommands |
| CLI framework | click | argparse | Argparse is too verbose and lacks subcommand ecosystem features |
| Version mgmt | hatch-vcs + python-semantic-release | manual version bumps | Manual is error-prone and doesn't generate changelogs |
| Distribution | PyPI + pipx + Homebrew tap | PyInstaller binary | Wrong model -- users need Python runtime for automation scripts |
| Distribution | PyPI + pipx + Homebrew tap | snap/flatpak | Wrong audience, wrong platform (macOS-primary) |
| Interactive prompts | questionary | InquirerPy | Questionary has cleaner API and better maintenance trajectory |
| Linter | ruff | flake8 + isort + black | Ruff replaces all three, faster, single config |

## Sources

- Training data knowledge (May 2025 cutoff) -- versions should be validated before implementation
- PyPI is the authoritative source for current versions of all recommended packages
- Homebrew formula patterns based on existing Python CLI tool formulas (poetry, httpie, aws-cli)
- `src/` layout recommendation from Python Packaging Authority (PyPA) guidelines
- `importlib.resources` API from Python 3.10+ stdlib documentation

## Validation Checklist (Pre-Implementation)

Before starting implementation, verify these with `pip index versions`:

- [ ] hatchling latest version (recommended >= 1.25.0)
- [ ] click latest version (recommended >= 8.1.0)
- [ ] rich latest version (recommended >= 13.0.0)
- [ ] questionary latest version (recommended >= 2.0.0)
- [ ] python-semantic-release latest version (recommended >= 9.0.0)
- [ ] ruff latest version (recommended >= 0.5.0)
- [ ] Confirm hatch-vcs works with hatchling version chosen
- [ ] Confirm Homebrew formula pattern for Python apps hasn't changed
