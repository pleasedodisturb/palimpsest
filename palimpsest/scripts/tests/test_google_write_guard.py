"""Tests for core/google_write_guard.py — write permission enforcement."""

import pytest
from unittest.mock import patch


def test_parse_allowlist_basic(load_module):
    mod = load_module("core/google_write_guard.py")
    result = mod._parse_allowlist("a, b, c")
    assert result == {"a", "b", "c"}


def test_parse_allowlist_empty(load_module):
    mod = load_module("core/google_write_guard.py")
    assert mod._parse_allowlist("") == set()


def test_parse_allowlist_with_whitespace(load_module):
    mod = load_module("core/google_write_guard.py")
    result = mod._parse_allowlist("  my-drive , folder123 ,  ")
    assert result == {"my-drive", "folder123"}


def test_parse_allowlist_single(load_module):
    mod = load_module("core/google_write_guard.py")
    result = mod._parse_allowlist("my-drive")
    assert result == {"my-drive"}


def test_write_blocked_without_env(load_module):
    mod = load_module("core/google_write_guard.py")
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(SystemExit):
            mod.require_write_enabled("test write")


def test_write_allowed_with_env(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    with mock_env(ALLOW_GOOGLE_WRITE="1"):
        # Should not raise
        mod.require_write_enabled("test write")


def test_write_blocked_with_allowlist_mismatch(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    with mock_env(ALLOW_GOOGLE_WRITE="1", GOOGLE_WRITE_ALLOWLIST="folder-a,folder-b"):
        with pytest.raises(SystemExit):
            mod.require_write_enabled("test", target_ids=["folder-c"])


def test_write_allowed_with_matching_allowlist(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    with mock_env(ALLOW_GOOGLE_WRITE="1", GOOGLE_WRITE_ALLOWLIST="folder-a,folder-b"):
        mod.require_write_enabled("test", target_ids=["folder-a"])


def test_write_my_drive_default(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    with mock_env(ALLOW_GOOGLE_WRITE="1", GOOGLE_WRITE_ALLOWLIST="my-drive"):
        # No target_ids, allow_my_drive=True (default) → targets={"my-drive"}
        mod.require_write_enabled("test")


def test_write_my_drive_blocked(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    with mock_env(ALLOW_GOOGLE_WRITE="1", GOOGLE_WRITE_ALLOWLIST="folder-a"):
        with pytest.raises(SystemExit):
            mod.require_write_enabled("test")  # defaults to my-drive, not in allowlist


def test_truthy_values_for_allow(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    for val in ["1", "true", "True", "yes", "y", "YES"]:
        with mock_env(ALLOW_GOOGLE_WRITE=val):
            mod.require_write_enabled(f"test with {val}")


def test_falsy_values_block(load_module, mock_env):
    mod = load_module("core/google_write_guard.py")
    for val in ["0", "false", "no", "nope", ""]:
        with mock_env(ALLOW_GOOGLE_WRITE=val):
            with pytest.raises(SystemExit):
                mod.require_write_enabled(f"test with {val}")
