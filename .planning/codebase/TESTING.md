# Testing Patterns

## Framework and Configuration

- **Framework**: pytest (>=7.4.0), with pytest-cov (>=4.0.0) available as a dev dependency.
- **Configuration** in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["scripts/tests"]
  pythonpath = ["scripts"]
  ```
- **CI**: GitHub Actions (`.github/workflows/test.yml`) runs on push/PR to `main` across Python 3.10, 3.11, and 3.12. Command: `python -m pytest scripts/tests/ -v --tb=short`.

## Test File Structure

All tests live in `scripts/tests/` as a flat directory (no subdirectories mirroring the source tree).

| Test File | Source Module | Focus |
|-----------|--------------|-------|
| `scripts/tests/test_agent_marker.py` | `scripts/core/agent_marker.py` | Marker building, env config, Drive/Confluence marker ops |
| `scripts/tests/test_google_write_guard.py` | `scripts/core/google_write_guard.py` | Write permission enforcement, allowlist parsing |
| `scripts/tests/test_upload_to_confluence.py` | `scripts/content/upload_to_confluence.py` | Markdown-to-Confluence XHTML conversion |
| `scripts/tests/test_upload_to_docs.py` | `scripts/content/upload_to_docs.py` | Markdown tokenization, Google Docs API request building |
| `scripts/tests/test_link_extractor.py` | `scripts/content/link_extractor.py` | URL extraction, categorization, deduplication |
| `scripts/tests/test_build_document_registry.py` | `scripts/content/build_document_registry.py` | Document classification, dedup, markdown generation |
| `scripts/tests/test_download_doc.py` | `scripts/content/download_doc.py` | Google Doc ID extraction from URLs |
| `scripts/tests/test_gdrive_sync.py` | `scripts/sync/gdrive_sync.py` | File categorization, Drive query building |
| `scripts/tests/test_draft_jira_tickets.py` | `scripts/publishing/draft_jira_tickets.py` | Jira ticket draft building, markdown preview |
| `scripts/tests/test_confluence_news.py` | `scripts/publishing/push_confluence_news.py` | Daily panel generation, weekly archiving |
| `scripts/tests/test_confluence_weekly.py` | `scripts/publishing/push_confluence_weekly.py` | Week info calculation, summary generation |
| `scripts/tests/test_members_sheet.py` | `scripts/publishing/create_members_sheet.py` | Channel data building, master view dedup |
| `scripts/tests/test_read_agent_markers.py` | `scripts/automation/read_agent_markers.py` | Drive/Confluence ID parsing, type detection |

## Shared Fixtures

Defined in `scripts/tests/conftest.py`:

### `load_module`

Dynamically loads a Python module by relative path (relative to `scripts/`). This is the primary mechanism for importing source modules in tests, avoiding import-time side effects from modules that call `load_dotenv()` or import Google API libraries at module level.

```python
def test_something(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("# Hello")
```

Every single test function in the codebase uses this fixture. The module is loaded fresh per call using `importlib.util.spec_from_file_location`.

### `mock_env`

Wraps `unittest.mock.patch.dict(os.environ, ...)` for clean environment variable mocking:

```python
def test_with_env(mock_env):
    with mock_env(ATLASSIAN_DOMAIN="test.atlassian.net"):
        # env vars are set here
        pass
```

## Test Design Patterns

### Pure Function Testing (Dominant Pattern)

The majority of tests exercise pure or near-pure functions -- functions that take input and return output without external I/O. This is the design philosophy: scripts separate their logic (categorization, conversion, building) from their I/O (API calls, file system), and tests target only the logic layer.

Examples:
- `test_categorize_file_planning` tests filename classification
- `test_inline_bold` tests markdown-to-HTML inline conversion
- `test_build_drafts_basic` tests Jira payload construction
- `test_parse_drive_id_from_file_url` tests URL parsing

### Environment Variable Behavior Testing

Tests that verify env-var-driven behavior use the `mock_env` fixture and `patch.dict("os.environ", ...)`:

```python
def test_markers_enabled_truthy_values(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    for val in ["1", "true", "True", "yes", "y", "YES"]:
        with mock_env(ENABLE_AGENT_MARKERS=val):
            assert mod._markers_enabled() is True, f"Expected True for '{val}'"
```

A recurring pattern is testing both truthy and falsy value sets to verify the boolean parsing logic.

### SystemExit Testing

Functions that call `sys.exit(1)` on invalid input are tested with `pytest.raises(SystemExit)`:

```python
def test_write_blocked_without_env(load_module):
    mod = load_module("core/google_write_guard.py")
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(SystemExit):
            mod.require_write_enabled("test write")
```

### Mock Service Objects

For tests involving Google Drive API calls, `unittest.mock.MagicMock` is used to create mock service objects with chained method calls:

```python
def test_upsert_drive_marker_success(load_module, mock_env):
    mod = load_module("core/agent_marker.py")
    mock_service = MagicMock()
    mock_service.files().get().execute.return_value = {"appProperties": {}}
    mock_service.files().update().execute.return_value = {}
    with mock_env(ENABLE_AGENT_MARKERS="1", USER="bob", PAC_AGENT="test"):
        result = mod.upsert_drive_marker(mock_service, "file123", "upload", "test.md")
    assert result is True
```

### Temporary File System (pytest built-in)

Tests that need file I/O use pytest's `tmp_path` fixture:

```python
def test_extract_from_json(load_module, tmp_path):
    mod = load_module("content/link_extractor.py")
    data = {"url": "https://github.com/user/repo"}
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(data))
    links = mod.extract_from_json(str(json_file))
    assert len(links) == 2
```

### Module State Mutation

Some tests directly mutate module-level state (dictionaries) for setup:

```python
def test_build_channel_data_unknown_member(load_module):
    mod = load_module("publishing/create_members_sheet.py")
    mod.MEMBER_DB.clear()
    channels = {
        "test": {"description": "", "members": ["unknown@example.com"]},
    }
    result = mod.build_channel_data(channels)
```

This works because `load_module` creates a fresh module instance each time.

## What Is NOT Tested

- **API integration**: No tests make real HTTP calls to Google, Atlassian, Slack, or Glean APIs.
- **CLI end-to-end**: No tests invoke `main()` functions or test argparse behavior.
- **OAuth flows**: Authentication and token refresh are not tested.
- **`scripts/core/service_clients.py`**: The service client classes have no dedicated test file.
- **`scripts/core/preflight_check.py`**: No tests for the preflight checker.
- **`scripts/core/google_auth.py`**: No tests (OAuth flow script).
- **`scripts/sync/` runners**: `calendar_sync.py`, `scheduled_sync.py` have no tests.
- **`scripts/automation/` runners**: `auto_commit_runner.py`, `daily_update_runner.py`, `clipboard_watcher.py`, `save_clipboard.py` have no tests.

## Assertion Style

Tests use plain `assert` statements (no `self.assertEqual`). Assertions are straightforward value checks:

```python
assert result == {"a", "b", "c"}
assert marker["action"] == "upload"
assert "<h1>Title</h1>" in result
assert len(links) == 2
assert result is True
assert "target_id" not in marker
```

Custom assertion messages are used occasionally for parameterized-style loops:

```python
assert mod._markers_enabled() is True, f"Expected True for '{val}'"
```

## Test Naming

Test functions follow `test_<function_or_feature>_<scenario>` naming:

- `test_categorize_link_confluence` -- function + input category
- `test_build_marker_with_target_id` -- function + variant
- `test_write_blocked_without_env` -- behavior + condition
- `test_parse_allowlist_with_whitespace` -- function + edge case
- `test_markers_enabled_truthy_values` -- function + value class

## Running Tests

```bash
# Full suite
python -m pytest scripts/tests/ -v

# Single file
python -m pytest scripts/tests/test_agent_marker.py -v

# With coverage
python -m pytest scripts/tests/ --cov=scripts --cov-report=term-missing
```

## Test Count

15 test files (including `__init__.py` and `conftest.py`), 13 of which contain test functions. Approximate total: ~120 test functions across all files.
