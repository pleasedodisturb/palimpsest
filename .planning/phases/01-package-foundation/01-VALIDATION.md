---
phase: 1
slug: package-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=7.4.0 (already configured) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ scripts/tests/ -v --tb=short` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ scripts/tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | CLI-01 | smoke | `pip install -e . && pal --help` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | CLI-02 | unit | `python -m pytest tests/test_cli.py::test_help_flags -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | CLI-03 | unit | `python -m pytest tests/test_cli.py::test_version -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | CLI-04 | unit | `python -m pytest tests/test_cli.py::test_rich_output -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | CLI-05 | unit | `python -m pytest tests/test_cli.py::test_error_handling -x` | ❌ W0 | ⬜ pending |
| 1-01-06 | 01 | 1 | DIST-02 | unit | `python -m pytest tests/test_content.py::test_bundled_content -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/` directory at project root (new, for palimpsest package tests)
- [ ] `tests/test_cli.py` — CLI smoke tests using `typer.testing.CliRunner`
- [ ] `tests/test_content.py` — Content bundling validation
- [ ] `tests/test_errors.py` — Error display formatting
- [ ] `tests/conftest.py` — Shared fixtures for new test suite
- [ ] Update `pyproject.toml` `[tool.pytest.ini_options]` testpaths to include `tests/`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rich-styled output looks good in terminal | CLI-04 | Visual inspection needed beyond "Rich is used" | Run `pal --help` and `pal --version` in terminal, verify colored output renders correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
