# Architecture

## Pattern

Palimpsest follows a **content-as-code** pattern: program management artifacts (status docs, decisions, backlogs, digests) live as markdown files in a git repository. AI agents read this structured state to answer questions, draft updates, and automate workflows. External services (Google Drive, Confluence, Jira, Slack, Glean) are integrated through a Python automation toolkit that syncs, transforms, and publishes content bidirectionally.

The architecture has no runtime server, no database, and no API of its own. It is a static repository structure plus a collection of scripts and agent configurations. Git is the persistence and audit layer.

## Layers

### Layer 1: Content Layer (Markdown + Git)

The foundational layer. All program state is expressed as markdown files committed to git. This gives:
- Version history for every decision and status change
- Diffable artifacts (who changed what, when)
- Branch/PR workflows for collaborative editing
- A format every AI agent can read natively

Key content types:
- `PROGRAM_OVERVIEW.md` -- full program state (the "source of truth")
- `DASHBOARD.md` -- quick status view for stakeholders
- `BACKLOG.md` -- TPM task list
- `docs/context/daily-digests/` -- sanitized daily summaries (public)
- `docs/context/transcripts/` -- meeting transcripts (gitignored, private)
- `docs/context/private-notes/` -- sensitive notes (gitignored, private)

### Layer 2: Agent Layer (AI Configurations)

Pre-built configuration templates that teach AI editors how to interact with the content layer. Three supported agents, all sharing a common protocol:

- **Cursor** -- `.cursorrules` template + skills directory
- **Claude Code** -- `CLAUDE.md` + `AGENTS.md` templates
- **Cline** -- Five modal rulesets (architect/code/debug/test/ask)

The **Memory Bank** protocol (`agents/memory-bank/`) is the shared state mechanism across agents. It consists of seven markdown files (sessionLog, activeContext, progress, decisionLog, systemPatterns, productContext, projectPreferences) that agents read at session start and update during work. This prevents blank-slate sessions.

### Layer 3: Automation Layer (Python Scripts)

A pip-installable Python package (`scripts/`) organized into five functional groups:

| Group | Purpose | Key Scripts |
|-------|---------|-------------|
| `core/` | Auth, service clients, markers, guards | `service_clients.py`, `preflight_check.py`, `google_auth.py`, `agent_marker.py`, `google_write_guard.py` |
| `sync/` | Pull data from external services | `gdrive_sync.py`, `calendar_sync.py`, `scheduled_sync.py` |
| `content/` | Transform and index documents | `upload_to_docs.py`, `upload_to_confluence.py`, `download_doc.py`, `build_document_registry.py`, `link_extractor.py` |
| `automation/` | Scheduled runners and watchers | `daily_update_runner.py`, `auto_commit_runner.py`, `clipboard_watcher.py`, `save_clipboard.py`, `read_agent_markers.py` |
| `publishing/` | Push content to stakeholder platforms | `push_confluence_news.py`, `push_confluence_weekly.py`, `create_members_sheet.py`, `draft_jira_tickets.py` |

### Layer 4: Project Scaffolding

`setup.sh` generates a new project from `project-template/`, creating the directory structure, .gitignore, MCP configuration, Memory Bank files, and initial git commit. The generated project is independent of the Palimpsest repository itself.

## Data Flow

```
External Services                 Local Repository              Stakeholder Outputs
==================               ==================            ===================

Google Drive -----> gdrive_sync.py -----> docs/knowledge-base/
                                              |
Google Calendar --> calendar_sync.py ---> docs/context/         upload_to_confluence.py ---> Confluence
                                              |                 push_confluence_news.py --->
Clipboard --------> clipboard_watcher.py -> docs/context/       push_confluence_weekly.py ->
                                              |
                                    build_document_registry.py   upload_to_docs.py ---------> Google Docs
                                    link_extractor.py
                                              |                  draft_jira_tickets.py -----> Jira
                                    auto_commit_runner.py
                                    daily_update_runner.py       create_members_sheet.py ---> Google Sheets
                                              |
                                         git commit
```

The flow is: **Gather** (sync from external sources into markdown) -> **Process** (index, extract, register) -> **Publish** (push to stakeholder platforms) -> **Commit** (persist to git).

This is orchestrated by two runners:
- `daily_update_runner.py` -- full pipeline: preflight, sync, build, publish, commit
- `scheduled_sync.py` -- three-phase runner (Gather, Push, Git) with granular skip flags

## Key Abstractions

### Service Clients (`scripts/core/service_clients.py`)

A unified interface to five external services: Google Drive, Atlassian (Confluence + Jira), Slack, Glean, GitHub. Each client:
- Is a class with typed methods for common operations
- Gracefully returns `None` when credentials are missing
- Reports availability through a global `ServiceStatus` singleton
- Gets all configuration from environment variables (zero hardcoded values)

Factory functions (`get_google_drive_client()`, `get_atlassian_client()`, etc.) return the client or `None`.

### Agent Markers (`scripts/core/agent_marker.py`)

A provenance tracking system. When scripts create or modify documents in Drive or Confluence, they attach invisible metadata (app properties / content properties) using the `pac` namespace. This lets agents and scripts distinguish human-authored content from machine-generated content.

Markers include: version, UID, timestamp, action, source, agent name, user.

### Write Guard (`scripts/core/google_write_guard.py`)

A safety mechanism that blocks all Google Drive/Docs write operations by default. Must be explicitly opted-in via `ALLOW_GOOGLE_WRITE=1`. Supports an allowlist of target IDs for fine-grained control. Calls `sys.exit(1)` when writes are not permitted.

A second write guard exists in `upload_to_docs.py` using `PAC_WRITE_GUARD=1`.

### Markdown-to-Platform Converters

Two independent converters handle the markdown -> platform format transformation:
- `upload_to_confluence.py` -- markdown to Confluence storage format (XHTML) with custom regex-based parser
- `upload_to_docs.py` -- markdown to Google Docs API batchUpdate requests, handling inline formatting, tables, code blocks, and lists

Both are standalone scripts with their own CLI entry points.

## Entry Points

| Entry Point | Type | Purpose |
|-------------|------|---------|
| `setup.sh` | Bash | Bootstrap a new project from template |
| `pac` (CLI) | Python console_script | Preflight check (`scripts.core.preflight_check:main`) |
| `scripts/core/preflight_check.py` | Python | Verify all service credentials |
| `scripts/core/google_auth.py` | Python | Run OAuth flow for Google APIs |
| `scripts/sync/scheduled_sync.py` | Python | Full three-phase sync pipeline |
| `scripts/automation/daily_update_runner.py` | Python | Daily/hourly orchestrated pipeline |
| `scripts/automation/auto_commit_runner.py` | Python | Scheduled git auto-commit loop |
| Individual scripts in `content/`, `publishing/` | Python | Standalone operations (upload, download, extract, draft) |

## Configuration Model

All configuration is environment-variable driven. No config files are required (though JSON configs are supported for some scripts like `auto_commit_runner.py` and `build_document_registry.py`).

Key environment variable groups:
- `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`, `ATLASSIAN_DOMAIN` -- Confluence/Jira
- `SLACK_BOT_TOKEN` -- Slack
- `GLEAN_API_TOKEN`, `GLEAN_API_URL`, `GLEAN_INSTANCE` -- Glean search
- `GITHUB_TOKEN` -- GitHub
- `GDRIVE_FOLDER_ID` -- Google Drive sync target
- `ALLOW_GOOGLE_WRITE`, `GOOGLE_WRITE_ALLOWLIST` -- Write safety
- `PAC_WRITE_GUARD` -- Docs upload safety
- `PAC_PROJECT_ROOT` -- Project root override
- `PAC_PYTHON` -- Python binary override
- `PAC_AGENT` -- Agent name for markers
- `ENABLE_AGENT_MARKERS` -- Toggle marker system

## Testing

Tests live in `scripts/tests/` and run via pytest. The CI pipeline (`.github/workflows/test.yml`) runs on Python 3.10, 3.11, and 3.12 against `ubuntu-latest` on push/PR to main. Tests mock external services and validate script logic in isolation.

## Privacy Model

The `.gitignore` enforces a clear public/private boundary:
- **Private (never committed):** `docs/context/transcripts/`, `docs/context/private-notes/`, `.env`, `token*.json`, `credentials.json`
- **Public (committed):** `docs/context/daily-digests/`, all program state documents, templates, agent configs

This lets TPMs keep sensitive context (meeting recordings, 1:1 notes) locally available to AI agents without ever pushing it to a remote.
