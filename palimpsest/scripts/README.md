# Palimpsest Scripts

Automation toolkit for the PAC methodology. Config-driven, no hardcoded project data.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install google-api-python-client google-auth-oauthlib requests pypdf pytest
```

Copy `examples/.env.example` to `.env` and fill in your credentials.

## Package Structure

```
scripts/
  content/          — Document transformation and registry
  automation/       — Runners, watchers, commit automation
  publishing/       — Confluence, Sheets, Jira output
  sync/             — External data sync (Google Drive, Calendar)
  core/             — Shared utilities and preflight checks
  tests/            — pytest test suite
  examples/         — Example configs and env template
```

## Quick Reference

### Content

| Script | Purpose | Usage |
|--------|---------|-------|
| `upload_to_docs.py` | Markdown to Google Docs | `python content/upload_to_docs.py file.md [title] [--shared]` |
| `upload_to_confluence.py` | Markdown to Confluence page | `python content/upload_to_confluence.py SPACE file.md "Title" [parent_id]` |
| `download_doc.py` | Google Doc to markdown | `python content/download_doc.py <url_or_id> [output]` |
| `build_document_registry.py` | Multi-source doc registry | `python content/build_document_registry.py --config cfg.json --output out.md` |
| `link_extractor.py` | Extract/categorize links | `python content/link_extractor.py <directory> [--output-dir DIR]` |

### Automation

| Script | Purpose | Usage |
|--------|---------|-------|
| `auto_commit_runner.py` | Scheduled git commits | `python automation/auto_commit_runner.py [--once] [--config cfg.json]` |
| `daily_update_runner.py` | Pipeline orchestrator | `python automation/daily_update_runner.py --mode daily\|hourly` |
| `clipboard_watcher.py` | Watch and save clipboard | `python automation/clipboard_watcher.py [--output-dir DIR]` |
| `save_clipboard.py` | One-shot clipboard save | `python automation/save_clipboard.py [output_dir]` |
| `read_agent_markers.py` | Read PAC markers | `python automation/read_agent_markers.py <url_or_id>` |

### Publishing

| Script | Purpose | Usage |
|--------|---------|-------|
| `push_confluence_news.py` | Daily Confluence updates | `python publishing/push_confluence_news.py [--dry-run]` |
| `push_confluence_weekly.py` | Weekly Confluence summary | `python publishing/push_confluence_weekly.py [--dry-run]` |
| `create_members_sheet.py` | Google Sheets member dir | `python publishing/create_members_sheet.py --spreadsheet-id ID` |
| `draft_jira_tickets.py` | Draft Jira tickets | `python publishing/draft_jira_tickets.py [input.json]` |

## Testing

```bash
python -m pytest scripts/tests/ -v
```

## Environment Variables

See `examples/.env.example` for the full list grouped by service.

## Write Guard

Google Docs/Sheets writes are blocked by default. Set `PAC_WRITE_GUARD=1` to enable.
