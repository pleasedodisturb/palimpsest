# Feature Landscape

**Domain:** Python CLI tool for distributing AI editor configurations + TPM methodology
**Researched:** 2026-03-17
**Overall confidence:** MEDIUM (training data, pattern analysis from comparable tools; no live web verification available)

## Table Stakes

Features users expect from any installable CLI tool in 2025-2026. Missing any of these and users abandon before getting value.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Single-command install** (`pip install palimpsest` / `pipx install palimpsest` / `uv tool install palimpsest`) | Every modern CLI tool is one command away. Cloning a repo and running setup.sh is 2015-era friction. | Medium | Requires restructuring pyproject.toml to include all content as package_data. Current setup only ships scripts/. |
| **`palimpsest init` scaffolding command** | Users expect `init` to create project structure in current directory. Replaces setup.sh. cookiecutter/copier established this pattern; django-admin startproject, cargo init, npm init all do it. | Medium | Must generate directory structure, templates, agent configs, .gitignore, memory bank. Interactive prompts for program name/context. |
| **`--help` on every command and subcommand** | Click/Typer/argparse standard. Users try `--help` first. No help text = abandoned tool. | Low | Use click or typer; both generate help automatically from docstrings. |
| **Semantic versioning with `palimpsest --version`** | Users need to know what they have installed, for bug reports and update decisions. | Low | Already have 0.1.0 in pyproject.toml. Just wire it to the CLI. |
| **`palimpsest update` command** | Once installed, users must be able to pull new methodology/templates without reinstalling. This is the core promise: "updatable AI-TPM." | High | Hardest table-stakes feature. Must diff installed content vs package content, detect user modifications, merge or warn. GSD's file manifest pattern is the right approach. |
| **Cross-platform support (macOS + Linux)** | Python devs and TPMs use both. Windows is nice-to-have but not day-one. | Low | Python handles this naturally. Watch for path separators and shell assumptions in setup.sh replacement. |
| **Editor auto-detection** | The tool serves 6+ AI editors. Users should not manually specify which editor they use. Detect `.cursor/`, `.claude/`, `.cline/`, etc. in the project or on the system. | Medium | File-system detection is straightforward. The mapping from "detected editor" to "correct config format" is the real work -- each editor has its own rules file format. |
| **Idempotent operations** | Running `init` or `update` twice must not corrupt the project. Users will accidentally double-run commands. | Medium | File manifest tracking (what was installed, what version, checksums) prevents duplicate writes and enables safe re-runs. |
| **Meaningful error messages** | When something fails (wrong Python version, missing directory, permission error), the message must say what went wrong and how to fix it. No tracebacks for user errors. | Low | click/typer exception handling. Wrap known failure modes with rich error messages. |
| **Dry-run mode** | `--dry-run` on destructive/write operations. Users want to see what will happen before it happens. Existing convention in the scripts. | Low | Already a pattern in the codebase. Extend to all CLI commands. |
| **Colored terminal output** | setup.sh already uses colors. Every modern CLI (gh, uv, ruff, poetry) uses colored output. Plain text feels broken. | Low | rich library or click's built-in styling. |

## Differentiators

Features that set palimpsest apart from "just another CLI scaffolding tool." These create the unique value of "one command, full AI-TPM."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Multi-editor agent config installation** | No other tool installs AI agent configurations for 6 editors simultaneously. This is the core differentiator. Detect Claude Code, Cursor, Cline, Codex, Goose, Kilo and install the correct rules format for each. | High | Each editor has different config locations, file formats, and rule semantics. Cursor uses .cursorrules, Claude Code uses CLAUDE.md, Cline uses .clinerules, Codex has .codex/, etc. Must maintain a registry of editor config specs. |
| **Memory Bank initialization across editors** | The 7-file shared memory bank protocol is unique to palimpsest. Auto-initializing it for whichever editor is detected provides instant AI context persistence. | Medium | The memory bank files are editor-agnostic markdown. The setup just needs to place them where each editor expects shared state. |
| **Interactive guided setup (post-init wizard)** | After scaffolding, walk the user through: program name, key stakeholders, timeline, which integrations to enable. Pre-fills templates with real data instead of [PLACEHOLDER]. | Medium | Use questionary or click prompts. Template variables with Jinja2 or simple string replacement. Significantly reduces time-to-first-value. |
| **Methodology docs shipped as browsable local reference** | `palimpsest docs` opens or lists the 10 methodology guides. Users get the full TPM playbook without visiting a website. Like `man` pages but for TPM methodology. | Low | Ship docs/ as package_data. CLI command to list, open (webbrowser module), or cat them. Unique because the content itself is the product. |
| **Template library with `palimpsest template <name>`** | Quick access to PRD, BRD, stakeholder update, go/no-go templates. Copy to clipboard or write to file. Like `gh` issue templates but for TPM documents. | Low | 7 templates already exist. CLI command to list and copy/output them. |
| **User-patch preservation during updates** | When `palimpsest update` runs, detect which files the user has modified and either skip them, show a diff, or create .palimpsest-backup copies. GSD does this with file manifests + checksums. | High | Store checksums of installed files in a manifest (.palimpsest/manifest.json). On update, compare current file checksum against original. If different, user modified it -- preserve their version and note what changed upstream. |
| **Selective editor targeting** | `palimpsest init --editors cursor,claude-code` to install configs only for specific editors, overriding auto-detection. Power users want control. | Low | Just a flag that filters the editor detection result. |
| **`palimpsest doctor` health check** | Validate the installation: are agent configs in the right places? Is the memory bank initialized? Are required Python packages available? Are env vars set for the automation scripts? | Medium | Extends the existing preflight_check.py concept. Useful for debugging "it doesn't work" reports. |
| **Homebrew formula distribution** | `brew install palimpsest` is the gold standard UX for CLI tools on macOS. Handles Python dependency management transparently. | Medium | Requires a homebrew tap repo and formula file. The formula must handle Python 3.10+ as a dependency. pipx/uv are alternatives but less discoverable for non-developers. |
| **Changelog between versions** | `palimpsest changelog` or automatic display after `palimpsest update` showing what changed. Users want to know what they are getting. | Low | Maintain CHANGELOG.md in the repo (keep-a-changelog format). CLI reads it and displays relevant section. |
| **Playbook quick-access** | `palimpsest playbook remote-onboarding` to quickly reference situation-specific guidance. Like a man page lookup for TPM scenarios. | Low | 4 playbooks exist. Same pattern as docs/template access. |

## Anti-Features

Features to explicitly NOT build. Each represents a common trap that would expand scope without proportional value.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **SaaS dashboard or web UI** | Out of scope per PROJECT.md. This is a local-first, open-source tool. A web UI would require hosting, auth, and ongoing maintenance for something that should be a CLI. | Keep it CLI. If users want a dashboard, DASHBOARD.md is a markdown file their AI editor renders. |
| **Custom AI model or LLM integration** | Palimpsest configures existing AI editors; it does not provide AI capabilities itself. Adding LLM API calls creates key management, cost, and reliability problems. | Ship agent configs that make existing editors smart about TPM. The editors bring the AI. |
| **MCP server (v1)** | Explicitly out of scope per PROJECT.md. Interesting but a separate project. An MCP server would need its own lifecycle, testing, and distribution story. | Defer to v2. The CLI + agent configs are the v1 product. |
| **Plugin/extension system** | Premature abstraction. With 6 editors and a methodology that is still evolving, adding a plugin API locks in interfaces before they are stable. | Ship opinionated defaults. Let users fork or submit PRs for customization. |
| **Auto-updating (background updates)** | Background auto-update is hostile UX for a tool that modifies project files. Users must consent to each update. Homebrew and pipx handle version management already. | Explicit `palimpsest update` command with preview of changes. |
| **Node.js/npx distribution** | The codebase is Python. Adding Node.js as a distribution channel doubles the packaging work for a tool whose automation scripts require Python anyway. | Python-native distribution (PyPI + pipx/uv + optional Homebrew). |
| **Windows support (v1)** | The existing scripts use macOS-specific features (osascript for notifications, clipboard_watcher). The target audience (AI-editor-using TPMs) is overwhelmingly macOS/Linux. | Ensure no hard crashes on Windows. Add a "Windows not yet supported" message. Prioritize for v2 based on demand. |
| **GUI installer** | CLI tools should not have GUI installers. The audience can run pip/pipx/brew. | Clear README installation instructions with copy-paste commands. |
| **Real-time sync between editors** | If a user has both Cursor and Claude Code open, syncing memory bank state in real time is a distributed systems problem. | Memory bank files are on disk. Editors read them when they need to. File-system-level consistency is sufficient. |
| **Automatic integration setup (OAuth flows, API key management)** | Setting up Google OAuth, Atlassian tokens, Slack webhooks -- this involves secrets management that varies wildly per organization. Automating it creates a security liability. | `palimpsest doctor` checks if integrations are configured. Documentation explains how to set up each one. |

## Feature Dependencies

```
palimpsest init -----> Editor auto-detection (init must know which editors to configure)
     |                      |
     v                      v
File manifest          Multi-editor config installation (detection feeds installation)
     |
     v
palimpsest update (manifest enables safe updates)
     |
     v
User-patch preservation (update needs manifest checksums to detect modifications)

palimpsest init -----> Interactive guided setup (wizard runs after scaffolding)
                            |
                            v
                       Template variable substitution (wizard answers fill templates)

palimpsest doctor ---> Editor auto-detection (reuses detection logic)
                  ---> File manifest (checks installed state)

palimpsest docs/template/playbook --- independent, can ship anytime

Homebrew formula --- requires stable PyPI release first
```

## MVP Recommendation

### Phase 1: Core CLI (must ship first)

1. **Single-command install** via PyPI (`pipx install palimpsest`)
2. **`palimpsest init`** replacing setup.sh, with editor auto-detection
3. **Multi-editor agent config installation** for at least Cursor + Claude Code + Cline
4. **`--help` / `--version`** on all commands
5. **Colored output and meaningful error messages**
6. **File manifest** (.palimpsest/manifest.json) tracking what was installed

### Phase 2: Update and Content Access

7. **`palimpsest update`** with user-patch preservation
8. **`palimpsest docs`** / **`palimpsest template`** / **`palimpsest playbook`** content access commands
9. **`palimpsest doctor`** health check
10. **Interactive guided setup wizard** (enhance init)

### Phase 3: Distribution Polish

11. **Homebrew formula**
12. **Changelog display on update**
13. **Additional editors** (Codex, Goose, Kilo)

### Defer

- **MCP server**: Separate project, not v1
- **Plugin system**: Wait until the editor config format stabilizes
- **Windows support**: Based on actual user demand
- **Real-time editor sync**: File-system consistency is enough

### Rationale

The ordering follows dependency chains: you cannot build `update` without the file manifest from `init`. You cannot ship Homebrew without a stable PyPI package. Editor detection feeds both `init` and `doctor`. The content access commands (docs/template/playbook) are independent and low-complexity, so they slot into Phase 2 as quick wins alongside the harder `update` command.

## Sources

- Project context: `.planning/PROJECT.md` (project requirements, GSD prior art analysis)
- Existing codebase analysis: `pyproject.toml`, `setup.sh`, `agents/` directory structure
- Technical debt: `.planning/codebase/CONCERNS.md`
- Comparable tools (training data, MEDIUM confidence): cookiecutter, copier, django-admin, cargo init, gh CLI, poetry, uv, GSD (Get Shit Done)
- Editor config format knowledge (training data, MEDIUM confidence): .cursorrules, CLAUDE.md, .clinerules formats -- should be verified against current editor documentation during implementation
