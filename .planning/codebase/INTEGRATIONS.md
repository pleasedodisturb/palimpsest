# External Integrations

## Google Workspace APIs

### Google Drive API v3

- **Auth**: OAuth2 user credentials (`token.json`) or service account (`GOOGLE_SERVICE_ACCOUNT_FILE` / `GOOGLE_SERVICE_ACCOUNT_JSON`)
- **Scopes**: `drive.readonly` (sync), `drive.file` (uploads)
- **Operations**: List folder contents, download files, export Google Docs/Sheets/Slides, keyword search across all drives (including shared drives), file metadata read/write (`appProperties` for agent markers)
- **Files**:
  - `scripts/core/service_clients.py` -- `get_google_drive_client()`
  - `scripts/sync/gdrive_sync.py` -- full sync, snapshot, keyword search
  - `scripts/content/upload_to_docs.py` -- move files to folders, set properties
  - `scripts/content/build_document_registry.py` -- folder listing, keyword search
  - `scripts/automation/read_agent_markers.py` -- read `pac_*` properties
  - `scripts/core/agent_marker.py` -- write `pac_*` appProperties

### Google Docs API v1

- **Auth**: OAuth2 (`token_docs.json`), scopes `drive.file` + `documents`
- **Operations**: Create documents, batchUpdate (insert text, apply styles, create tables), read document structure
- **Files**:
  - `scripts/content/upload_to_docs.py` -- full markdown-to-Docs conversion with formatting
  - `scripts/content/download_doc.py` -- Docs-to-markdown extraction preserving headings and inline styles

### Google Sheets API v4

- **Auth**: OAuth2 (`token_sheets.json`), scopes `spreadsheets` + `drive.file`
- **Operations**: Create sheets, update cell values, clear ranges, read spreadsheet metadata
- **Files**:
  - `scripts/publishing/create_members_sheet.py` -- team directory with per-channel and master views

### Google Calendar API v3

- **Auth**: OAuth2 (`token.json`), scope `calendar`
- **Operations**: List calendars, fetch events (with keyword filtering), create events (task time-blocking), save events to markdown
- **Files**:
  - `scripts/sync/calendar_sync.py` -- fetch, create, list, and export calendar events
  - `scripts/core/google_auth.py` -- tests Calendar API access

### Google Tasks API v1

- **Auth**: OAuth2 (`token.json`), scope `tasks`
- **Operations**: List task lists (tested during auth verification)
- **Files**:
  - `scripts/core/google_auth.py` -- tests Tasks API access

### Google People API v1

- **Auth**: OAuth2, scopes `userinfo.profile`, `contacts.readonly`, `directory.readonly`
- **Operations**: Get user profile, list contacts, list directory people
- **Files**:
  - `scripts/core/google_auth.py` -- tests People/Contacts/Directory API access

### Gmail API v1

- **Auth**: OAuth2 (`token.json`), scope `gmail.modify`
- **Operations**: Get user profile (tested during auth verification)
- **Files**:
  - `scripts/core/google_auth.py` -- tests Gmail API access

### Google OAuth Flow

- **Mechanism**: `InstalledAppFlow.from_client_secrets_file()` with `run_local_server(port=0)`
- **Credentials file**: `credentials.json` (OAuth2 Desktop client, from Google Cloud Console)
- **Token refresh**: Automatic via `google.auth.transport.requests.Request` when tokens expire
- **Token persistence**: JSON files written atomically via temp file + `shutil.move()`
- **Files**:
  - `scripts/core/google_auth.py` -- unified OAuth flow for all Google scopes
  - `scripts/core/preflight_check.py` -- `attempt_google_token()` for auto-fix

## Atlassian APIs

### Confluence REST API (v1)

- **Auth**: HTTP Basic Auth (`ATLASSIAN_EMAIL` + `ATLASSIAN_API_TOKEN`)
- **Base URL**: `https://{ATLASSIAN_DOMAIN}/wiki/rest/api/`
- **Operations**:
  - Get page content (`content/{pageId}`)
  - Search with CQL (`content/search`)
  - List pages in space
  - Update page content (XHTML storage format)
  - Get/set/create content properties (`pac.agent_marker`)
  - User identity check (`user/current`)
- **Files**:
  - `scripts/core/service_clients.py` -- `AtlassianClient` with full CRUD
  - `scripts/content/upload_to_confluence.py` -- markdown-to-Confluence XHTML conversion, page creation
  - `scripts/publishing/push_confluence_news.py` -- daily updates page with rolling archive
  - `scripts/publishing/push_confluence_weekly.py` -- weekly summary with CW panels and archival
  - `scripts/sync/scheduled_sync.py` -- space structure sync to `CONTEXT_INDEX.md`
  - `scripts/core/preflight_check.py` -- connectivity check
  - `scripts/core/agent_marker.py` -- marker via content properties
  - `scripts/automation/read_agent_markers.py` -- read `pac.agent_marker` property

### Jira REST API (v3)

- **Auth**: HTTP Basic Auth (same Atlassian credentials)
- **Base URL**: `https://{ATLASSIAN_DOMAIN}/rest/api/3/`
- **Operations**:
  - Get issue (`issue/{issueKey}`)
  - Search issues with JQL (`search`)
  - Identity check (`myself`)
  - Search for issues with attachments
- **Files**:
  - `scripts/core/service_clients.py` -- `AtlassianClient.get_jira_issue()`, `search_jira()`
  - `scripts/publishing/draft_jira_tickets.py` -- generates Jira API payloads (does not submit)
  - `scripts/content/build_document_registry.py` -- collects Jira attachment metadata
  - `scripts/core/preflight_check.py` -- connectivity check

### Markdown to Confluence Conversion

- Custom converter in `scripts/content/upload_to_confluence.py`
- Supports: headings, bold, italic, inline code, links, tables, bullet/numbered lists, blockquotes, checkboxes, code blocks (with `ac:structured-macro` for code)
- Output: Confluence XHTML storage format

## Slack Web API

- **Auth**: Bot token via `SLACK_BOT_TOKEN` (Bearer auth)
- **Base URL**: `https://slack.com/api/`
- **Operations**:
  - `auth.test` -- token validation
  - `users.info` -- get user by ID
  - `users.lookupByEmail` -- find user by email
  - `conversations.list` -- list channels
  - `conversations.history` -- channel message history
  - `conversations.replies` -- thread replies
  - `chat.postMessage` -- post messages
- **Files**:
  - `scripts/core/service_clients.py` -- `SlackClient` class
  - `scripts/core/preflight_check.py` -- connectivity check

## Glean Search API

- **Auth**: Bearer token via `GLEAN_API_TOKEN`
- **Base URL**: Configurable via `GLEAN_API_URL` or `GLEAN_INSTANCE` (resolves to `https://{instance}-be.glean.com/rest/api/v1`)
- **Operations**:
  - `search` -- full-text search with filters (app, workspace, channel, owner, date ranges, doc type, dynamic filters)
  - `people` -- look up person by email
  - `documents/{id}` -- get document by ID
- **Query builder**: Constructs filter strings with app-specific logic (e.g., Slack workspace defaults, domain filtering, channel key overrides)
- **Files**:
  - `scripts/core/service_clients.py` -- `GleanClient` with `search()`, `search_slack()`, `get_person()`, `get_document()`
  - `scripts/core/preflight_check.py` -- connectivity check via smoke test query

## GitHub API v3

- **Auth**: Personal access token via `GITHUB_TOKEN`
- **Base URL**: `https://api.github.com/`
- **Operations**:
  - `repos/{owner}/{repo}` -- get repository info
  - `repos/{owner}/{repo}/issues` -- list issues
  - `user` -- get authenticated user
- **Files**:
  - `scripts/core/service_clients.py` -- `GitHubClient` class
- **Also**: `gh` CLI used for GitHub operations (per CLAUDE.md conventions)

## MCP (Model Context Protocol)

- **Configured via**: `.cursor/mcp.json` (generated by `setup.sh`)
- **Optional servers**:
  - Glean MCP: `npx -y @anthropic/mcp-glean` with `GLEAN_API_TOKEN` + `GLEAN_INSTANCE`
  - GitHub MCP: `npx -y @anthropic/mcp-github` with `GITHUB_TOKEN`
- **Files**:
  - `setup.sh` -- generates MCP config based on `--with-glean` / `--with-github` flags

## System-Level Integrations

### Git

- **Operations**: status, add, commit, push, diff, rev-parse
- Used by `scripts/automation/auto_commit_runner.py` and `scripts/sync/scheduled_sync.py`
- Auto-commit with configurable interval, allowlist/denylist patterns

### Clipboard (macOS / Linux)

- **macOS**: `pbpaste` for reading clipboard
- **Linux**: `xclip -selection clipboard -o` as fallback
- **macOS notifications**: `osascript -e 'display notification ...'`
- **Files**:
  - `scripts/automation/clipboard_watcher.py` -- continuous polling watcher
  - `scripts/automation/save_clipboard.py` -- one-shot capture

## Authentication Summary

| Service | Auth Method | Credential Source |
|---------|-------------|-------------------|
| Google APIs | OAuth2 user credentials | `token.json`, `token_docs.json`, `token_sheets.json` via `credentials.json` |
| Google APIs (alt) | Service account | `GOOGLE_SERVICE_ACCOUNT_FILE` or `GOOGLE_SERVICE_ACCOUNT_JSON` |
| Confluence + Jira | HTTP Basic Auth | `ATLASSIAN_EMAIL` + `ATLASSIAN_API_TOKEN` |
| Slack | Bearer token | `SLACK_BOT_TOKEN` |
| Glean | Bearer token | `GLEAN_API_TOKEN` |
| GitHub | Personal access token | `GITHUB_TOKEN` |

## Safety Mechanisms

### Write Guards

- `scripts/core/google_write_guard.py` -- requires `ALLOW_GOOGLE_WRITE=1` and optional `GOOGLE_WRITE_ALLOWLIST` (comma-separated target IDs)
- `scripts/content/upload_to_docs.py` -- requires `PAC_WRITE_GUARD=1`
- All publishing scripts support `--dry-run` to preview without writing

### Agent Markers (Provenance Tracking)

- Invisible metadata attached to Google Drive files (`appProperties`) and Confluence pages (`pac.agent_marker` content property)
- Fields: `marker_version`, `uid`, `timestamp_utc`, `action`, `source`, `agent`, `user`
- Tracks both creation and last-update metadata
- Configurable via `PAC_AGENT`, `ENABLE_AGENT_MARKERS`, `MARKER_DEBUG`
- **Files**:
  - `scripts/core/agent_marker.py` -- build/write markers
  - `scripts/automation/read_agent_markers.py` -- read markers from Drive or Confluence

### Preflight Checks

- `scripts/core/preflight_check.py` -- validates all service credentials before operations
- `--attempt-fix` flag can auto-symlink `.env` files and trigger OAuth flows
- `--nonfatal` flag for optional service checks (exit 0 on failure)

## Pipeline Architecture

### Scheduled Sync (`scripts/sync/scheduled_sync.py`)

Three-phase pipeline: Gather (Drive sync, link extraction, registry build) -> Push (Confluence page updates) -> Git (stage, commit, push). Supports `--dry-run`, `--no-push`, `--skip-drive`, `--skip-links`, `--full-update`.

### Daily Update Runner (`scripts/automation/daily_update_runner.py`)

Two modes:
- **Daily**: Preflight -> Drive sync -> Calendar sync -> Registry build -> Link extraction -> Confluence news -> Weekly update -> Auto-commit (8 steps)
- **Hourly**: Drive sync -> Auto-commit (2 steps)

Tracks run state in `.run_state.json` (last 50 runs), optional archive log in markdown.

## Databases

None. All state is stored in:
- JSON files (manifests, indexes, run state, config)
- Markdown files (registries, reports, digests)
- Git history
- External service APIs (Google Drive properties, Confluence page properties)
