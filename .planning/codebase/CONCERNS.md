# Concerns: Tech Debt, Bugs, Security, Performance, Fragile Areas

## Static Analysis

The `sonar-bugs.json` at the repo root reports **0 issues** -- the codebase is clean from SonarQube's perspective. The concerns below are from manual review.

---

## 1. Code Duplication

### 1.1 Authentication boilerplate copied across 7+ files

The `get_credentials()` function for Google OAuth is duplicated nearly verbatim in:

- `scripts/content/upload_to_docs.py` (line 41)
- `scripts/content/download_doc.py` (line 29)
- `scripts/content/build_document_registry.py` (line 73)
- `scripts/publishing/create_members_sheet.py` (line 68)
- `scripts/sync/gdrive_sync.py` (line 83)
- `scripts/sync/calendar_sync.py` (line 52)
- `scripts/core/google_auth.py` (line 57) -- the canonical version
- `scripts/core/preflight_check.py` (lines 60-108) -- inline variant

Each copy uses different token paths, scopes, and error handling patterns. Any bug fix or improvement must be applied to all copies. The `scripts/core/service_clients.py` file has `get_google_drive_client()` which could serve as the central auth layer, but content scripts do not use it.

**Impact**: High maintenance burden. Divergence risk when one copy gets fixed and others do not.

### 1.2 Confluence auth duplicated across files

The `_require_env` / `get_auth` / `_get_auth` pattern for Atlassian credentials is repeated in:

- `scripts/content/upload_to_confluence.py` (lines 25-40)
- `scripts/publishing/push_confluence_news.py` (lines 33-69)
- `scripts/publishing/push_confluence_weekly.py` (lines 34-69)
- `scripts/core/service_clients.py` (lines 110-120) -- the AtlassianClient class

The publishing scripts do not use the `AtlassianClient` from `service_clients.py`, despite it being designed for exactly this purpose.

### 1.3 Agent marker logic duplicated

Agent marker setting exists in two independent implementations:
- `scripts/core/agent_marker.py` -- the canonical module with `set_confluence_marker()`
- `scripts/publishing/push_confluence_news.py` (line 136) and `scripts/publishing/push_confluence_weekly.py` (line 110) -- inline `set_agent_marker()` functions

The inline versions are simpler and do not use the same marker schema (missing `uid`, `source`, `user` fields).

---

## 2. Security Concerns

### 2.1 Shell injection in daily_update_runner.py

`scripts/automation/daily_update_runner.py` line 86 uses `shell=True` when the command is a string:

```python
result = subprocess.run(command, shell=True, ...)
```

If any step command is constructed from user-supplied or environment-variable input, this is a shell injection vector. Currently all commands are hardcoded lists (safe), but the code path exists and someone could pass a string command in the future.

### 2.2 osascript notification injection

`scripts/automation/clipboard_watcher.py` (line 81) and `scripts/automation/save_clipboard.py` (line 34) construct AppleScript strings from unsanitized input:

```python
script = f'display notification "{message}" with title "{title}"'
subprocess.run(["osascript", "-e", script], ...)
```

If `message` or `title` contains double quotes or AppleScript metacharacters, this could break or be exploited. The `filepath.name` used as notification content is generally safe but could contain crafted filenames.

### 2.3 Token files stored in scripts directory

Token files (`token.json`, `token_docs.json`, `token_sheets.json`) are expected to live in `scripts/core/` alongside the scripts. While `.gitignore` excludes `token*.json`, the pattern of storing credentials in the source tree (even gitignored) increases the risk of accidental commit or exposure via backup tools.

### 2.4 scheduled_sync.py auto-pushes to remote

`scripts/sync/scheduled_sync.py` line 310 runs `git add -A` followed by `git push` by default. This could accidentally commit and push sensitive files that are not yet in `.gitignore`. The `--dry-run` and `--no-push` flags exist but are not the default.

### 2.5 Confluence credentials in two auth schemes

`scripts/sync/scheduled_sync.py` (line 215) uses `base64.b64encode` to manually construct a Basic auth header, while all other scripts use `requests`' built-in `auth=(email, token)` tuple. The manual encoding is unnecessary and error-prone.

---

## 3. Deprecated / Unsafe API Usage

### 3.1 datetime.utcnow() is deprecated

`scripts/sync/calendar_sync.py` line 138 uses `datetime.utcnow()`, which is deprecated since Python 3.12. Other files in the codebase correctly use `datetime.now(timezone.utc)`.

### 3.2 Naive datetime usage throughout gdrive_sync.py and calendar_sync.py

Several files use `datetime.now()` without timezone info:

- `scripts/sync/gdrive_sync.py` lines 262, 374, 509
- `scripts/sync/calendar_sync.py` lines 248, 348
- `scripts/sync/scheduled_sync.py` lines 64, 268, 313

This produces naive datetimes that are ambiguous. The rest of the codebase uses `datetime.now(timezone.utc)` consistently, making these outliers.

### 3.3 MD5 used for deduplication hashing

`scripts/content/build_document_registry.py` line 402 uses `hashlib.md5()` for URL deduplication. While not a security vulnerability (not used for cryptographic purposes), it is flagged by security scanners. SHA-256 would avoid the false positive.

---

## 4. Error Handling and Resilience

### 4.1 Broad exception catching

Over 30 instances of `except Exception` across the scripts directory. Most catch-all handlers silently swallow errors with only a print statement, making debugging difficult. Notable cases:

- `scripts/sync/gdrive_sync.py` line 78: `except Exception:` with no variable -- completely silent failure in config loading
- `scripts/core/agent_marker.py` line 99: Silent failure when reading existing Drive properties
- `scripts/automation/read_agent_markers.py` line 190: Silent failure on Confluence property read

### 4.2 sys.exit(1) as error handling

Multiple scripts call `sys.exit(1)` deep inside library functions (not just `main()`), making them impossible to use as importable modules:

- `scripts/core/google_write_guard.py` line 76: `sys.exit(1)` inside `_abort()`
- `scripts/content/upload_to_docs.py` line 75: `sys.exit(1)` inside `check_write_guard()`
- `scripts/content/download_doc.py` line 75: `sys.exit(1)` inside `extract_doc_id()`

These should raise exceptions that the CLI layer catches.

### 4.3 No retry logic for API calls

All HTTP requests to Google, Atlassian, Slack, and Glean APIs have no retry mechanism. Transient network errors or rate limiting will cause immediate failure. The `requests` library calls use `timeout=20-30` but no retry/backoff.

### 4.4 Confluence API error responses not logged

In `scripts/core/service_clients.py` line 137, the `AtlassianClient._request()` method returns `None` on any non-200 response without logging the status code or response body. Same pattern in `SlackClient._request()` (line 271) and `GleanClient._request()` (line 490).

---

## 5. Fragile Code Areas

### 5.1 Google Docs table index arithmetic

`scripts/content/upload_to_docs.py` lines 268-320 manually compute document indices for table cells using hardcoded offset arithmetic (`cell_index += 1` for tableRow, tableCell, paragraph, newline). This is extremely fragile -- any change in Google Docs API behavior or table structure assumptions will produce corrupted documents with misplaced text.

### 5.2 Confluence regex-based HTML manipulation

Multiple scripts use regex to parse and modify Confluence storage format HTML:

- `scripts/publishing/push_confluence_news.py` lines 254-262 (date pattern in panels)
- `scripts/publishing/push_confluence_news.py` lines 279-287 (panel extraction)
- `scripts/publishing/push_confluence_weekly.py` lines 241-244 (CW panel pattern)
- `scripts/sync/scheduled_sync.py` lines 260-265 (CONTEXT_INDEX table replacement)

Regex-based HTML parsing is inherently brittle. Any change in panel structure, whitespace, or Confluence's output format will break these operations silently.

### 5.3 setup.sh heredoc quoting

`setup.sh` uses multiple heredoc styles (`<< 'EOF'` and `<< READMEEOF`) within the same script. The `READMEEOF` variant on line 86 does not use single quotes, meaning shell variables inside the README template will be expanded. Currently `\$` escaping is used correctly, but adding new template content without escaping would silently produce wrong output.

### 5.4 Inline markdown regex in upload_to_docs.py

The `_tokenise_inline()` function in `scripts/content/upload_to_docs.py` (lines 143-187) uses a combined regex with numbered groups (groups 1-9) to parse bold, italic, code, and links. Adding any new inline format requires renumbering all groups. The pattern also does not handle nested formatting (e.g., bold text inside a link).

---

## 6. Missing Features and Gaps

### 6.1 No root .gitignore entry for .run_state.json

`scripts/automation/daily_update_runner.py` writes `.run_state.json` to the scripts directory (line 27), but the root `.gitignore` only excludes `run_state.json` (without the dot prefix). The actual file written is `.run_state.json`, which would not be gitignored.

### 6.2 No write guard on Confluence scripts

`scripts/content/upload_to_docs.py` has a `check_write_guard()` that requires `PAC_WRITE_GUARD=1`. The Confluence upload script (`scripts/content/upload_to_confluence.py`) has no equivalent guard. The publishing scripts (`push_confluence_news.py`, `push_confluence_weekly.py`) also lack write guards, and `--dry-run` is optional.

### 6.3 pyproject.toml Python version mismatch

`pyproject.toml` declares `requires-python = ">=3.10"` and classifiers for 3.10-3.12, but the venv is built with Python 3.14. The CI matrix tests 3.10-3.12 only. If any code uses 3.13+ features, it will pass locally but fail in CI.

### 6.4 Empty screenpipe directory

The `screenpipe/` directory exists at the repo root but is empty. It appears to be a placeholder for a Screenpipe integration that was never implemented.

### 6.5 No test coverage for automation and publishing scripts

The `scripts/tests/` directory has tests for core and content modules but no test files for:
- `scripts/automation/auto_commit_runner.py`
- `scripts/automation/clipboard_watcher.py`
- `scripts/automation/save_clipboard.py`
- `scripts/automation/daily_update_runner.py`
- `scripts/sync/scheduled_sync.py`
- `scripts/sync/calendar_sync.py`
- `scripts/publishing/push_confluence_news.py`
- `scripts/publishing/push_confluence_weekly.py`
- `scripts/publishing/create_members_sheet.py`

These are the scripts most likely to break silently in production since they interact with external services.

### 6.6 CI does not run linting or type checking

The `.github/workflows/test.yml` pipeline runs `pytest` only. No `ruff`, `mypy`, `flake8`, or any other static analysis step. The `sonar-bugs.json` appears to be from a one-time manual run.

---

## 7. Design Concerns

### 7.1 Module-level singleton state in service_clients.py

`scripts/core/service_clients.py` line 54 instantiates a module-level `status = ServiceStatus()` singleton. This means importing the module and calling any `get_*_client()` function mutates global state. Two callers checking different services would see each other's status results. Not thread-safe.

### 7.2 Token path inconsistency

Different scripts look for tokens in different locations:
- `scripts/core/preflight_check.py`: `SCRIPT_DIR / "token.json"` (i.e., `scripts/core/token.json`)
- `scripts/content/upload_to_docs.py`: `SCRIPT_DIR / "token_docs.json"` where SCRIPT_DIR is `scripts/` (parent of content)
- `scripts/sync/gdrive_sync.py`: `SCRIPT_DIR / "token.json"` where SCRIPT_DIR is `scripts/sync/`
- `scripts/sync/calendar_sync.py`: `SCRIPT_DIR / os.getenv("GOOGLE_TOKEN_FILE", "token.json")` where SCRIPT_DIR is `scripts/sync/`

This means scripts expect tokens in different directories depending on which subdirectory they live in. The `SCRIPT_DIR` resolution varies: some use `Path(__file__).resolve().parent` (own directory), others use `.parent.parent` (scripts root).

### 7.3 daily_update_runner.py exit code mismatch

`scripts/automation/daily_update_runner.py` line 328: the main function exits with code 1 if **any** step failed, but all steps in `get_daily_steps()` have `allow_fail=True`. So the pipeline always returns results where all failures are "allowed," yet the exit code still reflects failure. This makes the script unsuitable for cron monitoring.

### 7.4 scheduled_sync.py references wrong script paths

`scripts/sync/scheduled_sync.py` line 128 runs `gdrive_sync.py` with `cwd=SCRIPT_DIR` (which is `scripts/sync/`), so the path resolves correctly. But line 145 runs `link_extractor.py` with the same `cwd=SCRIPT_DIR`, and `link_extractor.py` lives in `scripts/content/`, not `scripts/sync/`. This will fail at runtime with `FileNotFoundError`.

Similarly, line 183 runs `build_document_registry.py` with `cwd=SCRIPT_DIR` -- also wrong.

---

## 8. Documentation Debt

### 8.1 CLAUDE.md references non-existent preflight_check entry point

`CLAUDE.md` documents running `python scripts/core/preflight_check.py --service all`, but `pyproject.toml` also defines a `pac` entry point mapped to `scripts.core.preflight_check:main`. These two invocation methods have different Python path setups and may behave differently.

### 8.2 docs/08-known-issues.md acknowledges unfixed problems

The known-issues document explicitly calls out script maintenance debt, duplicated logic, and naming remnants -- confirming that the concerns identified in this analysis are known and accepted trade-offs, not oversights.

---

## Priority Summary

| Priority | Area | Files Affected |
|----------|------|----------------|
| High | Auth code duplication | 7+ files across scripts/ |
| High | Wrong script paths in scheduled_sync.py | `scripts/sync/scheduled_sync.py` |
| High | Token path inconsistency | Multiple scripts |
| Medium | Broad exception swallowing | 30+ locations |
| Medium | No write guard on Confluence scripts | 3 publishing scripts |
| Medium | No retry/backoff on API calls | All service client code |
| Medium | No tests for automation/publishing | 9 untested scripts |
| Medium | Naive datetime usage | 3 sync scripts |
| Low | MD5 for deduplication | `build_document_registry.py` |
| Low | Shell injection path in daily_update_runner | `daily_update_runner.py` |
| Low | Module-level singleton state | `service_clients.py` |
| Low | CI lacks linting/type checking | `.github/workflows/test.yml` |
