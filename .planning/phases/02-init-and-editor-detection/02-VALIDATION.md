---
phase: 2
slug: init-and-editor-detection
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=7.4.0 (already configured from Phase 1) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ scripts/tests/ -v --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ scripts/tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | INIT-01 | integration | `python -m pytest tests/test_init.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | INIT-02 | unit | `python -m pytest tests/test_editors.py -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 0 | INIT-07 | unit | `python -m pytest tests/test_manifest.py -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 01 | 1 | INIT-01 | integration | `python -m pytest tests/test_init.py::test_scaffold_creates_structure -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 01 | 1 | INIT-01 | integration | `python -m pytest tests/test_init.py::test_init_new_directory -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 01 | 1 | INIT-01 | integration | `python -m pytest tests/test_init.py::test_init_existing_repo -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 01 | 1 | INIT-02 | unit | `python -m pytest tests/test_editors.py::test_detect_cursor -x` | ❌ W0 | ⬜ pending |
| 02-03-02 | 01 | 1 | INIT-02 | unit | `python -m pytest tests/test_editors.py::test_detect_claude_code -x` | ❌ W0 | ⬜ pending |
| 02-03-03 | 01 | 1 | INIT-02 | unit | `python -m pytest tests/test_editors.py::test_detect_cline -x` | ❌ W0 | ⬜ pending |
| 02-04-01 | 01 | 1 | INIT-03 | unit | `python -m pytest tests/test_editors.py::test_generate_cursor_config -x` | ❌ W0 | ⬜ pending |
| 02-04-02 | 01 | 1 | INIT-03 | unit | `python -m pytest tests/test_editors.py::test_generate_claude_config -x` | ❌ W0 | ⬜ pending |
| 02-04-03 | 01 | 1 | INIT-03 | unit | `python -m pytest tests/test_editors.py::test_generate_cline_configs -x` | ❌ W0 | ⬜ pending |
| 02-05-01 | 01 | 2 | INIT-04 | integration | `python -m pytest tests/test_init.py::test_idempotent_reinit -x` | ❌ W0 | ⬜ pending |
| 02-05-02 | 01 | 2 | INIT-04 | integration | `python -m pytest tests/test_init.py::test_reinit_conflict_detection -x` | ❌ W0 | ⬜ pending |
| 02-06-01 | 01 | 1 | INIT-05 | unit | `python -m pytest tests/test_init.py::test_editors_override_flag -x` | ❌ W0 | ⬜ pending |
| 02-07-01 | 01 | 1 | INIT-06 | integration | `python -m pytest tests/test_init.py::test_memory_bank_created -x` | ❌ W0 | ⬜ pending |
| 02-08-01 | 01 | 1 | INIT-07 | unit | `python -m pytest tests/test_manifest.py::test_manifest_creation -x` | ❌ W0 | ⬜ pending |
| 02-08-02 | 01 | 1 | INIT-07 | unit | `python -m pytest tests/test_manifest.py::test_checksum_verification -x` | ❌ W0 | ⬜ pending |
| 02-09-01 | 01 | 2 | CLI-06 | integration | `python -m pytest tests/test_init.py::test_dry_run_no_writes -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_init.py` — Init command integration tests (uses tmp_path fixtures for isolated filesystem)
- [ ] `tests/test_editors.py` — Editor detection and config generation unit tests
- [ ] `tests/test_manifest.py` — Manifest creation, reading, checksum verification
- [ ] `tests/test_privacy.py` — Privacy profile selection, .gitignore generation
- [ ] Update `tests/conftest.py` — Add fixtures for temporary project directories, mock editor dotfiles

*Testing strategy: Integration tests use `tmp_path` pytest fixture. Editor detection tests create fake dotfiles. Use `typer.testing.CliRunner` for CLI-level tests (established in Phase 1). `--dry-run` tests verify no files written.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rich console output formatting | INIT-01 | Visual layout verification | Run `pal init` in a test project and verify tree output renders correctly |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
