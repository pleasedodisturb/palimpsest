# Domain Pitfalls

**Domain:** Python CLI packaging with non-Python content + multi-editor AI tool distribution
**Researched:** 2026-03-17
**Confidence:** HIGH (Python packaging pitfalls are well-documented; multi-editor detection is based on direct analysis of palimpsest's existing agent configs and AI editor conventions)

---

## Critical Pitfalls

Mistakes that cause rewrites, broken installs, or user data loss.

### Pitfall 1: Non-Python Files Silently Missing from Installed Package

**What goes wrong:** You declare `package_data` or `include_package_data` in `pyproject.toml`, but your markdown docs, templates, agent configs, and playbooks do not ship in the installed wheel. The CLI runs, finds zero content files, and either crashes or installs an empty skeleton.

**Why it happens:** setuptools has three independent mechanisms for including non-Python files, and they interact in confusing ways:
1. `package_data` -- glob patterns relative to each package directory. Only works for files **inside** a Python package (directory with `__init__.py`).
2. `include_package_data = true` -- includes files tracked by VCS (git), but **only** files inside packages. Still requires `__init__.py`.
3. `MANIFEST.in` -- controls what goes into sdist tarballs, but has **zero effect** on wheel contents.

Palimpsest's current structure has `docs/`, `templates/`, `agents/`, `playbooks/`, `showcase/`, and `case-study/` as **top-level directories outside any Python package**. None of them contain `__init__.py`. No `package_data` glob will find them. `include_package_data` will not see them. They will be absent from wheels.

The sdist (source distribution) includes everything in git, masking the problem -- `pip install` from sdist may work while `pip install` from wheel silently ships an empty package. Since PyPI prefers wheels, most users get the broken version.

**Consequences:** Users install the package, run `palimpsest init`, and get zero methodology docs, zero templates, zero agent configs. The core value proposition ("one command, full AI-TPM") is completely broken.

**Warning signs:**
- `pip install -e .` works (editable mode reads from source tree) but `pip install .` does not find content files
- Building a wheel with `python -m build` and inspecting it with `unzip -l dist/*.whl` shows no `.md` files outside `scripts/`
- Tests pass in CI because CI uses editable install or source checkout

**Prevention:**
1. Restructure content into a Python package: create `palimpsest/` as the top-level package with `__init__.py`, and move content directories underneath it (e.g., `palimpsest/content/docs/`, `palimpsest/content/templates/`, `palimpsest/content/agents/`)
2. Use `importlib.resources` (Python 3.9+) to read package data at runtime -- never use `__file__`-relative paths
3. Add a CI step that builds a wheel, installs it into a clean venv, and verifies content files are accessible via `importlib.resources`
4. Set `[tool.setuptools.package-data]` with explicit globs: `palimpsest = ["**/*.md", "**/*.template", "**/*.mdc", "**/*.json"]`

**Phase:** Must be solved in the initial packaging phase. Every subsequent feature depends on content being installable.

---

### Pitfall 2: `importlib.resources` vs `__file__` Path Resolution

**What goes wrong:** Code uses `Path(__file__).parent / "templates"` to find content files. This works in development but breaks when the package is installed inside a zip file (zipapp), a frozen binary (PyInstaller/Nuitka), or certain pip install modes where the package is not extracted to the filesystem.

**Why it happens:** `__file__` is a CPython implementation detail, not a packaging contract. `importlib.resources` is the correct API for accessing package data, but it has a different interface -- it returns `Traversable` objects, not `Path` objects, and the API changed significantly between Python 3.9, 3.11, and 3.12.

**Consequences:** Package works for the developer, breaks for users who install via pip from PyPI, especially on systems with non-standard Python installations.

**Warning signs:**
- `FileNotFoundError` or `NotADirectoryError` in production but never in dev
- Tests that reference fixture files via `__file__` paths all pass locally

**Prevention:**
1. Create a `palimpsest/resources.py` module that wraps `importlib.resources.files()` (Python 3.9+)
2. All content access goes through this single module -- never direct filesystem paths
3. For Python 3.10 compatibility, use the `importlib_resources` backport package (it smooths over API differences)
4. Test the resource access in CI using a wheel install, not editable install

**Phase:** Initial packaging phase, alongside Pitfall 1.

---

### Pitfall 3: Update Command Destroys User Customizations

**What goes wrong:** User runs `palimpsest init`, customizes templates and agent configs to their program, then runs `palimpsest update`. The update overwrites all their files with fresh defaults.

**Why it happens:** The simplest update mechanism copies new files over old files. Without a merge strategy, there is no way to know which parts of a file are "user content" vs "framework boilerplate."

**Consequences:** Users lose hours of work. After one bad update, they never run `update` again, defeating the purpose of versioned releases. Some users may not have git history in their project to recover from.

**Warning signs:**
- Users reporting lost customizations on GitHub issues
- Users pinning to old versions and never updating
- The update command having no `--dry-run` or preview mode

**Prevention:**
1. **Track what was installed.** Write a manifest file (e.g., `.palimpsest/manifest.json`) recording every file installed, its SHA-256 hash at install time, and the palimpsest version.
2. **Three-way classification on update:**
   - File unchanged by user (hash matches manifest) -> safe to overwrite
   - File modified by user AND changed in new version -> write `.palimpsest/conflicts/filename.md.new`, warn user
   - File modified by user, not changed in new version -> leave alone
   - New file in new version -> install it, add to manifest
   - File removed in new version -> warn, do not delete
3. **Always `--dry-run` first.** Default behavior shows what would change, requires `--apply` to execute.
4. **Never delete user files.** Mark files as deprecated in the manifest but do not remove them.

**Phase:** Must be designed in the packaging phase (manifest format), implemented in the update-command phase. Getting the manifest format wrong early means a painful migration later.

---

### Pitfall 4: Homebrew Formula Fights Python Packaging

**What goes wrong:** You publish to PyPI and create a Homebrew formula. The formula installs into Homebrew's Python prefix, but dependencies conflict with the user's global Python, or the formula breaks when Homebrew upgrades Python.

**Why it happens:** Homebrew manages its own Python installations and aggressively upgrades them. A formula using `pip install` inside Homebrew's Python will:
- Break when Homebrew bumps Python 3.12 -> 3.13 (compiled C extensions become invalid)
- Conflict with other Homebrew formulae that install the same Python dependencies
- Not work at all if the user has a different Python version expectation

**Consequences:** `brew upgrade` randomly breaks palimpsest. Users see `ModuleNotFoundError` for dependencies that were installed a week ago.

**Warning signs:**
- GitHub issues spike after Homebrew Python version bumps (happens ~every 6 months)
- Formula works on CI but fails for users with different Homebrew configurations
- `brew doctor` warnings about Python path conflicts

**Prevention:**
1. **Use `pipx` as the recommended install method**, not raw Homebrew. `pipx install palimpsest` creates an isolated venv automatically.
2. If Homebrew is a must, use `resource` blocks in the formula to vendor all Python dependencies, and use `virtualenv_install_with_resources` helper.
3. Add a `brew test` block that actually runs `palimpsest --version` and `palimpsest init --dry-run`.
4. Consider shipping as a Homebrew **cask** that bundles a pre-built venv (like `aws-cli` does) instead of a formula that builds from source.
5. Pin minimum Python version in the formula and test against Homebrew's current Python.

**Phase:** Distribution phase. Do not attempt Homebrew until `pipx install` works reliably.

---

### Pitfall 5: Editor Detection Based on Stale Heuristics

**What goes wrong:** The installer detects editors by checking for config directories (`.cursor/`, `.claude/`, `.cline/`) or running `which cursor`. The detection returns false negatives (editor is installed but not detected) or false positives (config directory exists from a previous install but editor is not in use).

**Why it happens:** AI editors are young, fast-moving projects. Their config locations change between versions:
- Claude Code: Uses `~/.claude/` globally and `CLAUDE.md` per-project (but also `AGENTS.md` as of recent versions)
- Cursor: Uses `.cursor/` in project root, `.cursorrules` (deprecated) or `.cursor/rules/` (new)
- Cline: Uses `.clinerules` or `.cline/` depending on version
- Codex, Goose, Kilo: No stable config conventions yet (pre-1.0 or newly released)

Hardcoding paths means the detection breaks with every editor update.

**Consequences:** Wrong config installed for the wrong editor. User has Cursor but gets Cline config. Or detection finds nothing and skips config installation entirely, leaving the user with no AI agent setup.

**Warning signs:**
- Issue reports of "editor not detected" from users who clearly have the editor installed
- Detection logic has version-specific `if/elif` chains that grow with every release
- Config installed for editor X does not actually work (wrong format, wrong location)

**Prevention:**
1. **Detection should be multi-signal:** check binary in PATH, check config directories, check running processes, check recently modified config files. Require 2+ signals for HIGH confidence.
2. **Always allow manual override:** `palimpsest init --editors=cursor,claude-code` bypasses detection entirely.
3. **Maintain an editor registry** (JSON/YAML) mapping editor names to: binary names, config paths, config formats, config file names, and minimum supported versions. Update the registry independently of the core code.
4. **Fail open:** If detection is uncertain, ask the user interactively rather than guessing.
5. **Test detection in CI** with mock filesystem layouts for each editor.

**Phase:** Editor detection is a core feature. Design the registry format in the packaging phase, implement detection in the init-command phase.

---

## Moderate Pitfalls

### Pitfall 6: Self-Update Mechanism Creates Chicken-and-Egg Problem

**What goes wrong:** `palimpsest update` needs to update itself, but the running process is the thing being replaced. On Windows, you cannot overwrite a running executable. On Unix, the old binary stays in memory but the new one is on disk, leading to mixed state.

**Why it happens:** CLI self-update is fundamentally different from "update the project content." Conflating the two into one command creates a confusing UX and tricky implementation.

**Prevention:**
1. **Separate "update tool" from "update project."** `palimpsest self-update` upgrades the CLI itself (via pip/pipx). `palimpsest update` upgrades the project content files only.
2. For `self-update`, delegate to the package manager: `pipx upgrade palimpsest` or `brew upgrade palimpsest`. Do not implement custom binary replacement.
3. Check for new versions (PyPI JSON API) and **print a notice**, but do not auto-update without user consent.
4. Version-check should be non-blocking and cached (check at most once per day, store timestamp in `~/.palimpsest/last_check`).

**Phase:** Update-command phase. Content updates first, self-update as a follow-up.

### Pitfall 7: `pyproject.toml` Entry Points vs. Package Layout Mismatch

**What goes wrong:** The current `pyproject.toml` declares `pac = "scripts.core.preflight_check:main"` with `include = ["scripts*"]`. If the package is restructured to `palimpsest/` as the top-level package, this entry point breaks. If both `scripts/` and `palimpsest/` exist, import paths are ambiguous.

**Why it happens:** Renaming the package directory is a one-time breaking change that affects every import statement, every entry point, and every test fixture path. Half-done renames (where some code references `scripts.` and other code references `palimpsest.`) cause import errors that are maddening to debug.

**Prevention:**
1. **Do the rename in one atomic commit.** Use `sed` or an AST-rewriting tool to update all imports.
2. **Update `pyproject.toml` entry points, test paths, and CI config in the same commit.**
3. **Keep `scripts/` as a compatibility alias** only if there are external users of the current package. Since palimpsest is pre-1.0 with likely zero external consumers, just rename cleanly.
4. Run the full test suite immediately after the rename. If imports are broken, tests will catch it.

**Phase:** First step of the packaging phase, before anything else.

### Pitfall 8: Agent Config Template Variable Injection

**What goes wrong:** Agent config templates use `$PROJECT_ROOT` and other variables (visible in the current `.template` files). The installer needs to expand these variables to actual paths. If the expansion is naive string replacement, edge cases break: paths with spaces, paths with `$` characters, Windows backslashes, or nested variable references.

**Why it happens:** Template engines are deceptively simple. `str.replace("$PROJECT_ROOT", actual_path)` works until it does not.

**Prevention:**
1. Use Python's `string.Template` (standard library) with `safe_substitute()` -- it handles undefined variables gracefully.
2. Define a strict set of supported variables and document them. Do not allow arbitrary environment variable expansion.
3. Quote all path references in templates. Use forward slashes universally (even on Windows, most tools accept them).
4. Test with adversarial paths: spaces, unicode characters, deeply nested directories.

**Phase:** Init-command phase, when templates are first written to user projects.

### Pitfall 9: Heavy Dependencies for a Content-Distribution Tool

**What goes wrong:** The current `dependencies` list includes `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `requests`, and `python-dotenv`. These are needed for the automation scripts but not for the core use case of "install TPM methodology into my project." A user who just wants `palimpsest init` must install Google API client libraries.

**Why it happens:** The package conflates two personas: (1) users who want the AI-TPM blueprint, and (2) power users who run the Python automation scripts.

**Consequences:** Slow install, dependency conflicts with the user's project, and a bad first impression. `pip install palimpsest` pulling in 40+ transitive dependencies when the user just wants to copy some markdown files is hostile.

**Warning signs:**
- `pip install palimpsest` takes 30+ seconds
- Dependency version conflicts with user's existing project
- Users asking "why does a TPM tool need Google API libraries?"

**Prevention:**
1. **Core package has minimal dependencies:** `click` (or `typer`) for CLI, `importlib-resources` backport, and nothing else.
2. **Automation scripts are optional extras:** `pip install palimpsest[automation]` pulls in Google, Confluence, Slack dependencies.
3. Restructure `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   automation = ["google-api-python-client>=2.100.0", ...]
   ```
4. The CLI itself only needs to copy files and detect editors -- zero network dependencies.

**Phase:** Packaging phase. The dependency split must happen during package restructure, not retroactively.

### Pitfall 10: `.cursorrules` Deprecation and Config Format Drift

**What goes wrong:** Palimpsest ships `.cursorrules` files, but Cursor deprecated `.cursorrules` in favor of `.cursor/rules/*.mdc` files with frontmatter. Users on newer Cursor versions get no rules applied. Meanwhile, Cline changes from `.clinerules` to a different format, or Claude Code adds new conventions.

**Why it happens:** AI editors are pre-1.0 software iterating rapidly. Config formats are not stable APIs.

**Prevention:**
1. **Version-aware config generation.** The editor registry (Pitfall 5) should also track config format versions. If the user has Cursor 0.45+, generate `.cursor/rules/` files. If older, generate `.cursorrules`.
2. **Ship configs as templates, not static files.** Templates can be regenerated for new formats without a full palimpsest version bump.
3. **Document the "last verified" date** for each editor's config format in the registry.
4. **Decouple content from format.** Store the agent instructions as structured data (YAML or markdown with frontmatter), and generate editor-specific config files from that source. One source of truth, multiple output formats.

**Phase:** Editor support phase. Design the structured source format before generating any editor-specific configs.

---

## Minor Pitfalls

### Pitfall 11: Version String Duplication

**What goes wrong:** Version is defined in `pyproject.toml`, but the CLI also needs to report it via `palimpsest --version`, and the manifest needs to record it. Three places get out of sync.

**Prevention:** Use `importlib.metadata.version("palimpsest")` at runtime to read the version from the installed package metadata. Single source of truth in `pyproject.toml`, zero duplication.

**Phase:** Packaging phase.

### Pitfall 12: CLI Framework Bloat

**What goes wrong:** Starting with a heavyweight CLI framework (e.g., `cement`, `cleo`) adds complexity without benefit for what is fundamentally a 4-command tool (`init`, `update`, `status`, `self-update`).

**Prevention:** Use `click` -- it is the de facto standard, well-maintained, and right-sized. `typer` is fine too (it wraps click) if type hints are preferred. Do not use `argparse` for anything beyond trivial scripts -- subcommands, help formatting, and plugin architecture are painful.

**Phase:** Packaging phase.

### Pitfall 13: Git Operations During Init Race with User

**What goes wrong:** `palimpsest init` creates files and optionally runs `git add`. If the user is in the middle of a commit, rebase, or merge, the git operations fail or corrupt state.

**Prevention:**
1. Never run `git commit` on behalf of the user during init.
2. `git add` is acceptable but should be opt-in (`--git-add`), not default.
3. Print a message: "Run `git add .palimpsest/` to track these files."

**Phase:** Init-command phase.

### Pitfall 14: Cross-Platform Path Separator Assumptions

**What goes wrong:** Manifest file records paths with `/` on macOS but the code later compares paths using `os.sep` on Windows, failing to find matches. Or vice versa.

**Prevention:** Always normalize to forward slashes (`/`) in manifest files and internal path representations. Use `pathlib.PurePosixPath` for manifest entries and `Path` for filesystem operations.

**Phase:** Packaging phase (manifest design).

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Package restructure | Pitfall 1 (missing content), Pitfall 7 (import breakage) | Build wheel, install in clean venv, verify content files exist. Do the rename atomically. |
| CLI creation | Pitfall 9 (heavy deps), Pitfall 12 (framework bloat) | Minimal core dependencies, optional extras for automation scripts. Use click. |
| Init command | Pitfall 5 (editor detection), Pitfall 8 (template variables), Pitfall 13 (git race) | Multi-signal detection with manual override, `string.Template`, no auto-commit. |
| Update command | Pitfall 3 (user data loss), Pitfall 6 (self-update) | Manifest-based three-way merge, separate self-update from content update. |
| Editor configs | Pitfall 10 (config drift) | Structured source data, version-aware generation, editor registry. |
| Homebrew distribution | Pitfall 4 (Python + Homebrew conflict) | Ship pipx as primary, Homebrew as secondary with vendored venv. |
| Existing tech debt | CONCERNS.md items 1-7 | Do NOT fix tech debt during packaging. Wrap what exists. Fix auth duplication and sys.exit usage only when it blocks packaging (e.g., sys.exit inside importable functions). |

---

## Palimpsest-Specific Risks

These are not generic Python packaging pitfalls but specific to this project's situation.

### Risk: Current `scripts/` Layout Is Not a Proper Python Package

The existing code uses `scripts/` as the package root with sub-packages `scripts.core`, `scripts.content`, etc. This is an unusual layout. The name `scripts` is generic and likely to collide with other packages. The `[tool.setuptools.packages.find] include = ["scripts*"]` pattern will break if any dependency also has a `scripts` top-level package.

**Mitigation:** Rename `scripts/` to `palimpsest/` (the actual package name) during restructure.

### Risk: 30+ Environment Variables for Optional Features

The automation scripts require 30+ env vars for Google, Confluence, Slack, and Glean integrations. If these are not cleanly separated from the core CLI, users will see confusing errors about missing env vars when they just want to run `palimpsest init`.

**Mitigation:** Core CLI must have zero required environment variables. All env-var-dependent code lives behind the `[automation]` optional extra and is only imported when automation commands are invoked.

### Risk: Memory Bank Path Hardcoded to `.cursor/memory/`

The current setup.sh and all agent configs assume Memory Bank lives at `.cursor/memory/`. This is Cursor-specific. Claude Code users would expect a different location. Kilo/Goose/Codex users would have no idea what `.cursor/` is.

**Mitigation:** Memory Bank path should be configurable, defaulting to `.palimpsest/memory/` (editor-neutral). Editor configs should reference this neutral path. The init command should offer to symlink or alias from editor-specific locations.

---

## Sources

- Direct analysis of palimpsest source tree (`pyproject.toml`, `setup.sh`, `agents/` configs, `scripts/` layout)
- `.planning/PROJECT.md` project requirements and GSD prior art
- `.planning/codebase/CONCERNS.md` existing tech debt inventory
- Python packaging knowledge: setuptools `package_data` vs `include_package_data` behavior, `MANIFEST.in` scope (sdist only), `importlib.resources` API (training data -- well-established, stable knowledge since Python 3.9)
- Homebrew Python formula patterns (training data -- `virtualenv_install_with_resources` helper, Python version bump breakage)
- AI editor config conventions: Claude Code `CLAUDE.md`, Cursor `.cursorrules` deprecation to `.cursor/rules/`, Cline `.clinerules` format (training data, verified against repo's existing templates)

**Confidence notes:**
- Python packaging pitfalls (1, 2, 7, 9, 11): HIGH -- these are long-standing, thoroughly documented issues
- Update/merge strategy (3, 6): HIGH -- well-known pattern from Homebrew, npm, yeoman generators
- Homebrew distribution (4): MEDIUM -- specific Homebrew Python behavior may have changed since training cutoff
- Editor detection and config drift (5, 10): MEDIUM -- AI editors are moving fast; specific config paths may have changed since May 2025
- Palimpsest-specific risks: HIGH -- derived from direct code analysis
