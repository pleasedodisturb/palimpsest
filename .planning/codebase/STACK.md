# Technology Stack

## Language and Runtime

- **Python** 3.10+ (supports 3.10, 3.11, 3.12; local venv runs 3.14)
- **Bash** for project scaffolding (`setup.sh`)
- **Markdown** as the primary content format across docs, templates, playbooks, and showcase

## Build System and Packaging

- **setuptools** >= 68.0 + **wheel** as the build backend
- Configured in `pyproject.toml` at the project root
- Package name: `palimpsest`, version `0.1.0`
- Editable install: `pip install -e .`
- Single CLI entry point: `pac` maps to `scripts.core.preflight_check:main`

### Key files

- `pyproject.toml` -- build config, dependencies, test config
- `setup.sh` -- Bash scaffolding script to generate new project instances

## Dependencies

### Core (required)

| Package | Version | Purpose |
|---------|---------|---------|
| `google-api-python-client` | >= 2.100.0 | Google Drive, Docs, Sheets, Calendar, Tasks, People APIs |
| `google-auth-httplib2` | >= 0.1.1 | HTTP transport for Google auth |
| `google-auth-oauthlib` | >= 1.1.0 | OAuth2 flow for Google APIs |
| `requests` | >= 2.31.0 | HTTP client for Atlassian, Slack, Glean, GitHub APIs |
| `python-dotenv` | >= 1.0.0 | Environment variable loading from `.env` files |

### Optional

| Package | Version | Purpose |
|---------|---------|---------|
| `PyPDF2` | >= 3.0.0 | PDF link extraction (install group: `pdf`) |
| `pypdf` | -- | Alternative PDF reader, tried as fallback in `scripts/content/link_extractor.py` |

### Dev

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >= 7.4.0 | Test runner |
| `pytest-cov` | >= 4.0.0 | Coverage reporting |

## Standard Library Usage (notable)

- `subprocess` -- git operations, clipboard access (`pbpaste`/`xclip`), macOS notifications (`osascript`)
- `argparse` -- CLI for every script
- `pathlib` -- all path handling
- `json` -- config files, API payloads, state persistence
- `re` -- markdown-to-HTML conversion, Confluence content manipulation
- `hashlib` -- MD5 for clipboard change detection and URL deduplication
- `fnmatch` -- glob-based allowlist/denylist in auto-commit

## Configuration Strategy

All configuration is driven by environment variables and JSON config files. Zero hardcoded credentials or IDs.

### Environment variables (sampled across all scripts)

| Variable | Used by | Purpose |
|----------|---------|---------|
| `ATLASSIAN_DOMAIN` | service_clients, preflight, confluence scripts | Atlassian instance domain |
| `ATLASSIAN_EMAIL` | service_clients, preflight, confluence scripts | Atlassian account email |
| `ATLASSIAN_API_TOKEN` | service_clients, preflight, confluence scripts | Atlassian API token |
| `CONFLUENCE_SPACE_KEY` | scheduled_sync | Confluence space for sync |
| `SLACK_BOT_TOKEN` | service_clients, preflight | Slack bot auth token |
| `GLEAN_API_TOKEN` | service_clients, preflight | Glean search API token |
| `GLEAN_API_URL` / `GLEAN_INSTANCE` | service_clients, preflight | Glean API endpoint |
| `GLEAN_WORKSPACE` / `GLEAN_SLACK_WORKSPACE` | service_clients | Default Glean workspace |
| `GLEAN_SLACK_DOMAIN` | service_clients | Domain filter for Slack results |
| `GLEAN_SLACK_CHANNEL_FILTER` | service_clients | Channel filter key |
| `GITHUB_TOKEN` | service_clients | GitHub API token |
| `GDRIVE_FOLDER_ID` | gdrive_sync | Source Drive folder ID |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | gdrive_sync | Service account JSON path |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | gdrive_sync | Service account JSON string |
| `GOOGLE_TOKEN_FILE` | gdrive_sync, calendar_sync | OAuth token file path |
| `GOOGLE_OAUTH_CREDENTIALS` | gdrive_sync | OAuth credentials file path |
| `CALENDAR_ID` | calendar_sync | Primary calendar ID |
| `TASKS_CALENDAR_ID` | calendar_sync | Task time-blocking calendar |
| `CALENDAR_TIMEZONE` | calendar_sync | Timezone for events |
| `EVENT_PREFIX` | calendar_sync | Prefix for agent-created events |
| `PAC_CALENDAR_KEYWORDS` | calendar_sync | Keywords for event filtering |
| `PAC_CALENDAR_OUTPUT_DIR` | calendar_sync | Output dir for calendar markdown |
| `PAC_PROJECT_ROOT` | gdrive_sync, scheduled_sync | Project root override |
| `PAC_PYTHON` | scheduled_sync, daily_update_runner | Python binary override |
| `PAC_AGENT` | agent_marker | Agent name in markers |
| `ENABLE_AGENT_MARKERS` | agent_marker | Toggle markers on/off |
| `MARKER_DEBUG` | agent_marker | Debug output for markers |
| `ALLOW_GOOGLE_WRITE` | google_write_guard | Write permission gate |
| `GOOGLE_WRITE_ALLOWLIST` | google_write_guard | Allowed write target IDs |
| `PAC_WRITE_GUARD` | upload_to_docs | Write guard for Docs uploads |
| `PAC_DOCS_FOLDER` | upload_to_docs | Default upload folder |
| `JIRA_PROJECT_KEY` | draft_jira_tickets | Jira project for ticket drafts |
| `PAGES_CONFIG` | push_confluence_news, push_confluence_weekly | Path to pages.json config |
| `PAC_CONFLUENCE_UPDATES_PAGE_ID` | push_confluence_news | Updates page ID fallback |
| `PAC_CONFLUENCE_WEEKLY_PAGE_ID` | push_confluence_weekly | Weekly page ID fallback |
| `PAC_ARCHIVE_LOG` | daily_update_runner | Archive log file path |
| `TPM_BUDDY_ENV_PATH` | preflight_check | Fallback .env path |
| `PROJECT_ROOT` | preflight_check | Fallback project root for .env |

### JSON config files

| File | Used by | Purpose |
|------|---------|---------|
| `pages.json` | push_confluence_news, push_confluence_weekly | Confluence page IDs |
| `members_config.json` | create_members_sheet | Team member and channel data |
| `registry_config.json` | build_document_registry | Multi-source registry config |
| `auto_commit_config.json` | auto_commit_runner | Commit interval, allowlist/denylist |
| `document_registry_config.json` | gdrive_sync | Drive search keywords, settings |
| `ticket_candidates.json` | draft_jira_tickets | Jira ticket input data |
| `jira_metrics.json` | push_confluence_news | Cached Jira metrics |
| `weekly_context.json` | push_confluence_weekly | Weekly summary context |

### Token files (all gitignored)

| File | Purpose |
|------|---------|
| `token.json` | Google Drive read-only OAuth token |
| `token_docs.json` | Google Docs/Drive write OAuth token |
| `token_sheets.json` | Google Sheets write OAuth token |
| `credentials.json` | Google OAuth client secrets |

## CI/CD

- **GitHub Actions** with workflow at `.github/workflows/test.yml`
- Matrix build: Python 3.10, 3.11, 3.12 on `ubuntu-latest`
- Triggers: push to `main`, PRs to `main`
- Steps: checkout, setup-python, `pip install -e ".[dev]"`, `pytest scripts/tests/ -v --tb=short`

## Testing

- **pytest** with test discovery in `scripts/tests/`
- `pythonpath = ["scripts"]` in `pyproject.toml`
- 13 test files covering: agent_marker, link_extractor, gdrive_sync, build_document_registry, draft_jira_tickets, confluence_news, confluence_weekly, members_sheet, read_agent_markers, google_write_guard, download_doc, upload_to_docs, upload_to_confluence

## Project Structure

```
scripts/
  __init__.py
  core/           -- Auth, preflight, write guards, agent markers, service clients
  sync/           -- Google Drive sync, calendar sync, scheduled sync orchestrator
  content/        -- Document registry builder, link extractor, upload/download converters
  publishing/     -- Confluence news/weekly push, Jira ticket drafting, Sheets member directory
  automation/     -- Auto-commit, clipboard watcher/saver, daily/hourly pipeline runner
  tests/          -- pytest test suite
```

## Script Categories

| Category | Scripts | Purpose |
|----------|---------|---------|
| Core (`scripts/core/`) | `google_auth.py`, `preflight_check.py`, `service_clients.py`, `google_write_guard.py`, `agent_marker.py` | Authentication, service health checks, write safety, provenance tracking |
| Sync (`scripts/sync/`) | `gdrive_sync.py`, `calendar_sync.py`, `scheduled_sync.py` | Data gathering from Google Drive and Calendar, orchestrated sync pipeline |
| Content (`scripts/content/`) | `build_document_registry.py`, `link_extractor.py`, `upload_to_confluence.py`, `upload_to_docs.py`, `download_doc.py` | Document indexing, link extraction, format conversion, bidirectional sync |
| Publishing (`scripts/publishing/`) | `push_confluence_news.py`, `push_confluence_weekly.py`, `create_members_sheet.py`, `draft_jira_tickets.py` | Automated Confluence updates, team directory, Jira ticket generation |
| Automation (`scripts/automation/`) | `auto_commit_runner.py`, `clipboard_watcher.py`, `save_clipboard.py`, `daily_update_runner.py`, `read_agent_markers.py` | Git automation, clipboard capture, pipeline orchestration, marker auditing |
