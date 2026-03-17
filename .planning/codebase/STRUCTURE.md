# Structure

## Directory Layout

```
palimpsest/
├── CLAUDE.md                           # Project instructions for Claude Code
├── README.md                           # Project overview and documentation
├── LICENSE                             # MIT license
├── pyproject.toml                      # Python package config (pip install -e .)
├── setup.sh                            # Project bootstrapper script
├── sonar-bugs.json                     # Static analysis results (untracked)
├── .gitignore
├── .github/
│   └── workflows/
│       └── test.yml                    # CI pipeline (pytest on 3.10/3.11/3.12)
├── docs/                               # Methodology guides (10 numbered docs)
│   ├── 01-problem-statement.md
│   ├── 02-the-solution.md
│   ├── 03-setup-guide.md
│   ├── 04-use-cases.md
│   ├── 05-why-ai-despite-hallucinations.md
│   ├── 06-faq.md
│   ├── 07-future-vision.md
│   ├── 08-known-issues.md
│   ├── 09-personal-ai-assistant.md
│   ├── 10-privacy-model.md
│   └── roadmap.md
├── case-study/
│   └── wolt-crm-migration.md           # Battle-tested case study narrative
├── templates/                           # Reusable TPM document templates
│   ├── README.md
│   ├── prd.md                          # Product requirements document
│   ├── brd.md                          # Business requirements document
│   ├── stakeholder-update.md
│   ├── first-weekly-update.md
│   ├── go-no-go-framework.md
│   ├── document-governance.md
│   └── async-reporting-playbook.md
├── agents/                              # AI agent configurations
│   ├── README.md
│   ├── formatting-standards.md         # Markdown and writing standards
│   ├── claude-code/
│   │   ├── CLAUDE.md.template
│   │   └── AGENTS.md.template
│   ├── cursor/
│   │   ├── cursorrules.template
│   │   └── skills/
│   │       └── auto-commit.md
│   ├── cline/
│   │   ├── clinerules-architect.template
│   │   ├── clinerules-code.template
│   │   ├── clinerules-debug.template
│   │   ├── clinerules-test.template
│   │   └── clinerules-ask.template
│   └── memory-bank/
│       ├── README.md                   # Memory Bank specification
│       ├── memory-bank.mdc            # Cursor rule file
│       └── example/                    # Starter templates
│           ├── sessionLog.md
│           ├── activeContext.md
│           ├── progress.md
│           ├── decisionLog.md
│           ├── systemPatterns.md
│           ├── productContext.md
│           └── projectPreferences.md
├── scripts/                             # Python automation toolkit
│   ├── __init__.py
│   ├── README.md
│   ├── core/                           # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── service_clients.py          # Unified client for 5 external services
│   │   ├── preflight_check.py          # Service connectivity validator (pac CLI)
│   │   ├── google_auth.py              # Google OAuth flow runner
│   │   ├── agent_marker.py             # Provenance tracking for Drive/Confluence
│   │   └── google_write_guard.py       # Write-operation safety gate
│   ├── sync/                           # External data ingestion
│   │   ├── __init__.py
│   │   ├── gdrive_sync.py             # Google Drive folder sync + search
│   │   ├── calendar_sync.py           # Google Calendar event sync
│   │   └── scheduled_sync.py          # Three-phase orchestrated sync runner
│   ├── content/                        # Document transformation
│   │   ├── __init__.py
│   │   ├── upload_to_docs.py          # Markdown -> Google Docs
│   │   ├── upload_to_confluence.py    # Markdown -> Confluence page
│   │   ├── download_doc.py            # Google Doc -> markdown
│   │   ├── build_document_registry.py # Multi-source document index
│   │   └── link_extractor.py          # Extract/categorize links from docs
│   ├── automation/                     # Scheduled runners and watchers
│   │   ├── __init__.py
│   │   ├── daily_update_runner.py     # Daily/hourly pipeline orchestrator
│   │   ├── auto_commit_runner.py      # Scheduled git auto-commit
│   │   ├── clipboard_watcher.py       # Watch clipboard for transcripts
│   │   ├── save_clipboard.py          # One-shot clipboard save
│   │   └── read_agent_markers.py      # Read pac markers from Drive docs
│   ├── publishing/                     # Push content to platforms
│   │   ├── __init__.py
│   │   ├── push_confluence_news.py    # Daily Confluence updates
│   │   ├── push_confluence_weekly.py  # Weekly Confluence summary
│   │   ├── create_members_sheet.py    # Google Sheets team directory
│   │   └── draft_jira_tickets.py      # Draft Jira tickets from backlog
│   └── tests/                          # pytest test suite
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_agent_marker.py
│       ├── test_build_document_registry.py
│       ├── test_confluence_news.py
│       ├── test_confluence_weekly.py
│       ├── test_download_doc.py
│       ├── test_draft_jira_tickets.py
│       ├── test_gdrive_sync.py
│       ├── test_google_write_guard.py
│       ├── test_link_extractor.py
│       ├── test_members_sheet.py
│       ├── test_read_agent_markers.py
│       ├── test_upload_to_confluence.py
│       └── test_upload_to_docs.py
├── playbooks/                           # TPM situation playbooks
│   ├── README.md
│   ├── remote-onboarding.md
│   ├── cross-timezone-collaboration.md
│   ├── decision-documentation.md
│   └── reducing-status-meetings.md
├── showcase/                            # Demo prompts and examples
│   ├── sample-queries.md
│   ├── before-after.md                 # Side-by-side workflow comparison
│   └── quick-wins.md
├── project-template/                    # Template used by setup.sh
│   ├── .gitignore
│   ├── README.md
│   ├── .cursor/
│   │   └── mcp.json
│   └── docs/
│       ├── PROGRAM_OVERVIEW.md
│       ├── DASHBOARD.md
│       ├── BACKLOG.md
│       ├── context/
│       │   └── README.md
│       └── templates/
│           └── STAKEHOLDER_UPDATE.md
├── example/                             # Fully populated fictional program
│   ├── README.md
│   └── docs/
│       ├── PROGRAM_OVERVIEW.md
│       ├── DASHBOARD.md
│       ├── BACKLOG.md
│       ├── context/
│       │   └── daily-digests/
│       │       ├── 2026-03-07.md
│       │       ├── 2026-03-10.md
│       │       └── 2026-03-11.md
│       └── templates/
│           └── stakeholder-update-2026-03-07.md
└── .planning/                           # Planning documents (untracked)
    └── codebase/
        ├── ARCHITECTURE.md
        └── STRUCTURE.md
```

## Key Locations

### Where to find things

| Looking for... | Location |
|----------------|----------|
| How the project works | `docs/01-problem-statement.md` through `docs/10-privacy-model.md` |
| Python scripts | `scripts/` (five subdirectories: core, sync, content, automation, publishing) |
| Script tests | `scripts/tests/test_*.py` |
| Agent configuration templates | `agents/claude-code/`, `agents/cursor/`, `agents/cline/` |
| Memory Bank protocol | `agents/memory-bank/README.md` and `agents/memory-bank/example/` |
| Document templates | `templates/` |
| TPM playbooks | `playbooks/` |
| Demo/showcase content | `showcase/` |
| Project bootstrapper | `setup.sh` (reads from `project-template/`) |
| Package metadata | `pyproject.toml` |
| CI configuration | `.github/workflows/test.yml` |
| Case study narrative | `case-study/wolt-crm-migration.md` |
| Example program | `example/` |
| Formatting rules | `agents/formatting-standards.md` |

### Where to add things

| Adding... | Put it in |
|-----------|-----------|
| New script | `scripts/<group>/` matching its function, add test in `scripts/tests/` |
| New methodology doc | `docs/` with `NN-` prefix |
| New template | `templates/` |
| New playbook | `playbooks/` |
| New agent config | `agents/<agent-name>/` |
| New showcase | `showcase/` |

## Naming Conventions

### Files

- **Markdown docs:** lowercase, hyphen-separated: `cross-timezone-collaboration.md`
- **Numbered docs:** `NN-description.md` (e.g., `01-problem-statement.md`)
- **Python scripts:** lowercase, underscore-separated: `auto_commit_runner.py`
- **Python tests:** `test_<module_name>.py` matching the script they test
- **Agent templates:** `<format>.template` (e.g., `cursorrules.template`, `CLAUDE.md.template`)
- **Memory Bank files:** camelCase markdown: `activeContext.md`, `sessionLog.md`

### Code

- **Package namespace:** `scripts.*` (e.g., `scripts.core.preflight_check`)
- **Agent marker namespace:** `pac` prefix on all marker keys (e.g., `pac_agent`, `pac_created_at_utc`)
- **CLI entry point:** `pac` (defined in `pyproject.toml` as `[project.scripts]`)
- **Environment variables:** uppercase, underscore-separated, prefixed by service or `PAC_` (e.g., `ATLASSIAN_DOMAIN`, `PAC_WRITE_GUARD`, `PAC_PROJECT_ROOT`)

### Git

- **Commit format:** `type: description` (types: `docs`, `feat`, `fix`, `chore`, `script`)
- **Branches:** `main` is the primary branch

## Python Package Structure

The project is a pip-installable package defined in `pyproject.toml`:
- Package name: `palimpsest`
- Version: `0.1.0`
- Python requirement: `>=3.10`
- Setuptools discovers packages matching `scripts*`
- Single console script: `pac` -> `scripts.core.preflight_check:main`
- Dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `requests`, `python-dotenv`
- Optional: `PyPDF2` (pdf), `pytest` + `pytest-cov` (dev)

## Test Structure

Tests in `scripts/tests/` are pure pytest with no external service dependencies. Each test file corresponds to a script module. `conftest.py` provides shared fixtures. The CI matrix tests against Python 3.10, 3.11, and 3.12.

Test files and their targets:
- `test_agent_marker.py` -> `core/agent_marker.py`
- `test_google_write_guard.py` -> `core/google_write_guard.py`
- `test_gdrive_sync.py` -> `sync/gdrive_sync.py`
- `test_upload_to_confluence.py` -> `content/upload_to_confluence.py`
- `test_upload_to_docs.py` -> `content/upload_to_docs.py`
- `test_download_doc.py` -> `content/download_doc.py`
- `test_build_document_registry.py` -> `content/build_document_registry.py`
- `test_link_extractor.py` -> `content/link_extractor.py`
- `test_confluence_news.py` -> `publishing/push_confluence_news.py`
- `test_confluence_weekly.py` -> `publishing/push_confluence_weekly.py`
- `test_members_sheet.py` -> `publishing/create_members_sheet.py`
- `test_draft_jira_tickets.py` -> `publishing/draft_jira_tickets.py`
- `test_read_agent_markers.py` -> `automation/read_agent_markers.py`
