# Code Conventions

## Project Layout

All Python code lives under `scripts/`, organized into five subpackages:

| Package | Purpose |
|---------|---------|
| `scripts/core/` | Shared infrastructure: auth, write guards, agent markers, service clients |
| `scripts/content/` | Document operations: download, upload, link extraction, registry |
| `scripts/sync/` | Google Drive and calendar synchronization |
| `scripts/automation/` | Scheduled runners, clipboard tools, agent marker readers |
| `scripts/publishing/` | Confluence/Jira publishing: news, weekly updates, ticket drafts |
| `scripts/tests/` | All tests (flat, not mirroring the package tree) |

The project is installable via `pip install -e .` with entry point `pac` mapping to `scripts.core.preflight_check:main`.

## File Structure Pattern

Every script follows the same template:

1. Shebang line: `#!/usr/bin/env python3`
2. Module docstring documenting purpose, usage, and required env vars
3. Imports (stdlib, then third-party, then local -- no explicit grouping enforced)
4. Module-level constants
5. Internal helpers (prefixed with `_`)
6. Public API functions
7. CLI via `argparse` in a `main()` function
8. Guard: `if __name__ == "__main__": sys.exit(main())`

Sections within files are separated by comment banners:

```python
# ---------------------------------------------------------------------------
# Section Name
# ---------------------------------------------------------------------------
```

or with `=` banners in `scripts/core/service_clients.py`:

```python
# =============================================================================
# GOOGLE DRIVE
# =============================================================================
```

## Naming Conventions

- **Files**: `snake_case.py` -- descriptive verb-noun names (`upload_to_confluence.py`, `build_document_registry.py`, `read_agent_markers.py`)
- **Functions**: `snake_case` -- public functions use bare names, private helpers use `_` prefix (`_inline`, `_now_utc`, `_markers_enabled`, `_parse_allowlist`)
- **Constants**: `UPPER_SNAKE_CASE` (`MARKER_VERSION`, `CONFLUENCE_MARKER_KEY`, `SCOPES`, `SCRIPT_DIR`)
- **Classes**: `PascalCase` -- used sparingly, only in `scripts/core/service_clients.py` (`AtlassianClient`, `SlackClient`, `GleanClient`, `GitHubClient`, `ServiceStatus`)
- **Env var keys**: `UPPER_SNAKE_CASE`, namespaced where relevant (`PAC_AGENT`, `ENABLE_AGENT_MARKERS`, `ALLOW_GOOGLE_WRITE`, `ATLASSIAN_DOMAIN`)
- **Agent namespace**: `pac` -- all agent markers, property keys, and automation tags use this prefix (e.g., `pac.agent_marker`, `pac_created_at_utc`)

## Type Annotations

Type hints are used in `scripts/core/` modules (the shared infrastructure layer):

```python
def build_marker(
    action: str,
    source: str,
    target_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
```

Content, sync, automation, and publishing scripts generally omit type annotations, using docstrings for parameter documentation instead.

All `scripts/core/` files include `from __future__ import annotations` for forward-reference support; other packages do not.

## Docstrings

Every module has a docstring. Functions use a mix of styles:

- **Core modules** (`scripts/core/`): reStructuredText-style parameter docs in the docstring, sometimes with `Parameters` sections using NumPy-style formatting (seen in `google_write_guard.py`).
- **Other modules**: Google-style `Args:` / `Returns:` blocks are the dominant pattern.

```python
def categorize_link(url):
    """Categorize a URL into a known service or 'other'.

    Args:
        url: URL string.

    Returns:
        str: Category name (e.g., 'confluence', 'github', 'other').
    """
```

## Configuration Pattern

All configuration is environment-variable-driven. No hardcoded credentials, domains, or project-specific identifiers appear in code.

The standard pattern for required config:

```python
def _require_env(name):
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Environment variable {name} is not set.")
        sys.exit(1)
    return value
```

Optional config uses `os.getenv()` with defaults:

```python
os.getenv("PAC_AGENT", "cursor")
os.getenv("GLEAN_API_URL", "https://api.glean.com/api/v1")
```

Several modules use `python-dotenv` with a graceful fallback when the package is not installed:

```python
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False
```

## Error Handling

The codebase uses three error handling strategies depending on context:

1. **Hard exit for user-facing errors** (missing config, bad input): `sys.exit(1)` with a printed `ERROR:` message.
2. **Return-value signaling for API operations**: functions return `False`, `None`, or empty collections on failure rather than raising.
3. **Broad `except Exception` with debug logging** for non-critical failures in marker operations:
   ```python
   except Exception as exc:
       _debug(f"Drive marker update failed for {file_id}: {exc}")
       return False
   ```

Warning-level messages use `print(f"WARNING: ...")`.

There are no custom exception classes. The `google_write_guard.py` module is the only place that raises `SystemExit` as a deliberate control flow mechanism (tested with `pytest.raises(SystemExit)`).

## Import Patterns

- Google API libraries are imported inside functions that use them, not at module level, allowing scripts to be imported/tested without the full dependency tree:
  ```python
  def read_drive_marker(file_id):
      from google.auth.transport.requests import Request
      from google.oauth2.credentials import Credentials
      from googleapiclient.discovery import build
  ```
- `requests` is imported at module level in some files (`scripts/content/upload_to_confluence.py`) and deferred in others (`scripts/core/agent_marker.py`).
- Conditional availability checks:
  ```python
  try:
      from google.oauth2.credentials import Credentials
      GOOGLE_API_AVAILABLE = True
  except Exception:
      GOOGLE_API_AVAILABLE = False
  ```

## Service Client Architecture

`scripts/core/service_clients.py` implements a factory pattern:

- Each service has a client class (`AtlassianClient`, `SlackClient`, etc.) with an `available` boolean attribute and a private `_request()` method.
- Factory functions return `None` when credentials are missing: `get_atlassian_client() -> Optional[AtlassianClient]`.
- A module-level `ServiceStatus` singleton tracks availability across all services.
- All HTTP calls include timeouts (typically 20-30 seconds).

## CLI Pattern

Every executable script uses `argparse` with a `main()` function:

```python
def main():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument(...)
    args = parser.parse_args()
    # ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Some scripts support `--dry-run`, `--nonfatal`, and `--attempt-fix` flags.

## Write Safety

Google Drive/Docs writes require explicit opt-in via `ALLOW_GOOGLE_WRITE=1` and optional allowlisting via `GOOGLE_WRITE_ALLOWLIST`. This is enforced by `scripts/core/google_write_guard.py` which calls `sys.exit(1)` when writes are not permitted.

Truthy value parsing is consistent across the codebase:

```python
value.strip().lower() in {"1", "true", "yes", "y"}
```

## Path Handling

Paths use `pathlib.Path` throughout. The common anchor pattern:

```python
SCRIPT_DIR = Path(__file__).resolve().parent
```

Token and credential files are resolved relative to `SCRIPT_DIR`, never hardcoded to absolute paths.

## Dependencies

Defined in `pyproject.toml`:

- **Runtime**: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `requests`, `python-dotenv`
- **Optional (pdf)**: `PyPDF2`
- **Dev**: `pytest`, `pytest-cov`
- **Python**: `>=3.10`
